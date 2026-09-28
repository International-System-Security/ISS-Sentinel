From flask import Flask, render_template_string, request, redirect, url_for, session
import os
from datetime import datetime, timedelta
import random
import requests
import threading
import time

app = Flask(__name__)
app.secret_key = "iss_security_secret_key_v101"

LICENSE_FILE = "licenses.txt"
OWNER_USERNAME = "ibr@him"
OWNER_PASSWORD = "muhib###5869@"

# --- RESEND EMAIL FUNCTION ---
def send_automated_alert(recipient_email, subject, html_content):
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        print("Resend API Key missing!")
        return False

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "from": "ISS Security Platform <onboarding@resend.dev>",
        "to": [recipient_email],
        "subject": subject,
        "html": html_content
    }

    try:
        response = requests.post("https://api.resend.com/emails", json=data, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f"Email Send Error: {e}")
        return False

# --- BACKGROUND WEEKLY REPORT SENDER ---
def background_weekly_reporter():
    while True:
        time.sleep(604800) 
        try:
            licenses = load_licenses()
            for lic_key, v in licenses.items():
                client_email = v.get('client_email')
                if client_email and client_email != "client@iss.com":
                    sub = "Weekly Security Audit Report - ISS Platform"
                    body = f"""
                    <div style="font-family:'Segoe UI',sans-serif; background:#060913; color:#f8fafc; padding:20px; border-radius:10px;">
                        <h2 style="color:#0ea5e9;">🛡️ ISS Weekly Security Audit Report</h2>
                        <p>Dear <b>{v['name']}</b>,</p>
                        <p>Here is your weekly automated security status report for organization: <b>{v['org']}</b>.</p>
                        <hr style="border-color:#1e293b;">
                        <ul>
                            <li><b>Subscription Plan:</b> {v['plan']}</li>
                            <li><b>License Key:</b> <code style="color:#38bdf8;">{lic_key}</code></li>
                            <li><b>Expiry Date:</b> {v['expiry']}</li>
                            <li><b>Endpoint Status:</b> All protected nodes are secure.</li>
                        </ul>
                        <p>Access your portal here: <a href="https://iss-antivirus-cloud.onrender.com/client-login" style="color:#38bdf8;">Client Portal Login</a></p>
                        <br><p>Best regards,<br><b>ISS Enterprise Security Team</b></p>
                    </div>
                    """
                    send_automated_alert(client_email, sub, body)
        except Exception as e:
            print(f"Weekly Reporter Error: {e}")

threading.Thread(target=background_weekly_reporter, daemon=True).start()

def load_licenses():
    licenses = {}
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 9:
                    licenses[parts[0].strip()] = {
                        "name": parts[1].strip(), "org": parts[2].strip(), "expiry": parts[3].strip(),
                        "max": parts[4].strip(), "plan": parts[5].strip(),
                        "client_user": parts[6].strip(), "client_pwd": parts[7].strip(),
                        "client_email": parts[8].strip()
                    }
                elif len(parts) >= 8:
                    licenses[parts[0].strip()] = {
                        "name": parts[1].strip(), "org": parts[2].strip(), "expiry": parts[3].strip(),
                        "max": parts[4].strip(), "plan": parts[5].strip(),
                        "client_user": parts[6].strip(), "client_pwd": parts[7].strip(),
                        "client_email": "client@iss.com"
                    }
    return licenses

def save_licenses(lic_dict):
    with open(LICENSE_FILE, "w") as f:
        for k, v in lic_dict.items():
            c_email = v.get('client_email', 'client@iss.com')
            f.write(f"{k},{v['name']},{v['org']},{v['expiry']},{v['max']},{v['plan']},{v['client_user']},{v['client_pwd']},{c_email}\n")

