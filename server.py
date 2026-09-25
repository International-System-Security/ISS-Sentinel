from datetime import datetime, timedelta
import os
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

LICENSE_FILE = "licenses.txt"
ADMIN_SECRET_KEY = "my_super_secret_admin_key_123"

# আমাদের জানা ম্যালওয়্যার বা থ্র্যাট হাশ লিস্ট
KNOWN_THREATS = [
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "44d88612fea8a8f36de82e1278abb02f",
]


def load_licenses():
  """ফাইল থেকে সব ক্লায়েন্টের ডাটা লোড করবে"""
  licenses_dict = {}
  if os.path.exists(LICENSE_FILE):
    with open(LICENSE_FILE, "r") as f:
      for line in f:
        parts = line.strip().split(",")
        if len(parts) >= 6:
          # ফরম্যাট: key, name, org, expiry, max_devices, plan_type, [pcs...]
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
  """সব লাইসেন্স ফাইল সেভ করবে"""
  with open(LICENSE_FILE, "w") as f:
    for k, v in licenses_dict.items():
      pcs_str = ",".join(v["pcs"])
      f.write(
          f"{k},{v['name']},{v['org']},{v['expiry']},{v['max_devices']},{v['plan_type']},{pcs_str}\n"
      )


@app.route("/", methods=["GET"])
def home():
  return "ISS Cloud Security Enterprise Backend is Active!"


# অ্যাডমিন ড্যাশবোর্ড ও প্ল্যান ম্যানেজমেন্ট প্যানেল
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
        <title>ISS Enterprise Subscription & License Dashboard</title>
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
        <h2>ISS Cloud Security - Subscription Manager</h2>
        <div class="container">
            <!-- ফর্ম সেকশন: নতুন প্ল্যান ও ক্লায়েন্ট অ্যাসাইন করা -->
            <div class="box">
                <h3>Add Client & Assign Plan</h3>
                <form action="/add-client" method="POST">
                    <input type="hidden" name="key" value="{ADMIN_SECRET_KEY}">
                    <label>Client Name:</label>
                    <input type="text" name="name" placeholder="e.g. Rahim Khan" required>
                    
                    <label>Organization Name:</label>
                    <input type="text" name="org" placeholder="e.g. ABC Tech Ltd" required>
                    
                    <label>License Key:</label>
                    <input type="text" name="license" placeholder="e.g. iss-1111-2026" required>
                    
                    <label>Select Subscription Plan:</label>
                    <select name="plan_choice">
                        <option value="Basic-Monthly">1. Single PC Plan (Monthly - $4.99)</option>
                        <option value="Basic-Yearly">1. Single PC Plan (Yearly - $49.99)</option>
                        <option value="Standard-Monthly">2. Multi-Device Plan 3 PCs (Monthly - $11.99)</option>
                        <option value="Standard-Yearly">2. Multi-Device Plan 3 PCs (Yearly - $119.99)</option>
                        <option value="Enterprise-Monthly">3. Enterprise Plan 5+ PCs (Monthly - $21.99)</option>
                        <option value="Enterprise-Yearly">3. Enterprise Plan 5+ PCs (Yearly - $219.99)</option>
                    </select>
                    
                    <button type="submit">Activate Plan & Save</button>
                </form>
            </div>

            <!-- ক্লায়েন্ট লিস্ট ও স্ট্যাটাস টেবিল -->
            <div class="table-box">
                <h3>Active Subscriptions & Connected Devices</h3>
                <table>
                    <tr>
                        <th>License Key</th>
                        <th>Client Name</th>
                        <th>Organization</th>
                        <th>Plan Type</th>
                        <th>Expiry Date</th>
                        <th>Devices Used</th>
                        <th>Connected PCs / IPs</th>
                    </tr>
                    {table_rows if table_rows else "<tr><td colspan='7' style='text-align:center;'>No active subscriptions found</td></tr>"}
                </table>
            </div>
        </div>
    </body>
    </html>
    """
  return render_template_string(html_page)


# নতুন ক্লায়েন্ট ও প্ল্যান ডাটাবেসে সেভ করার রুট (স্বয়ংক্রিয় মেয়াদ ক্যালকুলেশন সহ)
@app.route("/add-client", methods=["POST"])
def add_client():
  admin_key = request.form.get("key")
  client_name = request.form.get("name")
  org_name = request.form.get("org")
  license_key = request.form.get("license")
  plan_choice = request.form.get("plan_choice")

  if admin_key != ADMIN_SECRET_KEY:
    return "Unauthorized!", 401

  # প্ল্যান অনুযায়ী ডিভাইস লিমিট এবং মেয়াদ স্বয়ংক্রিয়ভাবে নির্ধারণ করা
  max_devices = 1
  duration_days = 30  # ডিফল্ট মাসিক

  if "Basic" in plan_choice:
    max_devices = 1
  elif "Standard" in plan_choice:
    max_devices = 3
  elif "Enterprise" in plan_choice:
    max_devices = 5

  if "Yearly" in plan_choice:
    duration_days = 365
  else:
    duration_days = 30

  expiry_date = (datetime.now() + timedelta(days=duration_days)).strftime(
      "%Y-%m-%d"
  )

  # ফাইল সেভ: Key, Name, Org, Expiry, MaxDevices, PlanType
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
    <h3>Success! Plan <b>{plan_choice}</b> activated for <b>{org_name}</b>. Expiry: {expiry_date}</h3>
    <a href="/admin?key={ADMIN_SECRET_KEY}">Back to Dashboard</a>
    """


# ক্লায়েন্ট স্ক্যান ও প্ল্যান ভ্যালিডেশন রুট
@app.route("/scan", methods=["POST"])
def scan_file():
  data = request.json or {}
  license_key = data.get("license_key")
  file_hash = data.get("hash")
  filename = data.get("filename", "Unknown")
  client_pc_id = data.get("pc_id", request.remote_addr)

  licenses = load_licenses()

  # ১. লাইসেন্স কি সঠিক কি না চেক
  if license_key not in licenses:
    return (
        jsonify({
            "status": "error",
            "message": "Access Denied: Invalid or Unregistered License Key!",
        }),
        403,
    )

  client_info = licenses[license_key]
  expiry_str = client_info["expiry"]
  client_name = client_info["name"]
  org_name = client_info["org"]
  max_dev = client_info["max_devices"]
  connected_pcs = client_info["pcs"]

  # ২. মেয়াদ শেষ হয়ে গেছে কি না চেক (Expiry Check)
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
                f" your subscription expired on {expiry_str}. Please renew"
                " your plan."
            ),
        }),
        403,
    )

  # ৩. ডিভাইস লিমিট চেক (Device Limit Check)
  if client_pc_id not in connected_pcs:
    if len(connected_pcs) >= max_dev:
      return (
          jsonify({
              "status": "error",
              "message": (
                  f"Device Limit Reached! Your current plan allows maximum"
                  f" {max_dev} PC(s). Please upgrade your plan."
              ),
          }),
          403,
      )
    # নতুন ডিভাইস হলে লিস্টে যুক্ত করে সেভ করা
    connected_pcs.append(client_pc_id)
    save_all_licenses(licenses)

  # ৪. থ্র্যাট বা স্ক্যান লজিক
  if file_hash in KNOWN_THREATS:
    return jsonify({
        "status": "danger",
        "is_threat": True,
        "message": f"ALERT: Threat found in {filename}!",
    })

  return jsonify(
      {"status": "clean", "is_threat": False, "message": f"{filename} is safe."}
  )


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
