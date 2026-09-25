from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
# সেশন ও নিরাপত্তার জন্য সিক্রেট কি
app.secret_key = "iss_antivirus_super_secret_key"

# ইন-মেমোরি ডাটাবেস
LICENSES = {}  # { license_key: { 'expiry_date': 'YYYY-MM-DD', 'plan': 'Basic/Standard/Enterprise', 'device_id': None } }
ACTIVATED_DEVICES = {}  # { ip_address: license_key }

# ডিফল্ট অ্যাডমিন ক্রিক্রেডেনশিয়াল
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin"}


# --- হোম পেজ (এখানে রুট করলে লগইন অপশনে পাঠাতে পারেন) ---
@app.route("/")
def home():
  return render_template("home.html") if "home.html" in globals() else """
    <h2>Welcome to ISS Antivirus Cloud</h2>
    <p><a href="/admin/login">Admin Login</a> | <a href="/client-login">Client Portal Login</a></p>
    """


# --- অ্যাডমিন লগইন রাউট ---
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
  if request.method == "POST":
    username = request.form.get("username")
    password = request.form.get("password")
    if (
        username == ADMIN_CREDENTIALS["username"]
        and password == ADMIN_CREDENTIALS["password"]
    ):
      session["is_admin"] = True
      return redirect(url_for("admin_dashboard"))
    else:
      flash("ভুল ইউজারনেম বা পাসওয়ার্ড!", "danger")
  return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
  session.pop("is_admin", None)
  return redirect(url_for("admin_login"))


# --- অ্যাডমিন ড্যাশবোর্ড (সিকিউরড) ---
@app.route("/admin", methods=["GET", "POST"])
def admin_dashboard():
  if not session.get("is_admin"):
    return redirect(url_for("admin_login"))

  if request.method == "POST":
    action = request.form.get("action")

    # পাসওয়ার্ড বা ইউজারনেম পরিবর্তনের অপশন
    if action == "change_credentials":
      new_user = request.form.get("new_username")
      new_pass = request.form.get("new_password")
      if new_user and new_pass:
        ADMIN_CREDENTIALS["username"] = new_user
        ADMIN_CREDENTIALS["password"] = new_pass
        flash(
            "অ্যাডমিন ইউজারনেম ও পাসওয়ার্ড সফলভাবে আপডেট করা হয়েছে!", "success"
        )
      else:
        flash("ইউজারনেম বা পাসওয়ার্ড খালি রাখা যাবে না!", "danger")

    # নতুন লাইসেন্স জেনারেট করা
    elif action == "generate_license":
      import uuid

      license_key = "ISS-" + str(uuid.uuid4())[:8].upper()
      expiry_date = request.form.get("expiry_date")
      plan_tier = request.form.get("plan_tier")

      if expiry_date and plan_tier:
        LICENSES[license_key] = {
            "expiry_date": expiry_date,
            "plan": plan_tier,
            "device_id": None,
        }
        flash(f"লাইসেন্স সফলভাবে তৈরি হয়েছে: {license_key}", "success")
      else:
        flash("তারিখ এবং প্ল্যান সিলেক্ট করুন!", "danger")

  return render_template(
      "admin.html", licenses=LICENSES, admin_user=ADMIN_CREDENTIALS["username"]
  )


# --- ক্লায়েন্ট লগইন রাউট ---
@app.route("/client-login", methods=["GET", "POST"])
def client_login():
  if request.method == "POST":
    license_key = request.form.get("license_key")
    if license_key in LICENSES:
      session["client_license"] = license_key
      return redirect(url_for("client_dashboard"))
    else:
      flash("অবৈধ বা ভুল লাইসেন্স কি!", "danger")
  return render_template("client_login.html")


@app.route("/client-logout")
def client_logout():
  session.pop("client_license", None)
  return redirect(url_for("client_login"))


# --- ক্লায়েন্ট ড্যাশবোর্ড (সিকিউরড) ---
@app.route("/client", methods=["GET", "POST"])
def client_dashboard():
  license_key = session.get("client_license")
  if not license_key or license_key not in LICENSES:
    return redirect(url_for("client_login"))

  license_data = LICENSES[license_key]
  client_ip = request.remote_addr

  if request.method == "POST":
    action = request.form.get("action")
    if action == "link_device":
      license_data["device_id"] = client_ip
      ACTIVATED_DEVICES[client_ip] = license_key
      flash("ডিভাইস সফলভাবে লিংক করা হয়েছে!", "success")

  return render_template(
      "client.html",
      license_key=license_key,
      data=license_data,
      client_ip=client_ip,
  )


# --- অ্যান্টিভাইরাস API (স্ক্যান করার জন্য) ---
@app.route("/api/scan", methods=["POST"])
def api_scan():
  data = request.json
  file_hash = data.get("file_hash")
  license_key = data.get("license_key")

  if not license_key or license_key not in LICENSES:
    return {"status": "error", "message": "Invalid License Key"}, 403

  license_info = LICENSES[license_key]
  expiry_date = datetime.strptime(license_info["expiry_date"], "%Y-%m-%d")
  if datetime.now() > expiry_date:
    return {"status": "error", "message": "License Expired"}, 403

  KNOWN_THREATS = {
      "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": (
          "EICAR-Test-File"
      ),
      "5d41402abc4b2a76b9719d911017c592": "Trojan.Generic.Sample",
  }

  if file_hash in KNOWN_THREATS:
    return {
        "status": "threat_found",
        "threat_name": KNOWN_THREATS[file_hash],
    }
  else:
    return {"status": "safe"}


if __name__ == "__main__":
  app.run(debug=True)
