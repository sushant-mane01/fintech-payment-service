from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
from app.payment_service import PaymentService

app = FastAPI(
    title="Fintech Payment Service",
    description="High-performance serverless payment and wallet processing engine",
    version="1.0.0"
)
payment_service = PaymentService()

class CreateWalletRequest(BaseModel):
    customer_id: str
    initial_balance: float = 0.0

class ChargeRequest(BaseModel):
    wallet_id: str
    amount: float
    description: str = ""

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "fintech-payment-service",
        "platform": "vercel",
        "version": "1.0.0"
    }

@app.get("/api/v1/wallets/{wallet_id}")
def get_wallet(wallet_id: str):
    wallet = payment_service.get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail=f"Wallet '{wallet_id}' not found.")
    return {
        "wallet_id": wallet.wallet_id,
        "customer_id": wallet.customer_id,
        "balance": float(wallet.balance),
        "currency": wallet.currency,
        "is_active": wallet.is_active
    }

@app.post("/api/v1/wallets")
def create_wallet(req: CreateWalletRequest):
    if not req.customer_id.strip():
        raise HTTPException(status_code=400, detail="Customer ID cannot be empty.")
    if req.initial_balance < 0:
        raise HTTPException(status_code=400, detail="Initial balance cannot be negative.")
    wallet = payment_service.create_wallet(req.customer_id.strip(), Decimal(str(req.initial_balance)))
    return {
        "wallet_id": wallet.wallet_id,
        "customer_id": wallet.customer_id,
        "balance": float(wallet.balance),
        "currency": wallet.currency
    }

