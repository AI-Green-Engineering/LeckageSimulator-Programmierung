import serial
import time

# ------------------------------------------------------------
# 20260401 - Weibull MP Programm 5
# ------------------------------------------------------------
# Intervall: 5
# Obere Intervallgrenze: 41.573140 Mio. Zyklen
# Öffnungsdauer: 8.35 min
# Haltezeit auf maximaler Öffnung: 30 s
# Tickdauer: 2.0 s
# Anzahl Takte: 250
# Geplante Gesamtöffnung: 1600 Schritte
#
# Befehlslogik:
#   R        = Referenzfahrt
#   2300z    = Ventil um 2300 Schritte schließen
#   na       = Ventil um n Schritte öffnen
#   nz       = Ventil um n Schritte schließen
#
# Ablauf:
#   1) Referenzfahrt
#   2) Ventil vollständig schließen
#   3) Exponentiell ansteigende Öffnung in diskreten 2-s-Takten
#   4) Maximale Öffnung 30 s halten
#   5) Exakt dieselbe insgesamt geöffnete Schrittzahl wieder schließen
# ------------------------------------------------------------

PORT = "/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_ETCRj137C01-if00-port0"
BAUDRATE = 9600
USE_SERIAL = True

REFERENCE_SLEEP_S = 8
CLOSE_SLEEP_S = 5
TICK_SECONDS = 2.0
HOLD_AT_MAX_S = 30
FINAL_CLOSE_SLEEP_S = 5

# ------------------------------------------------------------
# Schrittfolge pro Tick
# ------------------------------------------------------------
steps_per_tick = [
    1, 2, 1, 2, 1, 2, 1, 2, 1, 2,
    2, 1, 2, 2, 1, 2, 2, 1, 2, 2,
    1, 2, 2, 2, 2, 1, 2, 2, 2, 2,
    2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
    3, 2, 2, 2, 2, 3, 2, 2, 2, 3,
    2, 3, 2, 2, 3, 2, 3, 2, 3, 3,
    2, 3, 3, 2, 3, 3, 3, 2, 3, 3,
    3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
    4, 3, 3, 3, 4, 3, 3, 4, 3, 4,
    3, 4, 4, 3, 4, 4, 3, 4, 4, 4,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 5,
    4, 4, 5, 4, 5, 4, 5, 5, 4, 5,
    5, 5, 4, 5, 5, 5, 5, 6, 5, 5,
    5, 6, 5, 5, 6, 5, 6, 6, 5, 6,
    6, 6, 6, 6, 6, 6, 6, 6, 7, 6,
    7, 6, 7, 6, 7, 7, 7, 7, 7, 7,
    7, 7, 7, 8, 7, 7, 8, 8, 7, 8,
    8, 8, 8, 8, 8, 9, 8, 8, 9, 9,
    8, 9, 9, 9, 9, 9, 9, 10, 9, 10,
    9, 10, 10, 10, 10, 10, 10, 10, 11, 10,
    11, 11, 10, 11, 11, 12, 11, 11, 12, 11,
    12, 12, 12, 12, 12, 13, 12, 13, 12, 13,
    13, 13, 14, 13, 13, 14, 14, 14, 14, 14,
    14, 15, 14, 15, 15, 15, 16, 15, 15, 16,
    16, 16, 16, 16, 17, 17, 16, 17, 18, 17,
]

assert len(steps_per_tick) == 250, "Es müssen genau 250 Takte sein."
assert sum(steps_per_tick) == 1600, "Die Schrittfolge muss insgesamt 1600 Schritte ergeben."

def send_command(ser, cmd: str):
    print(f"SENDE: {cmd}")
    if ser is not None:
        ser.write(cmd.encode("utf-8") + b"\r\n")

ser = None

try:
    if USE_SERIAL:
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        time.sleep(2)

    # 1) Referenzfahrt
    send_command(ser, "R")
    time.sleep(REFERENCE_SLEEP_S)

    # 2) Ventil vollständig schließen
    send_command(ser, "2300z")
    time.sleep(CLOSE_SLEEP_S)

    # 3) Exponentieller Degradationsverlauf
    opened_steps = 0
    for i, step_count in enumerate(steps_per_tick, start=1):
        if step_count > 0:
            cmd = f"{step_count}a"
            send_command(ser, cmd)
            opened_steps += step_count
            print(f"Takt {i:03d}/250 | Öffne um {step_count:2d} Schritte | kumulativ offen: {opened_steps}")
        else:
            print(f"Takt {i:03d}/250 | keine Bewegung | kumulativ offen: {opened_steps}")
        time.sleep(TICK_SECONDS)

    print(f"Gesamt geöffnete Schritte: {opened_steps}")

    # 4) Maximale Öffnung halten
    time.sleep(HOLD_AT_MAX_S)

    # 5) Rückfahrt um genau die geöffnete Schrittzahl
    if opened_steps > 0:
        send_command(ser, f"{opened_steps}z")
        time.sleep(FINAL_CLOSE_SLEEP_S)

finally:
    if ser is not None:
        ser.close()
        print("Serielle Verbindung geschlossen.")
