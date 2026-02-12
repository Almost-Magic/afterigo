"""KnowYourself — Question banks for all assessments.

Big Five: 50 IPIP items (public domain, ipip.ori.org).
Archetype: 24 forced-choice items.
Consciousness: 10 Likert items.
Daily Inquiry: rotating prompts.
"""

# ============================================================
# BIG FIVE — 50 IPIP items (public domain)
# ============================================================
# Keyed: + = positive, R = reverse-keyed
# Order: E, A, C, N, O (repeating every 5 items)

BIG_FIVE_QUESTIONS = [
    # 1-5
    {"id": 1, "text": "I am the life of the party.", "trait": "E", "keyed": "+"},
    {"id": 2, "text": "I feel little concern for others.", "trait": "A", "keyed": "R"},
    {"id": 3, "text": "I am always prepared.", "trait": "C", "keyed": "+"},
    {"id": 4, "text": "I get stressed out easily.", "trait": "N", "keyed": "+"},
    {"id": 5, "text": "I have a rich vocabulary.", "trait": "O", "keyed": "+"},
    # 6-10
    {"id": 6, "text": "I don't talk a lot.", "trait": "E", "keyed": "R"},
    {"id": 7, "text": "I am interested in people.", "trait": "A", "keyed": "+"},
    {"id": 8, "text": "I leave my belongings around.", "trait": "C", "keyed": "R"},
    {"id": 9, "text": "I am relaxed most of the time.", "trait": "N", "keyed": "R"},
    {"id": 10, "text": "I have difficulty understanding abstract ideas.", "trait": "O", "keyed": "R"},
    # 11-15
    {"id": 11, "text": "I feel comfortable around people.", "trait": "E", "keyed": "+"},
    {"id": 12, "text": "I insult people.", "trait": "A", "keyed": "R"},
    {"id": 13, "text": "I pay attention to details.", "trait": "C", "keyed": "+"},
    {"id": 14, "text": "I worry about things.", "trait": "N", "keyed": "+"},
    {"id": 15, "text": "I have a vivid imagination.", "trait": "O", "keyed": "+"},
    # 16-20
    {"id": 16, "text": "I keep in the background.", "trait": "E", "keyed": "R"},
    {"id": 17, "text": "I sympathise with others' feelings.", "trait": "A", "keyed": "+"},
    {"id": 18, "text": "I make a mess of things.", "trait": "C", "keyed": "R"},
    {"id": 19, "text": "I seldom feel blue.", "trait": "N", "keyed": "R"},
    {"id": 20, "text": "I am not interested in abstract ideas.", "trait": "O", "keyed": "R"},
    # 21-25
    {"id": 21, "text": "I start conversations.", "trait": "E", "keyed": "+"},
    {"id": 22, "text": "I am not interested in other people's problems.", "trait": "A", "keyed": "R"},
    {"id": 23, "text": "I get chores done right away.", "trait": "C", "keyed": "+"},
    {"id": 24, "text": "I am easily disturbed.", "trait": "N", "keyed": "+"},
    {"id": 25, "text": "I have excellent ideas.", "trait": "O", "keyed": "+"},
    # 26-30
    {"id": 26, "text": "I have little to say.", "trait": "E", "keyed": "R"},
    {"id": 27, "text": "I have a soft heart.", "trait": "A", "keyed": "+"},
    {"id": 28, "text": "I often forget to put things back in their proper place.", "trait": "C", "keyed": "R"},
    {"id": 29, "text": "I get upset easily.", "trait": "N", "keyed": "+"},  # Note: keyed + not R for item 29
    {"id": 30, "text": "I do not have a good imagination.", "trait": "O", "keyed": "R"},
    # 31-35
    {"id": 31, "text": "I talk to a lot of different people at parties.", "trait": "E", "keyed": "+"},
    {"id": 32, "text": "I am not really interested in others.", "trait": "A", "keyed": "R"},
    {"id": 33, "text": "I like order.", "trait": "C", "keyed": "+"},
    {"id": 34, "text": "I change my mood a lot.", "trait": "N", "keyed": "+"},
    {"id": 35, "text": "I am quick to understand things.", "trait": "O", "keyed": "+"},
    # 36-40
    {"id": 36, "text": "I don't like to draw attention to myself.", "trait": "E", "keyed": "R"},
    {"id": 37, "text": "I take time out for others.", "trait": "A", "keyed": "+"},
    {"id": 38, "text": "I shirk my duties.", "trait": "C", "keyed": "R"},
    {"id": 39, "text": "I have frequent mood swings.", "trait": "N", "keyed": "+"},  # keyed + not R
    {"id": 40, "text": "I use difficult words.", "trait": "O", "keyed": "+"},  # keyed + not R
    # 41-45
    {"id": 41, "text": "I don't mind being the centre of attention.", "trait": "E", "keyed": "+"},
    {"id": 42, "text": "I feel others' emotions.", "trait": "A", "keyed": "+"},  # keyed + not R
    {"id": 43, "text": "I follow a schedule.", "trait": "C", "keyed": "+"},
    {"id": 44, "text": "I get irritated easily.", "trait": "N", "keyed": "+"},
    {"id": 45, "text": "I spend time reflecting on things.", "trait": "O", "keyed": "+"},
    # 46-50
    {"id": 46, "text": "I am quiet around strangers.", "trait": "E", "keyed": "R"},
    {"id": 47, "text": "I make people feel at ease.", "trait": "A", "keyed": "+"},
    {"id": 48, "text": "I am exacting in my work.", "trait": "C", "keyed": "+"},  # keyed + not R
    {"id": 49, "text": "I often feel blue.", "trait": "N", "keyed": "+"},
    {"id": 50, "text": "I am full of ideas.", "trait": "O", "keyed": "+"},  # keyed + not R
]


