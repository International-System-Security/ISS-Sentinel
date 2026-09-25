from datetime import datetime, timedelta
import os
from flask import Flask, jsonify, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = "iss_super_secure_client_session_key"

LICENSE_FILE = "licenses.txt"

# Default Admin Credentials for Admin Panel
ADMIN_CONFIG = {"username": "admin", "password": "admin"}

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
                if len(parts) >= 8:
                    key = parts[0].strip()
                    licenses_dict[key] = {
                        "name": parts[1].strip(),
                        "org": parts[2].strip(),
                        "expiry": parts[3].strip(),
                        "max_devices": int(parts[4].strip()),
                        "plan_type": parts[5].strip(),
                        "client_user": parts[6].strip(),
                        "client_pwd": parts[7].strip(),
                        "pcs": [p.strip() for p in parts[8:] if p.strip()]
                    }
                elif len(parts) >= 6:
                    key = parts[0].strip()
                    licenses_dict[key] = {
                        "name": parts[1].strip(),
                        "org": parts[2].strip(),
                        "expiry": parts[3].strip(),
                        "max_devices": int(parts[4].strip()),
                        "plan_type": parts[5].strip(),
                        "client_user": "admin",
                        "client_pwd": "admin",
                        "pcs": [p.strip() for p in parts[6:] if p.strip()]
                    }
    return licenses_dict

def save_all_licenses(licenses_dict):
    with open(LICENSE_FILE, "w") as f:
        for k, v in licenses_dict.items():
            pcs_str = ",".join(v["pcs"])
            f.write(f"{k},{v['name']},{v['org']},{v['expiry']},{v['max_devices']},{v['plan_type']},{v['client_user']},{v['client_pwd']},{pcs_str}\n")

