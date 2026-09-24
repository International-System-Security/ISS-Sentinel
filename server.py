from flask import Flask, jsonify, request

app = Flask(__name__)

# উদাহরণস্বরূপ জানা কিছু ভাইরাসের হ্যাশ (Malware Signatures)
KNOWN_THREATS = [
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "44d88612fea8a8f36de82e1278abb02f",  # EICAR Test Virus
]


@app.route("/scan", methods=["POST"])
def scan_file():
  data = request.json or {}
  file_hash = data.get("hash")
  filename = data.get("filename", "Unknown")

  if file_hash in KNOWN_THREATS:
    return jsonify({
        "status": "danger",
        "is_threat": True,
        "message": f"ALERT: Threat found in {filename}!",
    })

  return jsonify(
      {"status": "clean", "is_threat": False, "message": f"{filename} is safe."}
  )


if __name__ == "__main__":
  # Codespaces ক্লাউডের জন্য পোর্ট ৫০০০ এ সার্ভার চালু করা
  app.run(host="0.0.0.0", port=5000)
