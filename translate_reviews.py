import pandas as pd
# nicht die beste Übersetzung, aber immerhin verständlich
from deep_translator import GoogleTranslator
import os
import re

# Ordner definieren
input_folder = "originals"
output_folder = "translations"

# Falls Ausgabefolder noch nicht existiert, erstellen
os.makedirs(output_folder, exist_ok=True)


# Alle Dateien im Originals-Ordner durchgehen
for filename in os.listdir(input_folder):
    # nur .csv Dateien werden verarbeitet 
    if filename.endswith(".csv"):
        print(f"Verarbeite Datei: {filename}")
        
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, "translated_" + filename)
        
        # Nur bestimmte Spalten einlesen
        df = pd.read_csv(input_path, usecols=["PlayTimeTotal", "Recommended", "Timestamp Created","ReviewText"])
        # größe der Datei für Übersicht
        total_reviews = len(df)
        
        #HTML-Tags entfernen
        def clean_html(raw_text):
            cleanr = re.compile("<.*?>")
            clean_text = re.sub(cleanr, "", raw_text)
            return clean_text
        
        # Zusatz für tradiotionelles Chinesisch
        if "tchinese" in filename.lower():
            source_language = "zh-TW"
        else:
            source_language = "auto"

        # Übersetzte Reviews hinzufügen
        def translate_text(text, index):
            if not isinstance(text, str) or text.strip() == "":
                print(f"⚠️ Überspringe Review {index + 1}: Kein Text vorhanden.")
                return ""
        
            try:
                cleaned_text = clean_html(text)
                result = GoogleTranslator(source=source_language, target='de').translate(cleaned_text)
                if result:
                    print(f"✅ Review {index+1} von {total_reviews} übersetzt: {text[:15]}... ->{result[:15]}...")
                else:
                    print(f"⚠️ Überspringe Review {index+1} von {total_reviews}: Keine Übersetzung erhalten.")
                    result = ""
                return result
            
            except Exception as e:
                print(f"⚠️ Fehler bei Review {index+1}: {e}")
                return ""
        
        df["TranslatedReview"] = [
            translate_text(row["ReviewText"], idx) if pd.notna(row["ReviewText"]) else ""
            for idx, row in df.iterrows()
        ]
        # entfernen des original Reviews
        df = df.drop(columns=["ReviewText"])
        # Neue Datei speichern
        df.to_csv(output_path, index=False)
        print(f"✅ Übersetzt und gespeichert: {output_path}")

print("✅ Alle Dateien verarbeitet!")