@app.post("/api/v1/charges")
def charge_wallet(req: ChargeRequest):
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Charge amount must be greater than zero.")
    try:
        tx = payment_service.process_charge(req.wallet_id.strip(), Decimal(str(req.amount)), req.description)
        wallet = payment_service.get_wallet(req.wallet_id.strip())
        return {
            "transaction_id": tx.transaction_id,
            "wallet_id": tx.wallet_id,
            "status": tx.status,
            "amount": float(tx.amount),
            "currency": tx.currency,
            "remaining_balance": float(wallet.balance) if wallet else None,
            "description": tx.description
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.get("/", response_class=HTMLResponse)
def index_ui():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Fintech Payment Service — Deployed on Vercel</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090d16;
      --card-bg: rgba(18, 24, 38, 0.85);
      --card-border: rgba(255, 255, 255, 0.08);
      --accent-green: #10b981;
      --accent-cyan: #06b6d4;
      --accent-purple: #8b5cf6;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --input-bg: rgba(15, 23, 42, 0.7);
      --input-border: #334155;
    }
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      background-color: var(--bg);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background-image: 
        radial-gradient(circle at 15% 20%, rgba(16, 185, 129, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 85% 15%, rgba(6, 182, 212, 0.12) 0%, transparent 45%),
        radial-gradient(circle at 50% 80%, rgba(139, 92, 246, 0.08) 0%, transparent 50%);
      background-attachment: fixed;
    }
    header {
      border-bottom: 1px solid var(--card-border);
      background: rgba(9, 13, 22, 0.8);
      backdrop-filter: blur(12px);
      position: sticky;
      top: 0;
      z-index: 100;
      padding: 16px 32px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-icon {
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, #10b981, #06b6d4);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);
    }
    .brand-title {
      font-weight: 800;
      font-size: 1.15rem;
      letter-spacing: -0.02em;
      background: linear-gradient(to right, #ffffff, #cbd5e1);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .nav-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 12px;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
    }
    .pill-vercel {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #fff;
    }
    .pill-status {
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #34d399;
    }
    .pulse-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: #10b981;
      box-shadow: 0 0 10px #10b981;
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.85); }
    }
    .nav-btn {
      text-decoration: none;
      color: #cbd5e1;
      font-size: 0.8rem;
      font-weight: 600;
      padding: 6px 14px;
      border-radius: 8px;
      border: 1px solid var(--card-border);
      background: rgba(255, 255, 255, 0.03);
      transition: all 0.2s ease;
    }
    .nav-btn:hover {
      background: rgba(255, 255, 255, 0.1);
      color: #fff;
      border-color: rgba(255, 255, 255, 0.25);
    }
    main {
      flex: 1;
      max-width: 1200px;
      width: 100%;
      margin: 0 auto;
      padding: 40px 24px;
    }
    .hero {
      text-align: center;
      margin-bottom: 36px;
    }
    .hero-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 14px;
      border-radius: 9999px;
      background: linear-gradient(90deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.15));
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #34d399;
      font-size: 0.8rem;
      font-weight: 700;
      margin-bottom: 14px;
    }
    .hero h1 {
      font-size: 2.5rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      margin-bottom: 10px;
      background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .hero p {
      color: var(--text-muted);
      font-size: 1.05rem;
      max-width: 650px;
      margin: 0 auto;
      line-height: 1.5;
    }
    .stats-bar {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 36px;
    }
    .stat-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 16px 20px;
      backdrop-filter: blur(8px);
    }
    .stat-label {
      font-size: 0.75rem;
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 6px;
    }
    .stat-value {
      font-size: 1.25rem;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .grid-2 {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
      gap: 24px;
      margin-bottom: 36px;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 18px;
      padding: 24px;
      backdrop-filter: blur(12px);
      box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
      display: flex;
      flex-direction: column;
    }
    .card-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 18px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--card-border);
    }
    .card-icon {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
    }
    .card-title {
      font-size: 1.05rem;
      font-weight: 700;
      color: #fff;
    }
    .form-group {
      margin-bottom: 14px;
    }
    label {
      display: block;
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: 6px;
    }
    input {
      width: 100%;
      background: var(--input-bg);
      border: 1px solid var(--input-border);
      color: #fff;
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 0.9rem;
      font-family: inherit;
      outline: none;
      transition: border-color 0.2s;
    }
    input:focus {
      border-color: var(--accent-cyan);
    }
    .btn {
      width: 100%;
      background: linear-gradient(135deg, #10b981, #059669);
      color: #fff;
      border: none;
      padding: 11px 18px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 0.9rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      margin-top: 8px;
      transition: all 0.2s;
      box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);
    }
    .btn:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(16, 185, 129, 0.45);
    }
    .btn:active {
      transform: translateY(0);
    }
    .btn-secondary {
      background: linear-gradient(135deg, #0284c7, #0369a1);
      box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3);
    }
    .btn-secondary:hover {
      box-shadow: 0 6px 20px rgba(2, 132, 199, 0.45);
    }
    .btn-outline {
      background: transparent;
      border: 1px solid var(--input-border);
      color: var(--text-muted);
      box-shadow: none;
    }
    .btn-outline:hover {
      background: rgba(255, 255, 255, 0.05);
      color: #fff;
    }
    .output-box {
      margin-top: 16px;
      padding: 12px 14px;
      border-radius: 8px;
      background: rgba(0, 0, 0, 0.35);
      border: 1px solid rgba(255, 255, 255, 0.06);
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.8rem;
      color: #cbd5e1;
      max-height: 160px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-all;
    }
    .output-box.success {
      border-color: rgba(16, 185, 129, 0.3);
      color: #a7f3d0;
    }
    .output-box.error {
      border-color: rgba(239, 68, 68, 0.3);
      color: #fca5a5;
    }
    .activity-section {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 18px;
      padding: 24px;
      backdrop-filter: blur(12px);
    }
    .activity-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 14px;
      font-size: 0.82rem;
    }
    .activity-table th {
      text-align: left;
      padding: 8px 12px;
      color: var(--text-muted);
      border-bottom: 1px solid var(--card-border);
      font-weight: 600;
    }
    .activity-table td {
      padding: 10px 12px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      font-family: 'JetBrains Mono', monospace;
    }
    .badge-completed {
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 0.72rem;
      font-weight: 600;
    }
    footer {
      border-top: 1px solid var(--card-border);
      padding: 24px;
      text-align: center;
      color: #64748b;
      font-size: 0.8rem;
      margin-top: auto;
    }
  </style>
