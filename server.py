import os
from flask import Flask, render_template_string, request, redirect, url_for, session
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "iss_enterprise_security_secret_key_v18"

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

USER_FILE = "users.txt"

def load_users():
    users = {}
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|||")
                if len(parts) >= 2:
                    uname = parts[0].strip()
                    email = parts[1].strip() if len(parts) > 1 else ""
                    password = parts[2].strip() if len(parts) > 2 else ""
                    role = parts[3].strip() if len(parts) > 3 else "user"
                    pic = parts[4].strip() if len(parts) > 4 else "https://i.imgur.com/6VBx3io.png"
                    verified = parts[5].strip() == "True" if len(parts) > 5 else True
                    
                    users[uname] = {
                        "email": email, 
                        "password": password,
                        "role": role, 
                        "pic": pic,
                        "verified": verified
                    }
    return users

def save_all_users(users_dict):
    with open(USER_FILE, "w") as f:
        for uname, data in users_dict.items():
            f.write(f"{uname}|||{data['email']}|||{data['password']}|||{data['role']}|||{data['pic']}|||{data['verified']}\n")


@app.route("/", methods=["GET", "POST"])
@app.route("/my-profile", methods=["GET", "POST"])
def my_profile():
    users = load_users()
    current_user = session.get("username")
    msg = ""
    error = ""

    if request.method == "POST":
        action = request.form.get("action")
        
        # ১. নতুন অ্যাকাউন্ট রেজিস্টার (প্রথম ইউজার অটো এডমিন হবে)
        if action == "register":
            uname = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            pwd = request.form.get("password", "").strip()

            if not uname or not pwd:
                error = "ইউজারনেম এবং পাসওয়ার্ড দিতে হবে!"
            elif uname in users:
                error = "এই ইউজারনেমটি আগেই ব্যবহার করা হয়েছে!"
            else:
                # যদি ফাইলে কোনো ইউজার না থাকে, তবে প্রথম জন এডমিন হবে
                role = "admin" if len(users) == 0 else "user"

                users[uname] = {
                    "email": email,
                    "password": pwd,
                    "role": role,
                    "pic": "https://i.imgur.com/6VBx3io.png",
                    "verified": True
                }
                save_all_users(users)
                session["username"] = uname
                return redirect(url_for("my_profile"))

        # ২. লগইন হ্যান্ডেল
        elif action == "login":
            uname = request.form.get("username", "").strip()
            pwd = request.form.get("password", "").strip()
            if uname in users and users[uname]["password"] == pwd:
                session["username"] = uname
                return redirect(url_for("my_profile"))
            else:
                error = "ভুল ইউজারনেম বা পাসওয়ার্ড!"

        # ৩. পাসওয়ার্ড ও ইউজারনেম আপডেট
        elif action == "update_credentials" and current_user:
            new_uname = request.form.get("new_username", "").strip()
            new_pwd = request.form.get("new_password", "").strip()

            if current_user in users:
                target_key = current_user
                if new_uname and new_uname != current_user:
                    if new_uname in users:
                        error = "এই ইউজারনেমটি অন্য কেউ ব্যবহার করছে!"
                    else:
                        users[new_uname] = users.pop(current_user)
                        target_key = new_uname
                        session["username"] = target_key

                if new_pwd:
                    users[target_key]["password"] = new_pwd

                save_all_users(users)
                msg = "✅ সফলভাবে আপডেট করা হয়েছে!"

        # ৪. প্রোফাইল ছবি আপলোড
        elif action == "update_pic" and current_user:
            if 'profile_pic_file' in request.files:
                file = request.files['profile_pic_file']
                if file and file.filename != '':
                    filename = secure_filename(f"{current_user}_{int(datetime.now().timestamp())}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    
                    if current_user in users:
                        users[current_user]["pic"] = f"/static/uploads/{filename}"
                        save_all_users(users)
                        msg = "✅ প্রোফাইল ছবি সফলভাবে আপলোড হয়েছে!"
                else:
                    error = "দয়া করে একটি ছবি সিলেক্ট করুন।"

    user_data = users.get(current_user) if current_user else None
    user_role = user_data.get("role", "user") if user_data else ""

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>ISS Profile Settings</title></head>
    <body style="font-family:sans-serif; background:#060913; color:white; padding:30px;">
        <div style="max-width:500px; margin:0 auto; background:#111827; padding:30px; border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.5);">
            <h2>⚙️ ISS Profile & Settings</h2>
            
            {f'<p style="background:#7f1d1d; padding:10px; border-radius:5px; color:#fca5a5;">{error}</p>' if error else ''}
            {f'<p style="background:#065f46; padding:10px; border-radius:5px; color:#6ee7b7;">{msg}</p>' if msg else ''}

            {f'''
            <div style="text-align:center; margin-bottom:20px;">
                <img src="{user_data.get('pic', 'https://i.imgur.com/6VBx3io.png')}" style="width:90px; height:90px; border-radius:50%; object-fit:cover; border:2px solid #0ea5e9;"><br>
                <p>লগইন করা আছে: <b style="color:#38bdf8;">{current_user}</b></p>
                <p>রোল (Role): <span style="background:{"#dc2626" if user_role=="admin" else "#0284c7"}; padding:2px 8px; border-radius:4px; font-size:12px;">{user_role.upper()}</span></p>
            </div>

            <h3>পাসওয়ার্ড বা ইউজারনেম পরিবর্তন</h3>
            <form method="POST">
                <input type="hidden" name="action" value="update_credentials">
                <label>নতুন ইউজারনেম:</label><br>
                <input type="text" name="new_username" value="{current_user}" required style="width:100%; padding:8px; margin:5px 0; background:#1f2937; color:white; border:1px solid #374151;"><br>
                <label>নতুন পাসওয়ার্ড:</label><br>
                <input type="password" name="new_password" placeholder="নতুন পাসওয়ার্ড দিন" required style="width:100%; padding:8px; margin:5px 0; background:#1f2937; color:white; border:1px solid #374151;"><br>
                <button type="submit" style="background:#0ea5e9; color:white; border:none; padding:10px 15px; cursor:pointer; width:100%; border-radius:4px; font-weight:bold;">আপডেট করুন</button>
            </form>

            <h3 style="margin-top:20px;">প্রোফাইল ছবি আপলোড</h3>
            <form method="POST" enctype="multipart/form-data">
                <input type="hidden" name="action" value="update_pic">
                <input type="file" name="profile_pic_file" accept="image/*" required style="margin:5px 0;"><br>
                <button type="submit" style="background:#10b981; color:white; border:none; padding:10px 15px; cursor:pointer; width:100%; border-radius:4px; font-weight:bold;">ছবি আপলোড করুন</button>
            </form>

            <br><div style="text-align:center;"><a href="/logout" style="color:#ef4444; text-decoration:none; font-weight:bold;">লগআউট করুন</a></div>
            ''' if current_user else '''
            <div style="display:flex; gap:20px; margin-top:20px;">
                <div style="flex:1;">
                    <h3>লগইন</h3>
                    <form method="POST">
                        <input type="hidden" name="action" value="login">
                        <label>ইউজারনেম:</label><br>
                        <input type="text" name="username" required style="width:100%; padding:8px; margin:5px 0; background:#1f2937; color:white; border:1px solid #374151;"><br>
                        <label>পাসওয়ার্ড:</label><br>
                        <input type="password" name="password" required style="width:100%; padding:8px; margin:5px 0; background:#1f2937; color:white; border:1px solid #374151;"><br>
                        <button type="submit" style="background:#0ea5e9; color:white; border:none; padding:10px 15px; cursor:pointer; width:100%; border-radius:4px; margin-top:10px;">লগইন</button>
                    </form>
                </div>
                
                <div style="flex:1; border-left:1px solid #374151; padding-left:15px;">
                    <h3>নতুন অ্যাকাউন্ট (প্রথম জন এডমিন হবে)</h3>
                    <form method="POST">
                        <input type="hidden" name="action" value="register">
                        <label>ইউজারনেম:</label><br>
                        <input type="text" name="username" required style="width:100%; padding:8px; margin:5px 0; background:#1f2937; color:white; border:1px solid #374151;"><br>
                        <label>ইমেইল:</label><br>
                        <input type="email" name="email" style="width:100%; padding:8px; margin:5px 0; background:#1f2937; color:white; border:1px solid #374151;"><br>
                        <label>পাসওয়ার্ড:</label><br>
                        <input type="password" name="password" required style="width:100%; padding:8px; margin:5px 0; background:#1f2937; color:white; border:1px solid #374151;"><br>
                        <button type="submit" style="background:#10b981; color:white; border:none; padding:10px 15px; cursor:pointer; width:100%; border-radius:4px; margin-top:10px;">রেজিস্টার</button>
                    </form>
                </div>
            </div>
            '''}
        </div>
    </body>
    </html>
    """)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("my_profile"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
