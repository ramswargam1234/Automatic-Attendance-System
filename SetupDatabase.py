"""
SetupDatabase.py
Creates a local CSV file (students.csv) with pre-defined student information.
Run this ONCE before using the system.

(Replaces the Firebase-based AddDatatoDatabase.py.)
"""

import csv
import os

CSV_FILE = "students.csv"

# Pre-defined student data — student_id MUST match the image filename
# (e.g., student_id "321654" -> Images/321654.png)
students = [
    {
        "student_id": "321654",
        "name": "Keshav Sai Rao",
        "major": "Computer Science",
        "starting_year": 2022,
        "year": 3,
        "standing": "G",
        "total_attendance": 0,
        "last_attendance_time": "2024-01-01 00:00:00",
    },
    {
        "student_id": "852741",
        "name": "Sai Siddharth Kamlekar",
        "major": "Computer Science",
        "starting_year": 2022,
        "year": 3,
        "standing": "B",
        "total_attendance": 0,
        "last_attendance_time": "2024-01-01 00:00:00",
    },
    {
        "student_id": "963852",
        "name": "Ramchandar Rao Swargam",
        "major": "Computer Science",
        "starting_year": 2022,
        "year": 3,
        "standing": "G",
        "total_attendance": 0,
        "last_attendance_time": "2024-01-01 00:00:00",
    },
    # Add more students as needed
]

# CSV columns (kept in the same order as Firebase fields for easy reference)
fieldnames = [
    "student_id",
    "name",
    "major",
    "starting_year",
    "year",
    "standing",
    "total_attendance",
    "last_attendance_time",
]

# Warn if the file already exists so we don't accidentally wipe attendance counts
if os.path.exists(CSV_FILE):
    response = input(f"'{CSV_FILE}' already exists. Overwrite? (y/n): ")
    if response.lower() != "y":
        print("Aborted. Existing file kept.")
        raise SystemExit

with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(students)

print(f"Successfully wrote {len(students)} student records to {CSV_FILE}.")
