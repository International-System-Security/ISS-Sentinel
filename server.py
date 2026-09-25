from datetime import datetime
import os
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

LICENSE_FILE = "licenses.txt"
ADMIN_SECRET_KEY = (
    "my_super_secret_admin_key_123"  # এটি আপনার প্যানেলে ঢোকার পাসওয়ার্ড
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
        if len(parts) >= 3:
          # ফরম্যাট: license_key, client_name, expiry_date
          licenses_dict[parts[0].strip()] = {
              "name": parts[1].strip(),
              "expiry": parts[2].strip(),
          }
  return licenses_dict


@app.route("/", methods=["GET"])
def home():
  return "ISS Cloud Antivirus Admin & Backend is Running!"


# ১. ব্রাউজারে একটি সুন্দর ফর্ম দেখানোর রুট (যেখানে নাম, আইডি, ডেট বসাবেন)
@app.route("/admin", methods=["GET"])
def admin_panel():
  key = request.args.get("key")
  if key != ADMIN_SECRET_KEY:
    return (
        "<h3>Unauthorized! Please provide correct admin key in URL (e.g.,"
        " /admin?key=YOUR_KEY)</h3>",
        401,
    )

  html_page = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ISS License Manager</title>
        <style>
            body { font-family: Arial; background: #f4f4f9; padding: 50px; }
            .box { background: white; padding: 20px; border-radius: 8px; width: 350px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }
            input { width: 100%%; padding: 8px; margin: 8px 0; box-sizing: border-box; }
            button { background: #28a745; color: white; padding: 10px; border: none; width: 100%%; border-radius: 4px; cursor: pointer; }
            button:hover { background: #218838; }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Add New ISS License</h2>
            <form action="/add-client" method="POST">
                <input type="hidden" name="key" value="my_super_secret_admin_key_123">
                <label>Client Name:</label>
                <input type="text" name="name" placeholder="e.g. Rahim Khan" required>
                <label>License ID:</label>
                <input type="text" name="license" placeholder="e.g. iss-1111-2026" required>
                <label>Expiry Date:</label>
                <input type="date" name="expiry" required>
                <button type="submit">Save License</button>
            </form>
        </div>
    </body>
    </html>
    """
  return render_template_string(html_page)


# ২. ফর্ম থেকে ডাটা রিসিভ করে ফাইলে সেভ করার রুট
@app.route("/add-client", methods=["POST"])
def add_client():
  admin_key = request.form.get("key")
  client_name = request.form.get("name")
  license_key = request.form.get("license")
  expiry_date = request.form.get("expiry")

  if admin_key != ADMIN_SECRET_KEY:
    return "Unauthorized!", 401

  # ফাইলে ডাটা সেভ করা (License, Name, Expiry)
  with open(LICENSE_FILE, "a") as f:
    f.write(f"{license_key},{client_name},{expiry_date}\n")

  return f"""
    <h3>Success! License for <b>{client_name}</b> ({license_key}) has been added with expiry {expiry_date}.</h3>
    <a href="/admin?key={ADMIN_SECRET_KEY}">Go Back</a>
    """


# ৩. ক্লায়েন্টের অ্যান্টিভাইরাস থেকে স্ক্যান রিকোয়েস্ট ও মেয়াদ চেক করার রুট
@app.route("/scan", methods=["POST"])
def scan_file():
  data = request.json or {}
  license_key = data.get("license_key")
  file_hash = data.get("hash")
  filename = data.get("filename", "Unknown")

  active_licenses = load_licenses()

  # লাইসেন্স সার্ভারে আছে কি না চেক
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

  # আজকের ডেটের সাথে মেয়াদ মিলিয়ে দেখা
  today_date = datetime.now().date()
  try:
    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
  except ValueError:
    return jsonify({"status": "error", "message": "Date format error."}), 500

  # মেয়াদ পার হয়ে গেলে অটো বন্ধ হয়ে যাবে এবং নোটিফিকেশন পাঠাবে
  if today_date > expiry_date:
    return (
        jsonify({
            "status": "expired",
            "message": (
                f"Dear {client_name}, your ISS license has expired on"
                f" {expiry_str}. Please renew to continue protection."
            ),
        }),
        403,
    )

  # মেয়াদ ঠিক থাকলে স্ক্যান চলবে
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
