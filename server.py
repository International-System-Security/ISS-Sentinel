from datetime import datetime, timedelta
import os
from flask import Flask, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = "iss_enterprise_security_secret_key_v12"

USER_FILE = "users.txt"
POST_FILE = "posts.txt"
INQUIRY_FILE = "inquiries.txt"
TICKET_FILE = "tickets.txt"
LICENSE_FILE = "licenses.txt"
ADMIN_LIST_FILE = "admins.txt"

OWNER_EMAIL = "iss@owner.com"

# Exact Verified Blue Badge SVG for Admins
ADMIN_BADGE_SVG = '''
<svg width="16" height="16" viewBox="0 0 24 24" fill="#0ea5e9" style="vertical-align: middle; margin-left: 4px;" title="Verified Admin">
    <path d="M12 2L14.34 3.73L17.25 3.5L18.77 6.04L21.5 7.15L21.57 10.12L23.75 12.12L22.12 14.75L22.5 17.75L19.75 19L18.38 21.62L15.5 21.37L13.38 23.25L10.62 22.25L8.12 23.37L6.38 21.12L3.62 20.37L3.12 17.5L0.87 15.62L2.12 12.87L0.87 10.12L3.12 8.25L3.87 5.5L6.62 5.12L8.5 2.87L11.25 3.87L12 2Z" fill="#0ea5e9"/>
    <path d="M9 16.2L4.8 12L6.2 10.6L9 13.4L17.8 4.6L19.2 6L9 16.2Z" fill="white"/>
</svg>
'''

# Trusted Black Badge SVG for Trusted Members selected by Admin
TRUSTED_BLACK_BADGE_SVG = '''
<svg width="16" height="16" viewBox="0 0 24 24" fill="#000000" style="vertical-align: middle; margin-left: 4px;" title="Trusted Member">
    <path d="M12 2L14.34 3.73L17.25 3.5L18.77 6.04L21.5 7.15L21.57 10.12L23.75 12.12L22.12 14.75L22.5 17.75L19.75 19L18.38 21.62L15.5 21.37L13.38 23.25L10.62 22.25L8.12 23.37L6.38 21.12L3.62 20.37L3.12 17.5L0.87 15.62L2.12 12.87L0.87 10.12L3.12 8.25L3.87 5.5L6.62 5.12L8.5 2.87L11.25 3.87L12 2Z" fill="#1e293b" stroke="#38bdf8" stroke-width="1"/>
    <path d="M9 16.2L4.8 12L6.2 10.6L9 13.4L17.8 4.6L19.2 6L9 16.2Z" fill="#38bdf8"/>
</svg>
'''

def load_admin_emails():
    admins = [OWNER_EMAIL, "admin@iss.com"]
    if os.path.exists(ADMIN_LIST_FILE):
        with open(ADMIN_LIST_FILE, "r") as f:
            for line in f:
                em = line.strip()
                if em and em not in admins:
                    admins.append(em)
    return admins

def save_admin_email(email):
    admins = load_admin_emails()
    if email not in admins:
        admins.append(email)
        with open(ADMIN_LIST_FILE, "w") as f:
            for ad in admins:
                if ad != OWNER_EMAIL and ad != "admin@iss.com":
                    f.write(ad + "\n")

def remove_admin_email(email):
    admins = load_admin_emails()
    if email in admins and email != OWNER_EMAIL and email != "admin@iss.com":
        admins.remove(email)
        with open(ADMIN_LIST_FILE, "w") as f:
            for ad in admins:
                if ad != OWNER_EMAIL and ad != "admin@iss.com":
                    f.write(ad + "\n")

