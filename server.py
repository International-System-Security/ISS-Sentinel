from flask import Flask, render_template_string, request, redirect, url_for, session
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import random
import requests
import threading
import time

app = Flask(__name__)
app.secret_key = "iss_enterprise_security_secret_key_v17"

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

USER_FILE = "users.txt"
POST_FILE = "posts.txt"
INQUIRY_FILE = "inquiries.txt"
TICKET_FILE = "tickets.txt"
LICENSE_FILE = "licenses.txt"

OWNER_EMAIL = "admin@iss.com"
OWNER_USERNAME = "ibr@him"
OWNER_PASSWORD = "muhib###5869@"

# --- RESEND.COM AUTOMATED EMAIL FUNCTION ---
def send_automated_alert(recipient_email, subject, html_content):
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        print("API Key not found in environment variables!")
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
        print(f"Error sending email: {e}")
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
                            <li><b>Endpoint Status:</b> All protected nodes are secure. No active threats.</li>
                        </ul>
                        <p>Access your portal here: <a href="https://iss-antivirus-cloud.onrender.com/client-login" style="color:#38bdf8;">Client Portal Login</a></p>
                        <br><p>Best regards,<br><b>ISS Enterprise Security Team</b></p>
                    </div>
                    """
                    send_automated_alert(client_email, sub, body)
        except Exception as e:
            print(f"Weekly Reporter Error: {e}")

threading.Thread(target=background_weekly_reporter, daemon=True).start()

def load_users():
    users = {OWNER_USERNAME: {"email": OWNER_EMAIL, "password": OWNER_PASSWORD, "role": "Admin", "pic": "https://i.imgur.com/6VBx3io.png", "verified": True, "trusted": False}}
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|||")
                if len(parts) >= 6:
                    uname, email, pwd, role, pic, verified = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip(), parts[4].strip(), parts[5].strip() == "True"
                    users[uname] = {"email": email, "password": pwd, "role": role, "pic": pic, "verified": verified, "trusted": False}
    return users

def save_all_users(users_dict):
    with open(USER_FILE, "w") as f:
        for uname, data in users_dict.items():
            if uname == OWNER_USERNAME: continue
            f.write(f"{uname}|||{data['email']}|||{data['password']}|||{data['role']}|||{data['pic']}|||{data['verified']}|||{data.get('trusted', False)}\n")

def load_posts():
    posts = []
    if os.path.exists(POST_FILE):
        with open(POST_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|||")
                if len(parts) >= 5:
                    posts.append({"id": parts[0], "author": parts[1], "content": parts[2], "img": parts[3], "date": parts[4]})
    return posts

def save_post(author, content, img):
    posts = load_posts()
    p_id = f"POST-{int(datetime.now().timestamp())}"
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    posts.insert(0, {"id": p_id, "author": author, "content": content, "img": img if img else "", "date": date_str})
    with open(POST_FILE, "w") as f:
        for p in posts:
            f.write(f"{p['id']}|||{p['author']}|||{p['content']}|||{p['img']}|||{p['date']}\n")

def load_tickets():
    tickets = {}
    if os.path.exists(TICKET_FILE):
        with open(TICKET_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|||")
                if len(parts) >= 3:
                    t_id, user, msgs = parts[0], parts[1], parts[2:]
                    tickets[t_id] = {"user": user, "messages": msgs}
    return tickets

def save_ticket_msg(t_id, user, sender, text):
    tickets = load_tickets()
    if t_id not in tickets:
        tickets[t_id] = {"user": user, "messages": []}
    timestamp = datetime.now().strftime("%H:%M %d/%m")
    msg_str = f"{sender} ({timestamp}): {text}"
    tickets[t_id]["messages"].append(msg_str)
    with open(TICKET_FILE, "w") as f:
        for tid, data in tickets.items():
            msgs_joined = "|||".join(data["messages"])
            f.write(f"{tid}|||{data['user']}|||{msgs_joined}\n")

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
                elif len(parts) >= 6:
                    licenses[parts[0].strip()] = {
                        "name": parts[1].strip(), "org": parts[2].strip(), "expiry": parts[3].strip(),
                        "max": parts[4].strip(), "plan": parts[5].strip(),
                        "client_user": "admin", "client_pwd": "admin",
                        "client_email": "client@iss.com"
                    }
    return licenses

def save_licenses(lic_dict):
    with open(LICENSE_FILE, "w") as f:
        for k, v in lic_dict.items():
            c_email = v.get('client_email', 'client@iss.com')
            f.write(f"{k},{v['name']},{v['org']},{v['expiry']},{v['max']},{v['plan']},{v['client_user']},{v['client_pwd']},{c_email}\n")

# --- 1. HOME PANEL ---
@app.route("/", methods=["GET", "POST"])
def home():
    users = load_users()
    posts = load_posts()
    inquiry_msg = ""
    if request.method == "POST":
        form_type = request.form.get("form_type")
        if form_type == "inquiry":
            name, email, social = request.form.get("name"), request.form.get("email"), request.form.get("social")
            if name and email:
                with open(INQUIRY_FILE, "a") as f:
                    f.write(f"{name}|{email}|{social}|{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                inquiry_msg = "✅ Your service application has been submitted successfully!"
    current_user = session.get("username")
    is_admin = current_user == OWNER_USERNAME or (current_user in users and users[current_user]['role'] == 'Admin')
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>ISS Platform</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:#f8fafc; margin:0; padding:20px;">
        <div style="text-align:center; padding:30px;">
            <h1>🛡️ ISS Cloud Security Platform</h1>
            <p style="color:#94a3b8;">Welcome to the Next-Gen Security Platform</p>
            {% if current_user %}
                <p style="color:#34d399; font-weight:bold;">Logged in as: {{ current_user }}</p>
                <a href="/my-profile" style="color:#38bdf8; margin-right:15px;">My Profile</a>
                {% if is_admin %}<a href="/admin" style="color:#38bdf8; margin-right:15px; font-weight:bold;">Admin Panel</a>{% endif %}
                <a href="/client-login" style="color:#38bdf8; margin-right:15px;">Client Portal</a>
                <a href="/logout" style="color:#ef4444;">Logout</a>
            {% else %}
                <a href="/my-profile" style="background:#0ea5e9; color:white; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:bold;">Login / Register</a>
                <a href="/client-login" style="background:#1e293b; color:white; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:bold; margin-left:10px;">Client Portal</a>
            {% endif %}
        </div>
    </body>
    </html>
    """, current_user=current_user, is_admin=is_admin)

