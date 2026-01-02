from flask import Flask, render_template_string, request
import requests
import os

app = Flask(__name__)

# ================== GODOFPANEL CONFIG ==================
PANEL_NAME = "GodOfPanel API"
PANEL_URL = "https://godofpanel.com/api/v2"
API_KEY = "efe7efb51f8b32ead8553db6c1094c4e"
SERVICE_ID = 5836  # TikTok Comment Likes
# =======================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TikTok Comment Likes Sender</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {
      margin: 0;
      padding: 0;
      background: radial-gradient(circle at top, #1e293b 0, #020617 55%);
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #e5e7eb;
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
    }
    .box { width: 100%; max-width: 900px; padding: 20px; }
    .card {
      background: rgba(15,23,42,0.95);
      border-radius: 16px;
      padding: 22px;
      border: 1px solid rgba(148,163,184,0.25);
      box-shadow: 0 25px 60px rgba(0,0,0,0.7);
    }
    h1 { font-size: 22px; margin-bottom: 6px; text-transform: uppercase; }
    .sub { font-size: 13px; color: #9ca3af; margin-bottom: 16px; }
    textarea {
      width: 100%;
      min-height: 190px;
      background: rgba(2,6,23,0.9);
      border-radius: 12px;
      border: 1px solid rgba(55,65,81,0.9);
      padding: 12px;
      color: #e5e7eb;
      font-size: 13px;
      resize: vertical;
    }
    .hint { font-size: 11px; color: #9ca3af; margin-top: 6px; }
    button {
      margin-top: 14px;
      background: linear-gradient(135deg, #6366f1, #a855f7);
      color: white;
      border: none;
      border-radius: 999px;
      padding: 10px 22px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      float: right;
    }
    .log {
      margin-top: 16px;
      font-size: 11px;
      background: rgba(2,6,23,0.9);
      border-radius: 10px;
      padding: 10px;
      white-space: pre-wrap;
      border: 1px solid rgba(55,65,81,0.9);
      max-height: 260px;
      overflow-y: auto;
    }
    .status { margin-top: 8px; font-size: 12px; color: #9ca3af; }
  </style>
</head>
<body>
  <div class="box">
    <div class="card">
      <h1>TikTok Comment Likes Sender</h1>
      <div class="sub">
        Service ID: <b>{{ service_id }}</b> · Panel: <b>{{ panel_name }}</b>
      </div>

      <form method="post">
        <textarea name="orders" placeholder="Example:
https://www.tiktok.com/@user/video/123456789 username 100
https://www.tiktok.com/@user/video/987654321 anotheruser 250">{{ orders or '' }}</textarea>
        <div class="hint">
          Format: <b>LINK USERNAME QUANTITY</b>
        </div>

        <button type="submit">🚀 SEND TO PANEL</button>
      </form>

      <div class="status">{{ status or '' }}</div>
      {% if log %}<div class="log">{{ log }}</div>{% endif %}
    </div>
  </div>
</body>
</html>
"""

def send_order(link, username, quantity):
    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": link,
        "username": username,
        "quantity": quantity
    }
    r = requests.post(PANEL_URL, data=payload, timeout=20)
    try:
        return True, r.json()
    except Exception:
        return False, r.text


@app.route("/", methods=["GET", "POST"])
def index():
    orders = ""
    status = ""
    logs = []

    if request.method == "POST":
        orders = request.form.get("orders", "")
        lines = [l.strip() for l in orders.splitlines() if l.strip()]

        ok, fail = 0, 0

        for line in lines:
            parts = line.split()
            if len(parts) != 3:
                fail += 1
                logs.append(f"[SKIP] Wrong format: {line}")
                continue

            link, username, qty = parts
            try:
                qty = int(qty)
                if qty <= 0:
                    raise ValueError
            except:
                fail += 1
                logs.append(f"[SKIP] Invalid quantity: {line}")
                continue

            success, res = send_order(link, username, qty)
            if success and isinstance(res, dict) and "order" in res:
                ok += 1
                logs.append(f"[OK] {link} @{username} x{qty} → order {res['order']}")
            else:
                fail += 1
                logs.append(f"[FAIL] {link} @{username} x{qty} → {res}")

        status = f"Done. Success: {ok}, Failed: {fail}"

    return render_template_string(
        HTML_TEMPLATE,
        orders=orders,
        status=status,
        log="\n".join(logs),
        service_id=SERVICE_ID,
        panel_name=PANEL_NAME
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


