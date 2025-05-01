# logger_utils.py
import time
import os

LOGFILE_PATH = "translation_log.txt"

def init_logfile(game_id: str) -> str:
    os.makedirs("logs", exist_ok=True)
    logfile_path = f"logs/translation_log_{game_id}.txt"
    with open(logfile_path, "w", encoding="utf-8") as logfile:
        logfile.write(f"Übersetzungs-Log für App-ID {game_id} gestartet am {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    return logfile_path

def append_log(logfile_path: str, message: str):
    with open(logfile_path, "a", encoding="utf-8") as logfile:
        logfile.write(message + "\n")