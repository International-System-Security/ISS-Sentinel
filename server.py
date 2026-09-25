from datetime import datetime, timedelta
import os
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

LICENSE_FILE = "licenses.txt"
ADMIN_SECRET_KEY = "my_super_secret_admin_key_123"

# সাবস্ক্রিপশন প্ল্যান এবং ফিচারসমূহ
PLAN_FEATURES = {
    "Basic": {
        "max_devices": 1,
        "features": [
            "Real-time cloud threat scanning",
            "Single PC Protection",
            "Standard server response",
        ],
    },
    "Standard": {
        "max_devices": 3,
        "features": [
            "Real-time cloud threat scanning",
            "Up to 3 PCs Multi-Device Protection",
            "Centralized organization tracking",
            "Priority server response",
        ],
    },
    "Enterprise": {
        "max_devices": 5,
        "features": [
            "Real-time cloud threat scanning",
            "5+ PCs Corporate Protection",
            "Advanced multi-device management",
            "Dedicated VIP enterprise support & priority threat definitions",
        ],
    },
}

KNOWN_THREATS = [
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "44d88612fea8a8f36de82e1278abb02f",
]


def load_licenses():
  licenses_dict = {}
  if os.path.exists(LICENSE_FILE):
    with open(LICENSE_FILE, "r") as f:
      for line in f:
        parts = line.strip().split(",")
        if len(parts) >= 6:
          key = parts[0].strip()
          licenses_dict[key] = {
              "name": parts[1].strip(),
              "org": parts[2].strip(),
              "expiry": parts[3].strip(),
              "max_devices": int(parts[4].strip()),
              "plan_type": parts[5].strip(),
              "pcs": [p.strip() for p in parts[6:] if p.strip()],
          }
  return licenses_dict


def save_all_licenses(licenses_dict):
  with open(LICENSE_FILE, "w") as f:
    for k, v in licenses_dict.items():
      pcs_str = ",".join(v["pcs"])
      f.write(
          f"{k},{v['name']},{v['org']},{v['expiry']},{v['max_devices']},{v['plan_type']},{pcs_str}\n"
      )


@app.route("/", methods=["GET"])
def home():
  return """
    <h2>ISS Cloud Security Enterprise Backend is Active!</h2>
    <p>Client Portal & Auto-Setup: <a href='/client-login'>/client-login</a></p>
    <p>Admin Dashboard: <a href='/admin?key=my_super_secret_admin_key_123'>/admin</a></p>
    """


