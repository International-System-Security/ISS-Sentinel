from datetime import datetime, timedelta
import os
from flask import Flask, jsonify, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = "iss_super_secure_client_session_key_advanced"

LICENSE_FILE = "licenses.txt"
INQUIRY_FILE = "inquiries.txt"
TICKET_FILE = "tickets.txt"
ADMINS_FILE = "admins.txt"
SYSTEM_CONFIG_FILE = "system_config.txt"

# Default Master Admin
DEFAULT_MASTER_ADMIN = "admin@iss.com"

KNOWN_THREATS = [
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "44d88612fea8a8f36de82e1278abb02f",
]

def load_system_config():
    # Returns chat enabled status (True/False)
    if os.path.exists(SYSTEM_CONFIG_FILE):
        with open(SYSTEM_CONFIG_FILE, "r") as f:
            return f.read().strip() != "False"
    return True

def save_system_config(status):
    with open(SYSTEM_CONFIG_FILE, "w") as f:
        f.write(str(status))

def load_admins():
    admins = {DEFAULT_MASTER_ADMIN: {"password": "admin", "role": "Master"}}
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 2:
                    email = parts[0].strip()
                    pwd = parts[1].strip()
                    role = parts[2].strip() if len(parts) > 2 else "Admin"
                    admins[email] = {"password": pwd, "role": role}
    return admins

def save_all_admins(admins_dict):
    with open(ADMINS_FILE, "w") as f:
        for email, data in admins_dict.items():
            f.write(f"{email},{data['password']},{data['role']}\n")

def load_inquiries():
    inquiries = []
    if os.path.exists(INQUIRY_FILE):
        with open(INQUIRY_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) >= 4:
                    inquiries.append({"id": parts[0], "name": parts[1], "email": parts[2], "social": parts[3], "date": parts[4] if len(parts)>4 else "N/A"})
    return inquiries

def save_inquiry(name, email, social):
    inquiries = load_inquiries()
    inq_id = f"INQ-{int(datetime.now().timestamp())}"
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    inquiries.append({"id": inq_id, "name": name, "email": email, "social": social, "date": date_str})
    with open(INQUIRY_FILE, "w") as f:
        for i in inquiries:
            f.write(f"{i['id']}|{i['name']}|{i['email']}|{i['social']}|{i['date']}\n")

