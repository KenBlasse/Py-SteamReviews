# logger_utils.py
import time

LOGFILE_PATH = "translation_log.txt"

def init_logfile():
    with open(LOGFILE_PATH, "w", encoding="utf-8") as f:
        f.write(f"Übersetzungs-Log gestartet am {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

def append_log(text):
    with open(LOGFILE_PATH, "a", encoding="utf-8") as f:
        f.write(text + "\n")