def load_users():
    users = {}
    admin_emails = load_admin_emails()
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|||")
                if len(parts) >= 8:
                    uname = parts[0].strip()
                    email = parts[1].strip()
                    # Auto assign admin role if email is in admin list
                    role = "Admin" if email in admin_emails else parts[3].strip()
                    verified = True if role == "Admin" else parts[5].strip() == "True"
                    users[uname] = {
                        "email": email, "password": parts[2].strip(),
                        "role": role, "pic": parts[4].strip(),
                        "verified": verified, "trusted": parts[6].strip() == "True",
                        "last_active": parts[7].strip()
                    }
                elif len(parts) >= 6:
                    uname = parts[0].strip()
                    email = parts[1].strip()
                    role = "Admin" if email in admin_emails else parts[3].strip()
                    verified = True if role == "Admin" else parts[5].strip() == "True"
                    users[uname] = {
                        "email": email, "password": parts[2].strip(),
                        "role": role, "pic": parts[4].strip(),
                        "verified": verified, "trusted": False,
                        "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
    if "admin" not in users:
        users["admin"] = {
            "email": OWNER_EMAIL, "password": "admin", "role": "Admin",
            "pic": "https://i.imgur.com/6VBx3io.png", "verified": True, "trusted": False,
            "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    return users

def save_all_users(users_dict):
    with open(USER_FILE, "w") as f:
        for uname, data in users_dict.items():
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
                elif len(parts) >= 6:
                    licenses[parts[0].strip()] = {
                        "name": parts[1].strip(), "org": parts[2].strip(), "expiry": parts[3].strip(),
                        "max": parts[4].strip(), "plan": parts[5].strip(),
                        "client_user": "admin", "client_pwd": "admin"
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
            img = request.form.get("img")
            if content:
                save_post(session["username"], content, img)
                return redirect(url_for("home"))

    current_user = session.get("username")
    user_data = users.get(current_user) if current_user else None

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ISS Cloud Security & Social Platform</title>
        <style>
            :root {{
                --bg-primary: #060913; --bg-secondary: #0b1120; --bg-card: #111827;
                --accent-blue: #0ea5e9; --accent-hover: #0284c7; --text-main: #f8fafc;
                --text-muted: #94a3b8; --border-color: #1e293b;
            }}
            body {{ font-family: 'Segoe UI', system-ui, sans-serif; background-color: var(--bg-primary); color: var(--text-main); margin: 0; padding: 0; }}
            .navbar {{ display: flex; justify-content: space-between; align-items: center; padding: 18px 6%; border-bottom: 1px solid var(--border-color); background: rgba(6, 9, 19, 0.95); position: sticky; top: 0; z-index: 1000; }}
            .logo {{ font-size: 20px; font-weight: 800; color: var(--text-main); text-decoration: none; }}
            .logo span {{ color: var(--accent-blue); }}
            .nav-links {{ display: flex; gap: 20px; align-items: center; }}
            .nav-links a {{ color: var(--text-muted); text-decoration: none; font-size: 14px; font-weight: 500; }}
            .nav-links a:hover {{ color: var(--accent-blue); }}
            .container {{ max-width: 900px; margin: 30px auto; padding: 0 15px; }}
            .card {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 25px; margin-bottom: 25px; box-shadow: 0 8px 20px rgba(0,0,0,0.3); }}
            input, textarea {{ width: 100%; padding: 12px; margin: 8px 0 14px 0; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 6px; color: white; box-sizing: border-box; }}
            button {{ background: var(--accent-blue); color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; }}
            button:hover {{ background: var(--accent-hover); }}
            .avatar {{ width: 45px; height: 45px; border-radius: 50%; object-fit: cover; border: 2px solid var(--accent-blue); }}
        </style>
    </head>
    <body>
        <nav class="navbar">
            <a href="/" class="logo">🛡️ ISS <span>PLATFORM</span></a>
            <div class="nav-links">
                <a href="#social">ISS Social</a>
                <a href="#contact">Contact Us</a>
                <a href="#tickets">Support Tickets</a>
                <a href="/my-profile">My Profile</a>
                <a href="/client-login">Client Portal</a>
            </div>
        </nav>

        <div class="container">
            <div class="card" style="text-align: center; padding: 50px 20px;">
                <h1>Next-Gen Cloud Security & Social Hub</h1>
                <p style="color: var(--text-muted); max-width: 650px; margin: 0 auto 20px auto;">Connect with professionals, manage security licenses, and communicate securely through private tickets.</p>
                {'<p style="color: #34d399; font-weight: bold;">Welcome back, ' + current_user + (ADMIN_BADGE_SVG if user_data['role'] == 'Admin' else (TRUSTED_BLACK_BADGE_SVG if user_data.get('trusted') else '')) + '</p>' if current_user else '<a href="/my-profile" style="background:var(--accent-blue); color:white; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:bold;">Login / Register (Social Join)</a>'}
            </div>

            <!-- ISS Social Feed -->
            <div class="card" id="social">
                <h3>🌐 ISS Social Feed</h3>
                <p style="font-size: 13px; color: var(--text-muted);">Share your thoughts, updates, and images with the community.</p>
                
                <form method="GET" action="/" style="margin-bottom: 20px; display: flex; gap: 10px;">
                    <input type="text" name="search" placeholder="Search user by username..." value="{search_query}" style="margin:0;">
                    <button type="submit" style="width: auto;">Search</button>
                </form>

                {f'''
                <div style="background:var(--bg-secondary); padding:15px; border-radius:8px; margin-bottom:20px;">
                    <form method="POST">
                        <input type="hidden" name="form_type" value="create_post">
                        <textarea name="content" placeholder="What's on your mind?" rows="3" required style="margin:0 0 10px 0;"></textarea>
                        <input type="text" name="img" placeholder="Optional Image URL (https://...)" style="margin:0 0 10px 0;">
                        <button type="submit">Post to ISS Social</button>
                    </form>
                </div>
                ''' if current_user else '<p style="font-size:13px; color:#94a3b8;">Please <a href="/my-profile" style="color:#0ea5e9;">login via My Profile</a> to join social and create posts.</p>'}

                <div>
                    {"".join([f'''
                    <div style="background:var(--bg-secondary); padding:15px; border-radius:8px; margin-bottom:15px; border:1px solid var(--border-color);">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                            <b>{p['author']}</b> {ADMIN_BADGE_SVG if users.get(p['author'], {}).get('role') == 'Admin' else (TRUSTED_BLACK_BADGE_SVG if users.get(p['author'], {}).get('trusted') else '')}
                            <span style="font-size:11px; color:var(--text-muted);">{p['date']}</span>
                        </div>
                        <p style="margin:0 0 10px 0; font-size:14px;">{p['content']}</p>
                        {f'<img src="{p["img"]}" style="max-width:100%; border-radius:6px; max-height:300px; object-fit:cover;" />' if p['img'] else ''}
                    </div>
                    ''' for p in posts]) if posts else '<p style="color:var(--text-muted);">No posts shared yet.</p>'}
                </div>

                <h4 style="margin-top:30px;">Community Directory</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px;">
                    {"".join([f'''
                    <div style="background:var(--bg-secondary); padding:10px; border-radius:6px; display:flex; align-items:center; gap:10px;">
                        <img src="{d['pic']}" class="avatar" style="width:35px; height:35px;" />
                        <div>
                            <div style="font-size:13px; font-weight:bold;"><a href="/my-profile?user={u}" style="color:white; text-decoration:none;">{u}</a> {ADMIN_BADGE_SVG if d['role'] == 'Admin' else (TRUSTED_BLACK_BADGE_SVG if d.get('trusted') else '')}</div>
                            <div style="font-size:11px; color:var(--text-muted);">{d['role']}</div>
                        </div>
                    </div>
                    ''' for u, d in filtered_users.items()])}
                </div>
            </div>

            <!-- Contact Us & Tickets -->
            <div class="card" id="contact">
                <h3>📞 Contact Us & Service Application</h3>
                <p style="font-size: 13px; color: var(--text-muted);">Apply to get our enterprise security features and license solutions.</p>
                {f'<div style="background: rgba(16,185,129,0.1); border: 1px solid #10b981; color: #34d399; padding: 10px; border-radius: 6px; font-size: 13px; margin-bottom: 15px;">{inquiry_msg}</div>' if inquiry_msg else ''}
                <form method="POST">
                    <input type="hidden" name="form_type" value="inquiry">
                    <input type="text" name="name" placeholder="Your Full Name" required>
                    <input type="email" name="email" placeholder="Email Address" required>
                    <input type="text" name="social" placeholder="Social Media Profile Link" required>
                    <button type="submit">Submit Application</button>
                </form>
            </div>

            <div class="card" id="tickets">
                <h3>💬 Support Tickets (Messenger)</h3>
                <p style="font-size: 13px; color: var(--text-muted);">Have questions or need assistance? Open a support ticket to chat privately with admins.</p>
                {f'<a href="/ticket-chat" style="display:inline-block; background:var(--accent-blue); color:white; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:bold; margin-top:10px;">Open My Support Chat</a>' if current_user else '<p style="font-size:13px; color:#fca5a5;">Please login via My Profile to access support tickets.</p>'}
            </div>
        </div>
    </body>
    </html>
    """)

# --- MY PROFILE (Login & Register with Username, Email, Password) ---
@app.route("/my-profile", methods=["GET", "POST"])
def my_profile():
    users = load_users()
    admin_emails = load_admin_emails()
    msg = ""
    error = ""

    if request.method == "POST":
        action = request.form.get("action")
        if action == "register":
            uname = request.form.get("username").strip()
            email = request.form.get("email").strip()
            pwd = request.form.get("password").strip()
            pic = request.form.get("pic").strip() or "https://i.imgur.com/6VBx3io.png"

            if uname in users:
                error = "Username already exists!"
            else:
                role = "Admin" if email in admin_emails else "User"
                is_verified = True if role == "Admin" else False
                
                users[uname] = {
                    "email": email, "password": pwd, "role": role, "pic": pic,
                    "verified": is_verified, "trusted": False,
                    "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                save_all_users(users)
                session["username"] = uname
                if role == "Admin":
                    return redirect(url_for("admin_panel"))
                return redirect(url_for("my_profile"))

        elif action == "login":
            uname = request.form.get("username").strip()
            pwd = request.form.get("password").strip()

            if uname in users and users[uname]["password"] == pwd:
                session["username"] = uname
                users[uname]["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_all_users(users)
                
                if users[uname]["role"] == "Admin":
                    return redirect(url_for("admin_panel"))
                return redirect(url_for("my_profile"))
            else:
                error = "Invalid username or password!"

        elif action == "update_pic" and "username" in session:
            new_pic = request.form.get("pic").strip()
            if new_pic:
                users[session["username"]]["pic"] = new_pic
                save_all_users(users)
                msg = "✅ Profile picture updated successfully!"

        elif action == "toggle_trusted" and "username" in session:
            current_user = session["username"]
            if users.get(current_user, {}).get("role") == "Admin":
                target_user = request.form.get("target_user")
                if target_user in users:
                    users[target_user]["trusted"] = not users[target_user].get("trusted", False)
                    save_all_users(users)
                    msg = f"✅ Trusted Black Badge status updated for '{target_user}'!"

    current_user = session.get("username")
    user_data = users.get(current_user) if current_user else None
    
    view_user_name = request.args.get("user", current_user)
    view_data = users.get(view_user_name)

    is_viewer_admin = user_data and user_data['role'] == 'Admin'

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>My Profile - ISS Platform</title>
        <style>
            :root {{
                --bg-primary: #060913; --bg-secondary: #0b1120; --bg-card: #111827;
                --accent-blue: #0ea5e9; --accent-hover: #0284c7; --text-main: #f8fafc;
                --text-muted: #94a3b8; --border-color: #1e293b;
            }}
            body {{ font-family: 'Segoe UI', system-ui, sans-serif; background-color: var(--bg-primary); color: var(--text-main); margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 30px auto; background: var(--bg-card); padding: 35px; border-radius: 12px; border: 1px solid var(--border-color); box-shadow: 0 10px 25px rgba(0,0,0,0.4); }}
            input, select {{ width: 100%; padding: 12px; margin: 8px 0 16px 0; background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 6px; color: white; box-sizing: border-box; }}
            button {{ width: 100%; padding: 12px; background: var(--accent-blue); border: none; color: white; font-weight: bold; border-radius: 6px; cursor: pointer; }}
            button:hover {{ background: var(--accent-hover); }}
            .avatar-lg {{ width: 90px; height: 90px; border-radius: 50%; object-fit: cover; border: 3px solid var(--accent-blue); }}
        </style>
    </head>
    <body>
        <div style="text-align:center; margin-bottom:20px;">
            <a href="/" style="color:var(--accent-blue); text-decoration:none; font-weight:bold;">&larr; Back to Home / Social Feed</a>
        </div>
        <div class="container">
            {f'<div style="color:#ef4444; font-size:13px; margin-bottom:15px; padding:10px; background:rgba(239,68,68,0.1); border-radius:6px;">{error}</div>' if error else ''}
            {f'<div style="color:#34d399; font-size:13px; margin-bottom:15px; padding:10px; background:rgba(16,185,129,0.1); border-radius:6px;">{msg}</div>' if msg else ''}

            {f'''
            <div style="text-align:center;">
                <img src="{view_data['pic']}" class="avatar-lg" />
                <h2 style="margin:15px 0 5px 0;">{view_user_name} {ADMIN_BADGE_SVG if view_data['role'] == 'Admin' else (TRUSTED_BLACK_BADGE_SVG if view_data.get('trusted') else '')}</h2>
                <p style="color:var(--text-muted); font-size:14px; margin:0 0 20px 0;">Email: {view_data['email']} | Role: <b>{view_data['role']}</b></p>
            </div>

            {f'''
            <div style="background:var(--bg-secondary); padding:20px; border-radius:8px; margin-top:20px;">
                <h4>Update Profile Picture</h4>
                <form method="POST">
                    <input type="hidden" name="action" value="update_pic">
                    <input type="text" name="pic" placeholder="New Image URL (https://...)" required>
                    <button type="submit">Update Picture</button>
                </form>
            </div>
            ''' if view_user_name == current_user else ''}

            <!-- Admin Add to Trusted Button -->
            {f'''
            <div style="background:var(--bg-secondary); padding:20px; border-radius:8px; margin-top:20px; border: 1px dashed var(--accent-blue);">
                <h4 style="color:var(--accent-blue); margin-top:0;">Admin Trust Control</h4>
                <p style="font-size:12px; color:var(--text-muted);">As an admin, you can assign or remove the Trusted Black Badge for this profile.</p>
                <form method="POST">
                    <input type="hidden" name="action" value="toggle_trusted">
                    <input type="hidden" name="target_user" value="{view_user_name}">
                    <button type="submit" style="background:{'#ef4444' if view_data.get('trusted') else '#10b981'};">
                        {'Remove Trusted Black Badge' if view_data.get('trusted') else 'Add to Trusted (Black Badge)'}
                    </button>
                </form>
            </div>
            ''' if is_viewer_admin and view_data['role'] != 'Admin' else ''}

            <div style="text-align:center; margin-top:25px;">
                <a href="/logout" style="color:#ef4444; font-weight:bold; font-size:14px; text-decoration:none;">Log Out Account</a>
                {f'<br><br><a href="/admin" style="color:#38bdf8; font-weight:bold; text-decoration:none;">Go to Admin Control Panel &rarr;</a>' if user_data['role'] == 'Admin' else ''}
            </div>
            ''' if current_user else '''
            <div style="display:flex; justify-content:center; gap:10px; margin-bottom:20px;">
                <button onclick="document.getElementById('login-form').style.display='block'; document.getElementById('reg-form').style.display='none';" style="background:#1e293b;">Login</button>
                <button onclick="document.getElementById('reg-form').style.display='block'; document.getElementById('login-form').style.display='none';" style="background:#1e293b;">Register</button>
            </div>

            <!-- Simple Login Form (Username, Password) -->
            <div id="login-form">
                <h3>Account Login</h3>
                <p style="font-size:12px; color:var(--text-muted);">Owner Login: <b>admin / admin</b> ({OWNER_EMAIL})</p>
                <form method="POST">
                    <input type="hidden" name="action" value="login">
                    <label style="font-size:12px; color:var(--text-muted);">Username</label>
                    <input type="text" name="username" value="admin" required>
                    <label style="font-size:12px; color:var(--text-muted);">Password</label>
                    <input type="password" name="password" value="admin" required>
                    <button type="submit">Login</button>
                </form>
            </div>

            <!-- Simple Register Form (Username, Email, Password) -->
            <div id="reg-form" style="display:none;">
                <h3>Join ISS Social (Register)</h3>
                <form method="POST">
                    <input type="hidden" name="action" value="register">
                    <label style="font-size:12px; color:var(--text-muted);">Username</label>
                    <input type="text" name="username" required>
                    <label style="font-size:12px; color:var(--text-muted);">Email Address</label>
                    <input type="email" name="email" required>
                    <label style="font-size:12px; color:var(--text-muted);">Password</label>
                    <input type="password" name="password" required>
                    <label style="font-size:12px; color:var(--text-muted);">Profile Picture URL (Optional)</label>
                    <input type="text" name="pic" placeholder="https://...">
                    <button type="submit">Register Account</button>
                </form>
            </div>
            '''}
        </div>
    </body>
    </html>
    """)

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
        if action == "add_admin_email":
            new_em = request.form.get("new_admin_email", "").strip()
            if new_em:
                save_admin_email(new_em)
                msg = f"✅ Admin email '{new_em}' authorized successfully!"
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
            l_plan = request.form.get("l_plan", "Enterprise")
            l_user = request.form.get("l_user", "admin")
            l_pwd = request.form.get("l_pwd", "admin")
            
            licenses = load_licenses()
            licenses[l_key] = {
                "name": l_name, "org": l_org, "expiry": l_expiry,
                "max": "5", "plan": l_plan, "client_user": l_user, "client_pwd": l_pwd
            }
            save_licenses(licenses)
            msg = f"✅ License '{l_key}' created successfully with plan '{l_plan}'!"

    licenses = load_licenses()
    admin_emails = load_admin_emails()
    inquiries = []
    if os.path.exists(INQUIRY_FILE):
        with open(INQUIRY_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) >= 4:
                    inquiries.append({"name": parts[0], "email": parts[1], "social": parts[2], "date": parts[3]})

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Admin Control Panel</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #060913; color: #f8fafc; margin: 0; padding: 20px; }}
            .navbar {{ display: flex; justify-content: space-between; align-items: center; background: #111827; padding: 15px 25px; border-radius: 10px; border: 1px solid #1e293b; margin-bottom: 25px; }}
            .box {{ background: #111827; padding: 25px; border-radius: 12px; border: 1px solid #1e293b; margin-bottom: 25px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #1e293b; padding: 12px; text-align: left; font-size: 13px; }}
            th {{ background: #1a2234; color: #38bdf8; }}
            input, select, button {{ padding: 10px; margin: 5px 0; background: #060913; border: 1px solid #334155; color: white; border-radius: 6px; box-sizing: border-box; }}
            button {{ background: #0ea5e9; font-weight: bold; cursor: pointer; border: none; }}
        </style>
    </head>
    <body>
        <div class="navbar">
            <h2>🛡️ Admin Center ({current_user} {ADMIN_BADGE_SVG})</h2>
            <a href="/" style="color: #38bdf8; text-decoration: none; font-weight: bold;">&larr; Back to Home</a>
        </div>

        {f'<div style="background: rgba(16,185,129,0.1); border: 1px solid #10b981; color: #34d399; padding: 12px; border-radius: 8px; margin-bottom: 20px;">{msg}</div>' if msg else ''}

        <!-- Add Admin Email Section -->
        <div class="box">
            <h3>👥 Add New Admin Email</h3>
            <p style="font-size:13px; color:#94a3b8;">Enter an email address below to grant admin privileges. When that user registers or logs in with this email, they will automatically become an Admin.</p>
            <form method="POST" style="display:flex; gap:10px; margin-bottom:15px;">
                <input type="hidden" name="action" value="add_admin_email">
                <input type="email" name="new_admin_email" placeholder="Enter admin email (e.g. partner@gmail.com)" required style="flex:1; margin:0;">
                <button type="submit" style="width:auto; margin:0;">Add Admin Email</button>
            </form>
            <ul>
                {"".join([f'<li style="font-size:13px; margin:5px 0;">{em} ' + (f'<form method="POST" style="display:inline; margin-left:10px;"><input type="hidden" name="action" value="remove_admin_email"><input type="hidden" name="remove_email" value="{em}"><button type="submit" style="background:#ef4444; padding:2px 8px; font-size:11px;">Remove</button></form>' if em != OWNER_EMAIL and em != "admin@iss.com" else '<span style="color:#38bdf8; font-size:11px;">(Owner / Master)</span>') + '</li>' for em in admin_emails])}
            </ul>
        </div>

        <div class="box">
            <h3>💬 Support Ticket Control Center</h3>
            <a href="/admin/tickets" style="display:inline-block; background:#0284c7; color:white; padding:10px 18px; text-decoration:none; border-radius:6px; font-weight:bold; font-size:13px;">Open All Client Support Tickets (Messenger)</a>
        </div>

        <div class="box">
            <h3>🔑 License Management (Create with Plan Tier & Expiry)</h3>
            <form method="POST" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap:10px; margin-bottom:15px;">
                <input type="hidden" name="action" value="add_license">
                <input type="text" name="l_key" placeholder="License Key (e.g. iss-999)" required>
                <input type="text" name="l_name" placeholder="Client Name" required>
                <input type="text" name="l_org" placeholder="Organization" required>
                <select name="l_plan">
                    <option value="Enterprise">Enterprise Plan</option>
                    <option value="Professional">Professional Plan</option>
                    <option value="Standard">Standard Plan</option>
                </select>
                <input type="text" name="l_expiry" placeholder="Expiry (YYYY-MM-DD)" value="2027-01-01" required>
                <input type="text" name="l_user" placeholder="Client User" value="admin" required>
                <input type="text" name="l_pwd" placeholder="Client Pass" value="admin" required>
                <button type="submit" style="grid-column: 1 / -1;">Create License</button>
            </form>
            <table>
                <tr><th>Key</th><th>Client</th><th>Org</th><th>Plan Tier</th><th>Expiry</th><th>Client Credentials</th><th>Action</th></tr>
                {"".join([f'<tr><td><code>{k}</code></td><td>{v["name"]}</td><td>{v["org"]}</td><td><b>{v["plan"]}</b></td><td>{v["expiry"]}</td><td><code>{v.get("client_user","admin")} / {v.get("client_pwd","admin")}</code></td><td><form method="POST" style="margin:0;"><input type="hidden" name="action" value="delete_license"><input type="hidden" name="lic_key" value="{k}"><button type="submit" style="background:#ef4444; padding:4px 8px; font-size:11px;">Delete / Block</button></form></td></tr>' for k, v in licenses.items()]) if licenses else '<tr><td colspan="7" style="text-align:center; color:#94a3b8;">No licenses found.</td></tr>'}
            </table>
        </div>

        <div class="box">
            <h3>📋 'Contact Us' Service Applications</h3>
            <table>
                <tr><th>Name</th><th>Email</th><th>Social Link</th><th>Date</th></tr>
                {"".join([f'<tr><td>{i["name"]}</td><td>{i["email"]}</td><td><a href="{i["social"]}" target="_blank" style="color:#38bdf8;">Profile</a></td><td>{i["date"]}</td></tr>' for i in inquiries]) if inquiries else '<tr><td colspan="4" style="text-align:center; color:#94a3b8;">No applications.</td></tr>'}
            </table>
        </div>
    </body>
    </html>
    """)

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
            save_ticket_msg(t_id, tickets.get(t_id, {}).get("user", "client"), f"Admin ({current_user} 👑✔)", reply_text)
            return redirect(url_for('admin_tickets', tid=t_id))

    ticket_list_html = "".join([f'<a href="/admin/tickets?tid={tid}" style="display:block; padding:10px; margin:6px 0; background:#1e293b; color:#38bdf8; text-decoration:none; border-radius:6px; font-size:13px;">Ticket: {tid} (User: {data["user"]})</a>' for tid, data in tickets.items()])
    
    chat_box_html = "<p style='color:#94a3b8;'>Select a ticket from the left list to view and reply.</p>"
    if selected_tid and selected_tid in tickets:
        t_data = tickets[selected_tid]
        msgs_html = "".join([f"<div style='background:#060913; padding:8px 12px; margin:6px 0; border-radius:6px; font-size:13px;'>{m}</div>" for m in t_data["messages"]])
        chat_box_html = f"""
        <h4>Messenger Chat for Ticket: {selected_tid}</h4>
        <div style="background:#060913; height:260px; overflow-y:auto; border:1px solid #1e293b; padding:10px; border-radius:6px; margin-bottom:12px;">{msgs_html}</div>
        <form method="POST">
            <input type="hidden" name="tid" value="{selected_tid}">
            <input type="text" name="reply" placeholder="Type reply as admin..." required style="width:78%; padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px;">
            <button type="submit" style="width:20%; padding:10px; background:#0ea5e9; border:none; font-weight:bold; color:white; border-radius:6px; cursor:pointer;">Send</button>
        </form>
        """

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Admin Support Center</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; padding:20px;">
        <h2>💬 Admin Live Ticket Messenger (All Chats Visible to All Admins)</h2>
        <a href="/admin" style="color:#38bdf8; font-size:13px; text-decoration:none;">&larr; Back to Admin Panel</a>
        <div style="display:grid; grid-template-columns: 320px 1fr; gap:20px; margin-top:20px;">
            <div style="background:#111827; padding:15px; border-radius:10px; border:1px solid #1e293b;">
                <h4>All Tickets</h4>
                {ticket_list_html if ticket_list_html else '<p style="color:#94a3b8; font-size:13px;">No tickets found.</p>'}
            </div>
            <div style="background:#111827; padding:15px; border-radius:10px; border:1px solid #1e293b;">
                {chat_box_html}
            </div>
        </div>
    </body>
    </html>
    """)

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
                error_msg = "Incorrect Client Username or Password for this License ID!"
        else:
            error_msg = "Invalid or Blocked License ID!"

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Client Portal Login</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <div style="background:#111827; padding:35px; border-radius:12px; width:360px; border:1px solid #1e293b;">
            <h2>Client Portal Login</h2>
            <p style="font-size:13px; color:#94a3b8;">Enter License ID, Username & Password.</p>
            {f'<div style="color:#fca5a5; font-size:13px; margin-bottom:10px;">{error_msg}</div>' if error_msg else ''}
            <form method="POST">
                <label style="font-size:12px; color:#94a3b8;">License ID</label>
                <input type="text" name="lic_key" placeholder="Enter License ID" required style="width:100%; padding:10px; margin:5px 0 12px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                <label style="font-size:12px; color:#94a3b8;">Username</label>
                <input type="text" name="c_user" value="admin" required style="width:100%; padding:10px; margin:5px 0 12px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                <label style="font-size:12px; color:#94a3b8;">Password</label>
                <input type="password" name="c_pwd" value="admin" required style="width:100%; padding:10px; margin:5px 0 15px 0; background:#060913; border:1px solid #334155; color:white; border-radius:6px; box-sizing:border-box;">
                <button type="submit" style="width:100%; padding:12px; background:#0ea5e9; border:none; color:white; font-weight:bold; border-radius:6px; cursor:pointer;">Login Client Portal</button>
            </form>
            <br><a href="/" style="color:#38bdf8; font-size:13px; text-decoration:none;">&larr; Return to Home</a>
        </div>
    </body>
    </html>
    """)

@app.route("/client-dashboard", methods=["GET", "POST"])
def client_dashboard():
    lic_key = session.get("client_license")
    licenses = load_licenses()
    if not lic_key or lic_key not in licenses:
        return redirect(url_for("client_login"))

    v = licenses[lic_key]
    msg_status = ""
    if request.method == "POST":
        user_msg = request.form.get("message")
        if user_msg:
            save_ticket_msg(f"TICK-{lic_key}", lic_key, f"Client ({v['name']})", user_msg)
            msg_status = "✅ Message sent to support!"

    tickets = load_tickets()
    my_msgs = tickets.get(f"TICK-{lic_key}", {}).get("messages", [])
    chat_history = "".join([f"<div style='background:#111827; padding:8px 12px; margin:6px 0; border-radius:6px; font-size:13px;'>{m}</div>" for m in my_msgs])

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Client Security Dashboard</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; padding:20px;">
        <div style="max-width:650px; margin:0 auto; background:#111827; padding:30px; border-radius:12px; border:1px solid #1e293b;">
            <h2>🛡️ Client Security Dashboard</h2>
            <p>License Key: <code style="color:#38bdf8;">{lic_key}</code> | Organization: <b>{v['org']} ({v['name']})</b></p>
            <p>Plan Tier: <b>{v['plan']}</b> | Expiry: {v['expiry']}</p>
            <hr style="border-color:#1e293b; margin:20px 0;">
            
            <h3>💬 Private Support Messenger</h3>
            {f'<div style="background:rgba(16,185,129,0.1); border:1px solid #10b981; color:#34d399; padding:10px; border-radius:6px; font-size:13px; margin-bottom:12px;">{msg_status}</div>' if msg_status else ''}
            
            <div style="background:#060913; height:220px; overflow-y:auto; border:1px solid #1e293b; padding:10px; border-radius:6px; margin-bottom:12px;">
                {chat_history if chat_history else '<p style="color:#94a3b8; font-size:13px;">No messages yet. Send a message to contact admins.</p>'}
            </div>
            
            <form method="POST">
                <input type="text" name="message" placeholder="Type your message..." required style="width:78%; padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px;">
                <button type="submit" style="width:20%; padding:10px; background:#0ea5e9; border:none; font-weight:bold; color:white; border-radius:6px; cursor:pointer;">Send</button>
            </form>
            
            <br><a href="/" style="color:#ef4444; font-size:13px; font-weight:bold; text-decoration:none;">Logout / Return Home</a>
        </div>
    </body>
    </html>
    """)

# --- Dedicated Ticket Chat Route for ISS Social Users ---
@app.route("/ticket-chat", methods=["GET", "POST"])
def ticket_chat():
    current_user = session.get("username")
    if not current_user:
        return redirect(url_for("my_profile"))

    t_id = f"USER-TICK-{current_user}"
    msg_status = ""
    if request.method == "POST":
        user_msg = request.form.get("message")
        if user_msg:
            save_ticket_msg(t_id, current_user, f"User ({current_user})", user_msg)
            msg_status = "✅ Sent!"

    tickets = load_tickets()
    my_msgs = tickets.get(t_id, {}).get("messages", [])
    chat_history = "".join([f"<div style='background:#111827; padding:8px 12px; margin:6px 0; border-radius:6px; font-size:13px;'>{m}</div>" for m in my_msgs])

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Support Ticket Chat</title></head>
    <body style="font-family:'Segoe UI'; background:#060913; color:white; padding:20px;">
        <div style="max-width:650px; margin:30px auto; background:#111827; padding:30px; border-radius:12px; border:1px solid #1e293b;">
            <h2>💬 Support Ticket Chat ({current_user})</h2>
            <p style="font-size:13px; color:#94a3b8;">Only you and the administrators can view this private conversation.</p>
            <a href="/" style="color:#38bdf8; font-size:13px; text-decoration:none;">&larr; Return Home</a>
            <hr style="border-color:#1e293b; margin:15px 0;">

            <div style="background:#060913; height:240px; overflow-y:auto; border:1px solid #1e293b; padding:10px; border-radius:6px; margin-bottom:12px;">
                {chat_history if chat_history else '<p style="color:#94a3b8; font-size:13px;">No messages in this ticket yet.</p>'}
            </div>

            <form method="POST">
                <input type="text" name="message" placeholder="Type message to admin..." required style="width:78%; padding:10px; background:#060913; border:1px solid #334155; color:white; border-radius:6px;">
                <button type="submit" style="width:20%; padding:10px; background:#0ea5e9; border:none; font-weight:bold; color:white; border-radius:6px; cursor:pointer;">Send</button>
            </form>
        </div>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
