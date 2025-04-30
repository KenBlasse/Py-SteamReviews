import requests
import time

def fetch_reviews_from_api(app_id, max_reviews=None):
    print(f"\n🔎 Start fetching game reviews {app_id} ...\n")
    cursor = "*"
    all_reviews = []
    page = 1

    while True:
        url = f"https://store.steampowered.com/appreviews/{app_id}?json=1&num_per_page=100&cursor={cursor}&language=all&filter=recent"
        
        response = requests.get(url)
        
        if not response.ok:
            print("❌ Fehler beim Abruf der API.")
            break

        data = response.json()
        new_reviews = data.get("reviews", [])
        if not new_reviews:
            print("ℹ️ No further reviews found.")
            break

        all_reviews.extend(new_reviews)
        print(f"📄 Seite {page}: {len(new_reviews)} Reviews loaded...")

        if max_reviews and len(all_reviews) >= max_reviews:
            print(f"🔺 Abort: Maximal amount ({max_reviews}) reached.")
            all_reviews = all_reviews[:max_reviews]
            break
        
        if not data.get("cursor"):
            break
        # Cursor vorbereiten
        cursor = data["cursor"]
        page += 1
        time.sleep(1.1)  # API-Schutz (Rate Limit)

    print(f"✅ Total {len(all_reviews)} reviews loaded.\n")
    return all_reviews