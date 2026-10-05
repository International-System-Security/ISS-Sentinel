from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import random
import requests
import threading
import discord
from discord.ext import commands

app = Flask(__name__)
app.secret_key = "iss_enterprise_security_secret_key_v19_bot"

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

USER_FILE = "users.txt"
POST_FILE = "posts.txt"
INQUIRY_FILE = "inquiries.txt"
TICKET_FILE = "tickets.txt"
LICENSE_FILE = "licenses.txt"
ADMIN_LIST_FILE = "admins.txt"

OWNER_EMAIL = "admin@iss.com"
OWNER_USERNAME = "ibr@him"
OWNER_PASSWORD = "muhib###5869@"

# আপনার ডিসকর্ড ওয়েবহুক ইউআরএল
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1556104485439275099/dzkin3uRRAl68W6xW5vjDnwDt5j5yoV04AyMH1xbBEep6PDO0mYn28TmLfLbNoHH3MPE"

# আপনার ডিসকর্ড বটের টোকেন এখানে বসান
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "your_token_here")

def send_discord_alert(message_text):
    if not DISCORD_WEBHOOK_URL:
        return
    payload = {"content": message_text}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
    except Exception:
        pass

# Exact Verified Blue Badge SVG for Admins
ADMIN_BADGE_SVG = '''
<svg width="16" height="16" viewBox="0 0 24 24" fill="#0ea5e9" style="vertical-align: middle; margin-left: 4px;" title="Verified Admin">
    <path d="M12 2L14.34 3.73L17.25 3.5L18.77 6.04L21.5 7.15L21.57 10.12L23.75 12.12L22.12 14.75L22.5 17.75L19.75 19L18.38 21.62L15.5 21.37L13.38 23.25L10.62 22.25L8.12 23.37L6.38 21.12L3.62 20.37L3.12 17.5L0.87 15.62L2.12 12.87L0.87 10.12L3.12 8.25L3.87 5.5L6.62 5.12L8.5 2.87L11.25 3.87L12 2Z" fill="#0ea5e9"/>
    <path d="M9 16.2L4.8 12L6.2 10.6L9 13.4L17.8 4.6L19.2 6L9 16.2Z" fill="white"/>
</svg>
'''

TRUSTED_BLACK_BADGE_SVG = '''
<svg width="16" height="16" viewBox="0 0 24 24" fill="#000000" style="vertical-align: middle; margin-left: 4px;" title="Trusted Member">
    <path d="M12 2L14.34 3.73L17.25 3.5L18.77 6.04L21.5 7.15L21.57 10.12L23.75 12.12L22.12 14.75L22.5 17.75L19.75 19L18.38 21.62L15.5 21.37L13.38 23.25L10.62 22.25L8.12 23.37L6.38 21.12L3.62 20.37L3.12 17.5L0.87 15.62L2.12 12.87L0.87 10.12L3.12 8.25L3.87 5.5L6.62 5.12L8.5 2.87L11.25 3.87L12 2Z" fill="#1e293b" stroke="#38bdf8" stroke-width="1"/>
    <path d="M9 16.2L4.8 12L6.2 10.6L9 13.4L17.8 4.6L19.2 6L9 16.2Z" fill="#38bdf8"/>
</svg>
'''

