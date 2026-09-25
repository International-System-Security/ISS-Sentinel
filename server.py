from datetime import datetime, timedelta
import os
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

LICENSE_FILE = "licenses.txt"
ADMIN_SECRET_KEY = "my_super_secret_admin_key_123"

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
    <p>Client Portal: <a href='/client-login'>https://iss-antivirus-cloud.onrender.com/client-login</a></p>
    <p>Admin Dashboard: <a href='/admin?key=my_super_secret_admin_key_123'>https://iss-antivirus-cloud.onrender.com/admin?key=my_super_secret_admin_key_123</a></p>
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
            <td>{v['plan_type']}</td>
            <td>{v['expiry']}</td>
            <td><b>{len(v['pcs'])} / {v['max_devices']}</b></td>
            <td><code>{connected_list}</code></td>
        </tr>
        """

  html_page = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ISS Admin Dashboard</title>
        <style>
            body {{ font-family: Arial; background: #f4f4f9; padding: 25px; }}
            .container {{ display: flex; gap: 25px; flex-wrap: wrap; }}
            .box {{ background: white; padding: 20px; border-radius: 8px; width: 380px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); height: fit-content; }}
            .table-box {{ background: white; padding: 20px; border-radius: 8px; flex-grow: 1; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); overflow-x: auto; }}
            input, select {{ width: 100%%; padding: 8px; margin: 6px 0 12px 0; box-sizing: border-box; }}
            button {{ background: #2563eb; color: white; padding: 10px; border: none; width: 100%%; border-radius: 4px; cursor: pointer; font-weight: bold; }}
            table {{ width: 100%%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #e2e8f0; padding: 8px; text-align: left; font-size: 13px; }}
            th {{ background-color: #0f172a; color: white; }}
        </style>
    </head>
    <body>
        <h2>ISS Cloud Security - Admin Dashboard</h2>
        <div class="container">
            <div class="box">
                <h3>Create License</h3>
                <form action="/add-client" method="POST">
                    <input type="hidden" name="key" value="{ADMIN_SECRET_KEY}">
                    <label>Client Name:</label>
                    <input type="text" name="name" required>
                    <label>Organization:</label>
                    <input type="text" name="org" required>
                    <label>License ID:</label>
                    <input type="text" name="license" placeholder="e.g. iss-1111-2026" required>
                    <label>Plan:</label>
                    <select name="plan_choice">
                        <option value="Basic-Monthly">Basic Monthly ($4.99)</option>
                        <option value="Standard-Monthly">Standard Monthly ($11.99)</option>
                        <option value="Enterprise-Monthly">Enterprise Monthly ($21.99)</option>
                    </select>
                    <button type="submit">Create License</button>
                </form>
            </div>
            <div class="table-box">
                <h3>Active Licenses</h3>
                <table>
                    <tr>
                        <th>License ID</th>
                        <th>Name</th>
                        <th>Org</th>
                        <th>Plan</th>
                        <th>Expiry</th>
                        <th>Devices</th>
                        <th>Connected PCs</th>
                    </tr>
                    {table_rows if table_rows else "<tr><td colspan='7' style='text-align:center;'>No licenses found</td></tr>"}
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

  max_devices = 3
  if "Basic" in plan_choice:
    max_devices = 1
  elif "Enterprise" in plan_choice:
    max_devices = 5

  expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

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
    <h3>Success! License <b>{license_key}</b> created.</h3>
    <a href="/admin?key={ADMIN_SECRET_KEY}">Back to Dashboard</a>
    """


# ২. ক্লায়েন্ট পোর্টাল
@app.route("/client-login", methods=["GET", "POST"])
def client_login():
  error_msg = ""
  if request.method == "POST":
    license_key = request.form.get("license_key", "").strip()
    licenses = load_licenses()

    if license_key in licenses:
      v = licenses[license_key]
      connected_devices = (
          ", ".join(v["pcs"]) if v["pcs"] else "No devices connected yet"
      )

      return render_template_string(f"""
            <!DOCTYPE html>
            <html>
            <head><title>Client Portal</title></head>
            <body style="font-family: Arial; background: #f8fafc; padding: 30px;">
                <div style="background: white; max-width: 500px; margin: 0 auto; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2>Client Security Portal</h2>
                    <p style="color: green; font-weight: bold;">● Status: Active & Secured</p>
                    <p><b>Organization:</b> {v['org']} ({v['name']})</p>
                    <p><b>Plan:</b> {v['plan_type']}</p>
                    <p><b>Expiry Date:</b> {v['expiry']}</p>
                    <p><b>Devices Used:</b> {len(v['pcs'])} / {v['max_devices']} ({connected_devices})</p>
                    <a href="/client-login" style="background: #0284c7; color: white; padding: 8px 15px; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 15px;">Back</a>
                </div>
            </body>
            </html>
            """)
    else:
      error_msg = "Invalid License ID!"

  return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head><title>Client Login</title></head>
    <body style="font-family: Arial; background: #f1f5f9; display: flex; justify-content: center; align-items: center; height: 100vh;">
        <div style="background: white; padding: 25px; border-radius: 8px; width: 320px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3>Client Portal Login</h3>
            {f'<p style="color: red; font-size: 13px;">{error_msg}</p>' if error_msg else ''}
            <form method="POST">
                <input type="text" name="license_key" placeholder="Enter License ID" required style="width: 100%%; padding: 8px; margin: 10px 0; box-sizing: border-box;">
                <button type="submit" style="background: #0ea5e9; color: white; border: none; padding: 9px; width: 100%%; border-radius: 4px; font-weight: bold; cursor: pointer;">Login</button>
            </form>
        </div>
    </body>
    </html>
    """)


# ৩. স্ক্যান রুট
@app.route("/scan", methods=["POST"])
def scan_file():
  data = request.json or {}
  license_key = data.get("license_key")
  file_hash = data.get("hash")
  filename = data.get("filename", "Unknown")
  client_pc_id = data.get("pc_id", request.remote_addr)

  licenses = load_licenses()
  if license_key not in licenses:
    return jsonify({"status": "error", "message": "Invalid License ID!"}), 403

  client_info = licenses[license_key]
  if datetime.now().date() > datetime.strptime(
      client_info["expiry"], "%Y-%m-%d"
  ).date():
    return jsonify({"status": "expired", "message": "Subscription Expired!"}), 403

  if client_pc_id not in client_info["pcs"]:
    if len(client_info["pcs"]) >= client_info["max_devices"]:
      return jsonify({"status": "error", "message": "Device Limit Reached!"}), 403
    client_info["pcs"].append(client_pc_id)
    save_all_licenses(licenses)

  if file_hash in KNOWN_THREATS:
    return jsonify({"status": "danger", "is_threat": True, "message": "Threat found!"})

  return jsonify({"status": "clean", "is_threat": False, "message": "File is safe."})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
