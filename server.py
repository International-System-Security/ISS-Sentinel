from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

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
ADMIN_LIST_FILE = "admins.txt"

OWNER_EMAIL = "admin@iss.com"
OWNER_USERNAME = "ibr@him"
OWNER_PASSWORD = "muhib###5869@"

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
            .container { max-width: 900px; margin: 30px auto; padding: 0 15px; }
            .card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 25px; margin-bottom: 25px; }
            input, textarea { width: 100%; padding: 12px; margin: 8px 0 14px 0; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 6px; color: white; box-sizing: border-box; }
            button { background: var(--accent-blue); color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; }
            .avatar { width: 45px; height: 45px; border-radius: 50%; object-fit: cover; border: 2px solid var(--accent-blue); }
        </style>
    </head>
    <body>
        <nav class="navbar">
            <a href="/" class="logo">🛡️ ISS <span>PLATFORM</span></a>
            <div class="nav-links">
                <a href="#social">ISS Social</a>
                <a href="#plans">Membership Plans</a>
                <a href="#contact">Contact Us</a>
                <a href="/my-profile">My Profile</a>
                {% if is_admin %}<a href="/admin" style="color: #38bdf8; font-weight: bold;">Admin Panel</a>{% endif %}
                <a href="/client-login">Client Portal</a>
            </div>
        </nav>
        <div class="container">
            <div class="card" style="text-align: center; padding: 40px 20px;">
                <h1>Next-Gen Cloud Security & Social Hub</h1>
                {% if current_user %}
                    <p style="color: #34d399; font-weight: bold;">Welcome back, {{ current_user }}</p>
                {% else %}
                    <a href="/my-profile" style="background:var(--accent-blue); color:white; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:bold;">Login / Register</a>
                {% endif %}
            </div>
            <div class="card" id="social">
                <h3>🌐 ISS Social Feed</h3>
                <form method="GET" action="/" style="margin-bottom: 20px; display: flex; gap: 10px;">
                    <input type="text" name="search" placeholder="Search user..." value="{{ search_query }}" style="margin:0;">
                    <button type="submit" style="width: auto;">Search</button>
                </form>
                {% if current_user %}
                <div style="background:var(--bg-secondary); padding:15px; border-radius:8px; margin-bottom:20px;">
                    <form method="POST" enctype="multipart/form-data">
                        <input type="hidden" name="form_type" value="create_post">
                        <textarea name="content" placeholder="What's on your mind?" rows="3" required style="margin:0 0 10px 0;"></textarea>
                        <input type="file" name="post_img_file" accept="image/*" style="padding: 8px; background: #060913; margin: 0 0 10px 0;">
                        <button type="submit">Post</button>
                    </form>
                </div>
                {% endif %}
                <div>
                    {% for p in posts %}
                    <div style="background:var(--bg-secondary); padding:15px; border-radius:8px; margin-bottom:15px; border:1px solid var(--border-color);">
                        <b>{{ p.author }}</b> <span style="font-size:11px; color:var(--text-muted);">{{ p.date }}</span>
                        <p style="margin:10px 0;">{{ p.content }}</p>
                        {% if p.img %}<img src="{{ p.img }}" style="max-width:100%; border-radius:6px; max-height:300px;" />{% endif %}
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </body>
    </html>
    """, current_user=current_user, user_data=user_data, is_admin=is_admin, posts=posts, 
    filtered_users=filtered_users, search_query=search_query, inquiry_msg=inquiry_msg)

@app.route("/my-profile", methods=["GET", "POST"])
def my_profile():
    users = load_users()
    admin_data = load_admin_data()
    error = ""
    msg = ""

    if request.method == "POST":
        action = request.form.get("action")
        if action == "register":
            uname = request.form.get("username").strip()
            email = request.form.get("email").strip()
            pwd = request.form.get("password").strip()
            if uname in users:
                error = "Username already exists!"
            else:
                role = "Admin" if (email in admin_data or email == OWNER_EMAIL) else "User"
                users[uname] = {
                    "email": email, "password": pwd, "role": role, 
                    "pic": "https://i.imgur.com/6VBx3io.png",
                    "verified": True if role=="Admin" else False, "trusted": False,
                    "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                save_all_users(users)
                session["username"] = uname
                return redirect(url_for("my_profile"))
        elif action == "login":
            email = request.form.get("email").strip()
            uname = request.form.get("username").strip()
            pwd = request.form.get("password").strip()
            if uname in users and users[uname]["password"] == pwd and users[uname]["email"] == email:
                session["username"] = uname
                if users[uname]["role"] == "Admin":
                    return redirect(url_for("admin_panel"))
                return redirect(url_for("my_profile"))
            else:
                error = "Invalid credentials!"

    current_user = session.get("username")
    user_data = users.get(current_user) if current_user else None

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>My Profile</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; padding:30px;">
        <div style="max-width:500px; margin:auto; background:#111827; padding:30px; border-radius:12px; border:1px solid #1e293b;">
            <a href="/" style="color:#0ea5e9; text-decoration:none;">&larr; Back to Home</a>
            {% if error %}<div style="color:#ef4444; margin-top:10px;">{{ error }}</div>{% endif %}
            {% if current_user and user_data %}
                <h2 style="margin-top:15px;">{{ current_user }}</h2>
                <p>Email: {{ user_data.email }} | Role: <b>{{ user_data.role }}</b></p>
                <br><a href="/logout" style="color:#ef4444; font-weight:bold; text-decoration:none;">Log Out</a>
            {% else %}
                <h3>Login</h3>
                <form method="POST">
                    <input type="hidden" name="action" value="login">
                    <input type="email" name="email" placeholder="Email" required style="width:100%; padding:10px; margin:5px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                    <input type="text" name="username" placeholder="Username" required style="width:100%; padding:10px; margin:5px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                    <input type="password" name="password" placeholder="Password" required style="width:100%; padding:10px; margin:5px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                    <button type="submit" style="width:100%; padding:10px; background:#0ea5e9; border:none; color:white; font-weight:bold; border-radius:6px; margin-top:10px;">Login</button>
                </form>
                <hr style="border-color:#1e293b; margin:20px 0;">
                <h3>Register</h3>
                <form method="POST">
                    <input type="hidden" name="action" value="register">
                    <input type="text" name="username" placeholder="Username" required style="width:100%; padding:10px; margin:5px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                    <input type="email" name="email" placeholder="Email" required style="width:100%; padding:10px; margin:5px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                    <input type="password" name="password" placeholder="Password" required style="width:100%; padding:10px; margin:5px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                    <button type="submit" style="width:100%; padding:10px; background:#10b981; border:none; color:white; font-weight:bold; border-radius:6px; margin-top:10px;">Register</button>
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
                msg = f"🗑️ License deleted successfully!"
        elif action == "add_license":
            l_key = request.form.get("l_key")
            l_name = request.form.get("l_name")
            l_org = request.form.get("l_org")
            l_plan = request.form.get("l_plan", "Basic Plan")
            licenses = load_licenses()
            licenses[l_key] = {
                "name": l_name, "org": l_org, "expiry": "2027-01-01",
                "max": "5", "plan": l_plan, "client_user": "admin", "client_pwd": "admin"
            }
            save_licenses(licenses)
            msg = f"✅ License created successfully!"

    licenses = load_licenses()
    admin_data = load_admin_data()

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Admin Control Panel</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; padding:20px;">
        <div style="background:#111827; padding:20px; border-radius:10px; display:flex; justify-content:space-between; align-items:center;">
            <h2>🛡️ Admin Center</h2>
            <a href="/" style="color:#38bdf8; text-decoration:none;">&larr; Back to Home</a>
        </div>
        {% if msg %}<div style="background:rgba(16,185,129,0.1); border:1px solid #10b981; color:#34d399; padding:12px; border-radius:8px; margin-top:20px;">{{ msg }}</div>{% endif %}
        
        <div style="background:#111827; padding:20px; border-radius:10px; margin-top:20px;">
            <h3>👥 Manage Admins</h3>
            <form method="POST" style="display:flex; gap:10px; margin-bottom:15px;">
                <input type="hidden" name="action" value="add_admin">
                <input type="email" name="admin_email" placeholder="Email" required style="padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px; flex:1;">
                <input type="text" name="admin_username" placeholder="Username" required style="padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px; flex:1;">
                <input type="password" name="admin_password" placeholder="Password" required style="padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px; flex:1;">
                <button type="submit" style="padding:10px 20px; background:#0ea5e9; border:none; font-weight:bold; color:white; border-radius:6px; cursor:pointer;">Add Admin</button>
            </form>
            <ul>
                {% for em, data in admin_data.items() %}
                <li style="margin:8px 0;">{{ em }} ({{ data.username }}) 
                    {% if em != OWNER_EMAIL %}
                    <form method="POST" style="display:inline;">
                        <input type="hidden" name="action" value="remove_admin_email">
                        <input type="hidden" name="remove_email" value="{{ em }}">
                        <button type="submit" style="background:#ef4444; border:none; color:white; padding:3px 8px; border-radius:4px; cursor:pointer; font-size:11px;">Remove</button>
                    </form>
                    {% endif %}
                </li>
                {% endfor %}
            </ul>
        </div>

        <div style="background:#111827; padding:20px; border-radius:10px; margin-top:20px;">
            <h3>🔑 License Management</h3>
            <form method="POST" style="display:flex; gap:10px; margin-bottom:15px;">
                <input type="hidden" name="action" value="add_license">
                <input type="text" name="l_key" placeholder="License Key" required style="padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px;">
                <input type="text" name="l_name" placeholder="Client Name" required style="padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px;">
                <input type="text" name="l_org" placeholder="Org" required style="padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px;">
                <button type="submit" style="padding:10px 20px; background:#0ea5e9; border:none; font-weight:bold; color:white; border-radius:6px; cursor:pointer;">Create License</button>
            </form>
            <table style="width:100%; border-collapse:collapse;">
                <tr><th style="border:1px solid #1e293b; padding:10px; text-align:left;">Key</th><th style="border:1px solid #1e293b; padding:10px; text-align:left;">Client</th><th style="border:1px solid #1e293b; padding:10px; text-align:left;">Action</th></tr>
                {% for k, v in licenses.items() %}
                <tr>
                    <td style="border:1px solid #1e293b; padding:10px;">{{ k }}</td>
                    <td style="border:1px solid #1e293b; padding:10px;">{{ v.name }}</td>
                    <td style="border:1px solid #1e293b; padding:10px;">
                        <form method="POST" style="margin:0;">
                            <input type="hidden" name="action" value="delete_license">
                            <input type="hidden" name="lic_key" value="{{ k }}">
                            <button type="submit" style="background:#ef4444; border:none; color:white; padding:4px 8px; border-radius:4px; cursor:pointer;">Delete</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """, msg=msg, admin_data=admin_data, licenses=licenses)

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
                error_msg = "Incorrect credentials!"
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
                <input type="text" name="lic_key" placeholder="License ID" required style="width:100%; padding:10px; margin:5px 0 12px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                <input type="text" name="c_user" placeholder="Username" required style="width:100%; padding:10px; margin:5px 0 12px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                <input type="password" name="c_pwd" placeholder="Password" required style="width:100%; padding:10px; margin:5px 0 15px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                <button type="submit" style="width:100%; padding:12px; background:#0ea5e9; border:none; color:white; font-weight:bold; border-radius:6px; cursor:pointer;">Login</button>
            </form>
            <br><a href="/" style="color:#38bdf8; font-size:13px; text-decoration:none;">&larr; Home</a>
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
    antivirus_active = session.get(f"av_active_{lic_key}", False)
    test_result = session.get(f"test_result_{lic_key}", None)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "activate_antivirus":
            session[f"av_active_{lic_key}"] = True
            msg_status = "🛡️ Antivirus successfully activated! Test button unlocked."
            antivirus_active = True
        elif action == "run_test":
            if antivirus_active:
                # ডামি ভাইরাস অ্যাটাক সিমুলেশন (অ্যান্টিভাইরাস অন থাকলে ব্লক বা সাকসেস হবে)
                session[f"test_result_{lic_key}"] = "success"
                msg_status = "✅ সাকসেস: অ্যান্টিভাইরাস সফলভাবে ডামি ভাইরাস আক্রমণ প্রতিরোধ করেছে!"
                test_result = "success"
            else:
                session[f"test_result_{lic_key}"] = "failure"
                msg_status = "❌ পরাজয়: অ্যান্টিভাইরাস নিষ্ক্রিয় থাকায় হুমকি প্রতিরোধ করতে ব্যর্থ হয়েছে!"
                test_result = "failure"

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Client Security Dashboard</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; padding:20px;">
        <div style="max-width:650px; margin:0 auto; background:#111827; padding:30px; border-radius:12px; border:1px solid #1e293b;">
            <h2>🛡️ Client Security & Test Dashboard</h2>
            <p>License: <code style="color:#38bdf8;">{{ lic_key }}</code> | Client: <b>{{ v.name }}</b></p>
            
            {% if msg_status %}
            <div style="background:rgba(16,185,129,0.1); border:1px solid #10b981; color:#34d399; padding:12px; border-radius:8px; margin:15px 0;">{{ msg_status }}</div>
            {% endif %}

            <!-- Antivirus Activation Section -->
            <div style="background:#0b1120; border:1px solid #1e293b; padding:20px; border-radius:8px; margin:20px 0; text-align:center;">
                <h4 style="margin:0 0 10px 0; color:#38bdf8;">Device Protection & Antivirus</h4>
                <p style="font-size:13px; color:#94a3b8; margin-bottom:15px;">
                    {% if antivirus_active %}🟢 Antivirus Status: ACTIVE{% else %}🔴 Antivirus Status: INACTIVE{% endif %}
                </p>
                <form method="POST" style="display:inline;">
                    <input type="hidden" name="action" value="activate_antivirus">
                    <button type="submit" style="background:#10b981; color:white; padding:10px 20px; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">
                        {% if not antivirus_active %}Activate Antivirus{% else %}Re-Sync Antivirus{% endif %}
                    </button>
                </form>
            </div>

            <!-- Virus Attack Test Section -->
            <div style="background:#0b1120; border:1px solid #1e293b; padding:20px; border-radius:8px; margin:20px 0; text-align:center;">
                <h4 style="margin:0 0 10px 0; color:#38bdf8;">Simulate Virus Attack Test</h4>
                <p style="font-size:13px; color:#94a3b8; margin-bottom:15px;">
                    {% if antivirus_active %}Test button is unlocked. Click below to test your security defence.{% else %}🔒 Test button is locked. Please activate antivirus first to unlock.{% endif %}
                </p>
                <form method="POST">
                    <input type="hidden" name="action" value="run_test">
                    <button type="submit" {% if not antivirus_active %}disabled style="background:#334155; color:#94a3b8; cursor:not-allowed;"{% else %}style="background:#0ea5e9; color:white; cursor:pointer;"{% endif %} padding:12px 24px; border:none; border-radius:6px; font-weight:bold; font-size:14px;">
                        🚀 Run Test Attack
                    </button>
                </form>
            </div>

            <br><a href="/" style="color:#ef4444; font-size:13px; font-weight:bold; text-decoration:none;">Log Out / Home</a>
        </div>
    </body>
    </html>
    """, lic_key=lic_key, v=v, antivirus_active=antivirus_active, msg_status=msg_status, test_result=test_result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