def load_admin_data():
    admins = {OWNER_EMAIL: {"username": OWNER_USERNAME, "password": OWNER_PASSWORD}}
    if os.path.exists(ADMIN_LIST_FILE):
        with open(ADMIN_LIST_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|||")
                if len(parts) >= 3:
                    em, uname, pwd = parts[0].strip(), parts[1].strip(), parts[2].strip()
                    if em and em != OWNER_EMAIL:
                        admins[em] = {"username": uname, "password": pwd}
    return admins

def save_admin_data(email, username, password):
    admins = load_admin_data()
    admins[email] = {"username": username, "password": password}
    with open(ADMIN_LIST_FILE, "w") as f:
        for em, data in admins.items():
            if em != OWNER_EMAIL:
                f.write(f"{em}|||{data['username']}|||{data['password']}\n")

def remove_admin_email(email):
    admins = load_admin_data()
    if email in admins and email != OWNER_EMAIL:
        del admins[email]
        with open(ADMIN_LIST_FILE, "w") as f:
            for em, data in admins.items():
                if em != OWNER_EMAIL:
                    f.write(f"{em}|||{data['username']}|||{data['password']}\n")

def load_users():
    users = {}
    admin_data = load_admin_data()
    admin_emails = set(admin_data.keys())

    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|||")
                if len(parts) >= 8:
                    uname = parts[0].strip()
                    email = parts[1].strip()
                    if email in admin_emails:
                        continue
                    role = parts[3].strip()
                    verified = parts[5].strip() == "True"
                    users[uname] = {
                        "email": email, "password": parts[2].strip(),
                        "role": role, "pic": parts[4].strip(),
                        "verified": verified, "trusted": parts[6].strip() == "True",
                        "last_active": parts[7].strip()
                    }

    for em, data in admin_data.items():
        uname = data["username"]
        pwd = data["password"]
        users[uname] = {
            "email": em, "password": pwd, "role": "Admin",
            "pic": "https://i.imgur.com/6VBx3io.png", "verified": True, "trusted": False,
            "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    return users

def save_all_users(users_dict):
    with open(USER_FILE, "w") as f:
        admin_data = load_admin_data()
        admin_emails = set(admin_data.keys())
        for uname, data in users_dict.items():
            if data['email'] in admin_emails or data['role'] == 'Admin':
                continue
            f.write(f"{uname}|||{data['email']}|||{data['password']}|||{data['role']}|||{data['pic']}|||{data['verified']}|||{data['trusted']}|||{data.get('last_active', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}\n")

def check_inactivity_logout():
    current_user = session.get("username")
    if current_user:
        users = load_users()
        if current_user in users:
            last_active_str = users[current_user].get("last_active")
            if last_active_str:
                try:
                    last_active_time = datetime.strptime(last_active_str, "%Y-%m-%d %H:%M:%S")
                    if datetime.now() - last_active_time > timedelta(days=30):
                        session.pop("username", None)
                        return True
                except:
                    pass
            users[current_user]["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_all_users(users)
    return False

def load_posts():
    posts = []
    if os.path.exists(POST_FILE):
        with open(POST_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|||")
                if len(parts) >= 5:
                    posts.append({
                        "id": parts[0], "author": parts[1], "content": parts[2],
                        "img": parts[3], "date": parts[4]
                    })
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
                    t_id = parts[0]
                    user = parts[1]
                    msgs = parts[2:]
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
                if len(parts) >= 8:
                    licenses[parts[0].strip()] = {
                        "name": parts[1].strip(), "org": parts[2].strip(), "expiry": parts[3].strip(),
                        "max": parts[4].strip(), "plan": parts[5].strip(),
                        "client_user": parts[6].strip(), "client_pwd": parts[7].strip()
                    }
    return licenses

def save_licenses(lic_dict):
    with open(LICENSE_FILE, "w") as f:
        for k, v in lic_dict.items():
            f.write(f"{k},{v['name']},{v['org']},{v['expiry']},{v['max']},{v['plan']},{v['client_user']},{v['client_pwd']}\n")

@app.before_request
def before_request_func():
    check_inactivity_logout()

# --- 1. HOME PANEL ---
@app.route("/", methods=["GET", "POST"])
def home():
    users = load_users()
    posts = load_posts()
    inquiry_msg = ""

    search_query = request.args.get("search", "").strip()
    filtered_users = {u: d for u, d in users.items() if search_query.lower() in u.lower()} if search_query else users

    if request.method == "POST":
        form_type = request.form.get("form_type")
        if form_type == "inquiry":
            name = request.form.get("name")
            email = request.form.get("email")
            social = request.form.get("social")
            if name and email:
                with open(INQUIRY_FILE, "a") as f:
                    f.write(f"{name}|{email}|{social}|{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                inquiry_msg = "✅ Your service application has been submitted successfully!"
        elif form_type == "create_post" and "username" in session:
            content = request.form.get("content")
            img_path = ""
            if 'post_img_file' in request.files:
                file = request.files['post_img_file']
                if file and file.filename != '':
                    filename = secure_filename(f"post_{int(datetime.now().timestamp())}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    img_path = f"/static/uploads/{filename}"
            if not img_path:
                img_path = request.form.get("img", "").strip()
            if content:
                save_post(session["username"], content, img_path)
                return redirect(url_for("home"))

    current_user = session.get("username")
    user_data = users.get(current_user) if current_user else None
    is_admin = user_data and user_data['role'] == 'Admin'

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ISS Cloud Security & Social Platform</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {
                --bg-primary: #060913; --bg-secondary: #0b1120; --bg-card: #111827;
                --accent-blue: #0ea5e9; --accent-hover: #0284c7; --text-main: #f8fafc;
                --text-muted: #94a3b8; --border-color: #1e293b;
            }
            body { font-family: 'Segoe UI', system-ui, sans-serif; background-color: var(--bg-primary); color: var(--text-main); margin: 0; padding: 0; }
            .navbar { display: flex; justify-content: space-between; align-items: center; padding: 18px 6%; border-bottom: 1px solid var(--border-color); background: rgba(6, 9, 19, 0.95); position: sticky; top: 0; z-index: 1000; }
            .logo { font-size: 20px; font-weight: 800; color: var(--text-main); text-decoration: none; }
            .logo span { color: var(--accent-blue); }
            .nav-links { display: flex; gap: 20px; align-items: center; }
            .nav-links a { color: var(--text-muted); text-decoration: none; font-size: 14px; font-weight: 500; }
            .nav-links a:hover { color: var(--accent-blue); }
            .container { max-width: 900px; margin: 30px auto; padding: 0 15px; }
            .card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 25px; margin-bottom: 25px; box-shadow: 0 8px 20px rgba(0,0,0,0.3); }
            input, textarea { width: 100%; padding: 12px; margin: 8px 0 14px 0; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 6px; color: white; box-sizing: border-box; }
            button { background: var(--accent-blue); color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; }
            button:hover { background: var(--accent-hover); }
            footer { border-top: 1px solid var(--border-color); background: var(--bg-secondary); padding: 30px 20px; text-align: center; margin-top: 50px; color: var(--text-muted); font-size: 13px; }
            .social-icons { display: flex; justify-content: center; gap: 20px; margin-bottom: 15px; font-size: 20px; }
            .social-icons a { color: var(--text-muted); text-decoration: none; transition: 0.2s; }
            .social-icons a:hover { color: var(--accent-blue); }
        </style>
    </head>
    <body>
        <nav class="navbar">
            <a href="/" class="logo">🛡️ ISS <span>PLATFORM</span></a>
            <div class="nav-links">
                <a href="#social">ISS Social</a>
                <a href="#plans">Membership Plans</a>
                <a href="#contact">Contact Us</a>
                <a href="#tickets">Support Tickets</a>
                <a href="/my-profile">My Profile</a>
                {% if is_admin %}<a href="/admin" style="color: #38bdf8; font-weight: bold;">Admin Panel</a>{% endif %}
                <a href="/client-login">Client Portal</a>
            </div>
        </nav>

        <div class="container">
            <div class="card" style="text-align: center; padding: 50px 20px;">
                <h1>Next-Gen Cloud Security & Social Hub</h1>
                <p style="color: var(--text-muted); max-width: 650px; margin: 0 auto 20px auto;">Connect with professionals, manage security licenses, and communicate securely through private tickets.</p>
                {% if current_user %}
                    <p style="color: #34d399; font-weight: bold;">Welcome back, {{ current_user }} 
                    {% if is_admin %}{{ admin_badge | safe }}{% elif user_data.get('trusted') %}{{ trusted_badge | safe }}{% endif %}</p>
                {% else %}
                    <a href="/my-profile" style="background:var(--accent-blue); color:white; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:bold;">Login / Register (Social Join)</a>
                {% endif %}
            </div>

            <div class="card" id="plans">
                <h3>📦 Membership & Device Plans</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-top: 15px;">
                    <div style="background:var(--bg-secondary); padding:15px; border-radius:8px; border:1px solid var(--border-color);">
                        <h4 style="margin:0 0 5px 0; color:#38bdf8;">Basic Plan</h4>
                        <span style="font-size:12px; color:var(--accent-blue); font-weight:bold;">Limit: 2 Devices</span>
                    </div>
                    <div style="background:var(--bg-secondary); padding:15px; border-radius:8px; border:1px solid var(--border-color);">
                        <h4 style="margin:0 0 5px 0; color:#38bdf8;">Family Plan</h4>
                        <span style="font-size:12px; color:var(--accent-blue); font-weight:bold;">Limit: 5 Devices</span>
                    </div>
                    <div style="background:var(--bg-secondary); padding:15px; border-radius:8px; border:1px solid var(--border-color);">
                        <h4 style="margin:0 0 5px 0; color:#38bdf8;">Standard Plan</h4>
                        <span style="font-size:12px; color:var(--accent-blue); font-weight:bold;">Limit: 10 Devices</span>
                    </div>
                    <div style="background:var(--bg-secondary); padding:15px; border-radius:8px; border:1px solid var(--border-color);">
                        <h4 style="margin:0 0 5px 0; color:#38bdf8;">Business Plan</h4>
                        <span style="font-size:12px; color:var(--accent-blue); font-weight:bold;">Limit: Unlimited</span>
                    </div>
                </div>
            </div>

            <div class="card" id="social">
                <h3>🌐 ISS Social Feed</h3>
                <form method="GET" action="/" style="margin-bottom: 20px; display: flex; gap: 10px;">
                    <input type="text" name="search" placeholder="Search user by username..." value="{{ search_query }}" style="margin:0;">
                    <button type="submit" style="width: auto;">Search</button>
                </form>

                {% if current_user %}
                <div style="background:var(--bg-secondary); padding:15px; border-radius:8px; margin-bottom:20px;">
                    <form method="POST" enctype="multipart/form-data">
                        <input type="hidden" name="form_type" value="create_post">
                        <textarea name="content" placeholder="What's on your mind?" rows="3" required style="margin:0 0 10px 0;"></textarea>
                        <input type="file" name="post_img_file" accept="image/*" style="padding: 8px; background: #060913; margin: 0 0 10px 0;">
                        <button type="submit">Post to ISS Social</button>
                    </form>
                </div>
                {% endif %}

                <div>
                    {% if posts %}
                        {% for p in posts %}
                        <div style="background:var(--bg-secondary); padding:15px; border-radius:8px; margin-bottom:15px; border:1px solid var(--border-color);">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                <b>{{ p.author }}</b> 
                                {% if users.get(p.author, {}).get('role') == 'Admin' %}{{ admin_badge | safe }}
                                {% elif users.get(p.author, {}).get('trusted') %}{{ trusted_badge | safe }}{% endif %}
                                <span style="font-size:11px; color:var(--text-muted);">{{ p.date }}</span>
                            </div>
                            <p style="margin:0 0 10px 0; font-size:14px;">{{ p.content }}</p>
                            {% if p.img %}<img src="{{ p.img }}" style="max-width:100%; border-radius:6px; max-height:300px; object-fit:cover;" />{% endif %}
                        </div>
                        {% endfor %}
                    {% endif %}
                </div>
            </div>

            <div class="card" id="contact">
                <h3>📞 Contact Us & Service Application</h3>
                {% if inquiry_msg %}
                <div style="background: rgba(16,185,129,0.1); border: 1px solid #10b981; color: #34d399; padding: 10px; border-radius: 6px; font-size: 13px; margin-bottom: 15px;">{{ inquiry_msg }}</div>
                {% endif %}
                <form method="POST">
                    <input type="hidden" name="form_type" value="inquiry">
                    <input type="text" name="name" placeholder="Your Full Name" required>
                    <input type="email" name="email" placeholder="Email Address" required>
                    <input type="text" name="social" placeholder="Social Media Profile Link" required>
                    <button type="submit">Submit Application</button>
                </form>
            </div>

            <div class="card" id="tickets">
                <h3>💬 Support Tickets</h3>
                {% if current_user %}
                <a href="/ticket-chat" style="display:inline-block; background:var(--accent-blue); color:white; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:bold; margin-top:10px;">Open My Support Chat</a>
                {% else %}
                <p style="font-size:13px; color:#fca5a5;">Please login via My Profile to access support tickets.</p>
                {% endif %}
            </div>
        </div>

        <footer>
            <div class="social-icons">
                <a href="https://discord.com" target="_blank"><i class="fa-brands fa-discord"></i></a>
                <a href="https://github.com" target="_blank"><i class="fa-brands fa-github"></i></a>
                <a href="https://linkedin.com" target="_blank"><i class="fa-brands fa-linkedin"></i></a>
                <a href="https://twitter.com" target="_blank"><i class="fa-brands fa-twitter"></i></a>
            </div>
            <p>&copy; 2026 ISS Enterprise & Cloud Security Platform. All rights reserved.</p>
        </footer>
    </body>
    </html>
    """, current_user=current_user, user_data=user_data, is_admin=is_admin, posts=posts, 
    filtered_users=filtered_users, search_query=search_query, inquiry_msg=inquiry_msg, 
    admin_badge=ADMIN_BADGE_SVG, trusted_badge=TRUSTED_BLACK_BADGE_SVG, users=users)

# --- MY PROFILE ---
@app.route("/my-profile", methods=["GET", "POST"])
def my_profile():
    users = load_users()
    admin_data = load_admin_data()
    msg = ""
    error = ""

    if request.method == "POST":
        action = request.form.get("action")
        if action == "register":
            uname = request.form.get("username").strip()
            email = request.form.get("email").strip()
            pwd = request.form.get("password").strip()
            pic = "https://i.imgur.com/6VBx3io.png"

            if 'profile_pic_file' in request.files:
                file = request.files['profile_pic_file']
                if file and file.filename != '':
                    filename = secure_filename(f"{uname}_{int(datetime.now().timestamp())}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    pic = f"/static/uploads/{filename}"

            if uname in users:
                error = "Username already exists!"
            else:
                role = "Admin" if (email in admin_data or email == OWNER_EMAIL) else "User"
                users[uname] = {
                    "email": email, "password": pwd, "role": role, "pic": pic,
                    "verified": True if role == "Admin" else False, "trusted": False,
                    "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                save_all_users(users)
                session["username"] = uname
                return redirect(url_for("admin_panel") if role == "Admin" else url_for("my_profile"))

        elif action == "login":
            email = request.form.get("email").strip()
            uname = request.form.get("username").strip()
            pwd = request.form.get("password").strip()

            if uname in users and users[uname]["password"] == pwd and users[uname]["email"] == email:
                session["username"] = uname
                users[uname]["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_all_users(users)
                return redirect(url_for("admin_panel") if users[uname]["role"] == "Admin" else url_for("my_profile"))
            else:
                error = "Invalid email, username or password!"

    current_user = session.get("username")
    users = load_users() 
    user_data = users.get(current_user) if current_user else None
    view_user_name = request.args.get("user", current_user)
    view_data = users.get(view_user_name)
    is_viewer_admin = user_data and user_data['role'] == 'Admin'

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>My Profile - ISS Platform</title>
        <style>
            :root {
                --bg-primary: #060913; --bg-secondary: #0b1120; --bg-card: #111827;
                --accent-blue: #0ea5e9; --accent-hover: #0284c7; --text-main: #f8fafc;
                --text-muted: #94a3b8; --border-color: #1e293b;
            }
            body { font-family: 'Segoe UI', system-ui, sans-serif; background-color: var(--bg-primary); color: var(--text-main); margin: 0; padding: 20px; }
            .container { max-width: 600px; margin: 30px auto; background: var(--bg-card); padding: 35px; border-radius: 12px; border: 1px solid var(--border-color); }
            input, select { width: 100%; padding: 12px; margin: 8px 0 16px 0; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 6px; color: white; box-sizing: border-box; }
            button { width: 100%; padding: 12px; background: var(--accent-blue); border: none; color: white; font-weight: bold; border-radius: 6px; cursor: pointer; }
            .avatar-lg { width: 90px; height: 90px; border-radius: 50%; object-fit: cover; border: 3px solid var(--accent-blue); }
        </style>
    </head>
    <body>
        <div style="text-align:center; margin-bottom:20px;">
            <a href="/" style="color:var(--accent-blue); text-decoration:none; font-weight:bold;">&larr; Back to Home</a>
        </div>
        <div class="container">
            {% if error %}<div style="color:#ef4444; font-size:13px; margin-bottom:15px; padding:10px; background:rgba(239,68,68,0.1); border-radius:6px;">{{ error }}</div>{% endif %}
            {% if msg %}<div style="color:#34d399; font-size:13px; margin-bottom:15px; padding:10px; background:rgba(16,185,129,0.1); border-radius:6px;">{{ msg }}</div>{% endif %}

            {% if current_user and view_data %}
            <div style="text-align:center;">
                <img src="{{ view_data.pic }}" class="avatar-lg" />
                <h2 style="margin:15px 0 5px 0;">{{ view_user_name }} 
                {% if view_data.role == 'Admin' %}{{ admin_badge | safe }}{% elif view_data.get('trusted') %}{{ trusted_badge | safe }}{% endif %}</h2>
                <p style="color:var(--text-muted); font-size:14px; margin:0 0 20px 0;">Email: {{ view_data.email }} | Role: <b>{{ view_data.role }}</b></p>
            </div>
            <div style="text-align:center; margin-top:25px;">
                <a href="/logout" style="color:#ef4444; font-weight:bold; font-size:14px; text-decoration:none;">Log Out</a>
                {% if user_data.role == 'Admin' %}<br><br><a href="/admin" style="color:#38bdf8; font-weight:bold; text-decoration:none;">Admin Control Panel &rarr;</a>{% endif %}
            </div>
            {% else %}
            <div style="display:flex; justify-content:center; gap:10px; margin-bottom:20px;">
                <button onclick="document.getElementById('login-form').style.display='block'; document.getElementById('reg-form').style.display='none';" style="background:#1e293b;">Login</button>
                <button onclick="document.getElementById('reg-form').style.display='block'; document.getElementById('login-form').style.display='none';" style="background:#1e293b;">Register</button>
            </div>
            <div id="login-form">
                <h3>Account Login</h3>
                <form method="POST">
                    <input type="hidden" name="action" value="login">
                    <label style="font-size:12px; color:var(--text-muted);">Email</label>
                    <input type="email" name="email" required>
                    <label style="font-size:12px; color:var(--text-muted);">Username</label>
                    <input type="text" name="username" required>
                    <label style="font-size:12px; color:var(--text-muted);">Password</label>
                    <input type="password" name="password" required>
                    <button type="submit">Login</button>
                </form>
            </div>
            <div id="reg-form" style="display:none;">
                <h3>Register</h3>
                <form method="POST" enctype="multipart/form-data">
                    <input type="hidden" name="action" value="register">
                    <label style="font-size:12px; color:var(--text-muted);">Username</label>
                    <input type="text" name="username" required>
                    <label style="font-size:12px; color:var(--text-muted);">Email</label>
                    <input type="email" name="email" required>
                    <label style="font-size:12px; color:var(--text-muted);">Password</label>
                    <input type="password" name="password" required>
                    <button type="submit" style="margin-top: 10px;">Register Account</button>
                </form>
            </div>
            {% endif %}
        </div>
    </body>
    </html>
    """, error=error, msg=msg, current_user=current_user, view_data=view_data, 
    view_user_name=view_user_name, user_data=user_data, is_viewer_admin=is_viewer_admin, 
    admin_badge=ADMIN_BADGE_SVG, trusted_badge=TRUSTED_BLACK_BADGE_SVG)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

# --- 2. ADMIN PANEL ---
@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    users = load_users()
    current_user = session.get("username")
    if not current_user or users.get(current_user, {}).get("role") != "Admin":
        return redirect(url_for("my_profile"))

    msg = ""
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add_admin":
            new_em = request.form.get("admin_email", "").strip()
            new_uname = request.form.get("admin_username", "").strip()
            new_pwd = request.form.get("admin_password", "").strip()
            if new_em and new_uname and new_pwd:
                save_admin_data(new_em, new_uname, new_pwd)
                msg = f"✅ Admin '{new_uname}' added successfully!"
        elif action == "remove_admin_email":
            rem_em = request.form.get("remove_email", "").strip()
            if rem_em:
                remove_admin_email(rem_em)
                msg = f"🗑️ Admin email '{rem_em}' removed successfully!"
        elif action == "delete_license":
            lic_key = request.form.get("lic_key")
            licenses = load_licenses()
            if lic_key in licenses:
                del licenses[lic_key]
                save_licenses(licenses)
                msg = f"🗑️ License '{lic_key}' deleted & blocked successfully!"
        elif action == "add_license":
            l_key = request.form.get("l_key")
            l_name = request.form.get("l_name")
            l_org = request.form.get("l_org")
            l_expiry = request.form.get("l_expiry", "2027-01-01")
            l_plan = request.form.get("l_plan", "Basic Plan")
            l_user = request.form.get("l_user", "admin")
            l_pwd = request.form.get("l_pwd", "admin")

            licenses = load_licenses()
            licenses[l_key] = {
                "name": l_name, "org": l_org, "expiry": l_expiry,
                "max": "5", "plan": l_plan, "client_user": l_user, "client_pwd": l_pwd
            }
            save_licenses(licenses)
            send_discord_alert(f"🔑 **New Client API Key Created:** `{l_key}` | Client: **{l_name}** ({l_org}) | Plan: **{l_plan}**")
            msg = f"✅ License '{l_key}' created & broadcasted to Discord successfully!"

    licenses = load_licenses()
    admin_data = load_admin_data()

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Admin Control Panel</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #060913; color: #f8fafc; margin: 0; padding: 20px; }
            .navbar { display: flex; justify-content: space-between; align-items: center; background: #111827; padding: 15px 25px; border-radius: 10px; border: 1px solid #1e293b; margin-bottom: 25px; }
            .box { background: #111827; padding: 25px; border-radius: 12px; border: 1px solid #1e293b; margin-bottom: 25px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #1e293b; padding: 12px; text-align: left; font-size: 13px; }
            th { background: #1a2234; color: #38bdf8; }
            input, select, button { padding: 10px; margin: 5px 0; background: #060913; border: 1px solid #334155; color: white; border-radius: 6px; box-sizing: border-box; }
            button { background: #0ea5e9; font-weight: bold; cursor: pointer; border: none; }
        </style>
    </head>
    <body>
        <div class="navbar">
            <h2>🛡️ Admin Center ({{ current_user }})</h2>
            <a href="/" style="color: #38bdf8; text-decoration: none; font-weight: bold;">&larr; Back to Home</a>
        </div>

        {% if msg %}<div style="background: rgba(16,185,129,0.1); border: 1px solid #10b981; color: #34d399; padding: 12px; border-radius: 8px; margin-bottom: 20px;">{{ msg }}</div>{% endif %}

        <div class="box">
            <h3>👥 Add & Manage Admins</h3>
            <form method="POST" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-bottom: 15px;">
                <input type="hidden" name="action" value="add_admin">
                <input type="email" name="admin_email" placeholder="Email" required>
                <input type="text" name="admin_username" placeholder="Username" required>
                <input type="password" name="admin_password" placeholder="Password" required>
                <button type="submit" style="grid-column: 1 / -1;">Add Admin</button>
            </form>
        </div>

        <div class="box">
            <h3>💬 Support Ticket Control Center</h3>
            <a href="/admin/tickets" style="display:inline-block; background:#0284c7; color:white; padding:10px 18px; text-decoration:none; border-radius:6px; font-weight:bold; font-size:13px;">Open All Support Tickets</a>
        </div>

        <div class="box">
            <h3>🔑 License & API Key Management</h3>
            <form method="POST" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap:10px; margin-bottom:15px;">
                <input type="hidden" name="action" value="add_license">
                <input type="text" name="l_key" placeholder="License / API Key" required>
                <input type="text" name="l_name" placeholder="Client Name" required>
                <input type="text" name="l_org" placeholder="Organization" required>
                <select name="l_plan">
                    <option value="Basic Plan">Basic Plan</option>
                    <option value="Family Plan">Family Plan</option>
                    <option value="Standard Plan">Standard Plan</option>
                    <option value="Business Plan">Business Plan</option>
                </select>
                <input type="text" name="l_expiry" placeholder="Expiry (YYYY-MM-DD)" value="2027-01-01" required>
                <input type="text" name="l_user" placeholder="Client User" value="admin" required>
                <input type="text" name="l_pwd" placeholder="Client Pass" value="admin" required>
                <button type="submit" style="grid-column: 1 / -1;">Create License & Notify Discord</button>
            </form>
            <table>
                <tr><th>Key / API Key</th><th>Client</th><th>Org</th><th>Plan</th><th>Expiry</th><th>Action</th></tr>
                {% if licenses %}
                    {% for k, v in licenses.items() %}
                    <tr>
                        <td><code>{{ k }}</code></td>
                        <td>{{ v.name }}</td>
                        <td>{{ v.org }}</td>
                        <td>{{ v.plan }}</td>
                        <td>{{ v.expiry }}</td>
                        <td>
                            <form method="POST" style="margin:0;">
                                <input type="hidden" name="action" value="delete_license">
                                <input type="hidden" name="lic_key" value="{{ k }}">
                                <button type="submit" style="background:#ef4444; padding:4px 8px; font-size:11px;">Delete</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                {% endif %}
            </table>
        </div>
    </body>
    </html>
    """, current_user=current_user, msg=msg, admin_data=admin_data, licenses=licenses)

@app.route("/admin/tickets", methods=["GET", "POST"])
def admin_tickets():
    users = load_users()
    current_user = session.get("username")
    if not current_user or users.get(current_user, {}).get("role") != "Admin":
        return redirect(url_for("my_profile"))

    tickets = load_tickets()
    selected_tid = request.args.get("tid")

    if request.method == "POST":
        t_id = request.form.get("tid")
        reply_text = request.form.get("reply")
        if t_id and reply_text:
            save_ticket_msg(t_id, tickets.get(t_id, {}).get("user", "client"), f"Admin ({current_user})", reply_text)
            return redirect(url_for('admin_tickets', tid=t_id))

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Admin Support Center</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; padding:20px;">
        <h2>💬 Admin Live Ticket Messenger</h2>
        <a href="/admin" style="color:#38bdf8; font-size:13px; text-decoration:none;">&larr; Back to Admin Panel</a>
        <div style="display:grid; grid-template-columns: 320px 1fr; gap:20px; margin-top:20px;">
            <div style="background:#111827; padding:15px; border-radius:10px; border:1px solid #1e293b;">
                <h4>All Tickets</h4>
                {% if tickets %}
                    {% for tid, data in tickets.items() %}
                    <a href="/admin/tickets?tid={{ tid }}" style="display:block; padding:10px; margin:6px 0; background:#1e293b; color:#38bdf8; text-decoration:none; border-radius:6px; font-size:13px;">Ticket: {{ tid }}</a>
                    {% endfor %}
                {% endif %}
            </div>
            <div style="background:#111827; padding:15px; border-radius:10px; border:1px solid #1e293b;">
                {% if selected_tid and selected_tid in tickets %}
                    <h4>Chat: {{ selected_tid }}</h4>
                    <div style="background:#060913; height:260px; overflow-y:auto; border:1px solid #1e293b; padding:10px; border-radius:6px; margin-bottom:12px;">
                        {% for m in tickets[selected_tid].messages %}
                        <div style='background:#060913; padding:8px 12px; margin:6px 0; border-radius:6px; font-size:13px;'>{{ m }}</div>
                        {% endfor %}
                    </div>
                    <form method="POST">
                        <input type="hidden" name="tid" value="{{ selected_tid }}">
                        <input type="text" name="reply" placeholder="Type reply..." required style="width:78%; padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px;">
                        <button type="submit" style="width:20%; padding:10px; background:#0ea5e9; border:none; font-weight:bold; color:white; border-radius:6px; cursor:pointer;">Send</button>
                    </form>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """, tickets=tickets, selected_tid=selected_tid)

# --- 3. API ROUTES FOR REPORTS ---
@app.route('/report', methods=['GET'])
def api_report():
    license_key = request.args.get('license_key', '').strip()
    licenses = load_licenses()
    if not license_key or license_key not in licenses:
        return jsonify({"error": "Invalid or missing license key"}), 400
    
    client_info = licenses[license_key]
    report_data = {
        "client_name": client_info['name'],
        "organization": client_info['org'],
        "license_key": license_key,
        "plan": client_info['plan'],
        "status": "Active & Protected",
        "threats_blocked_today": 3,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    send_discord_alert(f"📊 **API Report Requested** for License: `{license_key}` ({client_info['name']})")
    return jsonify(report_data)

@app.route('/weekly_report', methods=['GET'])
def api_weekly_report():
    license_key = request.args.get('license_key', '').strip()
    licenses = load_licenses()
    if not license_key or license_key not in licenses:
        return jsonify({"error": "Invalid or missing license key"}), 400
    
    client_info = licenses[license_key]
    weekly_data = {
        "client_name": client_info['name'],
        "organization": client_info['org'],
        "license_key": license_key,
        "plan": client_info['plan'],
        "total_threats_this_week": 24,
        "security_score": "98%",
        "status": "Healthy",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    send_discord_alert(f"📈 **Weekly Security Report Generated** for License: `{license_key}` ({client_info['name']})")
    return jsonify(weekly_data)

# --- 4. CLIENT PANEL ---
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
                <label style="font-size:12px; color:#94a3b8;">License ID / API Key</label>
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
    api_response_msg = session.get(f"api_resp_{lic_key}", "")

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
        elif action == "fetch_report":
            try:
                res = requests.get(f"http://127.0.0.1:5000/report?license_key={lic_key}", timeout=3).json()
                session[f"api_resp_{lic_key}"] = f"📊 Report Fetched: {res}"
                api_response_msg = session[f"api_resp_{lic_key}"]
            except Exception:
                session[f"api_resp_{lic_key}"] = "📊 Report fetched & alert sent to Discord successfully!"
                api_response_msg = session[f"api_resp_{lic_key}"]
        elif action == "fetch_weekly_report":
            try:
                res = requests.get(f"http://127.0.0.1:5000/weekly_report?license_key={lic_key}", timeout=3).json()
                session[f"api_resp_{lic_key}"] = f"📈 Weekly Report Fetched: {res}"
                api_response_msg = session[f"api_resp_{lic_key}"]
            except Exception:
                session[f"api_resp_{lic_key}"] = "📈 Weekly Report fetched & alert sent to Discord successfully!"
                api_response_msg = session[f"api_resp_{lic_key}"]
        else:
            user_msg = request.form.get("message")
            if user_msg:
                save_ticket_msg(f"TICK-{lic_key}", lic_key, f"Client ({v['name']})", user_msg)
                msg_status = "✅ Message sent to support!"

    tickets = load_tickets()
    my_msgs = tickets.get(f"TICK-{lic_key}", {}).get("messages", [])

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Client Security Dashboard</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; padding:20px;">
        <div style="max-width:650px; margin:0 auto; background:#111827; padding:30px; border-radius:12px; border:1px solid #1e293b;">
            <h2>🛡️ Client Security Dashboard</h2>
            <p>License Key / API Key: <code style="color:#38bdf8;">{{ lic_key }}</code> | Organization: <b>{{ v.org }}</b></p>
            
            <div style="background:#0b1120; border:1px solid #1e293b; padding:15px; border-radius:8px; margin:20px 0; text-align:center;">
                <h4 style="margin:0 0 10px 0; color:#38bdf8;">📊 API Security Reports & Discord Alerts</h4>
                <div style="display:flex; justify-content:center; gap:10px;">
                    <form method="POST" style="margin:0;">
                        <input type="hidden" name="action" value="fetch_report">
                        <button type="submit" style="background:#0ea5e9; color:white; padding:10px 15px; border:none; border-radius:6px; font-weight:bold; cursor:pointer; font-size:12px;">See Your Report</button>
                    </form>
                    <form method="POST" style="margin:0;">
                        <input type="hidden" name="action" value="fetch_weekly_report">
                        <button type="submit" style="background:#8b5cf6; color:white; padding:10px 15px; border:none; border-radius:6px; font-weight:bold; cursor:pointer; font-size:12px;">See Your Weekly Report</button>
                    </form>
                </div>
                {% if api_response_msg %}
                <div style="margin-top:10px; font-size:12px; color:#34d399; background:rgba(16,185,129,0.1); padding:8px; border-radius:6px;">{{ api_response_msg }}</div>
                {% endif %}
            </div>

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

            <div style="background:#0b1120; border:1px solid #1e293b; padding:15px; border-radius:8px; margin:20px 0; text-align:center;">
                <h4 style="margin:0 0 8px 0; color:#38bdf8;">🧪 Test Virus Simulation</h4>
                {% if antivirus_active %}
                    <form method="POST" onsubmit="alert('⚠️ WARNING: Virus simulation or threat detected on system!');">
                        <input type="hidden" name="action" value="run_test_virus">
                        <button type="submit" style="background:#8b5cf6; color:white; padding:10px 20px; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">
                            Test
                        </button>
                    </form>
                    {% if test_result %}
                        <script>
                            alert("🛡️ Security Scan Result: {{ test_result }}");
                        </script>
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

            <hr style="border-color:#1e293b; margin:20px 0;">
            <h3>💬 Support Messenger</h3>
            {% if msg_status %}<div style="background:rgba(16,185,129,0.1); color:#34d399; padding:10px; border-radius:6px; font-size:13px; margin-bottom:12px;">{{ msg_status }}</div>{% endif %}
            
            <div style="background:#060913; height:180px; overflow-y:auto; border:1px solid #1e293b; padding:10px; border-radius:6px; margin-bottom:12px;">
                {% if my_msgs %}
                    {% for m in my_msgs %}
                    <div style='background:#111827; padding:8px 12px; margin:6px 0; border-radius:6px; font-size:13px;'>{{ m }}</div>
                    {% endfor %}
                {% endif %}
            </div>
            
            <form method="POST">
                <input type="text" name="message" placeholder="Type message..." required style="width:78%; padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px;">
                <button type="submit" style="width:20%; padding:10px; background:#0ea5e9; border:none; font-weight:bold; color:white; border-radius:6px; cursor:pointer;">Send</button>
            </form>
            <br><a href="/" style="color:#ef4444; font-size:13px; text-decoration:none;">Logout / Home</a>
        </div>
    </body>
    </html>
    """, lic_key=lic_key, v=v, antivirus_active=antivirus_active, msg_status=msg_status, my_msgs=my_msgs, test_result=test_result, api_response_msg=api_response_msg)

@app.route("/ticket-chat", methods=["GET", "POST"])
def ticket_chat():
    current_user = session.get("username")
    if not current_user:
        return redirect(url_for("my_profile"))

    t_id = f"USER-TICK-{current_user}"
    if request.method == "POST":
        user_msg = request.form.get("message")
        if user_msg:
            save_ticket_msg(t_id, current_user, f"User ({current_user})", user_msg)

    tickets = load_tickets()
    my_msgs = tickets.get(t_id, {}).get("messages", [])

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Support Ticket Chat</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; padding:20px;">
        <div style="max-width:650px; margin:30px auto; background:#111827; padding:30px; border-radius:12px; border:1px solid #1e293b;">
            <h2>💬 Support Ticket Chat ({{ current_user }})</h2>
            <a href="/" style="color:#38bdf8; font-size:13px; text-decoration:none;">&larr; Return Home</a>
            <hr style="border-color:#1e293b; margin:15px 0;">
            <div style="background:#060913; height:240px; overflow-y:auto; border:1px solid #1e293b; padding:10px; border-radius:6px; margin-bottom:12px;">
                {% if my_msgs %}
                    {% for m in my_msgs %}
                    <div style='background:#111827; padding:8px 12px; margin:6px 0; border-radius:6px; font-size:13px;'>{{ m }}</div>
                    {% endfor %}
                {% endif %}
            </div>
            <form method="POST">
                <input type="text" name="message" placeholder="Type message..." required style="width:78%; padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px;">
                <button type="submit" style="width:20%; padding:10px; background:#0ea5e9; border:none; font-weight:bold; color:white; border-radius:6px; cursor:pointer;">Send</button>
            </form>
        </div>
    </body>
    </html>
    """, current_user=current_user, my_msgs=my_msgs)

# --- DISCORD BOT SETUP & BACKGROUND THREAD ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Discord Bot logged in as {bot.user.name}")

@bot.command(name="report")
async def bot_report(ctx):
    await ctx.send("🛡️ ISS Security Report: System status is secure and active (3 threats blocked today).")

@bot.command(name="weekly_report")
async def bot_weekly_report(ctx):
    await ctx.send("📈 ISS Weekly Security Report: 24 threats blocked, 98% security score.")

def run_discord_bot():
    try:
        bot.run(BOT_TOKEN)
    except Exception as e:
        print(f"Bot error: {e}")

if __name__ == "__main__":
    # ব্যাকগ্রাউন্ড থ্রেডে ডিসকর্ড বট স্টার্ট হবে
    bot_thread = threading.Thread(target=run_discord_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # ফ্লাস্ক সার্ভার স্টার্ট
    app.run(host="0.0.0.0", port=5000, debug=True)

