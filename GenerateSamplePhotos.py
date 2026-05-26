"""
GenerateSamplePhotos.py
Downloads a few AI-generated faces from thispersondoesnotexist.com
and saves them into the Images/ folder using the student IDs from
SetupDatabase.py.

These are AI-generated faces of people who DO NOT exist — safe to use
for testing without copyright or privacy concerns.

NOTE: These sample images won't match YOUR face — so the live system
won't recognize you on the webcam. To test recognition, hold your
phone screen up to the webcam showing one of the downloaded images.
"""

import os
import time
import urllib.request

# Same IDs as SetupDatabase.py — keep these in sync
STUDENT_IDS = ["321654", "852741", "963852"]

IMAGES_FOLDER = "Images"
URL = "https://thispersondoesnotexist.com/"

os.makedirs(IMAGES_FOLDER, exist_ok=True)

# Pretend to be a browser — some servers reject the default urllib UA
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

for student_id in STUDENT_IDS:
    out_path = os.path.join(IMAGES_FOLDER, f"{student_id}.png")
    print(f"Downloading sample face for student {student_id}...")

    req = urllib.request.Request(URL, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        data = response.read()

    with open(out_path, "wb") as f:
        f.write(data)

    print(f"  Saved -> {out_path}")
    # Small delay so we get a fresh image each time (server caches briefly)
    time.sleep(2)

print(f"\nDone! Downloaded {len(STUDENT_IDS)} sample face(s) to '{IMAGES_FOLDER}/'.")
print("\nNext steps:")
print("  1. python SetupDatabase.py    (creates students.csv)")
print("  2. python EncodeGenerator.py  (encodes the sample faces)")
print("  3. python Face_Attendance.py  (run the live system)")
print("\nTo test recognition, display one of the downloaded images on your")
print("phone screen and hold it up to the webcam.")