</head>
<body>

  <header>
    <div class="brand">
      <div class="brand-icon">⚡</div>
      <div>
        <div class="brand-title">Fintech Payment Service</div>
      </div>
    </div>
    <div class="nav-actions">
      <span class="pill pill-vercel">
        <svg width="12" height="12" viewBox="0 0 76 65" fill="#fff"><path d="M37.5274 0L75.0548 65H0L37.5274 0Z"/></svg>
        Vercel Serverless
      </span>
      <span class="pill pill-status">
        <span class="pulse-dot"></span>
        <span id="service-status">Live & Ready</span>
      </span>
      <a href="/docs" target="_blank" class="nav-btn">API Docs ↗</a>
      <a href="/health" target="_blank" class="nav-btn">Healthcheck ↗</a>
    </div>
  </header>

  <main>
    <div class="hero">
      <div class="hero-badge">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        Deployment Successful & Verified
      </div>
      <h1>Fintech Payment Microservice</h1>
      <p>Instant serverless payment processing engine deployed on Vercel. Issue wallets, process charges, and inspect transactions via high-speed REST APIs.</p>
    </div>

    <!-- Live Stats -->
    <div class="stats-bar">
      <div class="stat-card">
        <div class="stat-label">Service Status</div>
        <div class="stat-value" style="color: #34d399;">
          <span class="pulse-dot"></span> Healthy
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Runtime Engine</div>
        <div class="stat-value">FastAPI / Python</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Response Time</div>
        <div class="stat-value" id="ping-time">Calculating...</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Deployment Platform</div>
        <div class="stat-value">Vercel Edge/Serverless</div>
      </div>
    </div>

    <!-- Interactive Grid -->
    <div class="grid-2">
      <!-- Create Wallet Card -->
      <div class="card">
        <div class="card-header">
          <div class="card-icon" style="background: rgba(16, 185, 129, 0.15); color: #10b981;">💳</div>
          <div class="card-title">1. Create Digital Wallet</div>
        </div>
        <div class="form-group">
          <label>Customer Identifier</label>
          <input type="text" id="wallet-customer" value="cust_fintech_77" placeholder="e.g. cust_101">
        </div>
        <div class="form-group">
          <label>Initial Balance (USD)</label>
          <input type="number" id="wallet-balance" value="250.00" step="10.00" min="0">
        </div>
        <button class="btn" id="create-wallet-btn" onclick="handleCreateWallet()">
          Generate & Issue Wallet
        </button>
        <div id="wallet-output" class="output-box" style="display: none;"></div>
      </div>

      <!-- Process Charge Card -->
      <div class="card">
        <div class="card-header">
          <div class="card-icon" style="background: rgba(6, 182, 212, 0.15); color: #06b6d4;">💸</div>
          <div class="card-title">2. Process Transaction / Charge</div>
        </div>
        <div class="form-group">
          <label>Target Wallet ID</label>
          <input type="text" id="charge-wallet-id" placeholder="Create a wallet or paste wal_..." />
        </div>
        <div class="form-group">
          <label>Amount (USD)</label>
          <input type="number" id="charge-amount" value="35.50" step="5.00" min="0.01">
        </div>
        <div class="form-group">
          <label>Description</label>
          <input type="text" id="charge-desc" value="Stripe Cloud Infrastructure fee">
        </div>
        <button class="btn btn-secondary" id="charge-btn" onclick="handleCharge()">
          Process & Authorize Charge
        </button>
        <div id="charge-output" class="output-box" style="display: none;"></div>
      </div>
    </div>

    <!-- Live Transaction Log -->
    <div class="activity-section">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <h3 style="font-size: 1rem; font-weight: 700;">Live Session Transactions</h3>
        <span style="font-size: 0.75rem; color: var(--text-muted);" id="tx-count">0 operations logged</span>
      </div>
      <table class="activity-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Type</th>
            <th>ID / Reference</th>
            <th>Amount / Balance</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody id="activity-body">
          <tr>
            <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 24px;">No transactions recorded yet in this session. Create a wallet above to get started!</td>
          </tr>
        </tbody>
      </table>
    </div>
  </main>

  <footer>
    Fintech Payment Service • Deployed via Vercel • FastAPI Python Serverless Architecture
  </footer>

  <script>
    let loggedTransactions = [];

    // Healthcheck ping
    async function checkHealth() {
      const start = performance.now();
      try {
        const res = await fetch('/health');
        const latency = Math.round(performance.now() - start);
        if (res.ok) {
          document.getElementById('ping-time').innerText = latency + ' ms';
          document.getElementById('service-status').innerText = 'Operational (' + latency + 'ms)';
        }
      } catch (e) {
        document.getElementById('ping-time').innerText = 'Error';
        document.getElementById('service-status').innerText = 'Degraded';
      }
    }

    async function handleCreateWallet() {
      const customerId = document.getElementById('wallet-customer').value;
      const initialBalance = parseFloat(document.getElementById('wallet-balance').value) || 0;
      const out = document.getElementById('wallet-output');
      const btn = document.getElementById('create-wallet-btn');

      btn.disabled = true;
      btn.innerText = 'Creating...';

      try {
        const res = await fetch('/api/v1/wallets', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ customer_id: customerId, initial_balance: initialBalance })
        });
        const data = await res.json();
        out.style.display = 'block';

        if (res.ok) {
          out.className = 'output-box success';
          out.innerText = '✓ Wallet Created:\\n' + JSON.stringify(data, null, 2);
          document.getElementById('charge-wallet-id').value = data.wallet_id;

          logActivity({
            time: new Date().toLocaleTimeString(),
            type: 'CREATE_WALLET',
            id: data.wallet_id,
            amount: '$' + data.balance.toFixed(2),
            status: 'COMPLETED'
          });
        } else {
          out.className = 'output-box error';
          out.innerText = '✗ Error: ' + (data.detail || JSON.stringify(data));
        }
      } catch (err) {
        out.style.display = 'block';
        out.className = 'output-box error';
        out.innerText = '✗ Network request failed: ' + err.message;
      } finally {
        btn.disabled = false;
        btn.innerText = 'Generate & Issue Wallet';
      }
    }

    async function handleCharge() {
      const walletId = document.getElementById('charge-wallet-id').value;
      const amount = parseFloat(document.getElementById('charge-amount').value) || 0;
      const description = document.getElementById('charge-desc').value;
      const out = document.getElementById('charge-output');
      const btn = document.getElementById('charge-btn');

      if (!walletId) {
        out.style.display = 'block';
        out.className = 'output-box error';
        out.innerText = '✗ Please enter a valid Wallet ID or create one first.';
        return;
      }

      btn.disabled = true;
      btn.innerText = 'Authorizing...';

      try {
        const res = await fetch('/api/v1/charges', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ wallet_id: walletId, amount: amount, description: description })
        });
        const data = await res.json();
        out.style.display = 'block';

        if (res.ok) {
          out.className = 'output-box success';
          out.innerText = '✓ Payment Authorized:\\n' + JSON.stringify(data, null, 2);

          logActivity({
            time: new Date().toLocaleTimeString(),
            type: 'CHARGE',
            id: data.transaction_id,
            amount: '-$' + data.amount.toFixed(2) + ' (rem: $' + data.remaining_balance.toFixed(2) + ')',
            status: data.status
          });
        } else {
          out.className = 'output-box error';
          out.innerText = '✗ Charge Failed: ' + (data.detail || JSON.stringify(data));
        }
      } catch (err) {
        out.style.display = 'block';
        out.className = 'output-box error';
        out.innerText = '✗ Network error: ' + err.message;
      } finally {
        btn.disabled = false;
        btn.innerText = 'Process & Authorize Charge';
      }
    }

    function logActivity(entry) {
      loggedTransactions.unshift(entry);
      document.getElementById('tx-count').innerText = loggedTransactions.length + ' operations logged';
      const tbody = document.getElementById('activity-body');
      tbody.innerHTML = loggedTransactions.map(tx => `
        <tr>
          <td style="color: #64748b;">${tx.time}</td>
          <td style="font-weight: 700; color: #38bdf8;">${tx.type}</td>
          <td style="color: #f1f5f9;">${tx.id}</td>
          <td style="color: #34d399;">${tx.amount}</td>
          <td><span class="badge-completed">${tx.status}</span></td>
        </tr>
      `).join('');
    }

    // Initialize
    checkHealth();
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)
