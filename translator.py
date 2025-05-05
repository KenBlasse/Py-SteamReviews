import os
import requests
import uuid
from langdetect import detect
import re
import time
import random

from dotenv import load_dotenv

load_dotenv()

AZURE_KEY = os.getenv("AZURE_KEY")
AZURE_REGION = os.getenv("AZURE_REGION")

endpoint = "https://api.cognitive.microsofttranslator.com"

headers = {
    'Ocp-Apim-Subscription-Key': AZURE_KEY,
    'Ocp-Apim-Subscription-Region': AZURE_REGION,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}



def clean_text(text: str) -> str:
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = text.replace("\n", " ").replace("\r", " ")
    return text.strip()

def translate_text(text: str, index: int) -> tuple[str | None, bool]:
    if not isinstance(text, str) or text.strip() == "":
        return None, False

    cleaned = clean_text(text)
    if not cleaned:
        return None, False

    try:
        if detect(cleaned) == "de":
            print(f"⚠️ Skipping review {index} (already German).")
            return None, True
    except Exception:
        pass

    try:
        url = f"{endpoint}/translate?api-version=3.0&to=de"
        body = [{ 'text': cleaned[:4900] }]
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        translation = response.json()[0]['translations'][0]['text']
        time.sleep(random.uniform(0.3, 0.7))
        return translation, False
    except Exception as e:
        print(f"⚠️ Azure Translation error at review {index}: {e}")
        time.sleep(random.uniform(0.3, 0.7))
        return None, False
    
    