# --- Professional Landing Page ---
@app.route("/", methods=["GET"])
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ISS Cloud Security & Enterprise Antivirus</title>
        <style>
            :root {
                --bg-primary: #090d16;
                --bg-card: #111827;
                --accent-blue: #0ea5e9;
                --accent-hover: #0284c7;
                --text-main: #f8fafc;
                --text-muted: #94a3b8;
                --border-color: #1e293b;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: var(--bg-primary);
                color: var(--text-main);
                margin: 0; padding: 0;
                display: flex; flex-direction: column; min-height: 100vh;
                justify-content: space-between;
            }
            .header {
                padding: 20px 40px; display: flex; justify-content: space-between; align-items: center;
                border-bottom: 1px solid var(--border-color);
            }
            .logo {
                font-size: 20px; font-weight: bold; letter-spacing: 1px; color: var(--accent-blue);
                display: flex; align-items: center; gap: 8px;
            }
            .container { max-width: 900px; margin: auto; text-align: center; padding: 40px 20px; }
            h1 {
                font-size: 42px; margin-bottom: 15px; font-weight: 800;
                background: linear-gradient(to right, #38bdf8, #818cf8);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            }
            p.subtitle { font-size: 18px; color: var(--text-muted); margin-bottom: 40px; line-height: 1.6; }
            .cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 40px; }
            .card {
                background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px;
                padding: 30px; text-align: left; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
                transition: transform 0.2s, border-color 0.2s;
            }
            .card:hover { transform: translateY(-5px); border-color: var(--accent-blue); }
            .card h3 { margin-top: 0; font-size: 20px; color: var(--text-main); }
            .card p { color: var(--text-muted); font-size: 14px; line-height: 1.5; }
            .btn {
                display: inline-block; background-color: var(--accent-blue); color: white;
                padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 14px;
                margin-top: 15px; transition: background-color 0.2s;
            }
            .btn:hover { background-color: var(--accent-hover); }
            .btn-outline { background-color: transparent; border: 1px solid var(--accent-blue); color: var(--accent-blue); }
            .btn-outline:hover { background-color: var(--accent-blue); color: white; }
            .footer { text-align: center; padding: 20px; color: var(--text-muted); font-size: 13px; border-top: 1px solid var(--border-color); }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">🛡️ ISS CLOUD SECURITY</div>
            <div><a href="/client-login" class="btn btn-outline" style="margin-top:0; padding: 8px 16px;">Client Portal</a></div>
        </div>
        <div class="container">
            <h1>Next-Gen Cloud Endpoint Security</h1>
            <p class="subtitle">Advanced enterprise-grade protection, real-time threat intelligence, and centralized device management backed by ISS infrastructure.</p>
            <div class="cards-grid">
                <div class="card">
                    <h3>Client Portal</h3>
                    <p>Manage your active license, monitor connected devices, and secure your endpoints instantly with one-click setup.</p>
                    <a href="/client-login" class="btn">Access Client Portal</a>
                </div>
                <div class="card">
                    <h3>Admin Dashboard</h3>
                    <p>Centralized control panel for issuing licenses, monitoring expiration cycles, and managing system credentials securely.</p>
                    <a href="/admin/login" class="btn btn-outline">Admin Login</a>
                </div>
            </div>
        </div>
        <div class="footer">&copy; 2026 ISS Security Systems. All Rights Reserved. Enterprise Cloud Backend Active.</div>
    </body>
    </html>
    """

# --- Admin Login Route ---
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error_msg = ""
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")
        if user == ADMIN_CONFIG["username"] and pwd == ADMIN_CONFIG["password"]:
            session['is_admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            error_msg = "Invalid Username or Password!"

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Login - ISS Security</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #090d16; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; color: #f8fafc; }}
            .card {{ background: #111827; padding: 35px; border-radius: 12px; width: 100%; max-width: 380px; border: 1px solid #1e293b; box-shadow: 0 15px 30px rgba(0,0,0,0.5); }}
            input {{ width: 100%; padding: 12px; margin: 8px 0 20px 0; box-sizing: border-box; background: #090d16; border: 1px solid #334155; border-radius: 6px; color: white; font-size: 14px; }}
            input:focus {{ outline: none; border-color: #0ea5e9; }}
            button {{ background: #0ea5e9; color: white; border: none; padding: 12px; width: 100%; border-radius: 6px; font-weight: bold; cursor: pointer; transition: background 0.2s; }}
            button:hover {{ background: #0284c7; }}
            .label {{ font-size: 13px; font-weight: 600; color: #94a3b8; display: block; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2 style="margin-top: 0; color: #f8fafc; font-size: 22px;">Admin Control Center</h2>
            <p style="font-size: 13px; color: #94a3b8; margin-bottom: 20px;">Secure administrative authentication required.</p>
            {f'<div style="background: rgba(239,68,68,0.1); border: 1px solid #ef4444; color: #fca5a5; padding: 10px; border-radius: 6px; font-size: 13px; margin-bottom: 15px;">{error_msg}</div>' if error_msg else ''}
            <form method="POST">
                <span class="label">Username</span>
                <input type="text" name="username" value="admin" required>
                <span class="label">Password</span>
                <input type="password" name="password" value="admin" required>
                <button type="submit">Authenticate</button>
            </form>
        </div>
    </body>
    </html>
    """)

@app.route("/admin/logout")
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))

