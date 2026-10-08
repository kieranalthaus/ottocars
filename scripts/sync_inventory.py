"""
Syncs Otto's for-sale items from the Google Form's response sheet into the site.

Every run reads ALL rows of the sheet (so edits, deleted rows, and rows marked
"Sold" are reflected), downloads any photos it hasn't seen before from Google
Drive, and writes data/inventory.json. Photos are resized for the web, rotated
upright, and stripped of metadata (e.g. GPS location). Photos that no longer
belong to any listed item are deleted. Run nightly by update_inventory.yml.

Required environment variables (GitHub Secrets):
  GOOGLE_SERVICE_ACCOUNT_JSON — full contents of the service account's JSON key.
                                The account needs Viewer access to the response
                                sheet and to the form's "(File responses)" folder.
  GOOGLE_SHEET_ID             — the ID in the sheet's URL: /spreadsheets/d/<ID>/edit

Optional:
  ALLOWED_EMAILS — comma-separated Google accounts allowed to publish. Requires
                   the form to collect verified email addresses. Strongly
                   recommended so a stranger with the form link can't post.
  SHEET_RANGE    — A1 range to read (default: columns A–Z of the first tab).
"""

import hashlib
import io
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote

from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

register_heif_opener()  # iPhone photos may arrive as HEIC

ROOT          = Path(__file__).resolve().parent.parent
OUTPUT_FILE   = ROOT / "data" / "inventory.json"
PHOTO_DIR     = ROOT / "assets" / "images" / "items"
PHOTO_URL     = "assets/images/items"   # same folder, relative to the site root

FULL_SIZE     = 1400   # longest edge, px — detail page
THUMB_SIZE    = 600    # longest edge, px — cards and thumbnails
JPEG_QUALITY  = 80

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

# Each field is found by a word that appears in its form question title,
# matched case-insensitively against the sheet's header row.
COLUMN_KEYWORDS = {
    "timestamp":   "timestamp",
    "email":       "email",         # "Email Address" — added by "Collect email addresses"
    "category":    "car or part",
    "title":       "title",
    "price":       "price",
    "description": "description",
    "ebay":        "ebay",
    "photos":      "photo",
    "sold":        "sold",          # optional column added by hand to the sheet
}
REQUIRED_COLUMNS = ["timestamp", "title", "price", "description", "photos"]

DRIVE_ID_RE = re.compile(r"(?:[?&]id=|/d/)([\w-]{20,})")
EBAY_URL_RE = re.compile(r"(?:https?://)?(?:[\w-]+\.)*ebay\.[a-z.]{2,6}/\S*", re.IGNORECASE)
PRICE_RE    = re.compile(r"\$?\s*(\d[\d,]*)(\.\d{1,2})?")
NOT_SOLD    = {"", "false", "no", "n"}


def warn(message: str) -> None:
    # "::warning::" makes the message show up on the GitHub Actions run summary.
    print(f"::warning::{message}", file=sys.stderr)


def get_session() -> AuthorizedSession:
    info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    credentials = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return AuthorizedSession(credentials)


def fetch_rows(session: AuthorizedSession) -> list[list[str]]:
    sheet_id = os.environ["GOOGLE_SHEET_ID"].strip()
    sheet_range = os.environ.get("SHEET_RANGE") or "A:Z"
    response = session.get(
        f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{quote(sheet_range)}",
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("values", [])


def map_columns(header: list[str]) -> dict[str, int]:
    columns = {}
    for field, keyword in COLUMN_KEYWORDS.items():
        for index, title in enumerate(header):
            if keyword in title.lower():
                columns[field] = index
                break
    missing = [field for field in REQUIRED_COLUMNS if field not in columns]
    if missing:
        sys.exit(
            f"Sheet is missing columns for {missing}. Found headers: {header}. "
            "Rename the form questions or update COLUMN_KEYWORDS."
        )
    return columns


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50].rstrip("-") or "item"


def format_price(raw: str) -> str:
    """'1200' or '$1,200' → '$1,200'. Anything else ('450 OBO', 'EUR 14,900') is kept as typed."""
    match = PRICE_RE.fullmatch(raw)
    if not match:
        return raw
    amount = float((match.group(1) + (match.group(2) or "")).replace(",", ""))
    return f"${amount:,.0f}" if amount.is_integer() else f"${amount:,.2f}"


