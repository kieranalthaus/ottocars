# Otto's Auto Parts — Website

Static landing page for Otto's Auto Parts, hosted on GitHub Pages.

## Deploy to GitHub Pages

1. **Create a GitHub repository**
   - Go to github.com → New repository
   - Name it (e.g. `ottocars`) — keep it public for free GitHub Pages hosting

2. **Initialize and push**
   ```bash
   cd /path/to/ottocars_website
   git init
   git add .
   git commit -m "Initial site"
   git remote add origin https://github.com/YOUR_USERNAME/ottocars.git
   git push -u origin main
   ```

3. **Enable GitHub Pages**
   - Repository → Settings → Pages
   - Source: **Deploy from a branch** → branch: `main`, folder: `/ (root)`
   - Save — your site will be live at `https://YOUR_USERNAME.github.io/ottocars/`

## Adding items for sale (Google Form → website)

Otto adds cars and parts by filling out a Google Form on his phone. Every night a
GitHub Action reads the form's response sheet, downloads the photos, and updates
the site, so nobody has to touch GitHub.

```
Google Form ──► Google Sheet + photos in Drive ──► nightly GitHub Action
(Otto's phone)                                    scripts/sync_inventory.py
                                                            │
                                  data/inventory.json + assets/images/items/
                                                            │
                                               commit ──► GitHub Pages rebuild
```

- **Cars** appear at the top of the *Cars for Sale* panel; **parts** appear in *Parts for Sale*.
- Each item gets its own page (`item.html?id=…`) with all photos, the description,
  and a "View on eBay" button if a link was given.
- Every run rebuilds the list from the **whole** sheet, so editing a row, deleting a
  row, or ticking *Sold* all take effect on the next run.

### One-time setup (about 30 minutes)

