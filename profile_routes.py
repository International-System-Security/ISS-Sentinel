import os
from flask import Blueprint, request, redirect, url_for, session
from werkzeug.utils import secure_filename

# ফ্লাস্ক ব্লুপ্রিন্ট তৈরি
profile_bp = Blueprint('profile_bp', __name__)

UPLOAD_FOLDER = 'static/uploads'

# ছবি এবং পাসওয়ার্ড আপডেট হ্যান্ডেল করার রুট
@profile_bp.route('/update-user-settings', methods=['POST'])
def update_user_settings():
    current_user = session.get("username")
    if not current_user:
        return redirect(url_for("my_profile"))

    action = request.form.get("action")

    # ১. পাসওয়ার্ড পরিবর্তনের লজিক
    if action == "update_credentials":
        new_pwd = request.form.get("new_password", "").strip()
        # আপনার সার্ভারের ডেটাবেজ বা ফাইল থেকে ইউজার লোড করে পাসওয়ার্ড আপডেট করার কোড এখানে বসবে
        # যেমন: users[current_user]["password"] = new_pwd

    # ২. প্রোফাইল ছবি আপলোডের লজিক
    elif action == "update_pic":
        if 'profile_pic_file' in request.files:
            file = request.files['profile_pic_file']
            if file and file.filename != '':
                filename = secure_filename(f"{current_user}_{int(datetime.now().timestamp())}_{file.filename}")
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                # ছবির পাথ ডেটাবেজে সেভ করার কোড এখানে বসবে
                # users[current_user]["pic"] = f"/static/uploads/{filename}"

    return redirect(url_for("my_profile"))