# ১. অ্যাডমিন ড্যাশবোর্ড
@app.route("/admin", methods=["GET"])
def admin_panel():
  key = request.args.get("key")
  if key != ADMIN_SECRET_KEY:
    return "<h3>Unauthorized! Incorrect Admin Key.</h3>", 401

  licenses = load_licenses()
  table_rows = ""
  for k, v in licenses.items():
    connected_list = (
        ", ".join(v["pcs"]) if v["pcs"] else "No devices connected yet"
    )
    table_rows += f"""
        <tr>
            <td><b>{k}</b></td>
            <td>{v['name']}</td>
            <td>{v['org']}</td>
            <td><span style="background:#e0f2fe; padding:2px 6px; border-radius:4px; font-size:11px;">{v['plan_type']}</span></td>
            <td>{v['expiry']}</td>
            <td><b>{len(v['pcs'])} / {v['max_devices']}</b></td>
            <td><code>{connected_list}</code></td>
        </tr>
        """

  html_page = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ISS Enterprise Admin Dashboard</title>
        <style>
            body {{ font-family: Arial; background: #f4f4f9; padding: 25px; }}
            .container {{ display: flex; gap: 25px; flex-wrap: wrap; }}
            .box {{ background: white; padding: 20px; border-radius: 8px; width: 380px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); height: fit-content; }}
            .table-box {{ background: white; padding: 20px; border-radius: 8px; flex-grow: 1; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); overflow-x: auto; }}
            input, select {{ width: 100%%; padding: 8px; margin: 6px 0 12px 0; box-sizing: border-box; }}
            button {{ background: #2563eb; color: white; padding: 10px; border: none; width: 100%%; border-radius: 4px; cursor: pointer; font-weight: bold; }}
            button:hover {{ background: #1d4ed8; }}
            table {{ width: 100%%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #e2e8f0; padding: 8px; text-align: left; font-size: 13px; }}
            th {{ background-color: #0f172a; color: white; }}
        </style>
    </head>
    <body>
        <h2>ISS Cloud Security - Admin Dashboard</h2>
        <div class="container">
            <div class="box">
                <h3>Create Client License ID</h3>
                <form action="/add-client" method="POST">
                    <input type="hidden" name="key" value="{ADMIN_SECRET_KEY}">
                    <label>Client Name:</label>
                    <input type="text" name="name" placeholder="e.g. Rahim Khan" required>
                    <label>Organization Name:</label>
                    <input type="text" name="org" placeholder="e.g. ABC Tech Ltd" required>
                    <label>License ID:</label>
                    <input type="text" name="license" placeholder="e.g. iss-1111-2026" required>
                    <label>Select Plan Tier & Cycle:</label>
                    <select name="plan_choice">
                        <option value="Basic-Monthly">1. Single PC Plan (Monthly - $4.99)</option>
                        <option value="Basic-Yearly">1. Single PC Plan (Yearly - $49.99)</option>
                        <option value="Standard-Monthly">2. Multi-Device Plan 3 PCs (Monthly - $11.99)</option>
                        <option value="Standard-Yearly">2. Multi-Device Plan 3 PCs (Yearly - $119.99)</option>
                        <option value="Enterprise-Monthly">3. Enterprise Plan 5+ PCs (Monthly - $21.99)</option>
                        <option value="Enterprise-Yearly">3. Enterprise Plan 5+ PCs (Yearly - $219.99)</option>
                    </select>
                    <button type="submit">Create License ID</button>
                </form>
            </div>
            <div class="table-box">
                <h3>Active Subscriptions</h3>
                <table>
                    <tr>
                        <th>License ID</th>
                        <th>Client Name</th>
                        <th>Organization</th>
                        <th>Plan Type</th>
                        <th>Expiry Date</th>
                        <th>Devices</th>
                        <th>Connected PCs</th>
                    </tr>
                    {table_rows if table_rows else "<tr><td colspan='7' style='text-align:center;'>No active subscriptions found</td></tr>"}
                </table>
            </div>
        </div>
    </body>
    </html>
    """
  return render_template_string(html_page)


@app.route("/add-client", methods=["POST"])
def add_client():
  admin_key = request.form.get("key")
  client_name = request.form.get("name")
  org_name = request.form.get("org")
  license_key = request.form.get("license")
  plan_choice = request.form.get("plan_choice")

  if admin_key != ADMIN_SECRET_KEY:
    return "Unauthorized!", 401

  base_tier = "Basic"
  if "Standard" in plan_choice:
    base_tier = "Standard"
  elif "Enterprise" in plan_choice:
    base_tier = "Enterprise"

  max_devices = PLAN_FEATURES[base_tier]["max_devices"]
  duration_days = 365 if "Yearly" in plan_choice else 30
  expiry_date = (datetime.now() + timedelta(days=duration_days)).strftime(
      "%Y-%m-%d"
  )

  licenses = load_licenses()
  licenses[license_key] = {
      "name": client_name,
      "org": org_name,
      "expiry": expiry_date,
      "max_devices": max_devices,
      "plan_type": plan_choice,
      "pcs": [],
  }
  save_all_licenses(licenses)

  return f"""
    <h3>Success! License ID <b>{license_key}</b> created for <b>{org_name}</b>.</h3>
    <a href="/admin?key={ADMIN_SECRET_KEY}">Back to Dashboard</a>
    """


# ২. ক্লায়েন্ট পোর্টাল ও অটো-কনফিগারেশন পেজ
@app.route("/client-login", methods=["GET", "POST"])
def client_login():
  error_msg = ""
  if request.method == "POST":
    license_key = request.form.get("license_key", "").strip()
    licenses = load_licenses()

    if license_key in licenses:
      v = licenses[license_key]
      base_tier = "Basic"
      if "Standard" in v["plan_type"]:
        base_tier = "Standard"
      elif "Enterprise" in v["plan_type"]:
        base_tier = "Enterprise"

      features_html = "".join(
          [f"<li>{f}</li>" for f in PLAN_FEATURES[base_tier]["features"]]
      )
      connected_devices = (
          ", ".join(v["pcs"]) if v["pcs"] else "No devices connected yet"
      )

      client_dashboard_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>ISS Client Auto-Setup Portal</title>
                <style>
                    body {{ font-family: Arial; background: #f8fafc; padding: 30px; color: #1e293b; }}
                    .card {{ background: white; max-width: 600px; margin: 0 auto; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                    h2 {{ color: #0f172a; margin-top: 0; }}
                    .info-group {{ margin: 15px 0; padding-bottom: 10px; border-bottom: 1px solid #e2e8f0; }}
                    .label {{ font-weight: bold; color: #64748b; font-size: 13px; }}
                    .value {{ font-size: 16px; color: #0f172a; margin-top: 3px; }}
                    .status-safe {{ color: #16a34a; font-weight: bold; }}
                    ul {{ margin: 5px 0; padding-left: 20px; font-size: 14px; color: #475569; }}
                    .setup-box {{ background: #e0f2fe; padding: 15px; border-radius: 6px; margin-top: 15px; border-left: 4px solid #0284c7; }}
                    .back-btn {{ display: inline-block; margin-top: 20px; background: #0284c7; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h2>Client Auto-Setup & Security Portal</h2>
                    <p class="status-safe">● License Status: Active & Auto-Linked</p>
                    
                    <div class="info-group">
                        <div class="label">Organization Name</div>
                        <div class="value">{v['org']} ({v['name']})</div>
                    </div>
                    
                    <div class="info-group">
                        <div class="label">Active Subscription Plan</div>
                        <div class="value"><b>{v['plan_type']}</b></div>
                    </div>

                    <div class="info-group">
                        <div class="label">Subscription Expiry Date</div>
                        <div class="value">{v['expiry']}</div>
                    </div>

                    <div class="info-group">
                        <div class="label">Device Usage & Limit</div>
                        <div class="value">{len(v['pcs'])} / {v['max_devices']} PC(s) [<code>{connected_devices}</code>]</div>
                    </div>

                    <div class="info-group">
                        <div class="label">Included Privileges & Features</div>
                        <ul>{features_html}</ul>
                    </div>

                    <div class="setup-box">
                        <strong>Auto-Setup Instructions:</strong><br>
                        আপনার সফটওয়্যারে শুধু এই লাইসেন্স আইডি (<code>{license_key}</code>) বসিয়ে দিন। সার্ভার স্বয়ংক্রিয়ভাবে আপনার পিসি কনফিগার ও সিংক করে নেবে! কোনো জিপ ফাইল বা এক্সট্রা কনফিগারেশনের প্রয়োজন নেই।
                    </div>

                    <a href="/client-login" class="back-btn">Logout / Enter Another ID</a>
                </div>
            </body>
            </html>
            """
      return render_template_string(client_dashboard_html)
    else:
      error_msg = (
          "Invalid License ID! Please enter a valid license provided by admin."
      )

  login_page = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ISS Client Auto-Setup Login</title>
        <style>
            body {{ font-family: Arial; background: #f1f5f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .login-card {{ background: white; padding: 30px; border-radius: 8px; width: 350px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }}
            input {{ width: 100%%; padding: 10px; margin: 10px 0; box-sizing: border-box; border: 1px solid #cbd5e1; border-radius: 4px; }}
            button {{ background: #0ea5e9; color: white; border: none; padding: 10px; width: 100%%; border-radius: 4px; font-weight: bold; cursor: pointer; }}
            button:hover {{ background: #0284c7; }}
            .error {{ color: #dc2626; font-size: 13px; margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="login-card">
            <h3>Client Auto-Setup Portal</h3>
            <p style="font-size: 13px; color: #64748b;">Enter your License ID for instant setup</p>
            {f'<div class="error">{error_msg}</div>' if error_msg else ''}
            <form method="POST">
                <input type="text" name="license_key" placeholder="Enter License ID (e.g. iss-1111-2026)" required>
                <button type="submit">Auto-Setup & View Status</button>
            </form>
        </div>
    </body>
    </html>
    """
  return render_template_string(login_page)


# ৩. অটো-কনফিগারেশন এবং স্ক্যান রুট (এজেন্ট সরাসরি লাইসেন্স আইডি দিয়ে সিংক করবে)
@app.route("/scan", methods=["POST"])
def scan_file():
  data = request.json or {}
  license_key = data.get("license_key")
  file_hash = data.get("hash")
  filename = data.get("filename", "Unknown")
  client_pc_id = data.get("pc_id", request.remote_addr)

  licenses = load_licenses()

  if license_key not in licenses:
    return (
        jsonify({
            "status": "error",
            "message": "Access Denied: Invalid or Unregistered License ID!",
        }),
        403,
    )

  client_info = licenses[license_key]
  expiry_str = client_info["expiry"]
  client_name = client_info["name"]
  org_name = client_info["org"]
  max_dev = client_info["max_devices"]
  plan_type = client_info["plan_type"]
  connected_pcs = client_info["pcs"]

  base_tier = "Basic"
  if "Standard" in plan_type:
    base_tier = "Standard"
  elif "Enterprise" in plan_type:
    base_tier = "Enterprise"

  current_tier_features = PLAN_FEATURES[base_tier]["features"]

  # মেয়াদ চেক
  today_date = datetime.now().date()
  try:
    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
  except ValueError:
    return jsonify({"status": "error", "message": "Date format error."}), 500

  if today_date > expiry_date:
    return (
        jsonify({
            "status": "expired",
            "message": (
                f"Subscription Expired: Dear {client_name} from {org_name},"
                f" your {plan_type} subscription expired on {expiry_str}."
            ),
        }),
        403,
    )

  # অটো-ডিভাইস বাইন্ডিং চেক
  if client_pc_id not in connected_pcs:
    if len(connected_pcs) >= max_dev:
      return (
          jsonify({
              "status": "error",
              "message": (
                  f"Device Limit Reached! Your {plan_type} plan allows a"
                  f" maximum of {max_dev} PC(s)."
              ),
          }),
          403,
      )
    connected_pcs.append(client_pc_id)
    save_all_licenses(licenses)

  if file_hash in KNOWN_THREATS:
    return jsonify({
        "status": "danger",
        "is_threat": True,
        "message": f"ALERT: Threat found in {filename}!",
        "plan_tier": base_tier,
        "active_features": current_tier_features,
    })

  return jsonify({
      "status": "clean",
      "is_threat": False,
      "message": f"{filename} is safe and auto-linked successfully.",
      "plan_tier": base_tier,
      "active_features": current_tier_features,
  })


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
