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
