# --- Service Leaflet & Membership Plans Route ---
@app.route("/service-leaflet")
def service_leaflet():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ISS Enterprise & Cloud Security - Service Leaflet</title>
        <style>
            :root {
                --bg-primary: #060913; --bg-secondary: #0b1120; --bg-card: #111827;
                --accent-blue: #0ea5e9; --text-main: #f8fafc; --text-muted: #94a3b8; --border-color: #1e293b;
            }
            body { font-family: 'Segoe UI', system-ui, sans-serif; background-color: var(--bg-primary); color: var(--text-main); margin: 0; padding: 30px; }
            .container { max-width: 800px; margin: 0 auto; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 40px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
            h1 { color: var(--accent-blue); text-align: center; font-size: 24px; margin-bottom: 5px; }
            .subtitle { text-align: center; color: var(--text-muted); font-size: 14px; margin-bottom: 30px; }
            .section-title { color: #38bdf8; font-size: 16px; border-bottom: 1px solid var(--border-color); padding-bottom: 6px; margin-top: 25px; margin-bottom: 15px; font-weight: bold; }
            .plans-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
            .plan-card { background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 8px; padding: 15px; }
            .plan-card h3 { margin: 0 0 5px 0; color: var(--text-main); font-size: 15px; }
            .plan-card span { color: var(--accent-blue); font-weight: bold; font-size: 13px; }
            .plan-card p { font-size: 12px; color: var(--text-muted); margin: 6px 0 0 0; }
            ul { padding-left: 20px; color: var(--text-muted); font-size: 14px; line-height: 1.6; }
            ul li { margin-bottom: 6px; }
            .footer { text-align: center; margin-top: 35px; padding-top: 15px; border-top: 1px solid var(--border-color); font-size: 13px; color: var(--text-muted); }
        </style>
    </head>
    <body>
        <div style="text-align:center; margin-bottom:15px;">
            <a href="/" style="color:var(--accent-blue); text-decoration:none; font-weight:bold;">&larr; Back to Home</a>
        </div>
        <div class="container">
            <h1>🛡️ ISS ENTERPRISE & CLOUD SECURITY</h1>
            <div class="subtitle">Next-Gen Cloud Security, Membership Plans & Professional Social Hub</div>

            <div class="section-title">📦 MEMBERSHIP & DEVICE PLANS</div>
            <div class="plans-grid">
                <div class="plan-card">
                    <h3>1. Basic Plan</h3>
                    <span>Limit: 2 Devices</span>
                    <p>Ideal for single users or small personal setups.</p>
                </div>
                <div class="plan-card">
                    <h3>2. Family Plan</h3>
                    <span>Limit: 5 Devices</span>
                    <p>Perfect for family members and multi-device safety.</p>
                </div>
                <div class="plan-card">
                    <h3>3. Standard Plan</h3>
                    <span>Limit: 10 Devices</span>
                    <p>Designed for growing teams and professionals.</p>
                </div>
                <div class="plan-card">
                    <h3>4. Business Plan</h3>
                    <span>Limit: Unlimited Devices</span>
                    <p>Enterprise-grade security with zero restrictions.</p>
                </div>
            </div>

            <div class="section-title">🌟 KEY PLATFORM FEATURES</div>
            <ul>
                <li>🌐 <strong>ISS Social Hub:</strong> Connect with verified professionals, share updates, and post media securely.</li>
                <li>💬 <strong>Private Support Tickets:</strong> Direct encrypted messenger chat with system administrators.</li>
                <li>🔑 <strong>Advanced License Portal:</strong> Secure client dashboard access using unique license keys.</li>
                <li>✔️ <strong>Verified & Trusted Badges:</strong> Authentic security badges for elite members.</li>
            </ul>

            <div class="footer">
                <p><b>Contact Us:</b> support@iss.com | Visit our official portal to apply for licenses.</p>
                <p style="color: var(--accent-blue); margin-top: 5px;">🛡️ ISS Platform — Securing Your Digital Future.</p>
            </div>
        </div>
    </body>
    </html>
    """)
