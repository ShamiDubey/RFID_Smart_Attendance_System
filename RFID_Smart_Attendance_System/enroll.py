#!/usr/bin/env python3
from mfrc522 import SimpleMFRC522
import csv, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "students.csv")

# Ensure header
if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
    with open(CSV_PATH, "w", newline="") as f:
        csv.writer(f).writerow(["uid","name","roll"])

reader = SimpleMFRC522()
print("Enroll mode. Press Ctrl+C to exit.")

while True:
    try:
        print("\n>> Tap card...")
        uid, _ = reader.read()
        print("UID:", uid)

        name = input("Name: ")
        roll = input("Roll: ")

        with open(CSV_PATH, "a", newline="") as f:
            csv.writer(f).writerow([uid, name, roll])
            print("Saved.")

    except KeyboardInterrupt:
        print("Done.")
        break