# ============================================================
# JUNGIAN ARCHETYPES — 24 forced-choice items
# ============================================================

ARCHETYPE_QUESTIONS = [
    {"id": 1, "a": "I want to prove my worth through courageous action.", "b": "I want to help and protect those around me.", "a_type": "Hero", "b_type": "Caregiver"},
    {"id": 2, "a": "I seek truth through knowledge and analysis.", "b": "I seek joy through play and humour.", "a_type": "Sage", "b_type": "Jester"},
    {"id": 3, "a": "I feel most alive discovering new places and ideas.", "b": "I feel most alive when I'm in control and leading.", "a_type": "Explorer", "b_type": "Ruler"},
    {"id": 4, "a": "Rules are made to be broken when they don't serve people.", "b": "There is a natural goodness in the world that should be preserved.", "a_type": "Outlaw", "b_type": "Innocent"},
    {"id": 5, "a": "I believe in transformation and making the impossible possible.", "b": "I value authenticity and being relatable to everyone.", "a_type": "Magician", "b_type": "Regular Person"},
    {"id": 6, "a": "Deep connection and intimacy matter most to me.", "b": "Creating something original and lasting matters most to me.", "a_type": "Lover", "b_type": "Creator"},
    {"id": 7, "a": "I rise to challenges and want to be the best.", "b": "I prefer to understand the world deeply before acting.", "a_type": "Hero", "b_type": "Sage"},
    {"id": 8, "a": "Freedom and independence drive my decisions.", "b": "Challenging the status quo drives my decisions.", "a_type": "Explorer", "b_type": "Outlaw"},
    {"id": 9, "a": "I want to create transformative experiences.", "b": "I want to create deep emotional connections.", "a_type": "Magician", "b_type": "Lover"},
    {"id": 10, "a": "Laughter and lightness make life worth living.", "b": "Caring for others gives my life meaning.", "a_type": "Jester", "b_type": "Caregiver"},
    {"id": 11, "a": "I want to build something that lasts and has structure.", "b": "I want to express my unique vision and creativity.", "a_type": "Ruler", "b_type": "Creator"},
    {"id": 12, "a": "I trust in the goodness of people and the world.", "b": "I prefer fitting in and being part of the group.", "a_type": "Innocent", "b_type": "Regular Person"},
    {"id": 13, "a": "I face obstacles head-on with determination.", "b": "I prefer to chart my own path away from the crowd.", "a_type": "Hero", "b_type": "Explorer"},
    {"id": 14, "a": "Understanding the deeper meaning of things drives me.", "b": "Turning visions into reality drives me.", "a_type": "Sage", "b_type": "Magician"},
    {"id": 15, "a": "I question authority and conventional wisdom.", "b": "I use humour to cope with life's difficulties.", "a_type": "Outlaw", "b_type": "Jester"},
    {"id": 16, "a": "I show love through passion and devotion.", "b": "I show love through nurturing and support.", "a_type": "Lover", "b_type": "Caregiver"},
    {"id": 17, "a": "I value order, responsibility, and leadership.", "b": "I value optimism, faith, and simplicity.", "a_type": "Ruler", "b_type": "Innocent"},
    {"id": 18, "a": "I express myself through original work and imagination.", "b": "I express myself through being genuine and down-to-earth.", "a_type": "Creator", "b_type": "Regular Person"},
    {"id": 19, "a": "Strength and mastery define who I am.", "b": "Revolution and disruption define who I am.", "a_type": "Hero", "b_type": "Outlaw"},
    {"id": 20, "a": "Wisdom and contemplation bring me peace.", "b": "Passion and connection bring me peace.", "a_type": "Sage", "b_type": "Lover"},
    {"id": 21, "a": "I'm happiest when exploring the unknown.", "b": "I'm happiest when creating something magical.", "a_type": "Explorer", "b_type": "Magician"},
    {"id": 22, "a": "I use wit and fun to bring people together.", "b": "I use strategy and vision to organise people.", "a_type": "Jester", "b_type": "Ruler"},
    {"id": 23, "a": "I give selflessly to those who need me.", "b": "I build and craft things that express beauty.", "a_type": "Caregiver", "b_type": "Creator"},
    {"id": 24, "a": "I believe the world is fundamentally good.", "b": "I believe the world is for everyone equally.", "a_type": "Innocent", "b_type": "Regular Person"},
]


# ============================================================
# HAWKINS CONSCIOUSNESS — 10 items
# ============================================================

CONSCIOUSNESS_QUESTIONS = [
    {"id": 1, "text": "I generally feel safe and secure in my daily life."},
    {"id": 2, "text": "I take responsibility for my own feelings and reactions."},
    {"id": 3, "text": "I feel willing to learn from my mistakes."},
    {"id": 4, "text": "I feel compassion for people I disagree with."},
    {"id": 5, "text": "I can observe my thoughts without being consumed by them."},
    {"id": 6, "text": "I feel grateful for what I have, even during difficult times."},
    {"id": 7, "text": "I experience moments of deep inner peace."},
    {"id": 8, "text": "I feel connected to something larger than myself."},
    {"id": 9, "text": "I can accept uncertainty without anxiety."},
    {"id": 10, "text": "I feel genuine love and goodwill towards others."},
]


# ============================================================
# DAILY INQUIRY — rotating prompts
# ============================================================

DAILY_PROMPTS = [
    "Who am I today?",
    "What am I avoiding?",
    "What would I do if I weren't afraid?",
    "What am I most grateful for right now?",
    "What pattern keeps repeating in my life?",
    "What would I say to my younger self?",
    "What does my body need right now?",
    "Where am I not being honest with myself?",
    "What brings me alive?",
    "What can I let go of today?",
]