**1. Create the Google Form** at [forms.google.com](https://forms.google.com). The
script finds each column by the **bold** word(s) in its question title, so keep those words:

| Question title | Type | Settings |
|---|---|---|
| **Car or part**? | Multiple choice | Options `Car` and `Part`. Required |
| **Title** | Short answer | Required. Help text: "e.g. Mercedes W113 wiper motor" |
| **Price** | Short answer | Required. Help text: "e.g. 450 or 450 OBO" |
| **Description** | Paragraph | Optional |
| **eBay** link | Short answer | Optional. Help text: "Paste the eBay link if it's listed there" |
| **Photo**s | File upload | Required. Allow only specific file types → Image; max 10 files; max 100 MB |

Plain-number prices become `$1,200`; anything else (`450 OBO`, `EUR 14,900`) is shown
as typed. The first photo becomes the main picture. Text copied from the eBay app's
Share button ("Check out this item… https://ebay.us/…") works; the script pulls out the link.

Then, in the form's **Settings**:
- *Responses → Collect email addresses → Verified* (lets the script check that it's
  Otto posting; see `ALLOWED_EMAILS` below).
- *Presentation → Confirmation message*: "Thanks! It will be on the website by tomorrow morning."

On the **Responses** tab, click **Link to Sheets** → create a new spreadsheet.

**2. Submit one test response with a photo.** This creates the Drive folder the photos
go into, named "*&lt;form name&gt;* (File responses)".

**3. Create a Google service account.** This lets the GitHub Action read the sheet and
photos without anyone's password.
1. At [console.cloud.google.com](https://console.cloud.google.com), create a project (e.g. "ottocars").
2. *APIs & Services → Library*: enable **Google Sheets API** and **Google Drive API**.
3. *IAM & Admin → Service Accounts → Create service account* (no roles needed). Open it →
   *Keys → Add key → Create new key → JSON*. A `.json` key file downloads.
4. Copy the service account's email address (`something@your-project.iam.gserviceaccount.com`).

**4. Share both of these with that email as Viewer** (in Google Drive; untick "Notify people"):
- the response spreadsheet
- the "*&lt;form name&gt;* (File responses)" folder

**5. Add repository secrets** under GitHub repo → *Settings → Secrets and variables → Actions*:

| Secret | Value |
|---|---|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | the entire contents of the downloaded JSON key file |
| `GOOGLE_SHEET_ID` | from the sheet's URL: `docs.google.com/spreadsheets/d/`**`THIS_PART`**`/edit` |
| `ALLOWED_EMAILS` | Otto's Google account email (comma-separate to add yours for testing) |

`ALLOWED_EMAILS` is technically optional, but without it **anyone who finds the form link
can post to the site**. Once the key is saved as a secret, delete the key file. Never commit it.

**6. Test it.** Go to repo → *Actions → Update Inventory from Google Form → Run workflow*.
About a minute after it finishes, GitHub Pages redeploys and the test item appears.
Then delete the test row from the sheet and run it again to clear it.

**7. Set up Otto's phone.**
- Google Forms requires respondents to be **signed in to a Google account** to upload
  photos. If Otto doesn't have one, you can create one with his existing email address
  (choose "Use your existing email" at sign-up; no Gmail needed). Sign him in in the
  phone's browser.
- Open the form link and add it to his home screen (Safari: *Share → Add to Home Screen*;
  Chrome: *⋮ → Add to Home screen*) so it's one tap away.

### Day to day (for Otto)

- **Add something:** tap the form icon, fill it in, add photos, tap *Submit*. It's on the
  site the next morning.
- **Something sold:** in the response sheet (Google Sheets app), tick the **Sold** checkbox
  on that row, or delete the row. *One-time prep:* type `Sold` as the header of the first
  empty column to the right of the form's columns, select the cells below it, then
  *Insert → Checkbox*.
- **Fix a typo:** edit the cell in the sheet.

### Good to know

- **Faster than nightly:** change the `cron` line in `.github/workflows/update_inventory.yml`,
  e.g. `'0 */3 * * *'` for every 3 hours. Runs with nothing new don't commit anything.
- **GitHub pauses scheduled workflows after 60 days with no repo activity** (public repos).
  It emails a warning first. Re-enable the workflow in the Actions tab. Any commit,
  including the Action's own commit when Otto adds an item, resets the clock.
- Photos are resized (1400px, plus a 600px thumbnail), turned upright, converted from
  iPhone HEIC if needed, and stripped of metadata such as GPS location before they're committed.
- If a photo can't be downloaded, the item is still published without it, the photo is
  retried on the next run, and the run shows a warning in the Actions tab.
- If the sheet can't be read (bad secret, renamed question), the run fails and the site is left unchanged.
- To run it locally: `pip install -r scripts/requirements.txt`, then
  `GOOGLE_SERVICE_ACCOUNT_JSON="$(cat path/to/key.json)" GOOGLE_SHEET_ID=… python3 scripts/sync_inventory.py`

## Before deploying — fill in placeholders

Open `index.html` and replace every `[...]` placeholder:

| Placeholder | Value |
|---|---|
| `[MERCEDES_PARTS_CATALOG_URL]` | URL to parts catalog |
| `[EBAY_SELLER_PROFILE_URL]` | `https://www.ebay.com/usr/YOUR_SELLER_ID` |
| `[PHONE_NUMBER]` | e.g. `(555) 123-4567` |
| `[EMAIL_USER]` | part before `@` in your email |
| `[EMAIL_DOMAIN]` | part after `@` in your email |
| Business address lines | actual address |

Open `assets/js/main.js` and set:
```js
const EBAY_SELLER_ID   = 'your_actual_seller_id';
const EBAY_PROFILE_URL = 'https://www.ebay.com/usr/your_actual_seller_id';
```

## Add header images

Drop your photos into `assets/images/` as:
- `welcome-image-1.jpg`
- `welcome-image-2.jpg`

## Optional: Automated eBay listings via GitHub Actions

If the RSS-to-JSON proxy in `main.js` becomes unreliable, switch to the GitHub Actions approach:

1. Register at [developer.ebay.com](https://developer.ebay.com) and create an app to get an **App ID**.
2. Add two repository secrets (Settings → Secrets → Actions):
   - `EBAY_APP_ID` — your eBay App ID
   - `EBAY_SELLER_ID` — your eBay seller username
3. The workflow (`.github/workflows/update_ebay.yml`) runs daily and commits `listings.json`.
4. Update `main.js` to fetch `/listings.json` instead of the RSS proxy:
   ```js
   const data = await fetch('listings.json').then(r => r.json());
   ```

## Local preview

```bash
python3 -m http.server 8000
# open http://localhost:8000
```
