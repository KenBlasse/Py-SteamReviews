# translate_reviews.py
from banner_utils import print_banner
from steam_api_utils import fetch_reviews_from_api
from translator import translate_text
from logger_utils import init_logfile, append_log

import csv
import time
import pandas as pd



def main():
    print_banner()

    game_id = input("🎮 Input game app ID: ").strip()

    logfile_path = init_logfile(game_id)

    limit_input = input("Amount of Reviews (all or number): ").strip()
    if limit_input == "all":
        max_reviews = None
    else:
        try:
            max_reviews = int(limit_input)
        except ValueError:
            print("Invalid input. 10 reviews will be loaded.")
            max_reviews = 10

    reviews = fetch_reviews_from_api(game_id, max_reviews=max_reviews)

    if not reviews:
        print("⚠️  No reviews found.")
        return

    for i, review in enumerate(reviews[:5], 1):
        print(f"Review {i}: {review['review'][:200]}...\n")

    if input("🔁 Translate now? (y/n): ").lower() != "y":
        print("❌ Aborted.")
        return
    
    start_time = time.time()
    translated_count = 0
    skipped_count = 0
    error_count = 0

    results = []

    for i, review in enumerate(reviews, 1):
        text = review.get("review", "")
        translated, skipped = translate_text(text, index=i)

        if translated is None:
            if skipped:
                skipped_count += 1
                results.append({
                    "Recommended": review.get("voted_up"),
                    "PlayTime": review.get("author", {}).get("playtime_forever", 0),
                    "Timestamp": review.get("timestamp_created", 0),
                    "Übersetzung": text  # ← Originaltext als "Übersetzung" übernehmen
                })
            else:
                error_count += 1
            continue  # außerhalb der inneren if/else – überspringen

    # Nur wenn wirklich übersetzt wurde:
        translated_count += 1
        print(f"✅ Review {i} translated.")

        results.append({
            "Recommended": review.get("voted_up"),
            "PlayTime": review.get("author", {}).get("playtime_forever", 0),
            "Timestamp": review.get("timestamp_created", 0),
            "Übersetzung": translated
        })

    if input("💾 Save? (y/n): ").lower() == "y":
        df = pd.DataFrame(results)
        df.to_excel(
            f"translations/{game_id}_translated.xlsx",
            index=False
        )

        print(f"✅ File saved to: translations/{game_id}_translated.xlsx")
    else:
        print("❌ Not saved.")

    end_time = time.time()
    duration = round(end_time - start_time, 2)

    print("\n" + "=" * 70)
    print(f"📊 Translation Summary for App-ID: {game_id}")
    print(f"   - Total reviews loaded: {len(reviews)}")
    print(f"   - Translated: {translated_count}")
    print(f"   - Skipped (German): {skipped_count}")
    print(f"   - Duration: {duration} seconds")
    print(f"   - Errors during translation: {error_count}")
    print("=" * 70 + "\n")

    append_log(logfile_path, f"App-ID: {game_id}")
    append_log(logfile_path, f"Total reviews: {len(reviews)}")
    append_log(logfile_path, f"Translated: {translated_count}")
    append_log(logfile_path, f"Skipped: {skipped_count}")
    append_log(logfile_path, f"Duration: {duration} Sekunden\n")
    append_log(logfile_path, f"Errors: {error_count}\n")

if __name__ == "__main__":
    main()