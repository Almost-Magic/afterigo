"""Seed Touchstone with realistic demo data for dashboard development.

Usage: cd backend && python -m seed
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import text
from app.database import engine, async_session
from app.models.contact import Contact
from app.models.campaign import Campaign
from app.models.touchpoint import Touchpoint
from app.models.deal import Deal
from app.models.attribution import Attribution


CAMPAIGNS = [
    {"name": "AI Governance Webinar", "channel": "email", "budget": Decimal("500")},
    {"name": "LinkedIn Thought Leadership", "channel": "social", "budget": Decimal("1200")},
    {"name": "Case Study Downloads", "channel": "organic", "budget": Decimal("300")},
    {"name": "Google Ads — CRM Software", "channel": "paid", "budget": Decimal("8000")},
    {"name": "Partner Referral Program", "channel": "referral", "budget": Decimal("2000")},
]

CHANNELS = ["paid", "email", "social", "organic", "referral", "direct"]
SOURCES = ["google", "linkedin", "facebook", "newsletter", "partner-site", "direct"]
MEDIUMS = ["cpc", "email", "social", "organic", "referral", None]
PAGES = [
    "/", "/pricing", "/about", "/features", "/demo",
    "/blog/ai-governance", "/blog/crm-for-smbs",
    "/case-studies", "/contact", "/webinar",
]
COMPANIES = [
    "Acme Corp", "Tech Solutions", "Digital Forge", "Nexus AI", "Green Energy Co",
    "Health First", "Edu Systems", "RetailPro", "SafeGuard Cyber", "DataPulse",
]
FIRST_NAMES = [
    "Alex", "Jordan", "Sam", "Taylor", "Morgan",
    "Casey", "Riley", "Avery", "Quinn", "Drew",
]
LAST_NAMES = [
    "Chen", "Patel", "Kim", "Singh", "Williams",
    "Brown", "Garcia", "Mueller", "Santos", "Nakamura",
]
DEAL_TYPES = [
    "CRM Setup", "AI Governance Audit", "Security Assessment",
    "Digital Transformation", "Data Strategy",
]


async def seed():
    async with async_session() as db:
        # Check if seed data already exists
        check = await db.execute(text("SELECT COUNT(*) FROM touchstone_campaigns"))
        count = check.scalar()
        if count > 0:
            print(f"Database already has {count} campaigns. Skipping seed.")
            print("To re-seed: DELETE FROM touchstone_attributions; DELETE FROM touchstone_deals; DELETE FROM touchstone_touchpoints; DELETE FROM touchstone_contacts; DELETE FROM touchstone_campaigns;")
            return

        random.seed(42)  # Reproducible

        # 1. Create 5 campaigns
        campaigns = []
        for c in CAMPAIGNS:
            start = datetime.now(timezone.utc) - timedelta(days=random.randint(45, 90))
            campaign = Campaign(
                name=c["name"],
                channel=c["channel"],
                budget=c["budget"],
                currency="AUD",
                start_date=start.date(),
                end_date=(start + timedelta(days=60)).date(),
            )
            db.add(campaign)
            campaigns.append(campaign)
        await db.flush()

        # 2. Create 50 contacts
        contacts = []
        for i in range(50):
            company = COMPANIES[i % len(COMPANIES)]
            first = FIRST_NAMES[i % len(FIRST_NAMES)]
            last = LAST_NAMES[i // len(FIRST_NAMES) % len(LAST_NAMES)]
            slug = company.lower().replace(" ", "")
            contact = Contact(
                anonymous_id=uuid.uuid4().hex[:16],
                email=f"{first.lower()}.{last.lower()}{i}@{slug}.com",
                name=f"{first} {last}",
                company=company,
                identified_at=datetime.now(timezone.utc) - timedelta(
                    days=random.randint(5, 60)
                ),
            )
            db.add(contact)
            contacts.append(contact)
        await db.flush()

        # 3. Create touchpoints (3-15 per contact, spread over 60 days)
        tp_count_total = 0
        for contact in contacts:
            tp_count = random.randint(3, 15)
            base_time = datetime.now(timezone.utc) - timedelta(
                days=random.randint(30, 60)
            )
            for j in range(tp_count):
                tp_time = base_time + timedelta(
                    days=j * random.uniform(0.5, 5),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                )
                campaign = random.choice(campaigns) if random.random() > 0.3 else None
                channel = campaign.channel if campaign else random.choice(CHANNELS)
                source = random.choice(SOURCES)
                medium = random.choice(MEDIUMS)
                tp = Touchpoint(
                    contact_id=contact.id,
                    anonymous_id=contact.anonymous_id,
                    campaign_id=campaign.id if campaign else None,
                    channel=channel,
                    source=source,
                    medium=medium,
                    utm_campaign=(
                        campaign.name.lower().replace(" ", "-").replace("—", "-")
                        if campaign
                        else None
                    ),
                    touchpoint_type=random.choice([
                        "page_view", "page_view", "page_view",
                        "form_submit", "button_click",
                    ]),
                    page_url=f"https://almostmagic.net.au{random.choice(PAGES)}",
                    referrer_url=(
                        f"https://{source}.com" if source != "direct" else None
                    ),
                    timestamp=tp_time,
                )
                db.add(tp)
                tp_count_total += 1

        # 4. Create deals: 20 won, 10 lost, 10 open (first 40 contacts)
        deal_contacts = contacts[:40]
        random.shuffle(deal_contacts)
        deals_created = {"won": 0, "lost": 0, "open": 0}
        for i, contact in enumerate(deal_contacts):
            if i < 20:
                stage = "won"
                amount = Decimal(str(random.randint(5, 150) * 1000))
                closed_at = datetime.now(timezone.utc) - timedelta(
                    days=random.randint(1, 20)
                )
            elif i < 30:
                stage = "lost"
                amount = Decimal(str(random.randint(5, 100) * 1000))
                closed_at = datetime.now(timezone.utc) - timedelta(
                    days=random.randint(1, 15)
                )
            else:
                stage = "open"
                amount = Decimal(str(random.randint(10, 200) * 1000))
                closed_at = None

            deal = Deal(
                contact_id=contact.id,
                crm_deal_id=f"SEED-{uuid.uuid4().hex[:8].upper()}",
                deal_name=f"{contact.company} — {random.choice(DEAL_TYPES)}",
                amount=amount,
                currency="AUD",
                stage=stage,
                closed_at=closed_at,
                crm_source="ripple",
            )
            db.add(deal)
            deals_created[stage] += 1

        await db.commit()

        print(f"Seeded successfully:")
        print(f"  {len(campaigns)} campaigns")
        print(f"  {len(contacts)} contacts")
        print(f"  {tp_count_total} touchpoints")
        print(f"  40 deals ({deals_created['won']} won, {deals_created['lost']} lost, {deals_created['open']} open)")
        print()
        print("Now run attribution for all 5 models:")
        print('  curl -X POST http://localhost:8200/api/v1/attribution/calculate -H "Content-Type: application/json" -d \'{"model": "first_touch"}\'')
        print('  curl -X POST http://localhost:8200/api/v1/attribution/calculate -H "Content-Type: application/json" -d \'{"model": "last_touch"}\'')
        print('  curl -X POST http://localhost:8200/api/v1/attribution/calculate -H "Content-Type: application/json" -d \'{"model": "linear"}\'')
        print('  curl -X POST http://localhost:8200/api/v1/attribution/calculate -H "Content-Type: application/json" -d \'{"model": "time_decay"}\'')
        print('  curl -X POST http://localhost:8200/api/v1/attribution/calculate -H "Content-Type: application/json" -d \'{"model": "position_based"}\'')


if __name__ == "__main__":
    asyncio.run(seed())
