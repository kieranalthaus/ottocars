// ── Configuration ──────────────────────────────────────────────
// Replace these with the actual seller values before deploying.
const EBAY_SELLER_ID   = 'dino23';
const EBAY_PROFILE_URL = 'https://www.ebay.com/str/dino23';

// Public RSS-to-JSON proxy (no API key required)
const RSS_FEED_URL = `https://www.ebay.com/sch/i.html?_ssn=${EBAY_SELLER_ID}&_rss=1`;
const PROXY_URL    = `https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(RSS_FEED_URL)}`;

// ── eBay Listings ───────────────────────────────────────────────
async function loadEbayListings() {
  const container = document.getElementById('ebay-listings');

  try {
    const response = await fetch(PROXY_URL);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const data = await response.json();
    if (data.status !== 'ok' || !Array.isArray(data.items) || data.items.length === 0) {
      throw new Error('No listings returned');
    }

    const grid = document.createElement('div');
    grid.className = 'listings-grid';

    data.items.forEach(item => {
      // eBay RSS items carry price in the description; extract it with a regex fallback.
      const priceMatch = (item.description || '').match(/\$[\d,]+\.?\d*/);
      const price = priceMatch ? priceMatch[0] : '';

      const card = document.createElement('article');
      card.className = 'listing-card';
      card.innerHTML = `
        <img
          src="${escapeHtml(item.thumbnail || item.enclosure?.link || '')}"
          alt="${escapeHtml(item.title)}"
          loading="lazy"
          onerror="this.style.display='none'"
        />
        <div class="listing-info">
          <span class="listing-title">${escapeHtml(item.title)}</span>
          ${price ? `<span class="listing-price">${escapeHtml(price)}</span>` : ''}
        </div>
        <a class="listing-link" href="${escapeHtml(item.link)}" target="_blank" rel="noopener">
          View on eBay
        </a>
      `;
      grid.appendChild(card);
    });

    container.innerHTML = '';
    container.appendChild(grid);

  } catch (err) {
    console.error('eBay listings fetch failed:', err);
    container.innerHTML = `
      <p class="listings-error">
        Could not load listings automatically.
        <a href="${escapeHtml(EBAY_PROFILE_URL)}" target="_blank" rel="noopener">
          Click here to view all active listings on eBay →
        </a>
      </p>
    `;
  }
}

// ── Email deobfuscation ─────────────────────────────────────────
function revealEmail() {
  const link = document.querySelector('.email-link');
  if (!link) return;
  const user   = link.dataset.user;
  const domain = link.dataset.domain;
  if (!user || !domain) return;
  const address = `${user}@${domain}`;
  link.href        = `mailto:${address}`;
  link.textContent = address;
}

// ── Utilities ───────────────────────────────────────────────────
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ── Init ────────────────────────────────────────────────────────
document.getElementById('year').textContent = new Date().getFullYear();
revealEmail();
loadEbayListings();
