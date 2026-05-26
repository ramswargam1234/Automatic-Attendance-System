# Automatic Attendance System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)

A facial-recognition-based attendance system that uses a webcam to detect students, identify them against a known set of faces, and log their attendance to a local CSV file in real time.

Built as a mini project to replace traditional manual sign-in sheets and instructor-verified attendance, which can be slow and error-prone.

## Features

- Real-time face detection and recognition from a webcam feed
- 128-dimensional face encodings using the `dlib` ResNet model (via the `face_recognition` library)
- Local CSV storage — no cloud account or internet connection required
- Configurable time threshold to prevent duplicate attendance marks within a short window
- Visual feedback on the webcam feed (bounding boxes, student info overlay, status)
- Easily extensible — add students by dropping a photo into `Images/` and updating the CSV

## Tech Stack

| Component | Used For |
|---|---|
| Python 3.8+ | Core language |
| OpenCV (`opencv-python`) | Webcam capture, image processing, display |
| `face_recognition` | Face detection and 128-d encoding (wraps dlib's ResNet model) |
| NumPy | Numeric operations on encodings |
| `cvzone` *(optional)* | Nicer UI overlays |
| CSV | Local storage for student data and attendance |

## Project Structure

```
AutomaticAttendanceSystem/
├── Images/                    # Student photos (filename = student ID)
│   ├── 321654.png
│   ├── 852741.png
│   └── 963852.png
├── SetupDatabase.py           # Creates students.csv with initial records
├── GenerateSamplePhotos.py    # (Optional) downloads AI-generated test faces
├── EncodeGenerator.py         # Encodes faces from Images/ → EncodeFile.p
├── Face_Attendance.py         # Main live attendance script
├── students.csv               # Student database (sample provided)
├── EncodeFile.p               # Auto-generated face encodings
├── requirements.txt           # Python dependencies
├── .gitignore
├── LICENSE
└── README.md
```

## Installation

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/AutomaticAttendanceSystem.git
cd AutomaticAttendanceSystem
```

### 2. Set up a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note for macOS users:** `face_recognition` depends on `dlib`, which needs CMake to build:
> ```bash
> brew install cmake
> ```
>
> **Note for Windows users:** If `dlib` fails to install, install Visual Studio Build Tools (Desktop development with C++ workload) first, then retry.

## Usage

### Quick Start (with sample photos)

Don't have student photos yet? Run the sample-photo generator to download a few AI-generated faces (from `thispersondoesnotexist.com`) so you can test the pipeline end-to-end:

```bash
python GenerateSamplePhotos.py    # downloads 3 sample faces to Images/
python SetupDatabase.py            # (optional — students.csv ships with the repo)
python EncodeGenerator.py          # encodes the faces
python Face_Attendance.py          # run the live system
```

To test recognition, display one of the downloaded images on your phone and hold it up to the webcam. You should see the matching student info appear and `students.csv` update.

### Real Usage

### Step 1: Add student photos
Place a clear, front-facing photo of each student in the `Images/` folder. The filename (without extension) must match the `student_id` you'll use in the CSV.

Example: `Images/321654.png` corresponds to student ID `321654`.

### Step 2: Initialize the student database
Edit the `students` list in `SetupDatabase.py` to match your students, then run:
```bash
python SetupDatabase.py
```
This creates `students.csv` with one row per student.

### Step 3: Generate face encodings
```bash
python EncodeGenerator.py
```
This reads every image in `Images/`, extracts the 128-d face encoding for each, and saves the results to `EncodeFile.p`.

> Re-run this step **any time you add, remove, or change student photos**.

### Step 4: Run the attendance system
```bash
python Face_Attendance.py
```
A window will pop up showing the webcam feed. When a known face is detected:
- A green box appears around the face
- Student info is shown on the frame
- `students.csv` is updated with the new attendance count and timestamp

Press **`q`** to quit.

## Configuration

Open `Face_Attendance.py` to adjust:

| Setting | Default | What it does |
|---|---|---|
| `ATTENDANCE_THRESHOLD` | `30` seconds | Minimum time before the same student can be re-marked. Bump this to `1800` (30 min) or higher in real use. |
| `USE_BACKGROUND_UI` | `False` | Set to `True` if you have a `Resources/background.png` and `Resources/Modes/` folder for the fancy UI overlay. |
| `CSV_FILE` | `"students.csv"` | Path to the local database file. |

## CSV Format

`students.csv` columns:

| Column | Type | Description |
|---|---|---|
| `student_id` | string | Unique ID, must match the image filename |
| `name` | string | Full name |
| `major` | string | Field of study |
| `starting_year` | int | Year enrolled (e.g., 2022) |
| `year` | int | Current year of study |
| `standing` | string | Academic standing code (e.g., "G", "B") |
| `total_attendance` | int | Auto-incremented counter |
| `last_attendance_time` | string | ISO-like timestamp, format `YYYY-MM-DD HH:MM:SS` |

## How It Works

1. **Capture** — `cv2.VideoCapture` pulls frames from the webcam at ~640×480.
2. **Detect** — Each frame is downsized 4× for speed, then `face_recognition.face_locations()` finds face bounding boxes.
3. **Encode** — `face_recognition.face_encodings()` turns each detected face into a 128-d vector.
4. **Match** — The encoding is compared to all known encodings loaded from `EncodeFile.p` using Euclidean distance.
5. **Lookup** — On a successful match, the corresponding `student_id` is used to fetch the student's row from `students.csv`.
6. **Threshold** — If enough time has passed since the last mark, attendance is incremented and the CSV is rewritten.
7. **Display** — The frame is shown with overlays indicating success / already-marked / unknown.

## Troubleshooting

**`No module named 'face_recognition'`**
Install it: `pip install face-recognition`. If it fails on dlib, install CMake (see Installation notes above).

**Webcam doesn't open / black window**
Try changing `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` in `Face_Attendance.py`. On macOS, also grant Terminal/your IDE camera permission in System Settings → Privacy & Security → Camera.

**"No face found in image" warning during encoding**
The photo is too small, too dark, or the face isn't clearly visible. Use a clear front-facing image at least 200×200 px.

**Attendance not updating**
Check that `ATTENDANCE_THRESHOLD` hasn't already elapsed. Open `students.csv` and look at the `last_attendance_time` column.

**Slow or laggy webcam feed**
Detection on every frame is expensive. You can skip frames by only running face detection every Nth frame — happy to add this if you need it.

## Future Improvements

- Web dashboard for viewing/exporting attendance
- Multi-camera support
- Liveness detection to prevent spoofing with printed photos
- Integration with existing learning management systems (LMS)
- Better handling of lighting variations and partial occlusion

## Team

- **D. Keshav Sai Rao**
- **Kamlekar Sai Siddharth**
- **Swargam Ramchandar Rao**

**Project Guide:** Dr. I. Govardhana Rao

## License

Released under the MIT License — see [LICENSE](LICENSE) for details.