def load_tickets():
    # Ticket format: ticket_id | client_email | subject | messages (json or formatted)
    tickets = {}
    if os.path.exists(TICKET_FILE):
        with open(TICKET_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|||")
                if len(parts) >= 3:
                    t_id = parts[0]
                    email = parts[1]
                    msgs = parts[2:]
                    tickets[t_id] = {"email": email, "messages": msgs}
    return tickets

def save_ticket_msg(t_id, email, sender, text):
    tickets = load_tickets()
    if t_id not in tickets:
        tickets[t_id] = {"email": email, "messages": []}
    timestamp = datetime.now().strftime("%H:%M %d/%m")
    msg_str = f"{sender} ({timestamp}): {text}"
    tickets[t_id]["messages"].append(msg_str)
    
    with open(TICKET_FILE, "w") as f:
        for tid, data in tickets.items():
             msgs_joined = "|||".join(data["messages"])
             f.write(f"{tid}|||{data['email']}|||{msgs_joined}\n")

def load_licenses():
    licenses_dict = {}
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 8:
                    key = parts[0].strip()
                    licenses_dict[key] = {
                        "name": parts[1].strip(), "org": parts[2].strip(), "expiry": parts[3].strip(),
                        "max_devices": int(parts[4].strip()), "plan_type": parts[5].strip(),
                        "client_user": parts[6].strip(), "client_pwd": parts[7].strip(),
                        "pcs": [p.strip() for p in parts[8:] if p.strip()]
                    }
    return licenses_dict

def save_all_licenses(licenses_dict):
    with open(LICENSE_FILE, "w") as f:
        for k, v in licenses_dict.items():
            pcs_str = ",".join(v["pcs"])
            f.write(f"{k},{v['name']},{v['org']},{v['expiry']},{v['max_devices']},{v['plan_type']},{v['client_user']},{v['client_pwd']},{pcs_str}\n")

# --- Home Page with Contact Us Form ---
@app.route("/", methods=["GET", "POST"])
def home():
    msg = ""
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        social = request.form.get("social")
        if name and email:
            save_inquiry(name, email, social)
            msg = "✅ Your service application has been submitted successfully! Our team will contact you soon."

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ISS Cloud Security | Next-Gen Enterprise Antivirus & Protection</title>
        <style>
            :root {{
                --bg-primary: #060913; --bg-secondary: #0b1120; --bg-card: #111827;
                --accent-blue: #0ea5e9; --accent-hover: #0284c7; --text-main: #f8fafc;
                --text-muted: #94a3b8; --border-color: #1e293b;
            }}
            body {{ font-family: 'Segoe UI', system-ui, sans-serif; background-color: var(--bg-primary); color: var(--text-main); margin: 0; padding: 0; }}
            .navbar {{ display: flex; justify-content: space-between; align-items: center; padding: 20px 8%; border-bottom: 1px solid var(--border-color); background: rgba(6, 9, 19, 0.85); backdrop-filter: blur(10px); position: sticky; top: 0; z-index: 1000; }}
            .logo {{ font-size: 22px; font-weight: 800; color: var(--text-main); text-decoration: none; }}
            .logo span {{ color: var(--accent-blue); }}
            .nav-links {{ display: flex; gap: 25px; align-items: center; }}
            .nav-links a {{ color: var(--text-muted); text-decoration: none; font-size: 14px; font-weight: 500; }}
            .nav-links a:hover {{ color: var(--accent-blue); }}
            .btn {{ background-color: var(--accent-blue); color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px; }}
            .hero {{ text-align: center; padding: 80px 20px 50px 20px; max-width: 900px; margin: 0 auto; }}
            h1 {{ font-size: 48px; font-weight: 800; margin-bottom: 20px; }}
            h1 span {{ background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .contact-section {{ background: var(--bg-secondary); border-top: 1px solid var(--border-color); padding: 60px 20px; text-align: center; }}
            .form-box {{ max-width: 500px; margin: 0 auto; background: var(--bg-card); padding: 30px; border-radius: 12px; border: 1px solid var(--border-color); text-align: left; }}
            input {{ width: 100%; padding: 12px; margin: 8px 0 16px 0; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 6px; color: white; box-sizing: border-box; }}
            button {{ width: 100%; padding: 12px; background: var(--accent-blue); border: none; color: white; font-weight: bold; border-radius: 6px; cursor: pointer; }}
            .footer {{ text-align: center; padding: 25px; color: var(--text-muted); font-size: 13px; border-top: 1px solid var(--border-color); }}
        </style>
    </head>
    <body>
        <nav class="navbar">
            <a href="/" class="logo">🛡️ ISS <span>SECURITY</span></a>
            <div class="nav-links">
                <a href="/">Home</a>
                <a href="#contact">Contact Us</a>
                <a href="/client-login">Client Portal</a>
                <a href="/admin/login">Admin Center</a>
            </div>
        </nav>

        <div class="hero">
            <h1>Secure Your Enterprise Fleet with <span>Cloud Intelligence</span></h1>
            <p style="color: var(--text-muted); font-size: 17px; margin-bottom: 30px;">Advanced real-time threat detection and centralized device licensing built for modern infrastructure.</p>
            <a href="/client-login" class="btn">Access Client Portal</a>
        </div>

        <div class="contact-section" id="contact">
            <div class="form-box">
                <h3 style="margin-top:0; color: #f8fafc;">Request Service / Contact Us</h3>
                <p style="font-size: 13px; color: var(--text-muted);">Apply to get our enterprise security features and license solutions.</p>
                {f'<div style="background: rgba(16,185,129,0.1); border: 1px solid #10b981; color: #34d399; padding: 10px; border-radius: 6px; font-size: 13px; margin-bottom: 15px;">{msg}</div>' if msg else ''}
                <form method="POST">
                    <label style="font-size: 12px; color: var(--text-muted); font-weight: 600;">Your Name</label>
                    <input type="text" name="name" placeholder="John Doe" required>
                    <label style="font-size: 12px; color: var(--text-muted); font-weight: 600;">Email Address</label>
                    <input type="email" name="email" placeholder="john@company.com" required>
                    <label style="font-size: 12px; color: var(--text-muted); font-weight: 600;">Social Media Link (Facebook/LinkedIn/Twitter)</label>
                    <input type="text" name="social" placeholder="https://facebook.com/username">
                    <button type="submit">Submit Inquiry</button>
                </form>
            </div>
        </div>

        <div class="footer">
            &copy; 2026 ISS Security Systems. All Rights Reserved.
        </div>
    </body>
    </html>
    """)

# --- Admin Login ---
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = ""
    if request.method == "POST":
        email = request.form.get("email")
        pwd = request.form.get("password")
        admins = load_admins()
        if email in admins and admins[email]["password"] == pwd:
            session['admin_email'] = email
            return redirect(url_for('admin_panel'))
        else:
            error = "Invalid Admin Email or Password!"

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Admin Login - ISS</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #060913; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .card {{ background: #111827; padding: 35px; border-radius: 12px; width: 350px; border: 1px solid #1e293b; }}
            input {{ width: 100%; padding: 12px; margin: 8px 0 16px 0; background: #060913; border: 1px solid #334155; border-radius: 6px; color: white; box-sizing: border-box; }}
            button {{ width: 100%; padding: 12px; background: #0ea5e9; border: none; color: white; font-weight: bold; border-radius: 6px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Admin Login</h2>
            {f'<div style="color: #fca5a5; font-size: 13px; margin-bottom: 10px;">{error}</div>' if error else ''}
            <form method="POST">
                <label style="font-size: 12px; color: #94a3b8;">Admin Email</label>
                <input type="email" name="email" value="admin@iss.com" required>
                <label style="font-size: 12px; color: #94a3b8;">Password</label>
                <input type="password" name="password" value="admin" required>
                <button type="submit">Login</button>
            </form>
        </div>
    </body>
    </html>
    """)

@app.route("/admin/logout")
def admin_logout():
    session.pop('admin_email', None)
    return redirect(url_for('admin_login'))

# --- Admin Dashboard with Member Management, Ticket Control & Inquiries ---
@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    admin_email = session.get('admin_email')
    admins = load_admins()
    if not admin_email or admin_email not in admins:
        return redirect(url_for('admin_login'))

    is_master = (admin_email == DEFAULT_MASTER_ADMIN or admins[admin_email]["role"] == "Master")
    msg = ""

    if request.method == "POST":
        action = request.form.get("action")
        if action == "toggle_chat":
            current_status = load_system_config()
            save_system_config(not current_status)
            msg = f"⚙️ Support chat system status updated successfully!"
        elif action == "add_admin" and is_master:
            new_mail = request.form.get("new_admin_email")
            new_pwd = request.form.get("new_admin_pwd")
            if new_mail:
                admins[new_mail] = {"password": new_pwd if new_pwd else "123456", "role": "Admin"}
                save_all_admins(admins)
                msg = f"✅ New Admin Member '{new_mail}' added successfully with Verified Blue Tick status!"
        elif action == "remove_admin" and is_master:
            target_mail = request.form.get("target_admin_email")
            if target_mail in admins and target_mail != DEFAULT_MASTER_ADMIN:
                del admins[target_mail]
                save_all_admins(admins)
                msg = f"🗑️ Admin '{target_mail}' has been removed."
        elif action == "delete_license":
            target_key = request.form.get("license_key")
            licenses = load_licenses()
            if target_key in licenses:
                del licenses[target_key]
                save_all_licenses(licenses)
                msg = f"🗑️ License '{target_key}' deleted & blocked."

    chat_status = load_system_config()
    licenses = load_licenses()
    inquiries = load_inquiries()

    # Admin List Table rows
    admin_rows = ""
    for mail, data in admins.items():
        admin_rows += f"""
        <tr>
            <td><b>{mail}</b> <span title="Verified Security Admin" style="color: #38bdf8; font-weight: bold; cursor: help;">🔵</span></td>
            <td>{data['role']}</td>
            <td>{'<form method="POST"><input type="hidden" name="action" value="remove_admin"><input type="hidden" name="target_admin_email" value="'+mail+'"><button type="submit" style="background:#ef4444; padding:4px 8px; font-size:11px;">Remove</button></form>' if mail != DEFAULT_MASTER_ADMIN and is_master else 'Protected'}</td>
        </tr>
        """

    # Inquiry Table rows
    inq_rows = ""
    for i in inquiries:
        inq_rows += f"""
        <tr>
            <td>{i['name']}</td>
            <td>{i['email']}</td>
            <td><a href="{i['social']}" target="_blank" style="color: #38bdf8;">Profile Link</a></td>
            <td>{i['date']}</td>
        </tr>
        """

    # License table rows
    table_rows = ""
    for k, v in licenses.items():
        table_rows += f"""
        <tr>
            <td><code>{k}</code></td>
            <td><b>{v['name']}</b></td>
            <td>{v['org']}</td>
            <td>{v['plan_type']}</td>
            <td>{v['expiry']}</td>
            <td>
                <form method="POST" onsubmit="return confirm('Block/Delete this license?');" style="margin:0;">
                    <input type="hidden" name="action" value="delete_license">
                    <input type="hidden" name="license_key" value="{k}">
                    <button type="submit" style="background: #ef4444; padding: 4px 8px; font-size: 11px;">Delete/Block</button>
                </form>
            </td>
        </tr>
        """

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ISS Control Center</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #060913; color: #f8fafc; margin: 0; padding: 20px; }}
            .navbar {{ display: flex; justify-content: space-between; align-items: center; background: #111827; padding: 15px 25px; border-radius: 10px; border: 1px solid #1e293b; margin-bottom: 20px; }}
            .box {{ background: #111827; padding: 20px; border-radius: 10px; border: 1px solid #1e293b; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #1e293b; padding: 10px; text-align: left; font-size: 13px; }}
            th {{ background: #1a2234; color: #38bdf8; }}
            input, button {{ padding: 10px; margin: 5px 0; background: #060913; border: 1px solid #334155; color: white; border-radius: 6px; }}
            button {{ background: #0ea5e9; font-weight: bold; cursor: pointer; border: none; }}
        </style>
    </head>
    <body>
        <div class="navbar">
            <h2>🛡️ Admin Center ({admin_email} <span style="color:#38bdf8;">🔵</span>)</h2>
            <a href="/admin/logout" style="color: #ef4444; text-decoration: none; font-weight: bold;">Logout</a>
        </div>

        {f'<div style="background: rgba(16,185,129,0.1); border: 1px solid #10b981; color: #34d399; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 13px;">{msg}</div>' if msg else ''}

        <div class="box">
            <h3>💬 Support Ticket & Messenger Control</h3>
            <p style="font-size: 13px; color: #94a3b8;">Current Status: <b style="color: {'#34d399' if chat_status else '#ef4444'};">{'ENABLED (Online)' if chat_status else 'DISABLED (Closed)'}</b></p>
            <form method="POST">
                <input type="hidden" name="action" value="toggle_chat">
                <button type="submit" style="background: {'#ef4444' if chat_status else '#10b981'};">{'Disable Messaging System' import None if False else ('Disable Chat System' if chat_status else 'Enable Chat System')}</button>
            </form>
            <a href="/admin/tickets" style="display:inline-block; margin-top:10px; background:#0284c7; color:white; padding:10px 15px; text-decoration:none; border-radius:6px; font-weight:bold; font-size:13px;">📁 Open Live Ticket Support Center</a>
        </div>

        {f'''
        <div class="box">
            <h3>👥 Admin Team Management (Add Member)</h3>
            <form method="POST">
                <input type="hidden" name="action" value="add_admin">
                <input type="email" name="new_admin_email" placeholder="New Admin Email" required style="width: 45%;">
                <input type="text" name="new_admin_pwd" placeholder="Temporary Password" required style="width: 45%;">
                <button type="submit" style="width: 100%; margin-top: 10px;">Grant Admin Access (Assign Blue Tick 🔵)</button>
            </form>
            <table>
                <tr><th>Admin Email & Verification</th><th>Role</th><th>Action</th></tr>
                {admin_rows}
            </table>
        </div>
        ''' if is_master else ''}

        <div class="box">
            <h3>📋 'Contact Us' Service Inquiries</h3>
            <table>
                <tr><th>Name</th><th>Email</th><th>Social Link</th><th>Date</th></tr>
                {inq_rows if inq_rows else '<tr><td colspan="4" style="text-align:center; color:#94a3b8;">No inquiries yet.</td></tr>'}
            </table>
        </div>

        <div class="box">
            <h3>🔑 Active License Fleet</h3>
            <table>
                <tr><th>License Key</th><th>Client</th><th>Org</th><th>Tier</th><th>Expiry</th><th>Action</th></tr>
                {table_rows if table_rows else '<tr><td colspan="6" style="text-align:center; color:#94a3b8;">No licenses found.</td></tr>'}
            </table>
        </div>
    </body>
    </html>
    """)

# --- Admin Ticket Center ---
@app.route("/admin/tickets", methods=["GET", "POST"])
def admin_tickets():
    admin_email = session.get('admin_email')
    admins = load_admins()
    if not admin_email or admin_email not in admins:
        return redirect(url_for('admin_login'))

    tickets = load_tickets()
    selected_tid = request.args.get("tid")

    if request.method == "POST":
        t_id = request.form.get("tid")
        reply_text = request.form.get("reply")
        if t_id and reply_text:
            save_ticket_msg(t_id, tickets.get(t_id, {}).get("email", "client"), f"Admin ({admin_email} 🔵)", reply_text)
            return redirect(url_for('admin_tickets', tid=t_id))

    ticket_list_html = ""
    for tid, data in tickets.items():
        ticket_list_html += f'<a href="/admin/tickets?tid={tid}" style="display:block; padding:10px; margin:5px 0; background:#1e293b; color:#38bdf8; text-decoration:none; border-radius:6px; font-size:13px;">Ticket: {tid} ({data["email"]})</a>'

    chat_box_html = "<p style='color:#94a3b8;'>Select a ticket from the left to start messaging.</p>"
    if selected_tid and selected_tid in tickets:
        t_data = tickets[selected_tid]
        msgs_html = "".join([f"<div style='background:#060913; padding:8px 12px; margin:6px 0; border-radius:6px; font-size:13px;'>{m}</div>" for m in t_data["messages"]])
        chat_box_html = f"""
        <h4>Chat for Ticket: {selected_tid}</h4>
        <div style="background:#111827; height:250px; overflow-y:auto; border:1px solid #1e293b; padding:10px; border-radius:6px; margin-bottom:10px;">{msgs_html}</div>
        <form method="POST">
            <input type="hidden" name="tid" value="{selected_tid}">
            <input type="text" name="reply" placeholder="Type reply as verified admin..." required style="width:78%; padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px;">
            <button type="submit" style="width:20%; padding:10px; background:#0ea5e9; border:none; font-weight:bold; color:white; border-radius:6px;">Send</button>
        </form>
        """

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Ticket Support Center</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; padding:20px;">
        <h2>💬 Live Messenger Ticket Center</h2>
        <a href="/admin" style="color:#38bdf8; font-size:13px; text-decoration:none;">&larr; Back to Dashboard</a>
        <div style="display:grid; grid-template-columns: 300px 1fr; gap:20px; margin-top:20px;">
            <div style="background:#111827; padding:15px; border-radius:10px; border:1px solid #1e293b;">
                <h4>All Client Tickets</h4>
                {ticket_list_html if ticket_list_html else '<p style="color:#94a3b8; font-size:13px;">No tickets created yet.</p>'}
            </div>
            <div style="background:#111827; padding:15px; border-radius:10px; border:1px solid #1e293b;">
                {chat_box_html}
            </div>
        </div>
    </body>
    </html>
    """)

# --- Client Support Ticket Portal ---
@app.route("/client-dashboard", methods=["GET", "POST"])
def client_dashboard():
    license_key = session.get('active_license')
    licenses = load_licenses()
    if not license_key or license_key not in licenses:
        return redirect(url_for('client_login'))

    v = licenses[license_key]
    chat_enabled = load_system_config()
    client_email = f"client_{license_key[:6]}@iss.com"
    ticket_id = f"TICK-{license_key[:6]}"

    msg_status = ""
    if request.method == "POST":
        if not chat_enabled:
            msg_status = "❌ Messaging system has been temporarily disabled by admin."
        else:
            action = request.form.get("action")
            if action == "send_ticket_msg":
                user_msg = request.form.get("message")
                if user_msg:
                    save_ticket_msg(ticket_id, client_email, f"Client ({v['name']})", user_msg)
                    msg_status = "✅ Message sent to admin support!"

    tickets = load_tickets()
    my_ticket_msgs = tickets.get(ticket_id, {}).get("messages", [])
    chat_history_html = "".join([f"<div style='background:#111827; padding:8px 12px; margin:6px 0; border-radius:6px; font-size:13px;'>{m}</div>" for m in my_ticket_msgs])

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Client Portal</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; padding:20px;">
        <div style="max-width:600px; margin:0 auto; background:#111827; padding:25px; border-radius:12px; border:1px solid #1e293b;">
            <h2>🛡️ Client Security & Support</h2>
            <p>License: <code style="color:#38bdf8;">{license_key}</code> | Organization: <b>{v['org']}</b></p>
            <hr style="border-color:#1e293b;">
            
            <h3>💬 Support Ticket Messenger</h3>
            {f'<div style="background:rgba(239,68,68,0.1); border:1px solid #ef4444; color:#fca5a5; padding:10px; border-radius:6px; font-size:13px; margin-bottom:10px;">{msg_status}</div>' if msg_status else ''}
            
            <div style="background:#060913; height:200px; overflow-y:auto; border:1px solid #1e293b; padding:10px; border-radius:6px; margin-bottom:10px;">
                {chat_history_html if chat_history_html else '<p style="color:#94a3b8; font-size:13px;">No messages in your ticket yet. Type below to chat with admin.</p>'}
            </div>
            
            {f'''
            <form method="POST">
                <input type="hidden" name="action" value="send_ticket_msg">
                <input type="text" name="message" placeholder="Type your message to support..." required style="width:78%; padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px;">
                <button type="submit" style="width:20%; padding:10px; background:#0ea5e9; border:none; font-weight:bold; color:white; border-radius:6px;">Send</button>
            </form>
            ''' if chat_enabled else '<p style="color:#ef4444; font-size:13px; font-weight:bold;">⚠️ Support chat is currently closed by administration.</p>'}
            
            <br><a href="/client-logout" style="color:#ef4444; font-size:13px; font-weight:bold; text-decoration:none;">Logout Portal</a>
        </div>
    </body>
    </html>
    """)

# Keep other client-login / scan routes intact...
@app.route("/client-login", methods=["GET", "POST"])
def client_login():
    error_msg = ""
    if request.method == "POST":
        license_key = request.form.get("license_key", "").strip()
        licenses = load_licenses()
        if license_key in licenses:
            session['active_license'] = license_key
            return redirect(url_for('client_dashboard'))
        else:
            error_msg = "Invalid or Blocked License ID!"
    return render_template_string(f"""
    <body style="font-family:'Segoe UI'; background:#060913; color:white; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <div style="background:#111827; padding:35px; border-radius:12px; width:350px; border:1px solid #1e293b;">
            <h2>Client Login</h2>
            {f'<div style="color:#fca5a5; font-size:13px; margin-bottom:10px;">{error_msg}</div>' if error_msg else ''}
            <form method="POST">
                <input type="text" name="license_key" placeholder="Enter License ID" required style="width:100%; padding:12px; margin:8px 0 16px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                <button type="submit" style="width:100%; padding:12px; background:#0ea5e9; border:none; color:white; font-weight:bold; border-radius:6px; cursor:pointer;">Login Portal</button>
            </form>
        </div>
    </body>
    """)

@app.route("/client-logout")
def client_logout():
    session.pop('active_license', None)
    return redirect(url_for('client_login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