# --- MY PROFILE ---
@app.route("/my-profile", methods=["GET", "POST"])
def my_profile():
    users = load_users()
    error, msg = "", ""
    if request.method == "POST":
        action = request.form.get("action")
        if action == "register":
            uname, email, pwd = request.form.get("username").strip(), request.form.get("email").strip(), request.form.get("password").strip()
            if uname in users or uname == OWNER_USERNAME:
                error = "Username already exists!"
            else:
                users[uname] = {"email": email, "password": pwd, "role": "User", "pic": "https://i.imgur.com/6VBx3io.png", "verified": False}
                save_all_users(users)
                session["username"] = uname
                return redirect(url_for("my_profile"))
        elif action == "login":
            email, uname, pwd = request.form.get("email").strip(), request.form.get("username").strip(), request.form.get("password").strip()
            if uname == OWNER_USERNAME and email == OWNER_EMAIL and pwd == OWNER_PASSWORD:
                session["username"] = OWNER_USERNAME
                return redirect(url_for("admin_panel"))
            elif uname in users and users[uname]["password"] == pwd and users[uname]["email"] == email:
                session["username"] = uname
                return redirect(url_for("admin_panel") if users[uname]["role"] == "Admin" else url_for("my_profile"))
            else:
                error = "Invalid credentials!"

    current_user = session.get("username")
    user_data = users.get(current_user) if current_user and current_user != OWNER_USERNAME else ({"email": OWNER_EMAIL, "role": "Admin"} if current_user == OWNER_USERNAME else None)
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>My Profile</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; padding:40px;">
        <div style="max-width:400px; margin:0 auto; background:#111827; padding:30px; border-radius:12px; border:1px solid #1e293b;">
            <a href="/" style="color:#38bdf8; text-decoration:none;">&larr; Home</a>
            {% if error %}<div style="color:#fca5a5; font-size:13px; margin:10px 0;">{{ error }}</div>{% endif %}
            {% if current_user and user_data %}
                <h2>Profile: {{ current_user }}</h2>
                <p>Email: {{ user_data.email }} | Role: <b>{{ user_data.role }}</b></p>
                {% if user_data.role == 'Admin' %}<a href="/admin" style="color:#38bdf8; display:block; margin:15px 0;">Go to Admin Panel &rarr;</a>{% endif %}
                <a href="/logout" style="color:#ef4444;">Log Out</a>
            {% else %}
                <h3>Login / Register</h3>
                <form method="POST">
                    <input type="hidden" name="action" value="login">
                    <input type="email" name="email" placeholder="Email" required style="width:100%; padding:10px; margin:8px 0; background:#060913; border:1px solid #334155; color:white; box-sizing:border-box;">
                    <input type="text" name="username" placeholder="Username" required style="width:100%; padding:10px; margin:8px 0; background:#060913; border:1px solid #334155; color:white; box-sizing:border-box;">
                    <input type="password" name="password" placeholder="Password" required style="width:100%; padding:10px; margin:8px 0; background:#060913; border:1px solid #334155; color:white; box-sizing:border-box;">
                    <button type="submit" style="width:100%; padding:10px; background:#0ea5e9; border:none; color:white; font-weight:bold; cursor:pointer; margin-top:10px;">Login</button>
                </form>
                <hr style="border-color:#1e293b; margin:20px 0;">
                <form method="POST">
                    <input type="hidden" name="action" value="register">
                    <input type="text" name="username" placeholder="New Username" required style="width:100%; padding:10px; margin:8px 0; background:#060913; border:1px solid #334155; color:white; box-sizing:border-box;">
                    <input type="email" name="email" placeholder="New Email" required style="width:100%; padding:10px; margin:8px 0; background:#060913; border:1px solid #334155; color:white; box-sizing:border-box;">
                    <input type="password" name="password" placeholder="New Password" required style="width:100%; padding:10px; margin:8px 0; background:#060913; border:1px solid #334155; color:white; box-sizing:border-box;">
                    <button type="submit" style="width:100%; padding:10px; background:#10b981; border:none; color:white; font-weight:bold; cursor:pointer; margin-top:10px;">Register</button>
                </form>
            {% endif %}
        </div>
    </body>
    </html>
    """, error=error, current_user=current_user, user_data=user_data)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

# --- 2. ADMIN PANEL ---
@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    current_user = session.get("username")
    users = load_users()
    is_admin = current_user == OWNER_USERNAME or (current_user in users and users[current_user]['role'] == 'Admin')
    if not is_admin:
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
            l_email = request.form.get("l_email").strip()
            l_plan = request.form.get("l_plan")
            l_expiry = request.form.get("l_expiry").strip()
            l_user = request.form.get("l_user").strip()
            l_pwd = request.form.get("l_pwd").strip()

            licenses = load_licenses()
            licenses[l_key] = {
                "name": l_name, "org": l_org, "expiry": l_expiry,
                "max": "5", "plan": l_plan, "client_user": l_user, "client_pwd": l_pwd,
                "client_email": l_email
            }
            save_licenses(licenses)
            
            # --- ইমেল পাঠানো ---
            if l_email:
                sub = f"Your ISS Security License & Subscription Details ({l_plan})"
                html_body = f"""
                <div style="font-family:'Segoe UI',sans-serif; background:#0b1120; color:#f8fafc; padding:25px; border-radius:12px; border:1px solid #1e293b;">
                    <h2 style="color:#0ea5e9; margin-top:0;">🛡️ Welcome to International System Security (ISS)</h2>
                    <p>Dear <b>{l_name}</b>,</p>
                    <p>Your security license has been successfully created and activated for organization: <b>{l_org}</b>.</p>
                    
                    <div style="background:#111827; padding:15px; border-radius:8px; border:1px solid #334155; margin:15px 0;">
                        <h4 style="color:#38bdf8; margin:0 0 10px 0;">📋 Subscription & License Credentials</h4>
                        <p style="margin:5px 0;"><b>Subscription Plan:</b> <span style="color:#34d399;">{l_plan}</span></p>
                        <p style="margin:5px 0;"><b>License Key:</b> <code style="background:#060913; padding:3px 6px; color:#38bdf8; border-radius:4px;">{l_key}</code></p>
                        <p style="margin:5px 0;"><b>Portal Username:</b> {l_user}</p>
                        <p style="margin:5px 0;"><b>Portal Password:</b> {l_pwd}</p>
                        <p style="margin:5px 0;"><b>Expiry Date:</b> {l_expiry}</p>
                    </div>

                    <div style="margin:20px 0;">
                        <p><b>Client Portal Login Link:</b><br>
                        <a href="https://iss-antivirus-cloud.onrender.com/client-login" style="background:#0ea5e9; color:white; padding:10px 18px; text-decoration:none; border-radius:6px; display:inline-block; font-weight:bold; margin-top:5px;">Access Client Portal</a></p>
                    </div>

                    <p style="color:#94a3b8; font-size:12px; margin-top:20px;">Note: You will receive weekly security audit reports automatically on this email address.</p>
                    <hr style="border-color:#1e293b; margin:20px 0;">
                    <p style="color:#94a3b8; font-size:12px;">Best regards,<br><b>ISS Enterprise Security Team</b></p>
                </div>
                """
                send_automated_alert(l_email, sub, html_body)

            msg = f"✅ License '{l_key}' created and credentials sent to {l_email}!"

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
                <h3 style="color:#38bdf8; margin-top:0;">🔑 Create New License & Auto-Email Details</h3>
                <form method="POST">
                    <input type="hidden" name="action" value="add_license">
                    
                    <div style="margin-bottom:15px; background:#0b1120; padding:15px; border:2px solid #f59e0b; border-radius:8px;">
                        <label style="display:block; color:#f59e0b; font-weight:bold; margin-bottom:5px;">📧 CLIENT EMAIL (Mandatory for sending credentials & reports)</label>
                        <input type="email" name="l_email" placeholder="client@gmail.com" required style="width:100%; padding:12px; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                    </div>

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

                    <button type="submit" style="width:100%; padding:14px; background:#10b981; border:none; color:white; font-weight:bold; border-radius:6px; cursor:pointer; font-size:15px;">🚀 Create License & Send Email Automatically</button>
                </form>
            </div>

            <div style="background:#111827; padding:25px; border-radius:12px; border:1px solid #1e293b;">
                <h3>Active Licenses</h3>
                <table style="width:100%; border-collapse:collapse; margin-top:10px;">
                    <tr><th style="border:1px solid #1e293b; padding:10px; background:#1a2234; text-align:left;">Key</th><th style="border:1px solid #1e293b; padding:10px; background:#1a2234; text-align:left;">Client Email</th><th style="border:1px solid #1e293b; padding:10px; background:#1a2234; text-align:left;">Plan</th><th style="border:1px solid #1e293b; padding:10px; background:#1a2234; text-align:left;">Action</th></tr>
                    {% for k, v in licenses.items() %}
                    <tr>
                        <td style="border:1px solid #1e293b; padding:10px;"><code>{{ k }}</code></td>
                        <td style="border:1px solid #1e293b; padding:10px; color:#38bdf8; font-weight:bold;">{{ v.get('client_email', 'N/A') }}</td>
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

# --- 3. CLIENT PANEL ---
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
            error_msg = "Invalid or Blocked License ID!"

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Client Portal Login</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <div style="background:#111827; padding:35px; border-radius:12px; width:360px; border:1px solid #1e293b;">
            <h2>Client Portal Login</h2>
            {% if error_msg %}<div style="color:#fca5a5; font-size:13px; margin-bottom:10px;">{{ error_msg }}</div>{% endif %}
            <form method="POST">
                <label style="font-size:12px; color:#94a3b8;">License ID</label>
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
        if action == "activate_antivirus":
            session[f"av_active_{lic_key}"] = True
            msg_status = "🛡️ Antivirus successfully activated!"
            antivirus_active = True
        elif action == "run_test_virus":
            if antivirus_active:
                is_success = random.choice([True, True, False])
                if is_success:
                    test_result = "Success: Antivirus successfully neutralized the simulated threat!"
                else:
                    test_result = "Failed: Threat bypassed the antivirus defense!"
                session[f"test_result_{lic_key}"] = test_result
                
                # --- ভাইরাস টেস্টের পর তাৎক্ষণিক ইমেল পাঠানো ---
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
    <head><title>Client Security Dashboard</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; padding:20px;">
        <div style="max-width:700px; margin:0 auto; background:#111827; padding:30px; border-radius:12px; border:1px solid #1e293b;">
            <h2>🛡️ Client Security Dashboard</h2>
            <p>License Key: <code style="color:#38bdf8;">{{ lic_key }}</code> | Organization: <b>{{ v.org }}</b></p>
            
            <div style="background:#0b1120; border:1px solid #1e293b; padding:15px; border-radius:8px; margin:20px 0; text-align:center;">
                <h4 style="margin:0 0 8px 0; color:#38bdf8;">Device Protection Status</h4>
                <p style="font-size:13px; color:#94a3b8; margin:0 0 12px 0;">
                    {% if antivirus_active %}✅ Antivirus is Active.{% else %}⚠️ Antivirus protection is inactive.{% endif %}
                </p>
                <form method="POST">
                    <input type="hidden" name="action" value="activate_antivirus">
                    <button type="submit" style="background:#10b981; color:white; padding:10px 20px; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">
                        {% if not antivirus_active %}Activate Antivirus{% else %}Re-Verify Antivirus{% endif %}
                    </button>
                </form>
            </div>

            <!-- Test Virus Simulation Section -->
            <div style="background:#0b1120; border:1px solid #1e293b; padding:15px; border-radius:8px; margin:20px 0; text-align:center;">
                <h4 style="margin:0 0 8px 0; color:#38bdf8;">🧪 Test Virus Simulation (Triggers Instant Email)</h4>
                {% if antivirus_active %}
                    <form method="POST">
                        <input type="hidden" name="action" value="run_test_virus">
                        <button type="submit" style="background:#8b5cf6; color:white; padding:10px 20px; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">
                            Run Threat Test & Email Report
                        </button>
                    </form>
                    {% if test_result %}
                        <div style="margin-top: 15px; padding: 10px; border-radius: 6px; font-weight: bold; background: {% if 'Success' in test_result %}rgba(16,185,129,0.2); color:#34d399; border:1px solid #10b981{% else %}rgba(239,68,68,0.2); color:#fca5a5; border:1px solid #ef4444{% endif %};">
                            {{ test_result }}
                        </div>
                    {% endif %}
                {% else %}
                    <p style="font-size:12px; color:#fca5a5;">The Test button will unlock after activating the antivirus.</p>
                    <button disabled style="background:#334155; color:#94a3b8; padding:10px 20px; border:none; border-radius:6px; cursor:not-allowed;">
                        Test (Locked)
                    </button>
                {% endif %}
            </div>

            <br><a href="/" style="color:#ef4444; font-size:13px; text-decoration:none;">Logout / Home</a>
        </div>
    </body>
    </html>
    """, lic_key=lic_key, v=v, antivirus_active=antivirus_active, msg_status=msg_status, test_result=test_result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
