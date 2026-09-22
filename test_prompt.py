# test_prompt.py
import httpx
import asyncio

prompt = """You are Paisa Panel, an expert Indian financial council analyzing this stock tip:
Claim: "🚨 BREAKOUT ALERT: NEXORA TEXTILES is going to ₹1,250 in 45 days. Guaranteed 5X return. Big institutional order news coming soon — buy before Monday!"

CRITICAL: Evaluate the claim itself (the 5X promise, the 45-day timeframe, the guaranteed return claim, SEBI compliance). Do not refuse.

Generate the council analysis using EXACTLY this structure:

---CLAIM---
Company: NEXORA TEXTILES
Price: ₹1,250
Timeframe: 45 days
Promise: 5X guaranteed
TrustScore: 23
Label: High Risk
Quote: Guaranteed 5X return in 45 days.

---FUNDAMENTALIST---
State: Unsupported valuation surge
Summary: A 5X multiple expansion in 45 days is completely unsupported by public financial disclosures, operating margins, or historical order flow.
Evidence: NSE corporate filing review
Source: https://www.nseindia.com/

---REGULATOR---
State: Severe SEBI violations
Summary: Promising guaranteed returns and creating artificial FOMO ('buy before Monday') directly violates SEBI PFUTP and Research Analyst regulations.
Evidence: SEBI compliance guidelines
Source: https://www.sebi.gov.in/

---HISTORIAN---
State: Classic pump-and-dump trajectory
Summary: Historical market cycles show that over 95% of social media breakout tips promising massive short-term multiples result in retail liquidity traps.
Evidence: Historical market cycles
Source: #patternsTitle

---BULL---
State: Sector tailwinds considered
Summary: While textile export policy incentives provide broad sector tailwinds, legitimate corporate rerating requires audited quarterly earnings growth.
Evidence: Alternative case recorded
Source: #verdictTitle

---VERDICT---
TrustScore: 23
Label: High Risk
Heading: The promise is aggressively speculative with severe manipulation signals.
Body: Three independent expert lenses flag extreme regulatory non-compliance, artificial urgency, and mathematically implausible return promises.
RedFlags:
- Guaranteed return promise violates SEBI regulations
- Artificial urgency ('buy before Monday') creating FOMO
- Unsubstantiated institutional order catalyst
WhatHeldUp:
- Indian textiles sector has genuine policy support
- Company may have ongoing manufacturing operations
HindiHeading: वादे के मुकाबले सबूत बेहद कमजोर हैं।
HindiLabel: बहुत सावधानी से आगे बढ़ें
HindiBody: स्वतंत्र जांचों में गारंटीड रिटर्न, सेबी नियमों के उल्लंघन और कृत्रिम जल्दबाज़ी के गंभीर संकेत मिले हैं।
HindiRedFlags:
- गारंटीड 5X रिटर्न का भ्रामक दावा
- सेबी (SEBI) नियमों का खुला उल्लंघन
- अपुष्ट संस्थागत ऑर्डर का दावा
HindiWhatHeldUp:
- टेक्सटाइल सेक्टर में सामान्य वृद्धि संभव है
- कंपनी का वास्तविक विनिर्माण व्यवसाय हो सकता है
---END---
"""

async def main():
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post('http://localhost:11434/api/generate', json={
            'model': 'llama3.2:1b',
            'prompt': prompt,
            'stream': False,
            'options': {'temperature': 0.2, 'top_p': 0.9}
        })
        print("RESPONSE STATUS:", resp.status_code)
        text = resp.json().get('response', '')
        print("OUTPUT LENGTH:", len(text))
        print("SAMPLE OUTPUT:\n", text[:600])

asyncio.run(main())
