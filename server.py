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
                # ফরম্যাট: License, Name, Org, Expiry, MaxDevices, PlanType, ClientUser, ClientPwd, [pcs...]
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
                elif len(parts) >= 6: # পুরানো ফাইল থাকলে ডিফল্ট admin/admin বসিয়ে ব্যাকওয়ার্ড কম্প্যাটিবিলিটি ঠিক রাখা
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

@app.route("/", methods=["GET"])
def home():
    return """
    <h2>ISS Cloud Security Enterprise Backend is Active!</h2>
    <p>Client Portal: <a href='/client-login'>/client-login</a></p>
    <p>Admin Login: <a href='/admin/login'>/admin/login</a></p>
    """

# --- 1. Admin Login Route ---
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
    <html>
    <head>
        <title>Admin Login - ISS Antivirus</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; background: #0f172a; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .card {{ background: white; padding: 30px; border-radius: 8px; width: 100%; max-width: 350px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }}
            input {{ width: 100%; padding: 12px; margin: 8px 0 15px 0; box-sizing: border-box; border: 1px solid #cbd5e1; border-radius: 4px; }}
            button {{ background: #2563eb; color: white; border: none; padding: 12px; width: 100%; border-radius: 4px; font-weight: bold; cursor: pointer; }}
            button:hover {{ background: #1d4ed8; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h3 style="margin-top: 0; color: #0f172a;">Admin Login</h3>
            {f'<p style="color: red; font-size: 13px;">{error_msg}</p>' if error_msg else ''}
            <form method="POST">
                <label style="font-size: 13px; font-weight: bold; color: #64748b;">Username</label>
                <input type="text" name="username" value="admin" required>
                <label style="font-size: 13px; font-weight: bold; color: #64748b;">Password</label>
                <input type="password" name="password" value="admin" required>
                <button type="submit">Login to Dashboard</button>
            </form>
        </div>
    </body>
    </html>
    """)

@app.route("/admin/logout")
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))

# --- 2. Admin Dashboard ---
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
                success_msg = "✅ Admin credentials updated successfully!"

    licenses = load_licenses()
    table_rows = ""
    for k, v in licenses.items():
        connected_list = ", ".join(v['pcs']) if v['pcs'] else "No devices connected yet"
        table_rows += f"""
        <tr>
            <td><b>{k}</b></td>
            <td>{v['name']}</td>
            <td>{v['org']}</td>
            <td>{v['plan_type']}</td>
            <td>{v['expiry']}</td>
            <td><code>{v['client_user']} / {v['client_pwd']}</code></td>
            <td><b>{len(v['pcs'])} / {v['max_devices']}</b></td>
            <td><code>{connected_list}</code></td>
        </tr>
        """

    default_expiry = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    html_page = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ISS Admin Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f4f9; padding: 15px; margin: 0; }}
            .container {{ display: flex; gap: 20px; flex-wrap: wrap; }}
            .box {{ background: white; padding: 20px; border-radius: 8px; width: 100%; max-width: 430px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); box-sizing: border-box; margin-bottom: 20px; }}
            .table-box {{ background: white; padding: 20px; border-radius: 8px; flex-grow: 1; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); overflow-x: auto; box-sizing: border-box; }}
            input, select {{ width: 100%; padding: 10px; margin: 6px 0 12px 0; box-sizing: border-box; border: 1px solid #cbd5e1; border-radius: 4px; }}
            button {{ background: #2563eb; color: white; padding: 12px; border: none; width: 100%; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 15px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; min-width: 600px; }}
            th, td {{ border: 1px solid #e2e8f0; padding: 10px; text-align: left; font-size: 13px; }}
            th {{ background-color: #0f172a; color: white; }}
            .side-by-side {{ display: flex; gap: 10px; align-items: center; margin-top: 5px; }}
            .side-by-side input[type="date"] {{ flex: 1.3; margin-bottom: 0; }}
            .side-by-side select {{ flex: 1.2; margin-bottom: 0; background: #f8fafc; font-weight: bold; color: #0284c7; }}
            .logout-btn {{ background: #dc2626; padding: 8px 15px; width: auto; float: right; text-decoration: none; color: white; border-radius: 4px; font-size: 13px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div style="overflow: hidden; margin-bottom: 15px;">
            <h2 style="margin: 0; float: left;">ISS Cloud Security - Admin Dashboard</h2>
            <a href="/admin/logout" class="logout-btn">Logout</a>
        </div>

        {f'<div style="background: #dcfce7; color: #166534; padding: 12px; border-radius: 6px; margin-bottom: 15px; font-weight: bold;">{success_msg}</div>' if success_msg else ''}

        <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0px 0px 5px rgba(0,0,0,0.05); max-width: 430px;">
            <h4 style="margin-top: 0; color: #334155;">Change Admin Username & Password</h4>
            <form method="POST">
                <input type="hidden" name="action" value="change_credentials">
                <input type="text" name="new_username" value="{ADMIN_CONFIG['username']}" placeholder="New Username" required>
                <input type="text" name="new_password" placeholder="New Password" required>
                <button type="submit" style="background: #0284c7; padding: 8px;">Update Admin Credentials</button>
            </form>
        </div>

        <div class="container">
            <div class="box">
                <h3>Create License ID</h3>
                <form action="/add-client" method="POST">
                    <label>Client Name:</label>
                    <input type="text" name="name" required>
                    <label>Organization:</label>
                    <input type="text" name="org" required>
                    <label>License ID:</label>
                    <input type="text" name="license" placeholder="e.g. iss-1111-2026" required>
                    
                    <label>Standard Plans (1 Month / 1 Year):</label>
                    <select name="plan_choice">
                        <option value="Basic-1Month">Basic Plan (1 Device - 1 Month)</option>
                        <option value="Basic-1Year">Basic Plan (1 Device - 1 Year)</option>
                        <option value="Standard-1Month">Standard Plan (3 Devices - 1 Month)</option>
                        <option value="Standard-1Year">Standard Plan (3 Devices - 1 Year)</option>
                        <option value="Enterprise-1Month">Enterprise Plan (5 Devices - 1 Month)</option>
                        <option value="Enterprise-1Year">Enterprise Plan (5 Devices - 1 Year)</option>
                        <option value="Custom-Duration">Custom Duration (Use Calendar & Plan Selector Below)</option>
                    </select>

                    <label>Custom Expiry Date & Plan Selector:</label>
                    <div class="side-by-side">
                        <input type="date" name="custom_expiry" value="{default_expiry}">
                        <select name="custom_plan_type">
                            <option value="Basic (Custom/Trial)">Basic</option>
                            <option value="Standard (Custom/Trial)">Standard</option>
                            <option value="Enterprise (Custom/Trial)">Enterprise</option>
                        </select>
                    </div>

                    <button type="submit">Create License ID (Default Client Login: admin / admin)</button>
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
                        <th>Client Credentials</th>
                        <th>Devices</th>
                        <th>Connected Devices</th>
                    </tr>
                    {table_rows if table_rows else "<tr><td colspan='8' style='text-align:center;'>No licenses found</td></tr>"}
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_page)

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
        if "Basic" in custom_plan_type:
            max_devices = 1
        elif "Enterprise" in custom_plan_type:
            max_devices = 5
        else:
            max_devices = 3
    else:
        if "1Year" in plan_choice:
            expiry_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        else:
            expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        if "Basic" in plan_choice:
            max_devices = 1
        elif "Enterprise" in plan_choice:
            max_devices = 5

    licenses = load_licenses()
    licenses[license_key] = {
        "name": client_name,
        "org": org_name,
        "expiry": expiry_date,
        "max_devices": max_devices,
        "plan_type": final_plan_type,
        "client_user": "admin",  # ডিফল্ট ক্লায়েন্ট ইউজারনেম admin
        "client_pwd": "admin",   # ডিফল্ট ক্লায়েন্ট পাসওয়ার্ড admin
        "pcs": []
    }
    save_all_licenses(licenses)

    return f"""
    <body style="font-family: Arial; padding: 30px; text-align: center;">
        <h3>Success! License ID <b>{license_key}</b> created successfully.</h3>
        <p>Default Client Credentials: <b>admin</b> / <b>admin</b></p>
        <a href="/admin" style="background: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 15px;">Back to Dashboard</a>
    </body>
    """

# --- 3. Client Portal Login Route ---
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
            # প্রতি লাইসেন্সের নিজস্ব ইউজারনেম ও পাসওয়ার্ড চেক করা হবে
            if user_input == client_data["client_user"] and pwd_input == client_data["client_pwd"]:
                session['active_license'] = license_key
                return redirect(url_for('client_dashboard'))
            else:
                error_msg = "Invalid Username or Password for this License ID!"
        else:
            error_msg = "Invalid License ID!"

    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Client Portal Login</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f1f5f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; padding: 15px; box-sizing: border-box; }}
            .login-card {{ background: white; padding: 25px; border-radius: 8px; width: 100%; max-width: 350px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            input {{ width: 100%; padding: 12px; margin: 6px 0 12px 0; box-sizing: border-box; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 15px; }}
            button {{ background: #0ea5e9; color: white; border: none; padding: 12px; width: 100%; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 15px; }}
            .label {{ font-size: 13px; font-weight: bold; color: #64748b; text-align: left; display: block; }}
        </style>
    </head>
    <body>
        <div class="login-card">
            <h3 style="margin-top: 0; color: #0f172a;">Client Portal Login</h3>
            <p style="font-size: 13px; color: #64748b;">Enter License ID & Credentials (Default: admin/admin)</p>
            {f'<p style="color: red; font-size: 13px;">{error_msg}</p>' if error_msg else ''}
            <form method="POST" style="text-align: left;">
                <span class="label">License ID</span>
                <input type="text" name="license_key" placeholder="Enter License ID" required>
                <span class="label">Username</span>
                <input type="text" name="client_username" value="admin" required>
                <span class="label">Password</span>
                <input type="password" name="client_password" value="admin" required>
                <button type="submit">Login to Portal</button>
            </form>
        </div>
    </body>
    </html>
    """)

@app.route("/client-logout")
def client_logout():
    session.pop('active_license', None)
    return redirect(url_for('client_login'))

# --- 4. Client Dashboard ---
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
        
        # নির্দিষ্ট ক্লায়েন্টের ইউজারনেম ও পাসওয়ার্ড পরিবর্তনের লজিক
        if action == "update_my_credentials":
            new_u = request.form.get("new_username")
            new_p = request.form.get("new_password")
            if new_u and new_p:
                v["client_user"] = new_u
                v["client_pwd"] = new_p
                save_all_licenses(licenses)
                success_msg = "✅ Your portal username and password updated successfully!"
        else:
            # ডিভাইস সেটআপ বা লিংক করার লজিক
            if client_ip not in v['pcs']:
                if len(v['pcs']) >= v['max_devices']:
                    setup_message = "❌ Device limit reached! Cannot setup more devices."
                else:
                    v['pcs'].append(client_ip)
                    save_all_licenses(licenses)
                    setup_message = "✅ Setup Successful! Your device is now linked and fully protected."
            else:
                setup_message = "ℹ️ This device is already set up and linked!"

    connected_devices = ", ".join(v['pcs']) if v['pcs'] else "Not setup yet"
    is_setup_done = client_ip in v['pcs']

    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ISS Client Security Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f8fafc; padding: 15px; margin: 0; color: #1e293b; box-sizing: border-box; }}
            .card {{ background: white; max-width: 600px; margin: 20px auto; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); box-sizing: border-box; }}
            h2 {{ color: #0f172a; margin-top: 0; font-size: 22px; }}
            .info-group {{ margin: 15px 0; padding-bottom: 10px; border-bottom: 1px solid #e2e8f0; }}
            .label {{ font-weight: bold; color: #64748b; font-size: 13px; }}
            .value {{ font-size: 15px; color: #0f172a; margin-top: 3px; word-break: break-all; }}
            .setup-btn {{ background: #16a34a; color: white; border: none; padding: 14px 20px; font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer; width: 100%; margin-top: 15px; }}
            .logout {{ display: inline-block; color: #dc2626; text-decoration: none; font-size: 14px; font-weight: bold; }}
            input {{ width: 100%; padding: 8px; margin: 6px 0 10px 0; box-sizing: border-box; border: 1px solid #cbd5e1; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div style="overflow: hidden;">
                <h2 style="margin: 0; float: left;">Client Security Dashboard</h2>
                <a href="/client-logout" class="logout" style="float: right;">Logout</a>
            </div>
            
            <p style="color: {'#16a34a' if is_setup_done else '#ca8a04'}; font-weight: bold; font-size: 14px; margin-top: 15px;">
                ● Status: {'Fully Protected & Configured' if is_setup_done else 'Pending One-Click Setup'}
            </p>

            {f'<div style="background: #dcfce7; color: #166534; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-weight: bold; font-size: 13px;">{success_msg}</div>' if success_msg else ''}
            {f'<div style="background: #e2e8f0; padding: 12px; border-radius: 5px; margin-bottom: 15px; font-weight: bold; font-size: 14px;">{setup_message}</div>' if setup_message else ''}

            <!-- Change Credentials Box for this Specific Client -->
            <div style="background: #f1f5f9; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #e2e8f0;">
                <h4 style="margin-top: 0; color: #334155; font-size: 14px;">Update Your Login Credentials</h4>
                <form method="POST">
                    <input type="hidden" name="action" value="update_my_credentials">
                    <span style="font-size: 12px; font-weight: bold; color: #64748b;">New Username</span>
                    <input type="text" name="new_username" value="{v['client_user']}" required>
                    <span style="font-size: 12px; font-weight: bold; color: #64748b;">New Password</span>
                    <input type="text" name="new_password" value="{v['client_pwd']}" required>
                    <button type="submit" style="background: #0284c7; color: white; padding: 8px; border: none; width: 100%; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 13px;">Save New Credentials</button>
                </form>
            </div>

            <div class="info-group">
                <div class="label">License ID & Client Info</div>
                <div class="value"><b>{license_key}</b> - {v['org']} ({v['name']})</div>
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
                <div class="label">Device Usage (Connected / Max Limit)</div>
                <div class="value">{len(v['pcs'])} / {v['max_devices']} Device(s) [<code>{connected_devices}</code>]</div>
            </div>

            {'<div style="background: #f0fdf4; padding: 15px; border-radius: 6px; border: 1px solid #bbf7d0; margin-top: 15px; font-size: 14px;"><b>Great!</b> Your device is already set up and linked with this license.</div>' if is_setup_done else '''
            <form method="POST">
                <p style="font-size: 14px; color: #475569;">Click the button below to configure your device. Setup will be completed instantly!</p>
                <button type="submit" class="setup-btn">🚀 Click Here to Setup Now (Instant)</button>
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
