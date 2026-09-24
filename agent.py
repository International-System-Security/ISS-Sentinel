import hashlib
import json
import os
import requests

# Render-এর লাইভ সার্ভার URL এবং Scan Endpoint
BASE_URL = "https://iss-antivirus-cloud.onrender.com"
SCAN_URL = f"{BASE_URL}/scan"


def get_license_key():
  """config.json ফাইল থেকে লাইসেন্স কী সংগ্রহ করে"""
  if os.path.exists("config.json"):
    try:
      with open("config.json", "r") as f:
        config = json.load(f)
        return config.get("license_key", "UNKNOWN_KEY")
    except Exception:
      return "INVALID_CONFIG"
  return "NO_KEY"


def get_file_hash(file_path):
  """ফাইলের SHA256 Hash তৈরি করে"""
  hasher = hashlib.sha256()
  try:
    with open(file_path, "rb") as f:
      while chunk := f.read(4096):
        hasher.update(chunk)
    return hasher.hexdigest()
  except Exception:
    return None


def scan_file(file_path):
  """ক্লাউড সার্ভারে ফাইল হ্যাশ ও লাইসেন্স পাঠায়"""
  license_key = get_license_key()
  file_hash = get_file_hash(file_path)

  if file_hash:
    payload = {
        "license_key": license_key,
        "filename": os.path.basename(file_path),
        "hash": file_hash,
    }
    try:
      response = requests.post(SCAN_URL, json=payload, timeout=10)
      result = response.json()
      print(f"[+] File: {os.path.basename(file_path)}")
      print(f"[Result]: {result.get('message', 'Scan completed')}")
    except Exception:
      print("[Error]: Server down or unreachable!")


if __name__ == "__main__":
  # টেস্ট রান (ফোল্ডারে থাকা README.md স্ক্যান করবে)
  if os.path.exists("README.md"):
    scan_file("README.md")
  else:
    print("[+] ISS Agent Initialized and Running...")
