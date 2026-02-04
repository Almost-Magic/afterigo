# Signal Desktop - User Manual

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Configuring Topics](#configuring-topics)
4. [Setting Filters](#setting-filters)
5. [Using the Bookmarklet](#using-the-bookmarklet)
6. [Understanding Scores](#understanding-scores)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Installation

### Method 1: Run from Source (Recommended for Developers)

**Requirements:**
- Python 3.8 or higher
- pip (Python package manager)

**Steps:**

1. Download or clone the repository
2. Open a terminal in the project folder
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the app:
   ```
   python main.py
   ```

### Method 2: Use Pre-built Executable (Easiest)

1. Download `Signal-Desktop.exe` from GitHub Releases
2. Double-click to run
3. No installation needed!

---

## Getting Started

When you launch Signal Desktop, you will see:

1. **Topics Section** - Your interests for filtering
2. **Filters Section** - Engagement and recency settings
3. **Bookmarklet Section** - The code to use on LinkedIn

---

## Configuring Topics

### Adding a Topic

1. Type the topic name in the input field
2. Click "Add" or press Enter
3. The topic appears in your list

**Good topics to add:**
- Industry terms: "FinTech", "HealthTech", "EdTech"
- Technologies: "Machine Learning", "Kubernetes", "React"
- Roles: "Product Management", "Sales Leadership"

### Removing a Topic

1. Find the topic in your list
2. Click the X button next to it
3. The topic is removed

### Default Topics

Signal comes with these defaults:
- AI Governance
- Cybersecurity
- Leadership
- Digital Transformation
- Startups
- SMB Technology

Click "Reset to Defaults" to restore these.

---

## Setting Filters

### Minimum Likes

Posts with fewer likes than this will be dimmed.

| Setting | Best For |
|---------|----------|
| 5+ likes | See more content |
| 10+ likes | Balanced (default) |
| 25+ likes | Quality focus |
| 50+ likes | Only viral posts |

### Time Window

How recent posts should be to avoid dimming.

| Setting | Best For |
|---------|----------|
| Last week | Fresh content only |
| Last 2 weeks | Balanced (default) |
| Last month | Catch up on older posts |

### Highlight Top

What percentage of posts get the green highlight.

| Setting | Best For |
|---------|----------|
| Top 10% | Very selective |
| Top 20% | Balanced (default) |
| Top 30% | More highlights |

---

## Using the Bookmarklet

### What is a Bookmarklet?

A bookmarklet is a bookmark that runs code instead of opening a webpage. It is safe and does not require any browser extension.

### Creating the Bookmark

**Chrome/Edge:**
1. Click "Copy Bookmarklet to Clipboard" in Signal Desktop
2. Press Ctrl+Shift+B to show bookmarks bar
3. Right-click the bookmarks bar and select "Add page"
4. Name: Signal
5. URL: Paste the copied code
6. Click Save

**Firefox:**
1. Click "Copy Bookmarklet to Clipboard"
2. Press Ctrl+B to open bookmarks
3. Right-click and select "New Bookmark"
4. Name: Signal
5. Location: Paste the copied code
6. Click Add

### Using on LinkedIn

1. Go to linkedin.com
2. Navigate to your feed
3. Click the Signal bookmark
4. Watch posts get scored!

**Note:** You need to click the bookmark once per LinkedIn session.

---

## Understanding Scores

### How Scoring Works

Each post gets a score from 0-100 based on:

| Factor | Weight | What It Measures |
|--------|--------|------------------|
| Topic Match | 50% | Does the post match your topics? |
| Engagement | 35% | How many likes/comments? |
| Base Score | 15% | Baseline relevance |

### Score Meanings

| Score | Display | Meaning |
|-------|---------|---------|
| 70-100 | Green highlight | High signal - read this! |
| 50-69 | Normal | Relevant content |
| 30-49 | Normal | Lower relevance |
| 0-29 | Dimmed | Probably skip |

### What Gets Dimmed

Posts are automatically dimmed if:
- They have fewer likes than your minimum setting
- They are older than your time window
- Their score is below 30

---

## Troubleshooting

### App will not start

**Cause:** Missing Python or dependencies

**Fix:**
1. Make sure Python 3.8+ is installed
2. Run: `pip install -r requirements.txt`
3. Try again: `python main.py`

### Bookmarklet does not work

**Cause:** Code was not copied correctly

**Fix:**
1. Click "Copy Bookmarklet" again
2. Delete the old bookmark
3. Create a new bookmark
4. Make sure you paste in the URL field, not the Name field

### Posts are not showing scores

**Cause:** LinkedIn changed their page structure

**Fix:**
1. Refresh the LinkedIn page
2. Click the bookmarklet again
3. Scroll slowly to let posts load

### Scores seem wrong

**Cause:** Topics do not match post content

**Fix:**
1. Add more specific topics
2. Check if your topics are too generic
3. The algorithm uses keyword matching, so specific terms work better

---

## FAQ

**Q: Is this safe to use?**

A: Yes! Signal Desktop runs 100% on your computer. Nothing is sent to any server. The code is open source.

**Q: Will LinkedIn ban me?**

A: No. Signal only reads and displays information. It does not automate any actions or violate LinkedIn terms.

**Q: Do I need to click the bookmarklet every time?**

A: Yes, once per LinkedIn session. It stays active while you scroll.

**Q: Can I use this on mobile?**

A: The desktop app is for computers only. The bookmarklet also does not work well on mobile browsers.

**Q: Where are my settings saved?**

A: In your home folder as `.signal_desktop_settings.json`

**Q: Can I share my bookmarklet with others?**

A: Yes! The bookmarklet contains your settings, so others will get your exact configuration.

---

## Support

Need help?

- GitHub Issues: Report a bug at github.com/Almost-Magic/signal-desktop/issues
- Email: support@almostmagic.tech

---

Signal Desktop v2.1 - By Almost Magic Tech Lab