def extract_ebay_url(raw: str) -> str:
    """Pulls the link out of text like 'Check out this item on eBay https://ebay.us/abc'."""
    match = EBAY_URL_RE.search(raw)
    if not match:
        if raw:
            warn(f"Ignoring eBay link that doesn't look like an eBay URL: {raw!r}")
        return ""
    url = match.group(0).rstrip(".,;)")
    return url if url.lower().startswith(("http://", "https://")) else f"https://{url}"


def save_photo(session: AuthorizedSession, file_id: str) -> bool:
    """Downloads one Drive photo and writes web-sized copies. Returns False on failure."""
    full_path  = PHOTO_DIR / f"{file_id}.jpg"
    thumb_path = PHOTO_DIR / f"{file_id}-thumb.jpg"
    if full_path.exists() and thumb_path.exists():
        return True

    try:
        response = session.get(
            f"https://www.googleapis.com/drive/v3/files/{file_id}",
            params={"alt": "media"},
            timeout=120,
        )
        response.raise_for_status()
        with Image.open(io.BytesIO(response.content)) as original:
            image = ImageOps.exif_transpose(original).convert("RGB")
    except Exception as exc:  # one bad photo shouldn't take down the whole sync
        warn(f"Could not download/convert photo {file_id}: {exc}")
        return False

    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    for path, size in ((full_path, FULL_SIZE), (thumb_path, THUMB_SIZE)):
        copy = image.copy()
        copy.thumbnail((size, size))
        # No exif= argument, so camera metadata (incl. GPS) is not written.
        copy.save(path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    print(f"  downloaded photo {file_id}")
    return True


def build_items(session: AuthorizedSession, rows: list[list[str]]) -> tuple[list[dict], set[str]]:
    header, *records = rows
    columns = map_columns(header)
    allowed = {e.strip().lower() for e in os.environ.get("ALLOWED_EMAILS", "").split(",") if e.strip()}
    if allowed and "email" not in columns:
        sys.exit("ALLOWED_EMAILS is set but the sheet has no email column. "
                 "Turn on 'Collect email addresses' in the form settings.")
    if not allowed:
        warn("ALLOWED_EMAILS is not set — anyone with the form link can publish to the site.")

    items, kept_photo_ids, used_ids = [], set(), set()

    # Newest submissions first.
    for number, record in reversed(list(enumerate(records, start=2))):
        def cell(field: str) -> str:
            index = columns.get(field)
            # The Sheets API drops trailing empty cells, so rows can be short.
            return record[index].strip() if index is not None and index < len(record) else ""

        title = cell("title")
        if not title:
            continue
        if cell("sold").lower() not in NOT_SOLD:
            print(f"Row {number}: skipping sold item {title!r}")
            continue
        if allowed and cell("email").lower() not in allowed:
            warn(f"Row {number}: skipping {title!r} — submitted by an address not in ALLOWED_EMAILS")
            continue

        print(f"Row {number}: {title}")
        photo_ids = list(dict.fromkeys(DRIVE_ID_RE.findall(cell("photos"))))  # dedupe, keep order
        kept_photo_ids.update(photo_ids)
        photos = [
            {"full": f"{PHOTO_URL}/{pid}.jpg", "thumb": f"{PHOTO_URL}/{pid}-thumb.jpg"}
            for pid in photo_ids
            if save_photo(session, pid)
        ]

        # Readable and unique: title slug + short hash of the submission time.
        item_id = f"{slugify(title)}-{hashlib.sha1(cell('timestamp').encode()).hexdigest()[:6]}"
        while item_id in used_ids:
            item_id += "x"
        used_ids.add(item_id)

        items.append({
            "id":          item_id,
            "category":    "car" if cell("category").lower().startswith("car") else "part",
            "title":       title,
            "price":       format_price(cell("price")),
            "description": cell("description"),
            "ebay":        extract_ebay_url(cell("ebay")),
            "photos":      photos,
        })

    return items, kept_photo_ids


def prune_photos(kept_photo_ids: set[str]) -> None:
    if not PHOTO_DIR.exists():
        return
    for path in PHOTO_DIR.glob("*.jpg"):
        if path.stem.removesuffix("-thumb") not in kept_photo_ids:
            path.unlink()
            print(f"  removed unused photo {path.name}")


def main() -> None:
    session = get_session()
    rows = fetch_rows(session)
    if not rows:
        sys.exit("Sheet returned no rows (not even a header) — check GOOGLE_SHEET_ID and SHEET_RANGE.")

    items, kept_photo_ids = build_items(session, rows)
    prune_photos(kept_photo_ids)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {len(items)} items to {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
