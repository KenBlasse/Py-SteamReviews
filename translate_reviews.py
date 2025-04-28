import pandas as pd
from googletrans import Translator as GoogleTranslator
import deepl
import os
import re
import time
from dotenv import load_dotenv

logfile_path = "translation_log.txt"

with open(logfile_path, "w", encoding="utf-8") as logfile:
    logfile.write(f"Übersetzungs-Log gestartet am {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

load_dotenv()

# 💬 DeepL API-Key hier einfügen
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

# DeepL Übersetzer initialisieren
deepl_translator = deepl.Translator(DEEPL_API_KEY)

# Google Übersetzer nur für Sprachenerkennung
google_translator = GoogleTranslator()

# Ordner definieren
input_folder = "originals"
output_folder = "translations"

# Falls Ausgabefolder noch nicht existiert, erstellen
os.makedirs(output_folder, exist_ok=True)

# Statistik
start_time = time.time()
reviewsum = 0
total_recommended = 0
total_not_recommended = 0

# Alle Dateien im Originals-Ordner durchgehen
for filename in os.listdir(input_folder):
    if filename.endswith(".csv"):
        print(f"🔵 Verarbeite Datei: {filename}")

        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, "translated_" + filename)

        df = pd.read_csv(input_path, usecols=["PlayTimeTotal", "Recommended", "Timestamp Created", "ReviewText"])
        total_reviews = len(df)

        # Resümee-Zähler initialisieren
        translated_reviews = 0
        skipped_reviews = 0
        errors = 0
        recommended = 0
        not_recommended = 0

        def clean_html(raw_text):
            cleanr = re.compile('<.*?>')
            cleaned_text = re.sub(cleanr, '', raw_text)
            bbcode = re.compile(r'\[.*?\]')
            cleaned_text = re.sub(bbcode, '', cleaned_text)
            return cleaned_text

        def translate_text(text, index):
            global translated_reviews, skipped_reviews, errors, reviewsum

            reviewsum += 1

            if not isinstance(text, str) or text.strip() == "":
                print(f"⚠️ Überspringe Review {index + 1}: Kein Text vorhanden.")
                skipped_reviews += 1
                return ""

            try:
                cleaned_text = clean_html(text)

                if not cleaned_text.strip():
                    print(f"⚠️ Überspringe Review {index + 1}: Nach Cleaning leer.")
                    skipped_reviews += 1
                    return ""

                if len(cleaned_text) > 4900:
                    print(f"⚠️ Review {index + 1} ist zu lang ({len(cleaned_text)} Zeichen). Text wird abgeschnitten.")
                    cleaned_text = cleaned_text[:4900]

                if not cleaned_text.strip():
                    print(f"⚠️ Review {index + 1}: Nach Kürzen leer. Überspringe.")
                    skipped_reviews += 1
                    return ""

                 # ➡ Sprache erkennen, um DE zu überspringen
                detected_lang = google_translator.detect(cleaned_text).lang
                if detected_lang == 'de':
                    print(f"⚠️ Überspringe Review {index + 1}: Bereits Deutsch erkannt.")
                    skipped_reviews += 1
                    return cleaned_text

                # Jetzt DeepL-Übersetzung in einem Try
                try:
                    result = deepl_translator.translate_text(cleaned_text, target_lang="DE").text
                except Exception as e:
                    print(f"⚠️ DeepL-Übersetzungsfehler bei Review {index + 1}: {e}")
                    errors += 1
                    return ""

                print(f"✅ Review {index + 1} von {total_reviews} übersetzt.")
                translated_reviews += 1
                return result

            except Exception as e:
                print(f"⚠️ Allgemeiner Fehler bei Review {index + 1}: {e}")
                errors += 1
                return ""

        # Neue Spalte für Übersetzungen erzeugen
        df["TranslatedReview"] = [
            translate_text(row["ReviewText"], idx) if pd.notna(row["ReviewText"]) else ""
            for idx, row in df.iterrows()
        ]

        # Empfehlungen zählen
        for index, row in df.iterrows():
            if row["Recommended"]:
                total_recommended += 1
                recommended += 1
            else:
                total_not_recommended += 1
                not_recommended += 1

        # Original-Review-Spalten entfernen
        df = df.drop(columns=["Recommended", "ReviewText"])

        # Übersetzte Datei speichern
        df.to_csv(output_path, index=False)
        print(f"✅ Übersetzt und gespeichert: {output_path}")

        # Resümee für diese Datei
        print("\n📋 Resümee für Datei:", filename)
        print(f"   - Reviews gesamt: {total_reviews}")
        print(f"   - Erfolgreich übersetzt: {translated_reviews}")
        print(f"   - Übersprungen: {skipped_reviews}")
        print(f"   - Fehler während Übersetzung: {errors}")
        print(f"   - Empfohlen: {recommended}")
        print(f"   - Nicht empfohlen: {not_recommended}\n")

        with open(logfile_path, "a", encoding="utf-8") as logfile:
            logfile.write(f"📋 Resümee für Datei: {filename}\n")
            logfile.write(f"   - Reviews gesamt: {total_reviews}\n")
            logfile.write(f"   - Erfolgreich übersetzt: {translated_reviews}\n")
            logfile.write(f"   - Übersprungen: {skipped_reviews}\n")
            logfile.write(f"   - Fehler während Übersetzung: {errors}\n")
            logfile.write(f"   - Empfohlen: {recommended}\n")
            logfile.write(f"   - Nicht empfohlen: {not_recommended}\n\n")



# Abschlussstatistik
end_time = time.time()
duration = end_time - start_time

print(f"\n🎉 Alle Dateien verarbeitet! Gesamtreviews: {reviewsum}, Gesamtdauer: {round(duration, 2)} Sekunden")
print(f"     Empfohlen: {total_recommended}, nicht empfohlen: {total_not_recommended}")

with open(logfile_path, "a", encoding="utf-8") as logfile:
    logfile.write("\n🎉 Alle Dateien verarbeitet!\n")
    logfile.write(f"Gesamtreviews: {reviewsum}\n")
    logfile.write(f"Gesamtdauer: {round(duration, 2)} Sekunden\n")
    logfile.write(f"Empfohlen: {total_recommended}\n")
    logfile.write(f"Nicht empfohlen: {total_not_recommended}\n")