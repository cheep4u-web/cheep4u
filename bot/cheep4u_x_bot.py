# Datei: cheep4u_grok_bot.py
import tweepy
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# === X API ===
client = tweepy.Client(
    bearer_token=os.getenv('X_BEARER_TOKEN'),
    consumer_key=os.getenv('X_API_KEY'),
    consumer_secret=os.getenv('X_API_SECRET'),
    access_token=os.getenv('X_ACCESS_TOKEN'),
    access_token_secret=os.getenv('X_ACCESS_SECRET'),
    wait_on_rate_limit=True
)

# === GROK API (xAI) ===
GROK_API_KEY = os.getenv("GROK_API_KEY")          # Dein Key aus https://x.ai/api
GROK_API_URL = "https://api.x.ai/v1/chat/completions"
GROK_MODEL = os.getenv("GROK_MODEL", "grok-3-mini")  # oder "grok-4"

# === Cheep4u ===
CHEEP4U_API = os.getenv("CHEEP4U_API", "https://cheep4u.com/api/check")

def check_with_grok(text):
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROK_MODEL,
        "messages": [
            {"role": "system", "content": "Du bist Cheep4u-Spatz. Prüfe auf Fake News. Antworte NUR mit: WAHR, FALSCH oder UNSICHER + 1 internationale Quelle (Link). Max 2 Sätze."},
            {"role": "user", "content": text[:8000]}
        ],
        "max_tokens": 80,
        "temperature": 0.3
    }
    try:
        r = requests.post(GROK_API_URL, json=payload, headers=headers, timeout=20)
        r.raise_for_status()
        return r.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"UNSICHER (Grok Fehler: {str(e)[:50]})"

def search_global_truth():
    query = '(("fake news" OR desinformation OR wahrheit OR "fact check" OR misinformation) (lang:de OR lang:en)) min_faves:3 filter:has_engagement -filter:replies'
    tweets = client.search_recent_tweets(query=query, max_results=15, tweet_fields=['author_id', 'public_metrics'])
    return tweets.data or []

def respond_and_save(tweet):
    verdict = check_with_grok(tweet.text)
    username = client.get_user(id=tweet.author_id).data.username
    
    reply = f"@{username} 🐦 Cheep4u x Grok-Check:\n{verdict}\n🔍 Live prüfen: https://cheep4u.com/check/{tweet.id}\n#WahrheitGemeinsam"
    
    try:
        client.create_tweet(text=reply, in_reply_to_tweet_id=tweet.id)
        requests.post(CHEEP4U_API, json={
            "tweet_id": str(tweet.id),
            "text": tweet.text,
            "verdict": verdict,
            "source": "grok_bot"
        })
        print(f"Check gesendet an @{username} | {verdict[:60]}")
    except Exception as e:
        print(f"Fehler bei @{username}: {e}")

# === MAIN LOOP – LEBENDIGES SYSTEM ===
print("Cheep4u + Grok Bot gestartet – jagt die 2% weltweit...")
while True:
    print(f"\n{time.strftime('%H:%M')} | Suche nach Wahrheitssuchern (DE/EN)...")
    for tweet in search_global_truth():
        if tweet.public_metrics['like_count'] >= 3:
            respond_and_save(tweet)
            time.sleep(12)  # Sicherer Abstand für Rate Limits
    time.sleep(3600)  # 1 Stunde Pause – oder 600 für 10-Minuten-Intervall
