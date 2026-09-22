#!/usr/bin/env python3
"""
Paisa Panel — Automated Regression Test Suite (Tests A through G)
Verifies factual accuracy, evidence grounding, 5-entity separation, and scoring logic.
"""

import sys
import unittest
from scoring_engine import compute_exact_score, find_matched_asset, identify_source_entity
from server import extract_claim_details, get_persona_sources

class TestVerificationEngine(unittest.TestCase):

    def test_a_legitimate_institutional_report(self):
        """
        TEST A: Legitimate institutional analyst report
        Goldman Sachs on HAL, BUY, Target ₹5,870
        - Must produce HIGH Trust Score (>=80)
        - Security identified as Hindustan Aeronautics Limited (NOT Goldman Sachs)
        - Source identified as Goldman Sachs
        - Goldman Sachs identified as SEBI-registered
        - HAL NOT identified as unregistered adviser
        - Verdict: VERIFIED
        """
        claim = "Goldman Sachs initiates coverage on HAL (Hindustan Aeronautics Limited) with a BUY recommendation and price target of ₹5,870."
        
        # 1. Scoring Engine Verification
        score_res = compute_exact_score(claim)
        self.assertGreaterEqual(score_res["exact_score"], 80, f"Score should be >= 80, got {score_res['exact_score']}")
        self.assertEqual(score_res["verdict"], "VERIFIED", f"Verdict should be VERIFIED, got {score_res['verdict']}")
        self.assertEqual(score_res["confidence"], "HIGH")

        # 2. Entity Extraction Verification (5-Entity Separation)
        details = extract_claim_details(claim)
        self.assertIn("Hindustan Aeronautics", details["company"], f"Company should be HAL, got {details['company']}")
        self.assertEqual(details["ticker"], "HAL")
        self.assertNotEqual(details["company"], "Goldman Sachs")
        self.assertEqual(details["sourceName"], "Goldman Sachs")
        self.assertIn("SEBI", details["regulatoryStatus"])
        self.assertNotIn("unregistered", details["regulatoryStatus"].lower())

        # 3. Council Persona Verification
        personas = get_persona_sources(details, claim)
        self.assertIn("Claim Analyst", personas["fundamentalist"]["role"])
        self.assertIn("Source Auditor", personas["bull"]["role"])
        self.assertIn("Goldman Sachs", personas["bull"]["summary"])
        self.assertIn("instrument and NOT an adviser", personas["bull"]["summary"])
        print(f"✅ TEST A PASSED: Goldman Sachs on HAL -> Score: {score_res['exact_score']}/100, Verdict: {score_res['verdict']}")

    def test_b_anonymous_telegram_pump(self):
        """
        TEST B: Pure anonymous Telegram pump
        "BUY NOW 100% GUARANTEED MULTIBAGGER! Rocket stock blast tomorrow buy huge qty for big profit don't miss!"
        - Low Trust Score (<=25)
        - Source: Unregistered / anonymous
        - Language risk: maximum penalty
        - Verdict: UNVERIFIED or CONTRADICTED
        """
        claim = "BUY NOW 100% GUARANTEED MULTIBAGGER! Rocket stock blast tomorrow buy huge qty for big profit don't miss!"
        score_res = compute_exact_score(claim)
        self.assertLessEqual(score_res["exact_score"], 25, f"Score should be <= 25, got {score_res['exact_score']}")
        self.assertIn(score_res["verdict"], ["UNVERIFIED", "CONTRADICTED"])
        
        # Check language risk penalty (pillar 5)
        lang_pillar = score_res["pillars"]["language_risk"]
        self.assertLessEqual(lang_pillar["score"], 2, f"Language pillar should be heavily penalized, got {lang_pillar['score']}")
        print(f"✅ TEST B PASSED: Anonymous Telegram Pump -> Score: {score_res['exact_score']}/100, Verdict: {score_res['verdict']}")

    def test_c_historical_sebi_darshan_orna(self):
        """
        TEST C: Historical SEBI regulatory case
        Darshan Orna Limited, BSE: 539884
        - Company: Darshan Orna Limited (NOT BSE Limited)
        - SEBI Adjudication Order cited by name and date
        - Telegram message text accurately represented
        - Verdict: CONTRADICTED
        """
        claim = "DELIVERY BUY CALL JACKPOT....DARSHAN ORNA LTD...BSE CODE 539884 BUY HUGE QTY FOR BIG PROFIT...BUY AT 127-132 MARKET CAP 120CR...1ST TARGET 200....2ND TARGET 250 STOP LOSS 100 SURESHOT CALL"
        
        details = extract_claim_details(claim)
        self.assertEqual(details["company"], "Darshan Orna Limited")
        self.assertNotEqual(details["company"], "BSE Limited")
        self.assertEqual(details["scripCode"], "539884")
        self.assertEqual(details["statedEntryRange"], "₹127–132")
        self.assertEqual(details["stopLoss"], "₹100")
        self.assertTrue(details["isHistorical"])

        score_res = compute_exact_score(claim)
        self.assertEqual(score_res["verdict"], "CONTRADICTED")
        self.assertLessEqual(score_res["exact_score"], 25)

        personas = get_persona_sources(details, claim)
        reg_summary = personas["regulator"]["summary"]
        self.assertIn("SEBI Adjudication Order", reg_summary)
        self.assertIn("July 30, 2025", reg_summary)
        self.assertIn("539884", reg_summary)
        print(f"✅ TEST C PASSED: Darshan Orna Case (BSE: 539884) -> Score: {score_res['exact_score']}/100, Verdict: {score_res['verdict']}")

    def test_d_mixed_claim(self):
        """
        TEST D: Mixed claim (authentic analyst target + forwarded fake return guarantee)
        "Jefferies says buy Zomato target ₹260, 100% return confirmed don't miss double money in 30 days"
        - Target sub-claim: VERIFIED
        - Return guarantee sub-claim: UNVERIFIED / CONTRADICTED
        - Verdict: PARTIALLY VERIFIED
        - Score reflects the mix (~40–60)
        """
        claim = "Jefferies says buy Zomato target ₹260, 100% return confirmed don't miss double money in 30 days"
        
        score_res = compute_exact_score(claim)
        self.assertEqual(score_res["verdict"], "PARTIALLY VERIFIED")
        self.assertTrue(35 <= score_res["exact_score"] <= 65, f"Score should reflect mix (~35-65), got {score_res['exact_score']}")
        
        details = extract_claim_details(claim)
        subclaims = details["subclaims"]
        
        # Check subclaims atomization
        target_sc = next((sc for sc in subclaims if "Target" in sc.get("category", "") or "₹260" in sc.get("claim", "")), None)
        self.assertIsNotNone(target_sc)
        self.assertEqual(target_sc["status"], "VERIFIED")

        guar_sc = next((sc for sc in subclaims if "Guarantee" in sc.get("category", "") or "Certainty" in sc.get("category", "")), None)
        self.assertIsNotNone(guar_sc)
        self.assertIn(guar_sc["status"], ["CONTRADICTED", "UNVERIFIED"])
        print(f"✅ TEST D PASSED: Mixed Claim (Jefferies + Guarantee) -> Score: {score_res['exact_score']}/100, Verdict: {score_res['verdict']}")

    def test_e_missing_evidence_handling(self):
        """
        TEST E: Missing evidence handling
        Claim about a company where historical market data is unavailable
        - Output MUST explicitly state: "Historical market data unavailable" or "Historical outcome could not be independently verified"
        - MUST NOT invent return percentages or drawdown figures
        """
        claim = "Buy XYZ Global Holdings target ₹950 in 30 days"
        details = extract_claim_details(claim)
        personas = get_persona_sources(details, claim)
        
        hist = personas["historian"]
        self.assertEqual(hist["state"], "Historical market data unavailable")
        self.assertIn("Historical outcome could not be independently verified", hist["summary"])
        self.assertIn("unavailable", hist["summary"])
        print(f"✅ TEST E PASSED: Missing Evidence -> Historian State: '{hist['state']}'")

    def test_f_confusable_company_entities(self):
        """
        TEST F: Confusable company entities
        - "Darshan Orna Limited, BSE Code 539884" must NEVER resolve to "BSE Limited"
        - "BSE Limited" must resolve to BSE Limited
        """
        claim1 = "DELIVERY BUY CALL JACKPOT....DARSHAN ORNA LTD...BSE CODE 539884"
        details1 = extract_claim_details(claim1)
        self.assertEqual(details1["company"], "Darshan Orna Limited")
        self.assertNotEqual(details1["company"], "BSE Limited")

        claim2 = "BSE Limited share price target ₹3200 based on transaction revenue growth"
        details2 = extract_claim_details(claim2)
        self.assertEqual(details2["company"], "BSE Limited")
        self.assertEqual(details2["ticker"], "BSE")
        print("✅ TEST F PASSED: Entity Resolution disambiguated Darshan Orna vs BSE Limited.")

    def test_g_unidentified_sources(self):
        """
        TEST G: Unidentified sources
        If source cannot be determined:
        - System states: "Source identity could not be independently verified"
        - Does NOT assume fraud, but does NOT grant credibility
        """
        claim = "Buy Welspun Living at ₹150 target ₹220 stop loss ₹135 for 6 months"
        details = extract_claim_details(claim)
        self.assertIn("could not be independently verified", details["sourceName"])
        
        score_res = compute_exact_score(claim)
        src_breakdown = next(b for b in score_res["breakdown"] if b["category"] == "Source Credibility")
        self.assertIn("could not be independently verified", src_breakdown["detail"])
        self.assertIn("Not assumed fraudulent", src_breakdown["detail"])
        
        personas = get_persona_sources(details, claim)
        bull = personas["bull"]
        self.assertIn("could not be independently verified", bull["summary"])
        self.assertIn("Paisa Panel does not assume fraud", bull["summary"])
        print("✅ TEST G PASSED: Unidentified source handled objectively without assuming fraud.")

    def test_h_irfc_whatsapp_claim(self):
        """
        TEST H: IRFC WhatsApp Tip Test Case (14 Strict QA Assertions)
        Evaluates the Amit Malhotra / Wealth Builders India WhatsApp message on IRFC.
        1. SOURCE != SEBI (Source is Amit Malhotra / Wealth Builders India)
        2. SECURITY resolves to Indian Railway Finance Corp (IRFC)
        3. UI chrome ('9:41', '12.4K members', 'Discipline today...') stripped
        4. Target range preserved as ₹180–₹200 (target_min=180, target_max=200)
        5. Timeframe preserved as 3–6 months (NOT truncated to 6 months)
        6. Stop loss preserved as ₹105 (and OCR 3105 repaired to 105)
        7. Upside calculated accurately: +46.9% to +63.3%
        8. Downside calculated accurately: -14.3%
        9. Language Risk score: 10/10 (0 penalty; targets are NOT guarantees)
        10. Regulator card: "NO SPECIFIC REGULATORY VIOLATION ESTABLISHED FROM THE SUPPLIED MESSAGE."
        11. Market Historian card: "Historical outcome could not be independently verified."
        12. Source Auditor: Identity & registration unverified, notes source disclaimer
        13. Claim-by-claim table atomizes all 6 thesis points + disclosure
        14. Trust score is 62/100, verdict: PARTIALLY VERIFIED
        """
        raw_message = """9:41
Wealth Builders India
12.4K members, 812 online
Pinned Message: Discipline today creates freedom tomorrow...

Amit Malhotra:
🚀 SWING / MEDIUM TERM PICK: IRFC (Indian Railway Finance Corporation)
CMP: ₹122.50
Target: ₹180–₹200
Timeframe: 3–6 months
Stop Loss: ₹105

Investment Thesis:
- Strong order pipeline from Indian Railways
- Increased railway budgetary support in Union Budget
- Government focus on infrastructure / capex expansion
- Healthy financials and consistent profits
- Attractive valuation compared with peers

Disclaimer: Not a SEBI registered advisor. Do your own research."""

        # 1. Entity Extraction & 5-Entity Separation
        details = extract_claim_details(raw_message)

        # Requirement 1: SOURCE != SEBI
        self.assertNotEqual(details["sourceName"], "Securities and Exchange Board of India (SEBI)")
        self.assertIn("Amit Malhotra", details["sourceName"])
        self.assertIn("Wealth Builders", details["sourceName"])

        # Requirement 2: SECURITY resolution
        self.assertIn("Indian Railway Finance", details["company"])
        self.assertEqual(details["ticker"], "IRFC")

        # Requirement 3: UI chrome stripped from claimText
        self.assertNotIn("9:41", details["claimText"])
        self.assertNotIn("12.4K members", details["claimText"])
        self.assertNotIn("Discipline today", details["claimText"])

        # Requirement 4: Target range preservation
        self.assertEqual(details["target_raw"], "₹180–₹200")
        self.assertEqual(details["target_min"], 180.0)
        self.assertEqual(details["target_max"], 200.0)

        # Requirement 5: Timeframe range preservation
        self.assertEqual(details["timeframe"], "3–6 months")
        self.assertNotEqual(details["timeframe"], "6 months")

        # Requirement 6: Stop loss preservation
        self.assertEqual(details["stopLoss"], "₹105")
        self.assertEqual(details["sl_val"], 105.0)

        # Requirement 7 & 8: Math return calculations
        # CMP = 122.50
        # Target 1: (180 - 122.5) / 122.5 * 100 = +46.9%
        # Target 2: (200 - 122.5) / 122.5 * 100 = +63.3%
        # Stop loss: (105 - 122.5) / 122.5 * 100 = -14.3%
        self.assertEqual(details["target_upside_str"], "+46.9% to +63.3%")
        self.assertEqual(details["downside_str"], "-14.3%")

        # Requirement 13: Claim-by-Claim table atomization
        subclaims = details["subclaims"]
        sc_categories = [sc.get("category", "") for sc in subclaims]
        self.assertIn("Corporate Fundamentals", sc_categories)
        self.assertIn("Public Policy & Budget", sc_categories)
        self.assertIn("Macroeconomic Tailwinds", sc_categories)
        self.assertIn("Corporate Financials", sc_categories)
        self.assertIn("Comparative Valuation", sc_categories)
        self.assertIn("Source Disclosure", sc_categories)

        # Requirement 9 & 14: Trust score calibration (62/100, PARTIALLY VERIFIED)
        score_res = compute_exact_score(raw_message)
        self.assertEqual(score_res["exact_score"], 62, f"Score should be 62, got {score_res['exact_score']}")
        self.assertEqual(score_res["verdict"], "PARTIALLY VERIFIED")
        self.assertEqual(score_res["pillars"]["language_risk"]["score"], 10, "Target language is not a guarantee: Language score must be 10/10")
        self.assertEqual(score_res["pillars"]["source_credibility"]["score"], 10)
        self.assertEqual(score_res["pillars"]["claim_verifiability"]["score"], 14)
        self.assertEqual(score_res["pillars"]["evidence_quality"]["score"], 14)
        self.assertEqual(score_res["pillars"]["transparency_risk"]["score"], 14)

        # Requirements 10, 11, 12: 4 Investigation Cards
        personas = get_persona_sources(details, raw_message)
        card1 = personas["fundamentalist"]["summary"]
        card2 = personas["regulator"]["summary"]
        card3 = personas["historian"]["summary"]
        card4 = personas["bull"]["summary"]

        # Card 1: The Claim Analyst
        self.assertIn("CMP: ₹122.50", card1)
        self.assertIn("TARGET: ₹180–₹200", card1)
        self.assertIn("TIMEFRAME: 3–6 months", card1)
        self.assertIn("STOP LOSS: ₹105", card1)
        self.assertIn("TARGET UPSIDE: +46.9% to +63.3%", card1)
        self.assertIn("STOP-LOSS DOWNSIDE: -14.3%", card1)

        # Card 2: The Regulator's Eye
        self.assertIn("NO SPECIFIC REGULATORY VIOLATION ESTABLISHED FROM THE SUPPLIED MESSAGE.", card2)
        self.assertIn("Regulatory enforcement finding: Not identified.", card2)
        self.assertIn("NOT the recommendation source", card2)

        # Card 3: The Market Historian
        self.assertIn("Historical outcome could not be independently verified.", card3)
        self.assertIn("Insufficient historical evidence", card3)

        # Card 4: The Source Auditor
        self.assertIn("Amit Malhotra / Wealth Builders India", card4)
        self.assertIn("Not independently verified", card4)
        self.assertIn("Not a SEBI registered advisor", card4)

        # OCR Artifact Recovery: Test if ₹105 misread as 3105
        ocr_message = raw_message.replace("Stop Loss: ₹105", "Stop Loss: ₹3105")
        ocr_details = extract_claim_details(ocr_message)
        self.assertEqual(ocr_details["stopLoss"], "₹105", "OCR artifact 3105 should be repaired to 105")
        self.assertEqual(ocr_details["downside_str"], "-14.3%")

        print(f"✅ TEST H PASSED: IRFC WhatsApp Claim -> Score: {score_res['exact_score']}/100, Verdict: {score_res['verdict']}")

    def test_i_pine_labs_motilal_oswal(self):
        """
        TEST I: Pine Labs / Motilal Oswal Test Case (13 Strict Assertions)
        1. Correct Entity Extraction: Security = Pine Labs (NOT "RESEARCH DESK", NOT "STOCK CALL")
        2. Source = Motilal Oswal (SEBI Registered Institutional Brokerage / Research Analyst, NOT "SEBI", NOT "Pine Labs")
        3. Stated CMP = ₹192
        4. Target = ₹250 (Single target, NOT ₹250–₹250, NOT 2nd target ₹250)
        5. Mathematical upside = +30.2% ((250 - 192) / 192 * 100)
        6. Time horizon = Medium term (Preserved textually, not truncated)
        7. Stop loss = Not stated (Fundamental research calls do not require stop losses, no penalty)
        8. Zero Hallucinated Guaranteed Return: "not a guaranteed return" is recognized as disclaimer, NOT certainty
        9. Language Risk score = 10/10 (0 penalty, urgency NOT DETECTED)
        10. Source Credibility = High (Motilal Oswal is SEBI-registered institutional broker)
        11. Trust Score = 78/100 (in range 78-82), Verdict: PARTIALLY VERIFIED, Confidence: MEDIUM-HIGH
        12. 4 Council Cards:
            - Card 1 (Claim Analyst): mentions Pine Labs, BUY, ₹192, ₹250, Medium term, +30.2%, thesis catalysts
            - Card 2 (Regulator's Eye): NO SPECIFIC REGULATORY VIOLATION ESTABLISHED FROM THE SUPPLIED MESSAGE
            - Card 3 (Market Historian): HISTORICAL OUTCOME COULD NOT BE INDEPENDENTLY VERIFIED (unlisted/pre-IPO)
            - Card 4 (Source Auditor): SOURCE: Motilal Oswal, Type: Brokerage / Research Institution, Pine Labs is evaluated security, NOT adviser
        13. Claim-by-Claim Table: atomizes 4 investment thesis points, rating, target, risk disclaimer
        """
        raw_message = """STOCK CALL — RESEARCH DESK
BUY: PINE LABS

CMP: ₹192
Target: ₹250
Time Horizon: Medium term

Why?
• Diversified digital payments and fintech
• Expansion in international markets
• Growth from affordability and EMI products
• EBITDA margins expected to improve significantly

Source: Motilal Oswal
This is a brokerage research view, not a guaranteed return. Investors should conduct their own due diligence."""

        # 1. Entity Extraction & 5-Entity Separation
        details = extract_claim_details(raw_message)

        # Requirement 1: Security Resolution
        self.assertEqual(details["company"], "Pine Labs", f"Company should be Pine Labs, got {details['company']}")
        self.assertEqual(details["ticker"], "PINELABS")
        self.assertNotIn("RESEARCH DESK", details["company"])
        self.assertNotIn("STOCK CALL", details["company"])

        # Requirement 2: Source Resolution
        self.assertEqual(details["sourceName"], "Motilal Oswal")
        self.assertNotEqual(details["sourceName"], "Securities and Exchange Board of India (SEBI)")
        self.assertNotEqual(details["sourceName"], "Pine Labs")

        # Requirement 3, 4, 5: Prices and Return Math
        self.assertEqual(details["cmp_raw"], "₹192")
        self.assertEqual(details["target_raw"], "₹250")
        self.assertNotEqual(details["target_raw"], "₹250–₹250")
        self.assertEqual(details["target_upside_str"], "+30.2%")

        # Requirement 6: Timeframe preservation
        self.assertEqual(details["timeframe"], "Medium term")

        # Requirement 7: Stop loss not stated
        self.assertFalse(details.get("stopLoss"), "Stop loss should not be stated")

        # Requirement 8 & 9: Language Risk & Zero Hallucinated Certainty
        score_res = compute_exact_score(raw_message)
        self.assertEqual(score_res["pillars"]["language_risk"]["score"], 10, "Negated disclaimer 'not a guaranteed return' must NOT be penalized")

        # Requirement 10 & 11: Trust Score Calibration (78/100, PARTIALLY VERIFIED)
        self.assertTrue(78 <= score_res["exact_score"] <= 82, f"Score should be 78-82, got {score_res['exact_score']}")
        self.assertEqual(score_res["verdict"], "PARTIALLY VERIFIED")
        self.assertEqual(score_res["confidence"], "MEDIUM-HIGH")
        self.assertEqual(score_res["pillars"]["source_credibility"]["score"], 22)
        self.assertEqual(score_res["pillars"]["claim_verifiability"]["score"], 16)
        self.assertEqual(score_res["pillars"]["evidence_quality"]["score"], 16)
        self.assertEqual(score_res["pillars"]["transparency_risk"]["score"], 14)

        # Requirement 12: 4 Council Cards
        personas = get_persona_sources(details, raw_message)
        card1 = personas["fundamentalist"]["summary"]
        card2 = personas["regulator"]["summary"]
        card3 = personas["historian"]["summary"]
        card4 = personas["bull"]["summary"]

        # Card 1: The Claim Analyst
        self.assertIn("SECURITY: Pine Labs", card1)
        self.assertIn("CMP: ₹192", card1)
        self.assertIn("TARGET: ₹250", card1)
        self.assertIn("TIMEFRAME: Medium term", card1)
        self.assertIn("TARGET UPSIDE: +30.2%", card1)
        self.assertIn("Diversified digital payments", card1)

        # Card 2: The Regulator's Eye
        self.assertIn("NO SPECIFIC REGULATORY VIOLATION ESTABLISHED FROM THE SUPPLIED MESSAGE.", card2)
        self.assertIn("Motilal Oswal", card2)

        # Card 3: The Market Historian
        self.assertIn("HISTORICAL OUTCOME COULD NOT BE INDEPENDENTLY VERIFIED.", card3)
        self.assertTrue("unlisted" in card3.lower() or "pre-ipo" in card3.lower())

        # Card 4: The Source Auditor
        self.assertIn("SOURCE: Motilal Oswal", card4)
        self.assertIn("Brokerage / Research Institution", card4)
        self.assertIn("NOT an advisory source", card4)

        # Requirement 13: Claim-by-Claim Table Atomization
        subclaims = details["subclaims"]
        sc_categories = [sc.get("category", "") for sc in subclaims]
        self.assertIn("Analyst Recommendation", sc_categories)
        self.assertIn("Corporate Profile", sc_categories)
        self.assertIn("Corporate Expansion", sc_categories)
        self.assertIn("Commercial Strategy", sc_categories)
        self.assertIn("Financial Outlook", sc_categories)
        self.assertIn("Source Disclosure", sc_categories)

        print(f"✅ TEST I PASSED: Pine Labs / Motilal Oswal Claim -> Score: {score_res['exact_score']}/100, Verdict: {score_res['verdict']}")

if __name__ == "__main__":
    unittest.main()

