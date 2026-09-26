elif action == "update_credentials" and "username" in session:
    curr_uname = session["username"]
    new_uname = request.form.get("new_username", "").strip()
    new_pwd = request.form.get("new_password", "").strip()

    if curr_uname in users:
        target_key = curr_uname
        if new_uname and new_uname != curr_uname:
            if new_uname in users:
                error = "Username already taken!"
            else:
                users[new_uname] = users.pop(curr_uname) # এখানে ডিকশনারির Key পরিবর্তন করা হচ্ছে
                target_key = new_uname
                session["username"] = target_key

        if new_pwd:
            users[target_key]["password"] = new_pwd

        user_email = users[target_key]["email"]
        if user_email in admin_data:
            save_admin_data(user_email, target_key, users[target_key]["password"])

        save_all_users(users)
