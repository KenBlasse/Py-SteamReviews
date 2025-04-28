# Py-SteamReviews

🛠️ A Python tool to automatically translate and analyze Steam reviews from CSV files.

---

## Features

- Automatically translates Steam reviews into German using the DeepL API
- Detects and skips reviews that are already written in German
- Removes HTML and BBCode tags from the review texts
- Handles very long reviews (cut off at 4900 characters if necessary)
- Detailed logging of all results into a log file
- Provides statistics on recommended and not recommended reviews

---

## Requirements

- Python 3.12 or newer
- Installed Python packages:
  - `pandas`
  - `deepl`
  - `googletrans`
  - `python-dotenv`

---

## Install the required packages using:

```bash
pip install pandas deepl googletrans python-dotenv
```

---

## Usage

1. Create a .env file and add your DeepL API key:

```.env
DEEPL_API_KEY=your_api_key_here
```

2. Place your CSV files with Steam reviews inside the originals/ folder.

3. Run the script:

``` bash
python translate_reviews.py
```

The translated files will be saved into the translations/ folder.
A detailed log file (translation_log.txt) will also be generated automatically.

---

## Future Improvements:

- Direct Steam review fetching via the Steam API

- Web interface for easier interaction

- Support for multiple target languages
