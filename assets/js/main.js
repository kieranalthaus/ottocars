// ── Configuration ──────────────────────────────────────────────
// Replace these with the actual seller values before deploying.
const EBAY_SELLER_ID   = 'dino23';
const EBAY_PROFILE_URL = 'https://www.ebay.com/str/dino23';

// Public RSS-to-JSON proxy (no API key required)
const RSS_FEED_URL = `https://www.ebay.com/sch/i.html?_ssn=${EBAY_SELLER_ID}&_rss=1`;
const PROXY_URL    = `https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(RSS_FEED_URL)}`;

// ── Demo Listings Data (from live eBay store) ───────────────────
const DEMO_LISTINGS = [
  { title: '2 SET ORIGINAL MERCEDES W113 DOOR PANEL, HARD POCKET, black/Tan 230 250 SL', price: '$1,100.00', image: 'https://i.ebayimg.com/images/g/Cu8AAeSwl7NpA8mQ/s-l500.jpg', link: 'https://www.ebay.com/itm/286907691875' },
  { title: 'Mercedes C107 W108 W109 W111 W116 R107 350 450 0280100012 Pressure Sensor', price: '$590.00', image: 'https://i.ebayimg.com/images/g/mtwAAeSwJEJpov8H/s-l500.jpg', link: 'https://www.ebay.com/itm/287170304045' },
  { title: '356 Porsche Steering Wheel 356A Original 420mm 42cm Coupe Cabriolet', price: '$890.00', image: 'https://i.ebayimg.com/images/g/kfwAAeSwWK1psJFB/s-l500.jpg', link: 'https://www.ebay.com/itm/327038391984' },
  { title: 'Mercedes-Benz R107 450 SL 1971-1977 NARDI Wood Steering Wheel 360mm', price: '$590.00', image: 'https://i.ebayimg.com/images/g/ZQoAAeSwwLBpPI7P/s-l500.jpg', link: 'https://www.ebay.com/itm/287007125536' },
  { title: 'MERCEDES BENZ ANZA 560SL R107 Exhaust Manifold / Muffler Rear', price: '$490.00', image: 'https://i.ebayimg.com/images/g/Ix8AAeSwTUtobSH~/s-l500.jpg', link: 'https://www.ebay.com/itm/286695739982' },
  { title: 'Mercedes Benz W113 Alternator AL64X', price: '$390.00', image: 'https://i.ebayimg.com/images/g/iR0AAeSw6~tpsJWu/s-l500.jpg', link: 'https://www.ebay.com/itm/327038400908' },
  { title: 'Porsche 911 SC 1982-1983 ECU Bosch Jetronic 0280800055', price: '$280.00', image: 'https://i.ebayimg.com/images/g/pZYAAeSwppFpbkaU/s-l500.jpg', link: 'https://www.ebay.com/itm/287086347799' },
  { title: 'Mercedes Benz Interior Door Handle Pull #1367660009 Fits Many 300 Models', price: '$190.00', image: 'https://i.ebayimg.com/images/g/ERMAAeSwyQlpYm1r/s-l500.jpg', link: 'https://www.ebay.com/itm/326949956423' },
  { title: '0280170015 NEW Cold Start Valve Fits Porsche 914 VW Type 3', price: '$250.00', image: 'https://i.ebayimg.com/images/g/Vg0AAeSw7NhpLyK8/s-l500.jpg', link: 'https://www.ebay.com/itm/286984958766' },
  { title: 'Porsche 911 Euro Used Taillight Lens', price: '$190.00', image: 'https://i.ebayimg.com/images/g/qnUAAeSwAI9pL1Nd/s-l500.jpg', link: 'https://www.ebay.com/itm/326895895832' },
];

// ── eBay Listings ───────────────────────────────────────────────
function loadEbayListings() {
  const container = document.getElementById('ebay-listings');

  const scroll = document.createElement('div');
  scroll.className = 'listings-scroll';

  DEMO_LISTINGS.forEach(item => {
    const card = document.createElement('article');
    card.className = 'listing-card';
    card.innerHTML = `
      <img
        src="${escapeHtml(item.image)}"
        alt="${escapeHtml(item.title)}"
        loading="lazy"
        onerror="this.style.display='none'"
      />
      <div class="listing-info">
        <span class="listing-title">${escapeHtml(item.title)}</span>
        <span class="listing-price">${escapeHtml(item.price)}</span>
      </div>
      <a class="listing-link" href="${escapeHtml(item.link)}" target="_blank" rel="noopener">
        View on eBay
      </a>
    `;
    scroll.appendChild(card);
  });

  container.innerHTML = '';
  container.appendChild(scroll);

  // "View all" link after the scroll
  const viewAll = document.createElement('p');
  viewAll.style.marginTop = '0.75rem';
  viewAll.style.fontFamily = 'var(--font-ui)';
  viewAll.style.fontSize = '0.9rem';
  viewAll.innerHTML = `<a href="${escapeHtml(EBAY_PROFILE_URL)}" target="_blank" rel="noopener">View all listings on eBay &rarr;</a>`;
  container.appendChild(viewAll);
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
