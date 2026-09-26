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
                if len(parts) >= 6:
                    uname = parts[0].strip()
                    users[uname] = {
                        "email": parts[1].strip(), 
                        "password": parts[2].strip(),
                        "role": parts[3].strip(), 
                        "pic": parts[4].strip(),
                        "verified": parts[5].strip() == "True"
                    }
    return users

def save_all_users(users_dict):
    with open(USER_FILE, "w") as f:
        for uname, data in users_dict.items():
            f.write(f"{uname}|||{data['email']}|||{data['password']}|||{data['role']}|||{data['pic']}|||{data['verified']}\n")


# --- হোম পেজ রুট ---
@app.route("/")
def home():
    return "<h2>Welcome to ISS Platform! <a href='/my-profile'>Go to My Profile</a></h2>"


# --- মূল প্রোফাইল পেজ (যেখানে পাসওয়ার্ড ও ছবি পরিবর্তনের কাজ হবে) ---
@app.route("/my-profile", methods=["GET", "POST"])
def my_profile():
    users = load_users()
    current_user = session.get("username")
    msg = ""
    error = ""

    if request.method == "POST":
        action = request.form.get("action")
        
        # ১. পাসওয়ার্ড ও ইউজারনেম পরিবর্তনের কাজ
        if action == "update_credentials" and current_user:
            new_uname = request.form.get("new_username", "").strip()
            new_pwd = request.form.get("new_password", "").strip()

            if current_user in users:
                target_key = current_user
                if new_uname and new_uname != current_user:
                    if new_uname in users:
                        error = "এই ইউজারনেমটি আগেই নেওয়া হয়েছে!"
                    else:
                        users[new_uname] = users.pop(current_user)
                        target_key = new_uname
                        session["username"] = target_key

                if new_pwd:
                    users[target_key]["password"] = new_pwd

                save_all_users(users)
                msg = "✅ পাসওয়ার্ড এবং ইউজারনেম সফলভাবে আপডেট করা হয়েছে!"

        # ২. প্রোফাইল ছবি আপলোডের কাজ
        elif action == "update_pic" and current_user:
            if curr_user := current_user:
                if 'profile_pic_file' in request.files:
                    file = request.files['profile_pic_file']
                    if file and file.filename != '':
                        filename = secure_filename(f"{curr_user}_{int(datetime.now().timestamp())}_{file.filename}")
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        
                        if curr_user in users:
                            users[curr_user]["pic"] = f"/static/uploads/{filename}"
                            save_all_users(users)
                            msg = "✅ প্রোফাইল ছবি সফলভাবে আপলোড করা হয়েছে!"
                    else:
                        error = "দয়া করে ছবি সিলেক্ট করুন।"

        # ৩. লগইন হ্যান্ডেল
        elif action == "login":
            uname = request.form.get("username", "").strip()
            pwd = request.form.get("password", "").strip()
            if uname in users and users[uname]["password"] == pwd:
                session["username"] = uname
                return redirect(url_for("my_profile"))
            else:
                error = "ভুল ইউজারনেম বা পাসওয়ার্ড!"

    user_data = users.get(current_user) if current_user else None

    # সাধারণ এইচটিএমএল ফর্ম ইন্টারফেস
    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><title>My Profile Settings</title></head>
    <body style="font-family:sans-serif; background:#060913; color:white; padding:30px;">
        <div style="max-width:500px; margin:0 auto; background:#111827; padding:30px; border-radius:10px;">
            <h2>⚙️ User Profile & Settings</h2>
            
            {f'<p style="color:#ef4444;">{error}</p>' if error else ''}
            {f'<p style="color:#34d399;">{msg}</p>' if msg else ''}

            {f'''
            <p>লগইন করা আছে: <b>{current_user}</b></p>
            <img src="{user_data.get('pic', 'https://i.imgur.com/6VBx3io.png')}" style="width:80px; height:80px; border-radius:50%; object-fit:cover;"><br><br>

            <h3>পাসওয়ার্ড বা ইউজারনেম পরিবর্তন করুন</h3>
            <form method="POST">
                <input type="hidden" name="action" value="update_credentials">
                <label>নতুন ইউজারনেম:</label><br>
                <input type="text" name="new_username" value="{current_user}" required style="width:100%; padding:8px; margin:5px 0;"><br>
                <label>নতুন পাসওয়ার্ড:</label><br>
                <input type="password" name="new_password" placeholder="নতুন পাসওয়ার্ড দিন" required style="width:100%; padding:8px; margin:5px 0;"><br>
                <button type="submit" style="background:#0ea5e9; color:white; border:none; padding:10px 15px; cursor:pointer; width:100%;">আপডেট করুন</button>
            </form>

            <h3 style="margin-top:20px;">প্রোফাইল ছবি আপলোড করুন</h3>
            <form method="POST" enctype="multipart/form-data">
                <input type="hidden" name="action" value="update_pic">
                <input type="file" name="profile_pic_file" accept="image/*" required style="margin:5px 0;"><br>
                <button type="submit" style="background:#10b981; color:white; border:none; padding:10px 15px; cursor:pointer; width:100%;">ছবি আপলোড করুন</button>
            </form>

            <br><a href="/logout" style="color:#ef4444;">লগআউট করুন</a>
            ''' if current_user else '''
            <h3>লগইন করুন</h3>
            <form method="POST">
                <input type="hidden" name="action" value="login">
                <label>ইউজারনেম:</label><br>
                <input type="text" name="username" required style="width:100%; padding:8px; margin:5px 0;"><br>
                <label>পাসওয়ার্ড:</label><br>
                <input type="password" name="password" required style="width:100%; padding:8px; margin:5px 0;"><br>
                <button type="submit" style="background:#0ea5e9; color:white; border:none; padding:10px 15px; cursor:pointer; width:100%;">লগইন</button>
            </form>
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
