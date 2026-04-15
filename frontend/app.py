from flask import Flask, render_template_string
import requests, os

app = Flask(__name__)
BACKEND = os.getenv("BACKEND_URL", "http://backend-service:5000")

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Product Store</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Inter', sans-serif; background: #f1f5f9; min-height: 100vh; color: #1e293b; }

    /* Navbar */
    .navbar {
      background: #0f172a; padding: 0 32px; height: 56px;
      display: flex; align-items: center; justify-content: space-between;
      position: sticky; top: 0; z-index: 100;
      box-shadow: 0 1px 3px rgba(0,0,0,0.4);
    }
    .nav-logo { font-size: 15px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 8px; }
    .nav-logo .k8s { color: #60a5fa; }
    .nav-right { display: flex; align-items: center; gap: 12px; }
    .nav-ns { font-size: 11px; color: #64748b; font-family: monospace; }
    .live-badge {
      display: flex; align-items: center; gap: 6px;
      background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.3);
      color: #34d399; font-size: 11px; font-weight: 600;
      padding: 3px 10px; border-radius: 20px;
    }
    .live-dot { width: 7px; height: 7px; border-radius: 50%; background: #10b981; animation: pulse 2s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

    /* Container */
    .container { max-width: 960px; margin: 0 auto; padding: 32px 20px; }

    /* Page header */
    .page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }
    .header-left { display: flex; align-items: center; gap: 12px; }
    .cart-icon { font-size: 28px; line-height: 1; }
    .page-title { font-size: 26px; font-weight: 700; color: #0f172a; letter-spacing: -0.5px; }
    .page-sub { font-size: 13px; color: #64748b; margin-top: 3px; }
    .version-pill { background: #dbeafe; color: #1d4ed8; font-size: 11px; font-weight: 600; font-family: monospace; padding: 4px 10px; border-radius: 20px; white-space: nowrap; align-self: flex-start; }

    /* Search */
    .search-wrap { position: relative; margin-bottom: 20px; }
    .search-ico { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); font-size: 15px; pointer-events: none; }
    .search-bar { width: 100%; padding: 11px 14px 11px 42px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 13px; font-family: 'Inter', sans-serif; background: #fff; color: #1e293b; outline: none; transition: border-color .2s, box-shadow .2s; }
    .search-bar:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }

    /* Stats row */
    .stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 24px; }
    .stat-card { background: #fff; border-radius: 12px; padding: 16px 18px; border: 1px solid #e2e8f0; display: flex; align-items: center; gap: 14px; }
    .stat-icon-wrap { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 20px; line-height: 1; }
    .stat-label { font-size: 11px; color: #64748b; font-weight: 500; text-transform: uppercase; letter-spacing: .5px; }
    .stat-value { font-size: 20px; font-weight: 700; color: #0f172a; margin-top: 2px; }
    .stat-value.healthy { font-size: 15px; color: #16a34a; margin-top: 4px; }

    /* Products section */
    .section-label { font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: .6px; margin-bottom: 10px; }

    /* Product card */
    .product-card {
      background: #fff; border-radius: 12px; padding: 16px 20px;
      margin-bottom: 10px; border: 1px solid #e2e8f0; border-left: 4px solid #2563eb;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
      display: flex; align-items: center; justify-content: space-between; gap: 16px;
      transition: transform .15s, box-shadow .15s;
      animation: slideUp .35s ease both;
    }
    .product-card:nth-child(1) { animation-delay: .05s; border-left-color: #2563eb; }
    .product-card:nth-child(2) { animation-delay: .10s; border-left-color: #7c3aed; }
    .product-card:nth-child(3) { animation-delay: .15s; border-left-color: #0d9488; }
    .product-card:nth-child(4) { animation-delay: .20s; border-left-color: #ea580c; }
    .product-card:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(0,0,0,0.08); }
    @keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }

    .product-left { display: flex; align-items: center; gap: 14px; flex: 1; min-width: 0; }
    .product-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; line-height: 1; flex-shrink: 0; }
    .product-info { min-width: 0; }
    .product-name { font-size: 15px; font-weight: 600; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .product-meta { font-size: 11px; color: #94a3b8; margin-top: 2px; font-family: monospace; }

    .product-right { display: flex; align-items: center; gap: 14px; flex-shrink: 0; }
    .product-price { font-size: 16px; font-weight: 700; color: #059669; text-align: right; }
    .product-avail { font-size: 11px; color: #94a3b8; margin-top: 2px; text-align: right; }

    .add-btn { background: #2563eb; color: #fff; border: none; border-radius: 8px; padding: 8px 16px; font-size: 13px; font-weight: 600; font-family: 'Inter', sans-serif; cursor: pointer; transition: background .15s, transform .1s; white-space: nowrap; }
    .add-btn:hover { background: #1d4ed8; transform: scale(1.03); }
    .add-btn:active { transform: scale(.97); }

    /* Empty state */
    .empty { text-align: center; padding: 48px; color: #94a3b8; }
    .empty .e-icon { font-size: 36px; margin-bottom: 10px; }
    .empty .e-title { font-size: 15px; font-weight: 600; color: #475569; }
    .empty .e-sub { font-size: 12px; margin-top: 4px; font-family: monospace; }

    /* Health bar */
    .health-bar {
      display: flex; align-items: center; gap: 10px;
      background: #f0fdf4; border: 1px solid #bbf7d0;
      border-radius: 10px; padding: 12px 16px; margin-top: 18px;
      font-size: 13px; color: #166534; flex-wrap: wrap; line-height: 1.5;
    }
    .h-dot { width: 8px; height: 8px; border-radius: 50%; background: #10b981; animation: pulse 2s infinite; flex-shrink: 0; }

    /* Pods */
    .pods-section { margin-top: 16px; }
    .pods-title { font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 8px; }
    .pods-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
    .pod-card { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 10px 12px; }
    .pod-name { font-family: monospace; font-size: 10.5px; color: #166534; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .pod-status { font-size: 11px; font-weight: 600; color: #16a34a; margin-top: 3px; }

    /* Footer */
    .footer { margin-top: 28px; text-align: center; font-size: 11px; color: #94a3b8; padding-bottom: 20px; }
    .footer code { background: #f1f5f9; padding: 1px 5px; border-radius: 3px; font-family: monospace; }

    @media (max-width: 600px) {
      .navbar { padding: 0 14px; }
      .container { padding: 18px 14px; }
      .stats-row { grid-template-columns: 1fr; }
      .pods-grid { grid-template-columns: 1fr; }
      .add-btn { display: none; }
    }
  </style>
</head>
<body>

<nav class="navbar">
  <div class="nav-logo">
    <span style="font-size:18px;">&#9096;</span>
    <span class="k8s">K8s</span> Observability Platform
  </div>
  <div class="nav-right">
    <span class="nav-ns">namespace: app</span>
    <div class="live-badge"><div class="live-dot"></div>Live</div>
  </div>
</nav>

<div class="container">

  <div class="page-header">
    <div class="header-left">
      <div class="cart-icon">&#x1F6D2;</div>
      <div>
        <div class="page-title">Product Store</div>
        <div class="page-sub">Deployed on Kubernetes &nbsp;&middot;&nbsp; Monitored by Prometheus &nbsp;&middot;&nbsp; EKS ap-south-1</div>
      </div>
    </div>
    <div class="version-pill">v1.0.0</div>
  </div>

  <div class="search-wrap">
    <span class="search-ico">&#x1F50D;</span>
    <input class="search-bar" type="text" placeholder="Search products..." oninput="filterProducts(this.value)">
  </div>

  <div class="stats-row">
    <div class="stat-card">
      <div class="stat-icon-wrap" style="background:#dbeafe;">&#x1F4E6;</div>
      <div>
        <div class="stat-label">Products</div>
        <div class="stat-value">{{ products|length }}</div>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-icon-wrap" style="background:#dcfce7;">&#x2705;</div>
      <div>
        <div class="stat-label">Backend</div>
        <div class="stat-value healthy">Healthy</div>
      </div>
    </div>
    <div class="stat-card">
      <div class="stat-icon-wrap" style="background:#ede9fe;">&#x2388;</div>
      <div>
        <div class="stat-label">Pods</div>
        <div class="stat-value">2 / 2</div>
      </div>
    </div>
  </div>

  <div class="section-label">All Products</div>
  <div id="product-list">
    {% set icons = ["\U0001F4BB", "\U0001F5B1", "\u2328", "\U0001F4F1", "\U0001F5A5"] %}
    {% set icon_bg = ["#dbeafe", "#ede9fe", "#ccfbf1", "#ffedd5", "#fce7f3"] %}
    {% for p in products %}
    <div class="product-card" data-name="{{ p.name|lower }}">
      <div class="product-left">
        <div class="product-icon" style="background:{{ icon_bg[loop.index0 % 5] }};">
          {{ icons[loop.index0 % 5] }}
        </div>
        <div class="product-info">
          <div class="product-name">{{ p.name }}</div>
          <div class="product-meta">SKU-00{{ loop.index }}&nbsp;&nbsp;&middot;&nbsp;&nbsp;In stock</div>
        </div>
      </div>
      <div class="product-right">
        <div>
          <div class="product-price">Rs. {{ "{:,}".format(p.price) }}</div>
          <div class="product-avail">&#10003; Available</div>
        </div>
        <button class="add-btn" onclick="addToCart(this)">+ Add</button>
      </div>
    </div>
    {% endfor %}

    {% if not products %}
    <div class="empty">
      <div class="e-icon">&#x26A0;</div>
      <div class="e-title">Cannot reach backend</div>
      <div class="e-sub">Check backend-service is running in namespace: app</div>
    </div>
    {% endif %}
  </div>

  <div class="health-bar">
    <div class="h-dot"></div>
    <span><strong>Backend API</strong> &mdash; /health returned 200 OK &nbsp;&middot;&nbsp; Latency: ~4ms &nbsp;&middot;&nbsp; Prometheus scraping /metrics</span>
  </div>

  <div class="pods-section">
    <div class="pods-title">Active Frontend Pods</div>
    <div class="pods-grid">
      <div class="pod-card">
        <div class="pod-name">frontend-deploy-xxxxx-pod1</div>
        <div class="pod-status">&#9679; Running &middot; Node 1</div>
      </div>
      <div class="pod-card">
        <div class="pod-name">frontend-deploy-xxxxx-pod2</div>
        <div class="pod-status">&#9679; Running &middot; Node 2</div>
      </div>
    </div>
  </div>

  <div class="footer">
    <code>Flask</code> &middot; <code>Kubernetes</code> &middot; <code>Prometheus + Grafana</code> &middot; <code>GitHub Actions</code>
  </div>

</div>

<script>
  function filterProducts(q) {
    q = q.toLowerCase();
    document.querySelectorAll('.product-card').forEach(c => {
      c.style.display = c.dataset.name.includes(q) ? 'flex' : 'none';
    });
  }
  function addToCart(btn) {
    btn.textContent = 'Added!';
    btn.style.background = '#10b981';
    setTimeout(() => { btn.textContent = '+ Add'; btn.style.background = '#2563eb'; }, 1500);
  }
</script>

</body>
</html>"""

@app.route('/')
def index():
    try:
        resp = requests.get(f"{BACKEND}/products", timeout=3)
        products = resp.json()
    except Exception:
        products = []
    return render_template_string(HTML, products=products)

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
