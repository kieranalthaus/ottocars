# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Otto's modernized landing page — a static site for an eBay automotive parts seller, hosted on GitHub Pages. Recreates `http://2-0-0-0.com/otto/` as a clean, minimal, responsive site.

**Stack:** Plain HTML5, CSS3, Vanilla JavaScript — no build tools, no frameworks, no npm.

## Development

Since this is a static site with no build step, open `index.html` directly in a browser or use a simple local server:

```bash
python3 -m http.server 8000
# or
npx serve .
```

There are no tests, linters, or build commands.

## Architecture

```
index.html              # Single-page site with <header>, <main>, <section>, <footer>
assets/
  css/style.css         # CSS variables for theming; mobile-first with flexbox/grid
  js/main.js            # Async eBay listings fetch + DOM injection
  images/               # welcome-image-1.jpg, welcome-image-2.jpg
.github/workflows/
  update_ebay.yml       # (Optional) Daily GitHub Action: fetches eBay Browse API,
                        #   commits listings.json for client-side consumption
```

## eBay Listings Integration

Two strategies (prefer the simpler one that works):

1. **Frontend-only (preferred):** `main.js` fetches the seller's eBay RSS feed through a public RSS-to-JSON proxy (no API keys exposed). Renders cards with image, title, price, and link into `<div id="ebay-listings">`.

2. **GitHub Actions fallback:** `update_ebay.yml` runs a Python script daily, writes `listings.json` to the repo, and `main.js` fetches that static file instead. Use this if the RSS proxy approach proves unreliable.

Always include a fallback in `main.js` for fetch failures — show a direct link to the eBay seller profile page.

## Design Constraints

- Bare-bones aesthetic: black, white, grays, one accent color for links
- Mobile-responsive (no horizontal scroll on small screens)
- Contact email should be obfuscated in HTML (e.g., split string or CSS reverse trick) to reduce spam harvesting
- No heavy dependencies — keep page weight minimal for GitHub Pages hosting
