"""
Face_Attendance.py
Main script: real-time face recognition + attendance updates in a local CSV file.

No Firebase / cloud required — pure local.
"""

import os
import csv
import pickle
import cv2
import face_recognition
import numpy as np
from datetime import datetime

# cvzone is optional — used for nicer UI overlays.
# If you don't want to install it, set USE_CVZONE = False below.
USE_CVZONE = True
try:
    import cvzone
except ImportError:
    USE_CVZONE = False
    print("cvzone not installed — running without fancy overlays.")

# ---------- Config ----------
CSV_FILE = "students.csv"
ENCODE_FILE = "EncodeFile.p"
ATTENDANCE_THRESHOLD = 30  # seconds before the same student can be re-marked
USE_BACKGROUND_UI = False   # set True if you have Resources/background.png + Modes/

CSV_FIELDS = [
    "student_id", "name", "major", "starting_year", "year",
    "standing", "total_attendance", "last_attendance_time",
]


# ---------- CSV helpers ----------
def load_students(csv_path):
    """Load students.csv into a dict keyed by student_id."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"'{csv_path}' not found. Run SetupDatabase.py first."
        )
    students = {}
    with open(csv_path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Cast numeric fields
            row["starting_year"] = int(row["starting_year"])
            row["year"] = int(row["year"])
            row["total_attendance"] = int(row["total_attendance"])
            students[row["student_id"]] = row
    return students


def save_students(csv_path, students):
    """Write the students dict back to CSV."""
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for sid in students:
            writer.writerow(students[sid])


# ---------- Load data ----------
students = load_students(CSV_FILE)
print(f"Loaded {len(students)} students from {CSV_FILE}.")

print("Loading encode file...")
with open(ENCODE_FILE, "rb") as f:
    encode_list_known_with_ids = pickle.load(f)
encode_list_known, student_ids = encode_list_known_with_ids
print(f"Encode file loaded ({len(student_ids)} known faces).")

# ---------- Webcam ----------
cap = cv2.VideoCapture(0)
cap.set(3, 640)   # width
cap.set(4, 480)   # height

# ---------- Optional UI assets ----------
img_background = None
img_mode_list = []
if USE_BACKGROUND_UI:
    img_background = cv2.imread("Resources/background.png")
    folder_mode_path = "Resources/Modes"
    if os.path.isdir(folder_mode_path):
        mode_path_list = sorted(os.listdir(folder_mode_path))
        img_mode_list = [cv2.imread(os.path.join(folder_mode_path, p))
                         for p in mode_path_list]
        print("Loaded mode images:", len(img_mode_list))
    else:
        print("Resources/Modes folder not found — falling back to plain view.")
        USE_BACKGROUND_UI = False

# ---------- State variables ----------
mode_type = 0       # 0 active, 1 marked, 2 already-marked, 3 unknown
counter = 0
student_id = None
student_info = None

# ---------- Main loop ----------
print("Starting attendance system. Press 'q' to quit.")
while True:
    success, img = cap.read()
    if not success:
        print("Failed to read from webcam.")
        break

    # Downsize for faster detection
    img_small = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    img_small_rgb = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(img_small_rgb)
    face_encodings = face_recognition.face_encodings(img_small_rgb, face_locations)

    # Choose display canvas
    if USE_BACKGROUND_UI and img_background is not None:
        display = img_background.copy()
        display[162:162 + 480, 55:55 + 640] = img
        if img_mode_list:
            display[44:44 + 633, 808:808 + 414] = img_mode_list[
                mode_type % len(img_mode_list)
            ]
    else:
        display = img.copy()

    if face_encodings:
        for encode_face, face_loc in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(encode_list_known, encode_face)
            face_dis = face_recognition.face_distance(encode_list_known, encode_face)
            match_index = int(np.argmin(face_dis))

            # Scale bbox back up (we ran detection on 0.25x image)
            y1, x2, y2, x1 = face_loc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            if matches[match_index]:
                student_id = student_ids[match_index]
                color = (0, 255, 0)  # green box for known
                # In simple view, bbox is on the raw webcam frame
                if not USE_BACKGROUND_UI:
                    cv2.rectangle(display, (x1, y1), (x2, y2), color, 2)
                else:
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    if USE_CVZONE:
                        display = cvzone.cornerRect(display, bbox, rt=0)
                    else:
                        cv2.rectangle(display,
                                      (bbox[0], bbox[1]),
                                      (bbox[0] + bbox[2], bbox[1] + bbox[3]),
                                      color, 2)

                if counter == 0:
                    counter = 1
                    mode_type = 1
            else:
                # Unknown face
                if not USE_BACKGROUND_UI:
                    cv2.rectangle(display, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(display, "Unknown", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                mode_type = 3
                counter = 0

        # ----- On first frame of recognition, update CSV -----
        if counter == 1 and student_id is not None:
            student_info = students.get(student_id)
            if student_info is None:
                print(f"Student {student_id} not in CSV. Skipping.")
                counter = 0
            else:
                last_time_str = student_info["last_attendance_time"]
                try:
                    last_dt = datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    last_dt = datetime(2000, 1, 1)

                seconds_elapsed = (datetime.now() - last_dt).total_seconds()
                print(f"{student_info['name']} — {seconds_elapsed:.1f}s since last mark.")

                if seconds_elapsed > ATTENDANCE_THRESHOLD:
                    student_info["total_attendance"] += 1
                    student_info["last_attendance_time"] = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    students[student_id] = student_info
                    save_students(CSV_FILE, students)
                    print(f"  Attendance marked! Total: {student_info['total_attendance']}")
                    mode_type = 1
                else:
                    print(f"  Already marked recently. Skipping.")
                    mode_type = 2

        # ----- Overlay student info text -----
        if counter > 0 and student_info is not None:
            if not USE_BACKGROUND_UI:
                # Simple top-left info panel
                lines = [
                    f"Name: {student_info['name']}",
                    f"ID: {student_info['student_id']}",
                    f"Major: {student_info['major']}",
                    f"Year: {student_info['year']}  Standing: {student_info['standing']}",
                    f"Total Attendance: {student_info['total_attendance']}",
                    "STATUS: " + ("MARKED" if mode_type == 1 else
                                  "ALREADY MARKED" if mode_type == 2 else ""),
                ]
                y = 25
                for line in lines:
                    cv2.putText(display, line, (10, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(display, line, (10, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
                    y += 25
            else:
                # Full background UI layout (same positions as Firebase version)
                cv2.putText(display, str(student_info["total_attendance"]),
                            (861, 125), cv2.FONT_HERSHEY_COMPLEX, 1,
                            (255, 255, 255), 1)
                cv2.putText(display, str(student_info["major"]),
                            (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                            (255, 255, 255), 1)
                cv2.putText(display, str(student_info["student_id"]),
                            (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                            (255, 255, 255), 1)
                cv2.putText(display, str(student_info["standing"]),
                            (910, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                            (100, 100, 100), 1)
                cv2.putText(display, str(student_info["year"]),
                            (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                            (100, 100, 100), 1)
                cv2.putText(display, str(student_info["starting_year"]),
                            (1125, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                            (100, 100, 100), 1)
                (w, h), _ = cv2.getTextSize(
                    student_info["name"], cv2.FONT_HERSHEY_COMPLEX, 1, 1
                )
                offset = (414 - w) // 2
                cv2.putText(display, str(student_info["name"]),
                            (808 + offset, 445), cv2.FONT_HERSHEY_COMPLEX,
                            1, (50, 50, 50), 1)

            counter += 1
            if counter > 30:  # show for ~30 frames then reset
                counter = 0
                mode_type = 0
                student_info = None
                student_id = None
    else:
        mode_type = 0
        counter = 0
        student_info = None

    cv2.imshow("Face Attendance", display)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("Attendance system stopped. Final CSV saved.")