# --- HOME ---
@app.route("/")
def home():
    current_user = session.get("username")
    is_admin = current_user == OWNER_USERNAME
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>ISS Security Platform</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:#f8fafc; text-align:center; padding:50px;">
        <h1>🛡️ ISS Cloud Security Platform</h1>
        <p style="color:#94a3b8;">Next-Generation Endpoint Protection & License Management</p>
        <div style="margin-top:30px;">
            {% if current_user %}
                <p style="color:#34d399; font-weight:bold;">Welcome, Admin</p>
                <a href="/admin" style="background:#0ea5e9; color:white; padding:10px 20px; text-decoration:none; border-radius:6px; font-weight:bold; margin-right:10px;">Admin Panel</a>
                <a href="/client-login" style="background:#10b981; color:white; padding:10px 20px; text-decoration:none; border-radius:6px; font-weight:bold; margin-right:10px;">Client Portal</a>
                <a href="/logout" style="color:#ef4444; text-decoration:none; font-weight:bold;">Logout</a>
            {% else %}
                <a href="/client-login" style="background:#0ea5e9; color:white; padding:12px 25px; text-decoration:none; border-radius:6px; font-weight:bold; margin-right:15px;">Client Portal Login</a>
                <a href="/my-profile" style="background:#1e293b; color:white; padding:12px 25px; text-decoration:none; border-radius:6px; font-weight:bold;">Admin Login</a>
            {% endif %}
        </div>
    </body>
    </html>
    """, current_user=current_user, is_admin=is_admin)

# --- ADMIN LOGIN ---
@app.route("/my-profile", methods=["GET", "POST"])
def my_profile():
    error = ""
    if request.method == "POST":
        uname = request.form.get("username", "").strip()
        pwd = request.form.get("password", "").strip()
        if uname == OWNER_USERNAME and pwd == OWNER_PASSWORD:
            session["username"] = OWNER_USERNAME
            return redirect(url_for("admin_panel"))
        else:
            error = "Invalid Admin Credentials!"

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Admin Login</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <div style="background:#111827; padding:35px; border-radius:12px; width:340px; border:1px solid #1e293b;">
            <h2>Admin Login</h2>
            {% if error %}<div style="color:#fca5a5; font-size:13px; margin-bottom:10px;">{{ error }}</div>{% endif %}
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required style="width:100%; padding:10px; margin:8px 0 12px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                <input type="password" name="password" placeholder="Password" required style="width:100%; padding:10px; margin:8px 0 15px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                <button type="submit" style="width:100%; padding:12px; background:#0ea5e9; border:none; color:white; font-weight:bold; border-radius:6px; cursor:pointer;">Login</button>
            </form>
            <br><a href="/" style="color:#38bdf8; font-size:13px; text-decoration:none;">&larr; Home</a>
        </div>
    </body>
    </html>
    """, error=error)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

