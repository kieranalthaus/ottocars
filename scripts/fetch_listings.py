"""
Fetches active eBay listings for a seller via the Browse API and writes
listings.json to the repo root. Run by the update_ebay.yml GitHub Action.

Required GitHub Secrets:
  EBAY_APP_ID    — your eBay developer App ID (client credentials)
  EBAY_SELLER_ID — the eBay seller username to query
"""

import json
import os
import sys
import requests

EBAY_APP_ID   = os.environ["EBAY_APP_ID"]
SELLER_ID     = os.environ["EBAY_SELLER_ID"]
OUTPUT_FILE   = "listings.json"

TOKEN_URL     = "https://api.ebay.com/identity/v1/oauth2/token"
BROWSE_URL    = "https://api.ebay.com/buy/browse/v1/item_summary/search"


def get_access_token() -> str:
    response = requests.post(
        TOKEN_URL,
        auth=(EBAY_APP_ID, ""),   # client_credentials flow; no secret needed for Browse
        data={"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def fetch_listings(token: str) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    params  = {
        "q":          f"seller:{SELLER_ID}",
        "limit":      "50",
        "fieldgroups": "MATCHING_ITEMS",
    }
    response = requests.get(BROWSE_URL, headers=headers, params=params, timeout=15)
    response.raise_for_status()
    items = response.json().get("itemSummaries", [])
    return [
        {
            "title":     item.get("title", ""),
            "price":     item.get("price", {}).get("value", ""),
            "currency":  item.get("price", {}).get("currency", "USD"),
            "url":       item.get("itemWebUrl", ""),
            "image":     item.get("image", {}).get("imageUrl", ""),
            "condition": item.get("condition", ""),
        }
        for item in items
    ]


def main():
    try:
        token    = get_access_token()
        listings = fetch_listings(token)
        with open(OUTPUT_FILE, "w") as f:
            json.dump(listings, f, indent=2)
        print(f"Wrote {len(listings)} listings to {OUTPUT_FILE}")
    except requests.HTTPError as exc:
        print(f"HTTP error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
