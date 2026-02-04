# Signal Desktop

> **Smart LinkedIn Post Filtering - No Extension Required**

Signal Desktop is a standalone application that helps you filter LinkedIn posts by relevance, engagement, and recency. No browser extension needed - works via a simple bookmarklet.

![Signal Desktop](https://img.shields.io/badge/Version-2.1-purple)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

| Feature | Description |
|---------|-------------|
| Topic Matching | Filter posts by your interests (AI, Cybersecurity, etc.) |
| Engagement Filter | Hide posts with low engagement (configurable) |
| Recency Filter | Focus on recent posts only |
| Visual Scores | See 0-100 scores on every post |
| Desktop App | Native window, no browser extension |
| Privacy First | 100% local, no data sent anywhere |

---

## Installation

### Option 1: Run from Source

**Requirements:**
- Python 3.8 or higher
- pip (Python package manager)

**Steps:**

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

### Option 2: Use the Executable

Download `Signal-Desktop.exe` from Releases and double-click to run.

---

## How to Use

1. **Launch Signal Desktop** - Run `python main.py` or double-click the executable

2. **Configure Your Topics** - Add topics you care about (AI Governance, Cybersecurity, etc.)

3. **Set Your Filters** - Minimum likes, time window, highlight threshold

4. **Copy the Bookmarklet** - Click "Copy Bookmarklet to Clipboard"

5. **Create a Bookmark** - In your browser, create a new bookmark and paste the code as the URL

6. **Use on LinkedIn** - Go to linkedin.com and click your Signal bookmark

---

## Understanding Scores

| Score | Badge | Meaning |
|-------|-------|---------|
| 70-100 | High Signal | Must read! Matches your topics + high engagement |
| 50-69 | Relevant | Worth a look |
| 30-49 | Low Signal | Might be interesting |
| 0-29 | Low Relevance | Dimmed - probably skip |

---

## Default Topics

- AI Governance
- Cybersecurity
- Leadership
- Digital Transformation
- Startups
- SMB Technology

You can add or remove topics in the app.

---

## Building the Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build
pyinstaller --onefile --windowed --name Signal-Desktop main.py

# Executable will be in dist/Signal-Desktop.exe
```

---

## Privacy

Signal Desktop is 100% local:
- No server communication
- No data collection
- No tracking
- Settings stored locally in your home folder

---

## Setup Summary

1. Install Python 3.8+
2. Run `pip install -r requirements.txt`
3. Run `python main.py`
4. Configure topics and copy bookmarklet
5. Use on LinkedIn

---

## License

MIT License - Use freely for personal and commercial purposes.

---

## Credits

Built by Almost Magic Tech Lab

---

## Support

- Issues: GitHub Issues
- Email: support@almostmagic.tech
