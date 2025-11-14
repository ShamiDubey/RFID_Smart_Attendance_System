#!/usr/bin/env python3
import csv, time, os, subprocess
from datetime import datetime
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from smbus2 import SMBus

# ---------- PATHS ----------
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
STUDENTS_CSV = os.path.join(BASE_DIR, "students.csv")
LOG_CSV      = os.path.join(BASE_DIR, "attendance.csv")

# ---------- CONFIG ----------
PHOTO_PIN    = 17           # Photo-interrupter sensor
LCD_ADDR     = 0x27         # LCD I2C address
DEBOUNCE_SEC = 0.35
SHOW_WELCOME = 1.0
SHOW_NAME    = 1.2
SHOW_ROLL    = 1.2
BUZZ_PIN     = 18           # Buzzer pin

# ---------- LCD CLASS ----------
class LCD:
    def __init__(self, addr=LCD_ADDR, busno=1):
        self.addr = addr
        self.bus = SMBus(busno)
        self._init()

    def _w(self, d):
        self.bus.write_byte(self.addr, d)

    def _stb(self, d):
        self._w(d | 0x04)
        time.sleep(0.0005)
        self._w(d & ~0x04)
        time.sleep(0.0001)

    def _send4(self, data, rs=0):
        v = data | 0x08 | (0x01 if rs else 0)
        self._w(v)
        self._stb(v)

    def cmd(self, c):
        self._send4(c & 0xF0)
        self._send4((c << 4) & 0xF0)

    def chr(self, ch):
        self._send4(ch & 0xF0, 1)
        self._send4((ch << 4) & 0xF0, 1)

    def _init(self):
        time.sleep(0.05)
        for _ in range(3):
            self._send4(0x30)
            time.sleep(0.0045)
        self._send4(0x20)
        for c in (0x28,0x08,0x01,0x06,0x0C):
            self.cmd(c)
            time.sleep(0.002)

    def clear(self):
        self.cmd(0x01)
        time.sleep(0.002)

    def print2(self, l1, l2=""):
        self.clear()
        for ch in l1[:16]:
            self.chr(ord(ch))
        self.cmd(0xC0)
        for ch in l2[:16]:
            self.chr(ord(ch))

# ---------- LOAD STUDENTS ----------
def load_students(path=STUDENTS_CSV):
    data = {}

    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", newline="") as f:
            csv.writer(f).writerow(["uid","name","roll"])

    with open(path, newline="") as f:
        reader = csv.DictReader((line.replace("\x00","") for line in f))
        for row in reader:
            uid = (row.get("uid","") or "").strip()
            if uid:
                data[uid] = {
                    "name": row.get("name","Unknown").strip(),
                    "roll": row.get("roll","").strip()
                }
    return data

# ---------- LOG ATTENDANCE ----------
def log_attendance(uid, name, roll, status="present", path=LOG_CSV):
    new = not os.path.exists(path) or os.path.getsize(path) == 0
    ts = datetime.now().isoformat(timespec="seconds")

    with open(path, "a", newline="") as f:
        writer = csv.writer(f)
        if new:
            writer.writerow(["timestamp","uid","name","roll","status"])
        writer.writerow([ts, uid, name, roll, status])

# ---------- PHOTO SENSOR ----------
def calibrate_photo(pin):
    samples = []
    t0 = time.time()

    while time.time() - t0 < 0.6:
        samples.append(GPIO.input(pin))
        time.sleep(0.02)

    idle = 1 if samples.count(1) >= samples.count(0) else 0
    trig = 0 if idle == 1 else 1
    return idle, trig

# ---------- RFID READ ----------
def read_uid_poll(reader):
    get_nb = getattr(reader, "read_no_block", None)

    if get_nb:
        while True:
            try:
                res = reader.read_no_block()
                if res and res[0]:
                    return str(res[0])
            except:
                pass
            time.sleep(0.08)
    else:
        uid, _ = reader.read()
        return str(uid)

def wait_card_removed(reader):
    get_id_nb = getattr(reader, "read_id_no_block", None)
    if not get_id_nb:
        time.sleep(0.8)
        return

    t0 = time.time()
    while time.time() - t0 < 3.0:
        try:
            if not get_id_nb():
                return
        except:
            return
        time.sleep(0.12)

# ---------- SHOW IP ----------
def show_ip_on_lcd(lcd, seconds=3):
    ip = ""
    private = ("192.","10.","172.16.","172.17.","172.18.","172.19.",
               "172.20.","172.21.","172.22.","172.23.","172.24.",
               "172.25.","172.26.","172.27.","172.28.","172.29.",
               "172.30.","172.31.")

    for _ in range(30):
        try:
            outs = subprocess.check_output("hostname -I", shell=True, text=True).strip().split()
            for cand in outs:
                if cand.startswith(private):
                    ip = cand
                    break
            if ip:
                break
        except:
            pass
        time.sleep(0.5)

    if ip:
        lcd.print2("IP:", ip)
        time.sleep(seconds)
    else:
        lcd.print2("Starting...")
        time.sleep(1)

# ---------- MAIN ----------
def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PHOTO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
    GPIO.setup(BUZZ_PIN, GPIO.OUT)

    def beep(n=3, on=0.12, off=0.08):
        for _ in range(n):
            GPIO.output(BUZZ_PIN, 1)
            time.sleep(on)
            GPIO.output(BUZZ_PIN, 0)
            time.sleep(off)

    lcd = LCD()
    reader = SimpleMFRC522()
    students = load_students()

    show_ip_on_lcd(lcd, seconds=3)
    lcd.print2("Initializing...", "Keep slot empty")
    time.sleep(0.6)

    idle_level, trigger_level = calibrate_photo(PHOTO_PIN)

    lcd.print2("Attendance Sys", "Ready...")
    last_edge = 0.0

    try:
        while True:
            if GPIO.input(PHOTO_PIN) == trigger_level:
                now = time.time()
                if now - last_edge < DEBOUNCE_SEC:
                    time.sleep(0.02)
                    continue

                last_edge = now

                lcd.print2("Scan your id", "card")
                beep(3)

                uid = read_uid_poll(reader)
                stu = students.get(uid)

                if stu:
                    name = stu["name"]
                    roll = stu.get("roll","")

                    lcd.print2("Welcome", "")
                    time.sleep(SHOW_WELCOME)

                    lcd.print2(name, "")
                    time.sleep(SHOW_NAME)

                    lcd.print2("Roll:", roll)
                    time.sleep(SHOW_ROLL)

                else:
                    name, roll = "Unknown", ""
                    lcd.print2("Unknown", "Enroll first")
                    beep(3, on=0.08, off=0.05)
                    time.sleep(1.2)

                log_attendance(uid, name, roll)
                wait_card_removed(reader)

                lcd.print2("Attendance Sys", "Ready...")

            time.sleep(0.02)

    except KeyboardInterrupt:
        pass

    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
