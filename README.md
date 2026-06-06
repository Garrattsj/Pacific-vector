# PACIFIC VECTOR — Setup Guide

## What This Does
Generates your daily Japan geopolitical brief as a clean HTML file you can open in any browser or paste into Beehiiv.

---

## One-Time Setup (10 minutes)

### 1. Install Python
Check if you have it: open Terminal and type `python3 --version`
If not: download from python.org

### 2. Install dependencies
In Terminal, run:
```
pip3 install requests
```

### 3. Add your API keys
Open `pacific_vector.py` in any text editor and replace:
- `YOUR_ANTHROPIC_KEY_HERE` → your Anthropic API key
- `YOUR_NEWSAPI_KEY_HERE`   → your NewsAPI key

Or set them as environment variables (more secure):
```
export ANTHROPIC_API_KEY="your-key-here"
export NEWS_API_KEY="your-key-here"
```

---

## Running It Each Morning

In Terminal, navigate to this folder and run:
```
python3 pacific_vector.py
```

It takes about 30–60 seconds. When done it prints the path to your HTML file.

Open the HTML file in your browser — that's your brief.

---

## Posting to Beehiiv

1. Open the generated HTML file in your browser
2. Select all (Cmd+A), copy (Cmd+C)
3. In Beehiiv → New Post → paste
4. Adjust formatting if needed → Publish

Or: open the .html file in a text editor, copy the raw HTML, and paste into Beehiiv's HTML editor for a cleaner import.

---

## Output Files
Each run creates two files in the `/output` folder:
- `pacific_vector_YYYY-MM-DD.html` — your brief (open this)
- `pacific_vector_YYYY-MM-DD.json` — raw data (useful later for email)

---

## Automating at 7am (Once You're Happy With It)

### Mac:
Use crontab. In Terminal:
```
crontab -e
```
Add this line:
```
0 7 * * * cd /path/to/pacific_vector && python3 pacific_vector.py
```

### Windows:
Use Task Scheduler — set it to run `python3 pacific_vector.py` daily at 7:00 AM.

---

## Troubleshooting

**"Module not found"** → run `pip3 install requests`
**"Invalid API key"** → double-check your keys in the script
**Empty sections** → NewsAPI free tier has rate limits; try again in an hour
**JSON parse error** → rare; just run it again

---

## Next Steps (When Ready)
- Auto-email via Beehiiv API
- Archive page showing all past briefs
- Expand to cover additional countries
- Add a web interface so others can subscribe
