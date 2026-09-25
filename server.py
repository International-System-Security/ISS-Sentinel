@app.route("/", methods=["GET"])
def home():
    return """
    <!DOCTYPE html>
    html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ISS Cloud Security & Enterprise Antivirus</title>
        <style>
            :root {
                --bg-primary: #090d16;
                --bg-card: #111827;
                --accent-blue: #0ea5e9;
                --accent-hover: #0284c7;
                --text-main: #f8fafc;
                --text-muted: #94a3b8;
                --border-color: #1e293b;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: var(--bg-primary);
                color: var(--text-main);
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                min-height: 100vh;
                justify-content: space-between;
            }
            .header {
                padding: 20px 40px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid var(--border-color);
            }
            .logo {
                font-size: 20px;
                font-weight: bold;
                letter-spacing: 1px;
                color: var(--accent-blue);
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .container {
                max-width: 900px;
                margin: auto;
                text-align: center;
                padding: 40px 20px;
            }
            h1 {
                font-size: 42px;
                margin-bottom: 15px;
                font-weight: 800;
                background: linear-gradient(to right, #38bdf8, #818cf8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            p.subtitle {
                font-size: 18px;
                color: var(--text-muted);
                margin-bottom: 40px;
                line-height: 1.6;
            }
            .cards-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            .card {
                background-color: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                padding: 30px;
                text-align: left;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
                transition: transform 0.2s, border-color 0.2s;
            }
            .card:hover {
                transform: translateY(-5px);
                border-color: var(--accent-blue);
            }
            .card h3 {
                margin-top: 0;
                font-size: 20px;
                color: var(--text-main);
            }
            .card p {
                color: var(--text-muted);
                font-size: 14px;
                line-height: 1.5;
            }
            .btn {
                display: inline-block;
                background-color: var(--accent-blue);
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: bold;
                font-size: 14px;
                margin-top: 15px;
                transition: background-color 0.2s;
            }
            .btn:hover {
                background-color: var(--accent-hover);
            }
            .btn-outline {
                background-color: transparent;
                border: 1px solid var(--accent-blue);
                color: var(--accent-blue);
            }
            .btn-outline:hover {
                background-color: var(--accent-blue);
                color: white;
            }
            .footer {
                text-align: center;
                padding: 20px;
                color: var(--text-muted);
                font-size: 13px;
                border-top: 1px solid var(--border-color);
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">🛡️ ISS CLOUD SECURITY</div>
            <div>
                <a href="/client-login" class="btn btn-outline" style="margin-top:0; padding: 8px 16px;">Client Portal</a>
            </div>
        </div>

        <div class="container">
            <h1>Next-Gen Cloud Endpoint Security</h1>
            <p class="subtitle">Advanced enterprise-grade protection, real-time threat intelligence, and centralized device management backed by ISS infrastructure.</p>

            <div class="cards-grid">
                <div class="card">
                    <h3>Client Portal</h3>
                    <p>Manage your active license, monitor connected devices, and secure your endpoints instantly with one-click setup.</p>
                    <a href="/client-login" class="btn">Access Client Portal</a>
                </div>
                <div class="card">
                    <h3>Admin Dashboard</h3>
                    <p>Centralized control panel for issuing licenses, monitoring expiration cycles, and managing system credentials securely.</p>
                    <a href="/admin/login" class="btn btn-outline">Admin Login</a>
                </div>
            </div>
        </div>

        <div class="footer">
            &copy; 2026 ISS Security Systems. All Rights Reserved. Enterprise Cloud Backend Active.
        </div>
    </body>
    </html>
    """
