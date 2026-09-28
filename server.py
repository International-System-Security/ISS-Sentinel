import os
import resend
from flask import Flask, request, jsonify

app = Flask(__name__)

# Resend API Key সেট করুন (আপনার ড্যাশবোর্ড থেকে পাওয়া কি এখানে দিন অথবা এনভায়রনমেন্ট ভ্যারিয়েবলে রাখুন)
resend.api_key = os.environ.get("RESEND_API_KEY", "your_resend_api_key_here")

@app.route('/create-license', methods=['POST'])
def create_license():
    data = request.json
    client_name = data.get('client_name')
    client_email = data.get('client_email')
    license_key = data.get('license_key')
    password = data.get('password')
    tutorial_link = "https://yourwebsite.com/tutorial" # আপনার টিউটোরিয়ালের লিংক এখানে দিন

    if not client_email or not license_key:
        return jsonify({"error": "Client email and license key are required!"}, 400)

    # এখানে আপনার ডেটাবেজে লাইসেন্স সেভ করার কোড থাকবে...
    # database_save(client_name, client_email, license_key, password)

    # ক্লায়েন্টের ইমেলে পাঠানোর জন্য সুন্দর একটি মেসেজ বডি
    email_html = f"""
    <h2>Hello {client_name},</h2>
    <p>Your license has been successfully created!</p>
    <hr>
    <p><b>License Key:</b> {license_key}</p>
    <p><b>Password:</b> {password}</p>
    <p><b>Tutorial Guide:</b> <a href="{tutorial_link}">Click here to watch the tutorial</a></p>
    <br>
    <p>Thank you for using our service!</p>
    """

    try:
        # Resend API-এর মাধ্যমে ইমেল পাঠানো
        params = {
            "from": "onboarding@resend.dev", # আপনার নিজস্ব ডোমেইন ভেরিফাই করা থাকলে সেটি এখানে দিতে পারেন
            "to": [client_email],
            "subject": "Your New License & Login Details",
            "html": email_html,
        }
        
        email_response = resend.Emails.send(params)
        return jsonify({"success": True, "message": "License created and email sent successfully!", "email_response": email_response}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