# --- Professional Admin Dashboard ---
@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    success_msg = ""
    if request.method == "POST":
        action = request.form.get("action")
        if action == "change_credentials":
            new_user = request.form.get("new_username")
            new_pwd = request.form.get("new_password")
            if new_user and new_pwd:
                ADMIN_CONFIG["username"] = new_user
                ADMIN_CONFIG["password"] = new_pwd
                success_msg = "✅ Admin security credentials updated successfully!"

    licenses = load_licenses()
    table_rows = ""
    for k, v in licenses.items():
        connected_list = ", ".join(v['pcs']) if v['pcs'] else "No devices connected"
        table_rows += f"""
        <tr>
            <td><code style="background: #1e293b; color: #38bdf8; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{k}</code></td>
            <td><b>{v['name']}</b></td>
            <td>{v['org']}</td>
            <td><span style="background: rgba(14,165,233,0.1); color: #38bdf8; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{v['plan_type']}</span></td>
            <td>{v['expiry']}</td>
            <td><code style="color: #cbd5e1;">{v['client_user']} / {v['client_pwd']}</code></td>
            <td><b>{len(v['pcs'])} / {v['max_devices']}</b></td>
            <td><code style="color: #94a3b8; font-size: 12px;">{connected_list}</code></td>
        </tr>
        """

    default_expiry = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ISS Enterprise Admin Dashboard</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #090d16; color: #f8fafc; margin: 0; padding: 20px; }}
            .navbar {{ display: flex; justify-content: space-between; align-items: center; background: #111827; padding: 15px 25px; border-radius: 10px; border: 1px solid #1e293b; margin-bottom: 25px; }}
            .navbar h2 {{ margin: 0; font-size: 20px; color: #38bdf8; display: flex; align-items: center; gap: 10px; }}
            .logout-btn {{ background: #ef4444; color: white; padding: 8px 16px; text-decoration: none; border-radius: 6px; font-size: 13px; font-weight: bold; transition: background 0.2s; }}
            .logout-btn:hover {{ background: #dc2626; }}
            .container {{ display: grid; grid-template-columns: 350px 1fr; gap: 20px; }}
            @media(max-width: 950px) {{ .container {{ grid-template-columns: 1fr; }} }}
            .box {{ background: #111827; padding: 25px; border-radius: 12px; border: 1px solid #1e293b; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }}
            .box h3 {{ margin-top: 0; font-size: 18px; color: #f8fafc; border-bottom: 1px solid #1e293b; padding-bottom: 10px; }}
            input, select {{ width: 100%; padding: 10px; margin: 6px 0 15px 0; box-sizing: border-box; background: #090d16; border: 1px solid #334155; border-radius: 6px; color: white; font-size: 14px; }}
            input:focus, select:focus {{ outline: none; border-color: #0ea5e9; }}
            button {{ background: #0ea5e9; color: white; padding: 12px; border: none; width: 100%; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; transition: background 0.2s; }}
            button:hover {{ background: #0284c7; }}
            .table-container {{ overflow-x: auto; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; min-width: 700px; }}
            th, td {{ border: 1px solid #1e293b; padding: 12px; text-align: left; font-size: 13px; }}
            th {{ background-color: #1a2234; color: #38bdf8; font-weight: 600; }}
            tr:hover {{ background: rgba(255,255,255,0.01); }}
            .side-by-side {{ display: flex; gap: 10px; }}
            .side-by-side input {{ flex: 1.3; }}
            .side-by-side select {{ flex: 1.2; background: #090d16; color: #38bdf8; font-weight: bold; }}
            .label {{ font-size: 12px; font-weight: 600; color: #94a3b8; display: block; }}
        </style>
    </head>
    <body>
        <div class="navbar">
            <h2>🛡️ ISS Enterprise Control Center</h2>
            <a href="/admin/logout" class="logout-btn">Secure Logout</a>
        </div>

        {f'<div style="background: rgba(16,185,129,0.1); border: 1px solid #10b981; color: #34d399; padding: 12px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; font-size: 14px;">{success_msg}</div>' if success_msg else ''}

        <div style="background: #111827; padding: 20px; border-radius: 12px; margin-bottom: 25px; border: 1px solid #1e293b; max-width: 450px;">
            <h4 style="margin-top: 0; color: #f8fafc; font-size: 15px;">Update Admin Credentials</h4>
            <form method="POST">
                <input type="hidden" name="action" value="change_credentials">
                <span class="label">New Admin Username</span>
                <input type="text" name="new_username" value="{ADMIN_CONFIG['username']}" required>
                <span class="label">New Admin Password</span>
                <input type="text" name="new_password" placeholder="Enter secure password" required>
                <button type="submit" style="background: #334155; padding: 8px;">Save Admin Security</button>
            </form>
        </div>

        <div class="container">
            <div class="box">
                <h3>Generate License</h3>
                <form action="/add-client" method="POST">
                    <span class="label">Client Name</span>
                    <input type="text" name="name" placeholder="e.g. John Doe" required>
                    <span class="label">Organization</span>
                    <input type="text" name="org" placeholder="e.g. Acme Corp" required>
                    <span class="label">License Key ID</span>
                    <input type="text" name="license" placeholder="e.g. iss-2026-xyz" required>
                    
                    <span class="label">Subscription Tier</span>
                    <select name="plan_choice">
                        <option value="Basic-1Month">Basic (1 Device - 1 Month)</option>
                        <option value="Basic-1Year">Basic (1 Device - 1 Year)</option>
                        <option value="Standard-1Month">Standard (3 Devices - 1 Month)</option>
                        <option value="Standard-1Year">Standard (3 Devices - 1 Year)</option>
                        <option value="Enterprise-1Month">Enterprise (5 Devices - 1 Month)</option>
                        <option value="Enterprise-1Year">Enterprise (5 Devices - 1 Year)</option>
                        <option value="Custom-Duration">Custom Duration / Tier</option>
                    </select>

                    <span class="label">Custom Date & Tier Settings</span>
                    <div class="side-by-side">
                        <input type="date" name="custom_expiry" value="{default_expiry}">
                        <select name="custom_plan_type">
                            <option value="Basic (Custom)">Basic</option>
                            <option value="Standard (Custom)">Standard</option>
                            <option value="Enterprise (Custom)">Enterprise</option>
                        </select>
                    </div>

                    <button type="submit" style="margin-top: 10px;">Issue License Key</button>
                </form>
            </div>

            <div class="box" style="display: flex; flex-direction: column;">
                <h3>Active Client Fleet & Licenses</h3>
                <div class="table-container">
                    <table>
                        <tr>
                            <th>License ID</th>
                            <th>Client</th>
                            <th>Organization</th>
                            <th>Tier</th>
                            <th>Expiry</th>
                            <th>Client Login</th>
                            <th>Devices</th>
                            <th>Connected IPs</th>
                        </tr>
                        {table_rows if table_rows else "<tr><td colspan='8' style='text-align:center; color: #94a3b8; padding: 30px;'>No active licenses found in system.</td></tr>"}
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

@app.route("/add-client", methods=["POST"])
def add_client():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    client_name = request.form.get("name")
    org_name = request.form.get("org")
    license_key = request.form.get("license")
    plan_choice = request.form.get("plan_choice")
    custom_expiry = request.form.get("custom_expiry")
    custom_plan_type = request.form.get("custom_plan_type")

    max_devices = 3
    final_plan_type = plan_choice

    if plan_choice == "Custom-Duration":
        expiry_date = custom_expiry if custom_expiry else (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        final_plan_type = custom_plan_type
        if "Basic" in custom_plan_type: max_devices = 1
        elif "Enterprise" in custom_plan_type: max_devices = 5
        else: max_devices = 3
    else:
        if "1Year" in plan_choice: expiry_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        else: expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        if "Basic" in plan_choice: max_devices = 1
        elif "Enterprise" in plan_choice: max_devices = 5

    licenses = load_licenses()
    licenses[license_key] = {
        "name": client_name,
        "org": org_name,
        "expiry": expiry_date,
        "max_devices": max_devices,
        "plan_type": final_plan_type,
        "client_user": "admin",
        "client_pwd": "admin",
        "pcs": []
    }
    save_all_licenses(licenses)

    return f"""
    <body style="font-family: 'Segoe UI'; background: #090d16; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0;">
        <div style="background: #111827; padding: 35px; border-radius: 12px; border: 1px solid #1e293b; text-align: center; max-width: 400px;">
            <h3 style="color: #34d399; margin-top: 0;">License Generated Successfully!</h3>
            <p style="color: #94a3b8; font-size: 14px;">Key: <code style="color: #38bdf8;">{license_key}</code></p>
            <p style="color: #94a3b8; font-size: 14px;">Default Client Login: <code style="color: #38bdf8;">admin / admin</code></p>
            <a href="/admin" style="display: inline-block; background: #0ea5e9; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 15px;">Return to Dashboard</a>
        </div>
    </body>
    """

# --- Client Portal Login Route ---
@app.route("/client-login", methods=["GET", "POST"])
def client_login():
    error_msg = ""
    if request.method == "POST":
        license_key = request.form.get("license_key", "").strip()
        user_input = request.form.get("client_username", "").strip()
        pwd_input = request.form.get("client_password", "").strip()
        
        licenses = load_licenses()
        if license_key in licenses:
            client_data = licenses[license_key]
            if user_input == client_data["client_user"] and pwd_input == client_data["client_pwd"]:
                session['active_license'] = license_key
                return redirect(url_for('client_dashboard'))
            else:
                error_msg = "Invalid Username or Password for this License ID!"
        else:
            error_msg = "Invalid or Unrecognized License ID!"

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Client Portal Login - ISS Security</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #090d16; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; color: #f8fafc; padding: 15px; box-sizing: border-box; }}
            .card {{ background: #111827; padding: 35px; border-radius: 12px; width: 100%; max-width: 380px; border: 1px solid #1e293b; box-shadow: 0 15px 30px rgba(0,0,0,0.5); }}
            input {{ width: 100%; padding: 12px; margin: 6px 0 15px 0; box-sizing: border-box; background: #090d16; border: 1px solid #334155; border-radius: 6px; color: white; font-size: 14px; }}
            input:focus {{ outline: none; border-color: #0ea5e9; }}
            button {{ background: #0ea5e9; color: white; border: none; padding: 12px; width: 100%; border-radius: 6px; font-weight: bold; cursor: pointer; transition: background 0.2s; }}
            button:hover {{ background: #0284c7; }}
            .label {{ font-size: 12px; font-weight: 600; color: #94a3b8; display: block; text-align: left; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2 style="margin-top: 0; color: #f8fafc; font-size: 22px;">Client Portal Access</h2>
            <p style="font-size: 13px; color: #94a3b8; margin-bottom: 20px;">Provide your License ID and client credentials.</p>
            {f'<div style="background: rgba(239,68,68,0.1); border: 1px solid #ef4444; color: #fca5a5; padding: 10px; border-radius: 6px; font-size: 13px; margin-bottom: 15px;">{error_msg}</div>' if error_msg else ''}
            <form method="POST" style="text-align: left;">
                <span class="label">License Key ID</span>
                <input type="text" name="license_key" placeholder="Enter License ID" required>
                <span class="label">Username (Default: admin)</span>
                <input type="text" name="client_username" value="admin" required>
                <span class="label">Password (Default: admin)</span>
                <input type="password" name="client_password" value="admin" required>
                <button type="submit">Access Security Portal</button>
            </form>
        </div>
    </body>
    </html>
    """)

@app.route("/client-logout")
def client_logout():
    session.pop('active_license', None)
    return redirect(url_for('client_login'))

# --- Professional Client Dashboard ---
@app.route("/client-dashboard", methods=["GET", "POST"])
def client_dashboard():
    license_key = session.get('active_license')
    licenses = load_licenses()

    if not license_key or license_key not in licenses:
        return redirect(url_for('client_login'))

    v = licenses[license_key]
    client_ip = request.remote_addr
    setup_message = ""
    success_msg = ""

    if request.method == "POST":
        action = request.form.get("action")
        if action == "update_my_credentials":
            new_u = request.form.get("new_username")
            new_p = request.form.get("new_password")
            if new_u and new_p:
                v["client_user"] = new_u
                v["client_pwd"] = new_p
                save_all_licenses(licenses)
                success_msg = "✅ Portal credentials successfully updated and secured!"
        else:
            if client_ip not in v['pcs']:
                if len(v['pcs']) >= v['max_devices']:
                    setup_message = "❌ Device limit reached! Max slots occupied."
                else:
                    v['pcs'].append(client_ip)
                    save_all_licenses(licenses)
                    setup_message = "✅ Endpoint successfully linked and protected!"
            else:
                setup_message = "ℹ️ This device is already linked and verified."

    connected_devices = ", ".join(v['pcs']) if v['pcs'] else "No active devices connected"
    is_setup_done = client_ip in v['pcs']

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ISS Client Security Dashboard</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #090d16; color: #f8fafc; margin: 0; padding: 20px; }}
            .navbar {{ display: flex; justify-content: space-between; align-items: center; background: #111827; padding: 15px 25px; border-radius: 10px; border: 1px solid #1e293b; margin-bottom: 25px; max-width: 650px; margin-left: auto; margin-right: auto; }}
            .navbar h2 {{ margin: 0; font-size: 18px; color: #38bdf8; }}
            .card {{ background: #111827; max-width: 650px; margin: 0 auto; padding: 30px; border-radius: 12px; border: 1px solid #1e293b; box-shadow: 0 10px 25px rgba(0,0,0,0.4); box-sizing: border-box; }}
            .info-group {{ margin: 18px 0; padding-bottom: 12px; border-bottom: 1px solid #1e293b; }}
            .label {{ font-weight: 600; color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
            .value {{ font-size: 15px; color: #f8fafc; margin-top: 4px; word-break: break-all; }}
            .setup-btn {{ background: #10b981; color: white; border: none; padding: 14px 20px; font-size: 15px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 15px; transition: background 0.2s; }}
            .setup-btn:hover {{ background: #059669; }}
            .logout {{ color: #ef4444; text-decoration: none; font-size: 13px; font-weight: bold; }}
            .logout:hover {{ text-decoration: underline; }}
            input {{ width: 100%; padding: 10px; margin: 6px 0 12px 0; box-sizing: border-box; background: #090d16; border: 1px solid #334155; border-radius: 6px; color: white; font-size: 14px; }}
            input:focus {{ outline: none; border-color: #0ea5e9; }}
        </style>
    </head>
    <body>
        <div class="navbar">
            <h2>🛡️ Client Security Control</h2>
            <a href="/client-logout" class="logout">Logout Portal</a>
        </div>

        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <span style="background: {'rgba(16,185,129,0.1); border: 1px solid #10b981; color: #34d399;' if is_setup_done else 'rgba(234,179,8,0.1); border: 1px solid #eab308; color: #facc15;'}; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: bold;">
                    ● Status: {'Endpoint Fully Protected' if is_setup_done else 'Setup Pending'}
                </span>
            </div>

            {f'<div style="background: rgba(16,185,129,0.1); border: 1px solid #10b981; color: #34d399; padding: 12px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; font-size: 13px;">{success_msg}</div>' if success_msg else ''}
            {f'<div style="background: rgba(30,41,59,0.8); border: 1px solid #334155; padding: 12px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; font-size: 13px; color: #38bdf8;">{setup_message}</div>' if setup_message else ''}

            <!-- Change Credentials Box -->
            <div style="background: #090d16; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #1e293b;">
                <h4 style="margin-top: 0; color: #f8fafc; font-size: 15px; border-bottom: 1px solid #1e293b; padding-bottom: 8px;">Modify Security Credentials</h4>
                <form method="POST">
                    <input type="hidden" name="action" value="update_my_credentials">
                    <span class="label">New Username</span>
                    <input type="text" name="new_username" value="{v['client_user']}" required>
                    <span class="label">New Password</span>
                    <input type="text" name="new_password" value="{v['client_pwd']}" required>
                    <button type="submit" style="background: #0284c7; padding: 9px; font-size: 13px;">Update Portal Credentials</button>
                </form>
            </div>

            <div class="info-group">
                <div class="label">Active License & Client Info</div>
                <div class="value"><code style="color: #38bdf8; font-weight: bold;">{license_key}</code> — {v['org']} ({v['name']})</div>
            </div>

            <div class="info-group">
                <div class="label">Subscription Plan Tier</div>
                <div class="value"><b>{v['plan_type']}</b></div>
            </div>

            <div class="info-group">
                <div class="label">Subscription Expiry Date</div>
                <div class="value">{v['expiry']}</div>
            </div>

            <div class="info-group">
                <div class="label">Device Slots (Active / Max Allowed)</div>
                <div class="value">{len(v['pcs'])} / {v['max_devices']} Device(s) [<code style="color: #94a3b8;">{connected_devices}</code>]</div>
            </div>

            {'<div style="background: rgba(16,185,129,0.08); border: 1px solid #10b981; padding: 15px; border-radius: 8px; margin-top: 20px; font-size: 14px; color: #34d399;"><b>Protected:</b> Your current endpoint is linked and authenticated with this license key.</div>' if is_setup_done else '''
            <form method="POST">
                <p style="font-size: 13px; color: #94a3b8; margin-bottom: 10px;">Link this current device to your active subscription instantly with one click.</p>
                <button type="submit" class="setup-btn">🚀 Initialize Endpoint Setup Now</button>
            </form>
            '''}
        </div>
    </body>
    </html>
    """)

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
    if datetime.now().date() > datetime.strptime(client_info["expiry"], "%Y-%m-%d").date():
        return jsonify({"status": "expired", "message": "Subscription Expired!"}), 403

    if client_pc_id not in client_info["pcs"]:
        if len(client_info["pcs"]) >= client_info["max_devices"]:
            return jsonify({"status": "error", "message": "Device Limit Reached!"}), 403
        client_info["pcs"].append(client_pc_id)
        save_all_licenses(licenses)

    if file_hash in KNOWN_THREATS:
        return jsonify({"status": "danger", "is_threat": True, "message": "Threat found in " + filename})

    return jsonify({"status": "clean", "is_threat": False, "message": filename + " is safe."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
