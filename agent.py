import hashlib
import os
import requests

# Codespaces-এর লোকাল হোস্ট ইউআরএল
SERVER_URL = "http://127.0.0.1:5000/scan"


def get_file_hash(file_path):
  hasher = hashlib.sha256()
  try:
    with open(file_path, "rb") as f:
      while chunk := f.read(4096):
        hasher.update(chunk)
    return hasher.hexdigest()
  except Exception:
    return None


def test_scan(file_path):
  print(f"[+] Scanning file: {file_path}")
  file_hash = get_file_hash(file_path)

  if file_hash:
    payload = {"filename": os.path.basename(file_path), "hash": file_hash}
    try:
      response = requests.post(SERVER_URL, json=payload)
      print(f"[Result]: {response.json().get('message')}")
    except Exception as e:
      print("[Error]: Server down or unreachable!")


if __name__ == "__main__":
  # টেস্ট করার জন্য একটি ফাইল স্ক্যান
  test_scan("README.md")