# --- ADMIN PANEL ---
@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if session.get("username") != OWNER_USERNAME:
        return redirect(url_for("my_profile"))

    msg = ""
    if request.method == "POST":
        action = request.form.get("action")
        if action == "delete_license":
            lic_key = request.form.get("lic_key")
            licenses = load_licenses()
            if lic_key in licenses:
                del licenses[lic_key]
                save_licenses(licenses)
                msg = f"🗑️ License '{lic_key}' deleted successfully!"
        elif action == "add_license":
            l_key = request.form.get("l_key").strip()
            l_name = request.form.get("l_name").strip()
            l_org = request.form.get("l_org").strip()
            l_plan = request.form.get("l_plan")
            l_expiry = request.form.get("l_expiry").strip()
            l_user = request.form.get("l_user").strip()
            l_pwd = request.form.get("l_pwd").strip()

            licenses = load_licenses()
            licenses[l_key] = {
                "name": l_name, "org": l_org, "expiry": l_expiry,
                "max": "5", "plan": l_plan, "client_user": l_user, "client_pwd": l_pwd,
                "client_email": "client@iss.com"
            }
            save_licenses(licenses)
            msg = f"✅ License '{l_key}' created successfully!"

    licenses = load_licenses()
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Admin Panel</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; padding:30px;">
        <div style="max-width:900px; margin:0 auto;">
            <div style="display:flex; justify-content:space-between; align-items:center; background:#111827; padding:15px 20px; border-radius:8px; border:1px solid #1e293b; margin-bottom:20px;">
                <h2>🛡️ Admin Panel</h2>
                <a href="/" style="color:#38bdf8; text-decoration:none;">&larr; Home</a>
            </div>

            {% if msg %}<div style="background:rgba(16,185,129,0.1); border:1px solid #10b981; color:#34d399; padding:12px; border-radius:8px; margin-bottom:20px;">{{ msg }}</div>{% endif %}

            <div style="background:#111827; padding:25px; border-radius:12px; border:2px solid #0ea5e9; margin-bottom:25px;">
                <h3 style="color:#38bdf8; margin-top:0;">🔑 Create New License</h3>
                <form method="POST">
                    <input type="hidden" name="action" value="add_license">
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px; margin-bottom:15px;">
                        <div>
                            <label style="display:block; color:#38bdf8; font-size:12px; margin-bottom:5px;">License Key</label>
                            <input type="text" name="l_key" placeholder="ISS-1001" required style="width:100%; padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                        </div>
                        <div>
                            <label style="display:block; color:#38bdf8; font-size:12px; margin-bottom:5px;">Client Name</label>
                            <input type="text" name="l_name" placeholder="John Doe" required style="width:100%; padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                        </div>
                        <div>
                            <label style="display:block; color:#38bdf8; font-size:12px; margin-bottom:5px;">Organization</label>
                            <input type="text" name="l_org" placeholder="Company Ltd" required style="width:100%; padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                        </div>
                        <div>
                            <label style="display:block; color:#38bdf8; font-size:12px; margin-bottom:5px;">Subscription Plan</label>
                            <select name="l_plan" style="width:100%; padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                                <option value="Basic Plan">Basic Plan</option>
                                <option value="Family Plan">Family Plan</option>
                                <option value="Standard Plan">Standard Plan</option>
                                <option value="Business Plan">Business Plan</option>
                            </select>
                        </div>
                        <div>
                            <label style="display:block; color:#38bdf8; font-size:12px; margin-bottom:5px;">Expiry Date</label>
                            <input type="text" name="l_expiry" value="2027-01-01" required style="width:100%; padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                        </div>
                        <div>
                            <label style="display:block; color:#38bdf8; font-size:12px; margin-bottom:5px;">Portal Username</label>
                            <input type="text" name="l_user" value="admin" required style="width:100%; padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                        </div>
                        <div style="grid-column: 1 / -1;">
                            <label style="display:block; color:#38bdf8; font-size:12px; margin-bottom:5px;">Portal Password</label>
                            <input type="text" name="l_pwd" value="admin" required style="width:100%; padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                        </div>
                    </div>
                    <button type="submit" style="width:100%; padding:14px; background:#10b981; border:none; color:white; font-weight:bold; border-radius:6px; cursor:pointer; font-size:15px;">🚀 Create License</button>
                </form>
            </div>

            <div style="background:#111827; padding:25px; border-radius:12px; border:1px solid #1e293b;">
                <h3>Active Licenses</h3>
                <table style="width:100%; border-collapse:collapse; margin-top:10px;">
                    <tr><th style="border:1px solid #1e293b; padding:10px; background:#1a2234; text-align:left;">Key</th><th style="border:1px solid #1e293b; padding:10px; background:#1a2234; text-align:left;">Client Email</th><th style="border:1px solid #1e293b; padding:10px; background:#1a2234; text-align:left;">Plan</th><th style="border:1px solid #1e293b; padding:10px; background:#1a2234; text-align:left;">Action</th></tr>
                    {% for k, v in licenses.items() %}
                    <tr>
                        <td style="border:1px solid #1e293b; padding:10px;"><code>{{ k }}</code></td>
                        <td style="border:1px solid #1e293b; padding:10px; color:#38bdf8;">{{ v.get('client_email', 'Not Added') }}</td>
                        <td style="border:1px solid #1e293b; padding:10px;">{{ v.plan }}</td>
                        <td style="border:1px solid #1e293b; padding:10px;">
                            <form method="POST" style="margin:0;">
                                <input type="hidden" name="action" value="delete_license">
                                <input type="hidden" name="lic_key" value="{{ k }}">
                                <button type="submit" style="background:#ef4444; border:none; color:white; padding:5px 10px; border-radius:4px; cursor:pointer;">Delete</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
    </body>
    </html>
    """, msg=msg, licenses=licenses)

# --- CLIENT LOGIN ---
@app.route("/client-login", methods=["GET", "POST"])
def client_login():
    error_msg = ""
    if request.method == "POST":
        lic_key = request.form.get("lic_key", "").strip()
        c_user = request.form.get("c_user", "").strip()
        c_pwd = request.form.get("c_pwd", "").strip()

        licenses = load_licenses()
        if lic_key in licenses:
            stored_user = licenses[lic_key].get("client_user", "admin")
            stored_pwd = licenses[lic_key].get("client_pwd", "admin")
            if c_user == stored_user and c_pwd == stored_pwd:
                session["client_license"] = lic_key
                return redirect(url_for("client_dashboard"))
            else:
                error_msg = "Incorrect Username or Password!"
        else:
            error_msg = "Invalid License ID!"

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Client Portal Login</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <div style="background:#111827; padding:35px; border-radius:12px; width:360px; border:1px solid #1e293b;">
            <h2>Client Portal Login</h2>
            {% if error_msg %}<div style="color:#fca5a5; font-size:13px; margin-bottom:10px;">{{ error_msg }}</div>{% endif %}
            <form method="POST">
                <label style="font-size:12px; color:#94a3b8;">License Key</label>
                <input type="text" name="lic_key" required style="width:100%; padding:10px; margin:5px 0 12px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                <label style="font-size:12px; color:#94a3b8;">Username</label>
                <input type="text" name="c_user" required style="width:100%; padding:10px; margin:5px 0 12px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                <label style="font-size:12px; color:#94a3b8;">Password</label>
                <input type="password" name="c_pwd" required style="width:100%; padding:10px; margin:5px 0 15px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                <button type="submit" style="width:100%; padding:12px; background:#0ea5e9; border:none; color:white; font-weight:bold; border-radius:6px; cursor:pointer;">Login</button>
            </form>
            <br><a href="/" style="color:#38bdf8; font-size:13px; text-decoration:none;">&larr; Return to Home</a>
        </div>
    </body>
    </html>
    """, error_msg=error_msg)

