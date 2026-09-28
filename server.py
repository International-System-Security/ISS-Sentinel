from flask import Flask, render_template_string, jsonify, request
import time

app = Flask(__name__)

# ফ্রন্টএন্ড এবং ব্যাকএন্ড একসাথে রাখার জন্য একটি সিম্পল টেমপ্লেট
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Security & Antivirus Scanner</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 50px; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .scanner-card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 450px; text-align: center; }
        h2 { color: #333; margin-bottom: 20px; }
        .btn { background: #007bff; color: white; border: none; padding: 12px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; width: 100%; transition: 0.3s; }
        .btn:hover { background: #0056b3; }
        .steps-container { text-align: left; margin-top: 20px; display: none; }
        .step-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #eee; font-size: 14px; color: #555; }
        .status { font-weight: bold; }
        .pending { color: #f39c12; }
        .success { color: #28a745; }
        .failed { color: #dc3545; }
        /* Popup Modal */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); justify-content: center; align-items: center; }
        .modal-content { background: white; padding: 25px; border-radius: 8px; width: 350px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        .modal-content h3 { color: #dc3545; margin-top: 0; }
        .close-btn { background: #dc3545; color: white; border: none; padding: 8px 15px; margin-top: 15px; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>

<div class="scanner-card">
    <h2>System Vulnerability & Virus Scanner</h2>
    <button class="btn" onclick="startScan()">Start Security Scan</button>
    
    <div class="steps-container" id="stepsContainer">
        <!-- Steps will be dynamically inserted here -->
    </div>
</div>

<!-- Alert Popup Modal -->
<div class="modal" id="alertModal">
    <div class="modal-content">
        <h3 id="modalTitle">Security Alert</h3>
        <p id="modalMessage">Virus detected in the system!</p>
        <button class="close-btn" onclick="closeModal()">Acknowledge & Close</button>
    </div>
</div>

<script>
    const steps = [
        "Checking your device integrity...",
        "Detecting active virus signatures...",
        "Scanning system memory & processes...",
        "Analyzing network packets & firewall...",
        "Inspecting browser extensions & cookies...",
        "Verifying system registry files..."
    ];

    function startScan() {
        const container = document.getElementById('stepsContainer');
        container.style.display = 'block';
        container.innerHTML = '';

        // Render all steps as Pending initially
        steps.forEach((stepText, index) => {
            container.innerHTML += `
                <div class="step-item">
                    <span>${index + 1}. ${stepText}</span>
                    <span class="status pending" id="step-${index}">Pending...</span>
                </div>
            `;
        });

        // Execute steps sequentially with a delay (e.g., 2 to 3 seconds per step for UX, can be adjusted)
        let currentStep = 0;
        
        function processNextStep() {
            if (currentStep < steps.length) {
                const statusSpan = document.getElementById(`step-${currentStep}`);
                
                // Simulate processing time
                setTimeout(() => {
                    // Logic: Let's assume step 2 or a test condition triggers detection, or everything passes successfully.
                    // Here we can make step 2 or 5 show infected/failed or success based on your requirement.
                    if (currentStep === 1) { 
                        // Example: Triggering virus detection simulation on step 2
                        statusSpan.className = "status failed";
                        statusSpan.innerText = "❌ Infected";
                        showPopup("Virus Threat Detected!", "Critical Warning: Real/Test Virus signature identified in system memory!");
                    } else {
                        statusSpan.className = "status success";
                        statusSpan.innerText = "✔ Success";
                    }
                    
                    currentStep++;
                    if (currentStep < steps.length && statusSpan.className !== "status failed") {
                        processNextStep();
                    } else if (currentStep === steps.length) {
                        // Final Success check if no major blocks occurred
                        setTimeout(() => {
                            // If it passes all layers without failing
                            console.log("Scan completed successfully.");
                        }, 500);
                    }
                }, 2000); // প্রতি ধাপের জন্য ২ সেকেন্ড করে ডিলে (আপনার ইচ্ছেমতো বাড়িয়ে ৩০ সেকেন্ড বা কম-বেশি করতে পারেন)
            }
        }

        processNextStep();
    }

    function showPopup(title, message) {
        document.getElementById('modalTitle').innerText = title;
        document.getElementById('modalMessage').innerText = message;
        document.getElementById('alertModal').style.display = 'flex';
    }

    function closeModal() {
        document.getElementById('alertModal').style.display = 'none';
    }
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
