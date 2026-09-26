import os
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# ডামি ডাটা বা স্টেট (আপনার প্রজেক্ট অনুযায়ী এটি ডেটাবেস বা গ্লোবাল ভেরিয়েবল হতে পারে)
app_state = {
    "antivirus_active": False,  # ক্লায়েন্ট অ্যান্টিভাইরাস অ্যাক্টিভেট করেছে কিনা
    "test_result": None,
}


@app.route("/")
def index():
  return render_template(
      "index.html", antivirus_active=app_state["antivirus_active"]
  )


# অ্যান্টিভাইরাস স্ট্যাটাস আপডেট করার রুট (ক্লায়েন্ট সাইড থেকে কল হবে)
@app.route("/api/update-antivirus", methods=["POST"])
def update_antivirus():
  data = request.get_json()
  app_state["antivirus_active"] = data.get("active", False)
  return jsonify(
      {
          "status": "success",
          "antivirus_active": app_state["antivirus_active"],
      }
  )


# টেস্ট ভাইরাস রান করার রুট
@app.route("/api/run-test", methods=["POST"])
def run_test():
  if not app_state["antivirus_active"]:
    return (
        jsonify({"status": "error", "message": "Antivirus is not active!"}),
        400,
    )

  # এখানে টেস্ট ভাইরাসের সিমুলেশন লজিক কাজ করবে
  # ধরে নিচ্ছি অ্যান্টিভাইরাস প্রটেকশন অন থাকলে টেস্ট সফল হবে, না হলে পরাজয়।
  # আপনি আপনার রিয়েল অ্যান্টিভাইরাস চেকিং লজিক এখানে বসাতে পারেন।

  is_blocked = (
      app_state["antivirus_active"]
  )  # উদাহরণস্বরূপ: অ্যাক্টিভ থাকলে ব্লক করবে

  if is_blocked:
    result_message = "সাকসেস: অ্যান্টিভাইরাস সফলভাবে ভাইরাস প্রতিরোধ করেছে!"
    status_type = "success"
  else:
    result_message = (
        "পরাজয়: অ্যান্টিভাইরাস হুমকি প্রতিরোধ করতে ব্যর্থ হয়েছে!"
    )
    status_type = "failure"

  return jsonify(
      {"status": status_type, "message": result_message, "result": status_type}
  )


if __name__ == "__main__":
  # সার্ভার রান করার জন্য
  app.run(host="0.0.0.0", port=5000, debug=True)
