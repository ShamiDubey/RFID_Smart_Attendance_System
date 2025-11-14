# RFID-Based Smart Attendance System (Raspberry Pi + RFID MFRC522)

This project implements a Smart Attendance System using RFID cards and a Raspberry Pi.
Students tap their RFID card, and the system automatically marks attendance with timestamp and stores it in CSV files.

# Features

RFID tag reading using MFRC522

Automatic attendance marking

Stores attendance in CSV files

Student enrollment system

LCD (I2C) display support

Buzzer notification

Photo-interrupter sensor for card detection

Raspberry Pi hotspot mode (optional)

# Technology Stack
Component	Purpose
Python	Main programming language
Raspberry Pi (GPIO)	Hardware control
MFRC522 RFID Reader	Reads RFID UID
I²C (SMBus)	LCD communication
CSV	Data storage
hostapd	WiFi hotspot feature
# Project Structure
RFID-Smart-Attendance-System/
│
├── attendance.py        → Main attendance script
├── enroll.py            → Script to add new students
├── students.csv         → Registered students list
├── attendance.csv       → Attendance log file
├── hotspot.conf         → Raspberry Pi hotspot settings
└── README.md            → Project documentation

# Hardware Required

Raspberry Pi (3/4/Zero-W)

MFRC522 RFID Reader

RFID Cards/Tags

I2C 16x2 LCD (optional)

Buzzer

Photo interrupter module (optional)

Jumper wires

# Wiring Diagram (Summary)
MFRC522 to Raspberry Pi
MFRC522	Raspberry Pi
SDA	GPIO 8 (CE0)
SCK	GPIO 11
MOSI	GPIO 10
MISO	GPIO 9
IRQ	Not connected
GND	GND
RST	GPIO 22
3.3V	3.3V
LCD (I²C)
LCD Pin	Raspberry Pi
SDA	GPIO 2
SCL	GPIO 3
VCC	5V
GND	GND
# How the System Works
1. Enrollment Mode

Run:

python3 enroll.py


Tap card → Reads UID

Enter name + roll number

Saves it into students.csv

2. Attendance Mode

Run:

python3 attendance.py


Shows welcome message

Detects card insertion using photo sensor

Reads UID

Looks up student details

Displays:
✔ Name
✔ Roll
✔ Status

Logs attendance in attendance.csv

# CSV File Formats
students.csv
uid,name,roll
3231221233,John Doe,CS01

attendance.csv
timestamp,uid,name,roll,status
2025-01-05T09:15:30,3231221233,John Doe,CS01,present

# Hotspot Configuration

hotspot.conf lets Raspberry Pi create a hotspot:

SSID       : Smart-Attendance
Password   : 12345678
IP Address : 192.168.4.1


You can access it using:

http://192.168.4.1:8000


(If you add a web server later)

# Project Purpose

This project removes the need for manual attendance. It provides:

Accurate record-keeping

Faster attendance taking

RFID-based identity verification

Offline mode using hotspot

# Author

Shami Dubey
SGSITS,Indore