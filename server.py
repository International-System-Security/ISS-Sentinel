from datetime import datetime
import os
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

LICENSE_FILE = "licenses.txt"
ADMIN_SECRET_KEY = (
    "my_super_secret_admin_key_123"  # আপনার সিক্রেট অ্যাডমিন পাসওয়ার্ড
)

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
        if len(parts) >= 4:
          # ফরম্যাট: license_key, client_name, org_name, expiry_date, connected_pc
          key = parts[0].strip()
          licenses_dict[key] = {
              "name": parts[1].strip(),
              "org": parts[2].strip(),
              "expiry": parts[3].strip(),
              "pc": parts[4].strip() if len(parts) > 4 else "Not Recorded",
          }
  return licenses_dict


def update_pc_info(target_key, new_pc):
  """ক্লায়েন্ট স্ক্যান করার সময় তার পিসির নাম বা আইপি আপডেট করে দেবে"""
  licenses = load_licenses()
  if target_key in licenses:
    licenses[target_key]["pc"] = new_pc

    # আবার ফাইলে সব ডেটা রি-রাইট করা
    with open(LICENSE_FILE, "w") as f:
      for k, v in licenses.items():
        f.write(f"{k},{v['name']},{v['org']},{v['expiry']},{v['pc']}\n")


@app.route("/", methods=["GET"])
def home():
  return "ISS Cloud Antivirus Enterprise Backend is Running!"


# ১. অ্যাডমিন প্যানেল ফর্ম (যেখানে অর্গানাইজেশন ও পিসির তথ্য সহ লাইসেন্স এড করা যাবে)
@app.route("/admin", methods=["GET"])
def admin_panel():
  key = request.args.get("key")
  if key != ADMIN_SECRET_KEY:
    return "<h3>Unauthorized! Incorrect Admin Key.</h3>", 401

  licenses = load_licenses()

  # বর্তমান সব ক্লায়েন্টের লিস্ট টেবিল আকারে দেখানোর জন্য HTML
  table_rows = ""
  for k, v in licenses.items():
    table_rows += f"""
        <tr>
            <td><b>{k}</b></td>
            <td>{v['name']}</td>
            <td>{v['org']}</td>
            <td>{v['expiry']}</td>
            <td><code>{v['pc']}</code></td>
        </tr>
        """

  html_page = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ISS Enterprise License Manager</title>
        <style>
            body {{ font-family: Arial; background: #f4f4f9; padding: 30px; }}
            .container {{ display: flex; gap: 30px; flex-wrap: wrap; }}
            .box {{ background: white; padding: 20px; border-radius: 8px; width: 350px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); height: fit-content; }}
            .table-box {{ background: white; padding: 20px; border-radius: 8px; flex-grow: 1; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); overflow-x: auto; }}
            input {{ width: 100%%; padding: 8px; margin: 8px 0; box-sizing: border-box; }}
            button {{ background: #28a745; color: white; padding: 10px; border: none; width: 100%%; border-radius: 4px; cursor: pointer; }}
            button:hover {{ background: #218838; }}
            table {{ width: 100%%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 14px; }}
            th {{ background-color: #007bff; color: white; }}
        </style>
    </head>
    <body>
        <h2>ISS Enterprise License & Client Manager</h2>
        <div class="container">
            <!-- ফর্ম সেকশন -->
            <div class="box">
                <h3>Add New Client</h3>
                <form action="/add-client" method="POST">
                    <input type="hidden" name="key" value="{ADMIN_SECRET_KEY}">
                    <label>Client Name:</label>
                    <input type="text" name="name" placeholder="e.g. Rahim Khan" required>
                    <label>Organization Name:</label>
                    <input type="text" name="org" placeholder="e.g. Acme Corporation" required>
                    <label>License ID:</label>
                    <input type="text" name="license" placeholder="e.g. iss-1111-2026" required>
                    <label>Expiry Date:</label>
                    <input type="date" name="expiry" required>
                    <button type="submit">Save License</button>
                </form>
            </div>

            <!-- ক্লায়েন্ট লিস্ট ও পিসি ইনফো টেবিল -->
            <div class="table-box">
                <h3>Active Clients & Connected Devices</h3>
                <table>
                    <tr>
                        <th>License Key</th>
                        <th>Client Name</th>
                        <th>Organization</th>
                        <th>Expiry Date</th>
                        <th>Connected PC / Host</th>
                    </tr>
                    {table_rows if table_rows else "<tr><td colspan='5' style='text-align:center;'>No clients found</td></tr>"}
                </table>
            </div>
        </div>
    </body>
    </html>
    """
  return render_template_string(html_page)


# ২. নতুন ক্লায়েন্ট সেভ করার রুট
@app.route("/add-client", methods=["POST"])
def add_client():
  admin_key = request.form.get("key")
  client_name = request.form.get("name")
  org_name = request.form.get("org")
  license_key = request.form.get("license")
  expiry_date = request.form.get("expiry")

  if admin_key != ADMIN_SECRET_KEY:
    return "Unauthorized!", 401

  # ফাইল সেভ: Key, Name, Org, Expiry, Default PC status
  with open(LICENSE_FILE, "a") as f:
    f.write(f"{license_key},{client_name},{org_name},{expiry_date},Not Connected Yet\n")

  return f"""
    <h3>Success! Organization <b>{org_name}</b> ({client_name}) added.</h3>
    <a href="/admin?key={ADMIN_SECRET_KEY}">Go Back to Dashboard</a>
    """


# ৩. স্ক্যান এবং পিসি ট্র্যাক করার রুট
@app.route("/scan", methods=["POST"])
def scan_file():
  data = request.json or {}
  license_key = data.get("license_key")
  file_hash = data.get("hash")
  filename = data.get("filename", "Unknown")
  client_pc_name = data.get("pc_name", request.remote_addr)  # ক্লায়েন্টের পিসি নাম বা আইপি

  active_licenses = load_licenses()

  if license_key not in active_licenses:
    return (
        jsonify({
            "status": "error",
            "message": "Access Denied: Invalid License Key!",
        }),
        403,
    )

  client_info = active_licenses[license_key]
  expiry_str = client_info["expiry"]
  client_name = client_info["name"]
  org_name = client_info["org"]

  # স্ক্যান করার সময় স্বয়ংক্রিয়ভাবে পিসির নাম বা আইপি আপডেট করে নেওয়া
  update_pc_info(license_key, client_pc_name)

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
                f" your license expired on {expiry_str}. Please renew."
            ),
        }),
        403,
    )

  # স্ক্যান প্রসেস
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
