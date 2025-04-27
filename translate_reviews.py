import pandas as pd
from deep_translator import GoogleTranslator
import os
import re
import time

# Ordner definieren
input_folder = "originals"
output_folder = "translations"

# Falls Ausgabefolder noch nicht existiert, erstellen
os.makedirs(output_folder, exist_ok=True)

#Statistik
start_time = time.time()
reviewsum = 0
recommended = 0
not_recommended = 0

# Alle Dateien im Originals-Ordner durchgehen
for filename in os.listdir(input_folder):
    if filename.endswith(".csv"):
        print(f"🔵 Verarbeite Datei: {filename}")

        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, "translated_" + filename)

        df = pd.read_csv(input_path, usecols=["PlayTimeTotal", "Recommended", "Timestamp Created", "ReviewText", "Recommended"])
        total_reviews = len(df)

        # Resümee-Zähler initialisieren
        translated_reviews = 0
        skipped_reviews = 0
        errors = 0
        
    
        def clean_html(raw_text):
            cleanr = re.compile('<.*?>')
            cleaned_text = re.sub(cleanr, '', raw_text)
            bbcode = re.compile(r'\[.*?\]')
            cleaned_text = re.sub(bbcode, '', cleaned_text)
            return cleaned_text

        if "tchinese" in filename.lower():
            source_language = "zh-TW"
        else:
            source_language = "auto"

        

        def translate_text(text, index):
            global translated_reviews, skipped_reviews, errors, reviewsum, recommended

            reviewsum +=1

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

                if len(cleaned_text) > 4999:
                    print(f"⚠️ Review {index + 1} ist zu lang ({len(cleaned_text)} Zeichen). Text wird abgeschnitten.")
                    cleaned_text = cleaned_text[:4999]

                if len(cleaned_text) > 5000:
                    print(f"⚠️ Review {index + 1}: Selbst nach Kürzen zu lang. Überspringe.")
                    skipped_reviews += 1
                    return ""

                result = GoogleTranslator(source=source_language, target='de').translate(cleaned_text)

                print(f"✅ Review {index + 1} von {total_reviews} übersetzt.")
                translated_reviews += 1
                return result

            except Exception as e:
                print(f"⚠️ Fehler bei Review {index+1}: {e}")
                errors += 1
                return ""

        df["TranslatedReview"] = [
            translate_text(row["ReviewText"], idx) if pd.notna(row["ReviewText"]) else ""
            for idx, row in df.iterrows()
        ]

        
        for index, row in df.iterrows():
            if row["Recommended"]:
                recommended += 1
            else:
                not_recommended += 1


        df = df.drop(columns=["Recommended"])
        df = df.drop(columns=["ReviewText"])

        df.to_csv(output_path, index=False)
        print(f"✅ Übersetzt und gespeichert: {output_path}")

        # Nach jeder Datei Resümee ausgeben
        print("\n📋 Resümee für Datei:", filename)
        print(f"   - Reviews gesamt: {total_reviews}")
        print(f"   - Erfolgreich übersetzt: {translated_reviews}")
        print(f"   - Übersprungen: {skipped_reviews}")
        print(f"   - Fehler während Übersetzung: {errors}\n")
        
    

end_time = time.time()
duration = end_time - start_time

print(f"\n🎉 Alle Dateien verarbeitet! Gesamtreviews: {reviewsum}, Gesamtdauer: {round(duration, 2)} Sekunden")
print(f"     Empfohlen: {recommended}, nicht empfohlen: {not_recommended}")