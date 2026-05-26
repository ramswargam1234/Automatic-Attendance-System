"""
EncodeGenerator.py
Reads student images from the Images/ folder, generates 128-d face encodings,
and saves them along with student IDs into EncodeFile.p

No Firebase / cloud required — pure local.
"""

import os
import pickle
import cv2
import face_recognition

# Folder containing student images. Each image filename = student ID (e.g., "321654.png")
folder_path = "Images"

if not os.path.isdir(folder_path):
    raise FileNotFoundError(
        f"'{folder_path}' folder not found. "
        f"Create it and put student photos inside (filename = student ID)."
    )

path_list = os.listdir(folder_path)
print("Images found:", path_list)

img_list = []
student_ids = []

for path in path_list:
    full_path = os.path.join(folder_path, path)
    img = cv2.imread(full_path)
    if img is None:
        print(f"Skipping {path} (could not read)")
        continue
    img_list.append(img)
    student_ids.append(os.path.splitext(path)[0])  # filename without extension

print("Student IDs:", student_ids)


def find_encodings(images_list, ids_list):
    """Generate 128-d face encodings for a list of BGR images.

    Returns (encodings, valid_ids) — IDs whose image had no detectable face
    are dropped so the two lists stay aligned.
    """
    encode_list = []
    valid_ids = []
    for img, sid in zip(images_list, ids_list):
        # face_recognition expects RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img_rgb)
        if len(encodings) > 0:
            encode_list.append(encodings[0])
            valid_ids.append(sid)
        else:
            print(f"Warning: no face found in image for student {sid}. Skipped.")
    return encode_list, valid_ids


print("Encoding started...")
encode_list_known, student_ids = find_encodings(img_list, student_ids)
encode_list_known_with_ids = [encode_list_known, student_ids]
print("Encoding complete.")

# Save to pickle file
with open("EncodeFile.p", "wb") as f:
    pickle.dump(encode_list_known_with_ids, f)

print(f"EncodeFile.p saved successfully ({len(student_ids)} students encoded).")