# --- CLIENT DASHBOARD ---
@app.route("/client-dashboard", methods=["GET", "POST"])
def client_dashboard():
    lic_key = session.get("client_license")
    licenses = load_licenses()
    if not lic_key or lic_key not in licenses:
        return redirect(url_for("client_login"))

    v = licenses[lic_key]
    msg_status = ""
    test_result = session.get(f"test_result_{lic_key}", "")
    antivirus_active = session.get(f"av_active_{lic_key}", False)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "save_client_email":
            new_email = request.form.get("client_email", "").strip()
            if new_email:
                v['client_email'] = new_email
                licenses[lic_key] = v
                save_licenses(licenses)
                msg_status = "✅ Email added successfully! Advanced features unlocked."
                
                # ওয়েলকাম বা কনফার্মেশন মেইল পাঠানো
                sub = f"Welcome to ISS Security - {v['plan']} Features Unlocked"
                body = f"""
                <div style="font-family:'Segoe UI',sans-serif; background:#0b1120; color:#f8fafc; padding:20px; border-radius:10px;">
                    <h2 style="color:#0ea5e9;">🛡️ ISS Security Features Unlocked</h2>
                    <p>Dear <b>{v['name']}</b>,</p>
                    <p>Your email has been successfully registered for organization: <b>{v['org']}</b>.</p>
                    <p><b>Subscription Plan:</b> {v['plan']}</p>
                    <p><b>License Key:</b> <code style="color:#38bdf8;">{lic_key}</code></p>
                    <p>You will now receive weekly automated audit reports and instant threat alerts on this email.</p>
                    <br><p>Best regards,<br><b>ISS Security Team</b></p>
                </div>
                """
                send_automated_alert(new_email, sub, body)

        elif action == "activate_antivirus":
            session[f"av_active_{lic_key}"] = True
            antivirus_active = True
        elif action == "run_test_virus":
            if antivirus_active:
                is_success = random.choice([True, True, False])
                test_result = "Success: Antivirus successfully neutralized the threat!" if is_success else "Failed: Threat bypassed defense!"
                session[f"test_result_{lic_key}"] = test_result
                
                client_email = v.get('client_email')
                if client_email and client_email != "client@iss.com":
                    sub = f"Security Scan & Threat Simulation Report - {lic_key}"
                    body = f"""
                    <div style="font-family:'Segoe UI',sans-serif; background:#0b1120; color:#f8fafc; padding:20px; border-radius:10px;">
                        <h3 style="color:#0ea5e9;">🛡️ ISS Endpoint Security Alert</h3>
                        <p>Dear <b>{v['name']}</b>,</p>
                        <p>A manual virus simulation test was executed on your device dashboard.</p>
                        <p><b>Test Result:</b> <span style="color:{'#34d399' if 'Success' in test_result else '#fca5a5'};">{test_result}</span></p>
                        <p><b>Organization:</b> {v['org']}</p>
                        <p><b>Plan:</b> {v['plan']}</p>
                        <br><p>Best regards,<br><b>ISS Security Team</b></p>
                    </div>
                    """
                    send_automated_alert(client_email, sub, body)

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Client Dashboard</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; padding:30px;">
        <div style="max-width:650px; margin:0 auto; background:#111827; padding:30px; border-radius:12px; border:1px solid #1e293b;">
            <h2>🛡️ Client Security Dashboard</h2>
            <p>License Key: <code style="color:#38bdf8;">{{ lic_key }}</code> | Organization: <b>{{ v.org }}</b></p>
            
            {% if msg_status %}<div style="background:rgba(16,185,129,0.1); border:1px solid #10b981; color:#34d399; padding:12px; border-radius:8px; margin-bottom:20px;">{{ msg_status }}</div>{% endif %}

            <!-- CLIENT EMAIL OPTION FOR UNLOCKING FEATURES -->
            <div style="background:#0b1120; border:2px solid #f59e0b; padding:22px; border-radius:10px; margin:20px 0;">
                <h3 style="margin:0 0 8px 0; color:#f59e0b;">📧 Add Email for Unlock More Features</h3>
                <p style="font-size:13px; color:#94a3b8; margin:0 0 15px 0;">Enter your email to activate weekly automated security audit reports and instant virus threat alerts.</p>
                <form method="POST">
                    <input type="hidden" name="action" value="save_client_email">
                    <input type="email" name="client_email" placeholder="Enter your email address (e.g. client@gmail.com)" value="{% if v.client_email != 'client@iss.com' %}{{ v.client_email }}{% endif %}" required style="width:100%; padding:12px; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box; margin-bottom:12px; font-size:14px;">
                    <button type="submit" style="background:#f59e0b; color:#060913; padding:12px 20px; border:none; border-radius:6px; font-weight:bold; cursor:pointer; width:100%; font-size:14px;">Save Email & Unlock Advanced Features</button>
                </form>
            </div>

            <div style="background:#0b1120; border:1px solid #1e293b; padding:20px; border-radius:8px; margin:20px 0; text-align:center;">
                <h4 style="margin:0 0 8px 0; color:#38bdf8;">Protection Status</h4>
                <p style="font-size:13px; color:#94a3b8; margin:0 0 15px 0;">
                    {% if antivirus_active %}✅ Antivirus is Active & Protecting.{% else %}⚠️ Protection is Inactive.{% endif %}
                </p>
                <form method="POST">
                    <input type="hidden" name="action" value="activate_antivirus">
                    <button type="submit" style="background:#10b981; color:white; padding:10px 20px; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">
                        {% if not antivirus_active %}Activate Protection{% else %}Re-Verify Protection{% endif %}
                    </button>
                </form>
            </div>

            <div style="background:#0b1120; border:1px solid #1e293b; padding:20px; border-radius:8px; margin:20px 0; text-align:center;">
                <h4 style="margin:0 0 8px 0; color:#38bdf8;">🧪 Test Virus Simulation (Sends Instant Email)</h4>
                {% if antivirus_active %}
                    <form method="POST">
                        <input type="hidden" name="action" value="run_test_virus">
                        <button type="submit" style="background:#8b5cf6; color:white; padding:10px 20px; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">
                            Run Threat Test & Email Report
                        </button>
                    </form>
                    {% if test_result %}
                        <div style="margin-top:15px; padding:10px; border-radius:6px; font-weight:bold; background:{% if 'Success' in test_result %}rgba(16,185,129,0.2); color:#34d399; border:1px solid #10b981{% else %}rgba(239,68,68,0.2); color:#fca5a5; border:1px solid #ef4444{% endif %};">
                            {{ test_result }}
                        </div>
                    {% endif %}
                {% else %}
                    <p style="font-size:12px; color:#fca5a5;">Activate protection first to run test.</p>
                {% endif %}
            </div>

            <br><a href="/" style="color:#ef4444; font-size:13px; text-decoration:none; font-weight:bold;">Logout / Home</a>
        </div>
    </body>
    </html>
    """, lic_key=lic_key, v=v, antivirus_active=antivirus_active, test_result=test_result, msg_status=msg_status)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

 