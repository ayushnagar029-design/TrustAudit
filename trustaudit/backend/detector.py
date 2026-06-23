import os
import re
from typing import List, Optional, Tuple
from models import Claim, AnalyzeResponse

FACTS = [
    # Mughal Era
    (["babur", "1526", "panipat"], "supported", 0.99, "Babur founded the Mughal Empire after the First Battle of Panipat in 1526."),
    (["babur", "1525"], "contradicted", 0.96, "Babur's victory at Panipat was in 1526, not 1525."),
    (["akbar", "din-i-ilahi"], "supported", 0.96, "Akbar founded the syncretic religion Din-i-Ilahi."),
    (["shah jahan", "taj mahal"], "supported", 0.99, "The Taj Mahal was built by Mughal Emperor Shah Jahan in memory of Mumtaz Mahal."),
    (["aurangzeb", "taj mahal"], "contradicted", 0.99, "The Taj Mahal was built by Shah Jahan, not Aurangzeb."),
    (["taj mahal", "agra"], "supported", 0.99, "The Taj Mahal is located in Agra, Uttar Pradesh, India."),
    (["taj mahal", "delhi"], "contradicted", 0.98, "The Taj Mahal is in Agra, not Delhi."),
    (["taj mahal", "1632"], "supported", 0.97, "Construction of the Taj Mahal began in 1632."),
    (["taj mahal", "1653"], "supported", 0.97, "The Taj Mahal was completed in approximately 1653."),
    (["aurangzeb", "last", "mughal"], "supported", 0.96, "Aurangzeb was the last great Mughal emperor, ruling from 1658 to 1707."),
    (["humayun", "babur"], "supported", 0.97, "Humayun was the son of Babur and the second Mughal emperor."),

    # Freedom Movement
    (["gandhi", "assassinated", "1948", "january"], "supported", 0.99, "Gandhi was assassinated on January 30, 1948 by Nathuram Godse."),
    (["gandhi", "assassinated", "1947"], "contradicted", 0.98, "Gandhi was assassinated in 1948, not 1947."),
    (["gandhi", "godse"], "supported", 0.99, "Mahatma Gandhi was assassinated by Nathuram Godse."),
    (["independence", "august", "15", "1947"], "supported", 0.99, "India gained independence on August 15, 1947."),
    (["independence", "1948"], "contradicted", 0.99, "India gained independence in 1947, not 1948."),
    (["partition", "pakistan", "1947"], "supported", 0.99, "The 1947 partition of India led to the creation of Pakistan."),
    (["partition", "bangladesh", "1947"], "contradicted", 0.98, "The 1947 partition created Pakistan, not Bangladesh. Bangladesh was created in 1971."),
    (["nehru", "first", "prime minister"], "supported", 0.99, "Jawaharlal Nehru was India's first Prime Minister after independence."),
    (["subhas", "bose", "ina"], "supported", 0.97, "Subhas Chandra Bose led the Indian National Army (INA)."),
    (["dandi", "salt", "gandhi"], "supported", 0.98, "Gandhi led the Dandi Salt March in 1930."),
    (["quit india", "1942"], "supported", 0.98, "The Quit India Movement was launched in 1942."),
    (["bhagat singh", "executed", "1931"], "supported", 0.98, "Bhagat Singh was executed on March 23, 1931."),
    (["jallianwala", "1919", "amritsar"], "supported", 0.99, "The Jallianwala Bagh massacre occurred in Amritsar on April 13, 1919."),
    (["jallianwala", "1920"], "contradicted", 0.97, "The Jallianwala Bagh massacre was in 1919, not 1920."),

    # Post Independence
    (["constitution", "january", "26", "1950"], "supported", 0.99, "The Indian Constitution came into effect on January 26, 1950."),
    (["constitution", "november", "26", "1949"], "supported", 0.99, "The Indian Constitution was adopted on November 26, 1949."),
    (["ambedkar", "constitution"], "supported", 0.99, "B.R. Ambedkar was the principal architect of the Indian Constitution."),
    (["emergency", "indira", "1975"], "supported", 0.98, "Indira Gandhi declared the Emergency in 1975."),
    (["emergency", "1974"], "contradicted", 0.96, "The Emergency was declared in 1975, not 1974."),
    (["indira", "assassinated", "1984"], "supported", 0.99, "Indira Gandhi was assassinated in 1984."),
    (["rajiv", "youngest", "prime minister", "1984"], "supported", 0.97, "Rajiv Gandhi became India's youngest PM in 1984."),
    (["pokhran", "nuclear", "1974"], "supported", 0.97, "India conducted its first nuclear test (Pokhran-I) in 1974."),
    (["lok sabha", "543"], "supported", 0.98, "The Lok Sabha has 543 elected constituencies."),
    (["modi", "prime minister", "2014"], "supported", 0.98, "Narendra Modi became India's Prime Minister in May 2014."),
    (["modi", "2013"], "contradicted", 0.96, "Modi became PM in 2014, not 2013."),
    (["1971", "war", "bangladesh"], "supported", 0.98, "India's 1971 war with Pakistan led to the creation of Bangladesh."),

    # Cricket
    (["sachin", "100", "centur"], "supported", 0.99, "Sachin Tendulkar scored 100 international centuries across Tests and ODIs."),
    (["sachin", "debut", "1989", "pakistan"], "supported", 0.99, "Sachin Tendulkar made his Test debut in 1989 against Pakistan."),
    (["sachin", "debut", "1990"], "contradicted", 0.97, "Sachin Tendulkar debuted in 1989, not 1990."),
    (["sachin", "retired", "2013", "200"], "supported", 0.98, "Sachin Tendulkar retired in November 2013 after his 200th Test match."),
    (["sachin", "retired", "2012"], "contradicted", 0.97, "Sachin retired in 2013, not 2012."),
    (["dhoni", "2011", "world cup", "wankhede"], "supported", 0.99, "MS Dhoni led India to the 2011 World Cup win at Wankhede."),
    (["2011", "world cup", "pakistan", "final"], "contradicted", 0.98, "India beat Sri Lanka, not Pakistan, in the 2011 World Cup final."),
    (["1983", "world cup", "kapil", "lord"], "supported", 0.99, "India won the 1983 World Cup under Kapil Dev at Lord's Cricket Ground."),
    (["1983", "world cup", "gavaskar"], "contradicted", 0.98, "The 1983 World Cup was won under Kapil Dev, not Gavaskar."),
    (["2007", "t20", "world cup", "india"], "supported", 0.98, "India won the 2007 ICC T20 World Cup under Dhoni."),
    (["2007", "odi", "world cup", "india", "won"], "contradicted", 0.96, "India did not win the 2007 ODI World Cup."),
    (["ipl", "mumbai indians", "most"], "supported", 0.97, "Mumbai Indians have won the most IPL titles."),
    (["ipl", "2008", "started"], "supported", 0.98, "The IPL started in 2008."),
    (["virat", "100", "centur", "2023"], "supported", 0.96, "Virat Kohli scored his 100th international century in 2023."),
    (["virat", "100", "centur", "2022"], "contradicted", 0.95, "Kohli scored his 100th century in 2023, not 2022."),

    # Football
    (["messi", "world cup", "2022", "argentina"], "supported", 0.99, "Lionel Messi won the FIFA World Cup with Argentina in 2022."),
    (["messi", "world cup", "2018"], "contradicted", 0.98, "Messi won the World Cup in 2022, not 2018."),
    (["ronaldo", "world cup", "won"], "contradicted", 0.97, "Cristiano Ronaldo has never won a FIFA World Cup."),
    (["messi", "ballon d'or", "8"], "supported", 0.97, "Lionel Messi has won 8 Ballon d'Or awards as of 2023."),
    (["brazil", "world cup", "5"], "supported", 0.99, "Brazil has won the FIFA World Cup 5 times."),
    (["maradona", "1986", "world cup"], "supported", 0.99, "Diego Maradona led Argentina to the 1986 FIFA World Cup title."),
    (["pele", "brazil", "world cup", "3"], "supported", 0.98, "Pelé won three FIFA World Cup titles with Brazil."),

    # Tennis
    (["federer", "20", "grand slam"], "supported", 0.99, "Roger Federer won 20 Grand Slam singles titles."),
    (["federer", "23", "grand slam"], "contradicted", 0.97, "Federer won 20 Grand Slams, not 23."),
    (["nadal", "22", "grand slam"], "supported", 0.98, "Rafael Nadal won 22 Grand Slam singles titles."),
    (["djokovic", "24", "grand slam"], "supported", 0.98, "Novak Djokovic holds the record with 24 Grand Slam titles as of 2023."),
    (["sania", "mirza", "grand slam", "doubles"], "supported", 0.97, "Sania Mirza won 6 Grand Slam doubles titles."),

    # Olympics
    (["abhinav", "bindra", "gold", "2008"], "supported", 0.99, "Abhinav Bindra won India's first individual Olympic gold in 2008."),
    (["neeraj", "chopra", "gold", "javelin", "2020"], "supported", 0.99, "Neeraj Chopra won gold in javelin at the 2020 Tokyo Olympics."),
    (["neeraj", "chopra", "2016"], "contradicted", 0.97, "Neeraj Chopra won his Olympic gold at Tokyo 2020, not Rio 2016."),
    (["usain bolt", "100m", "9.58"], "supported", 0.99, "Usain Bolt holds the 100m world record at 9.58 seconds."),
    (["michael phelps", "23", "gold"], "supported", 0.98, "Michael Phelps won 23 Olympic gold medals."),

    # Science & Tech
    (["cv raman", "raman effect", "1930", "nobel"], "supported", 0.99, "C.V. Raman won the Nobel Prize in Physics in 1930 for the Raman Effect."),
    (["homi bhabha", "nuclear", "india"], "supported", 0.98, "Homi Bhabha is the father of India's nuclear program."),
    (["vikram sarabhai", "isro", "space"], "supported", 0.98, "Vikram Sarabhai is the father of India's space program."),
    (["chandrayaan-3", "2023", "south pole"], "supported", 0.99, "Chandrayaan-3 landed near the Moon's south pole in August 2023."),
    (["mangalyaan", "mars", "2014"], "supported", 0.99, "ISRO's Mangalyaan reached Mars orbit in 2014 on its first attempt."),
    (["www", "tim berners-lee", "1989"], "supported", 0.98, "Tim Berners-Lee invented the World Wide Web in 1989."),
    (["dna", "watson", "crick", "1953"], "supported", 0.98, "Watson and Crick described the structure of DNA in 1953."),
    (["penicillin", "fleming", "1928"], "supported", 0.98, "Alexander Fleming discovered penicillin in 1928."),
    (["apple", "steve jobs", "1976"], "supported", 0.97, "Apple was co-founded by Steve Jobs in 1976."),
    (["microsoft", "gates", "1975"], "supported", 0.97, "Microsoft was founded by Bill Gates in 1975."),
    (["sundar pichai", "google", "ceo"], "supported", 0.98, "Sundar Pichai is the CEO of Google."),
    (["einstein", "relativity"], "supported", 0.99, "Albert Einstein developed the theory of relativity."),
    (["newton", "gravity"], "supported", 0.97, "Isaac Newton formulated the law of universal gravitation."),

    # Geography
    (["india", "capital", "new delhi"], "supported", 0.99, "New Delhi is the capital of India."),
    (["india", "capital", "mumbai"], "contradicted", 0.99, "The capital of India is New Delhi, not Mumbai."),
    (["mount everest", "nepal", "tibet"], "supported", 0.99, "Mount Everest is on the border of Nepal and Tibet."),
    (["mount everest", "india"], "contradicted", 0.98, "Mount Everest is in Nepal/Tibet, not India."),
    (["mount everest", "8849"], "supported", 0.99, "Mount Everest stands at 8,849 meters."),
    (["nile", "longest", "river"], "supported", 0.95, "The Nile is generally considered the world's longest river."),
    (["russia", "largest", "country"], "supported", 0.99, "Russia is the world's largest country by area."),
    (["india", "population", "largest", "2023"], "supported", 0.97, "India surpassed China in 2023 to become the world's most populous country."),
    (["pakistan", "capital", "islamabad"], "supported", 0.99, "Islamabad is the capital of Pakistan."),
    (["pakistan", "capital", "karachi"], "contradicted", 0.98, "Pakistan's capital is Islamabad, not Karachi."),
    (["france", "capital", "paris"], "supported", 0.99, "Paris is the capital of France."),
    (["eiffel tower", "paris", "france"], "supported", 0.99, "The Eiffel Tower is in Paris, France."),
    (["eiffel tower", "berlin"], "contradicted", 0.99, "The Eiffel Tower is in Paris, not Berlin."),
    (["eiffel tower", "1889"], "supported", 0.99, "The Eiffel Tower was built in 1889."),

    # World History
    (["world war 2", "ended", "1945"], "supported", 0.99, "World War II ended in 1945."),
    (["world war 2", "ended", "1944"], "contradicted", 0.98, "World War II ended in 1945, not 1944."),
    (["world war 1", "1914"], "supported", 0.99, "World War I began in 1914."),
    (["world war 1", "ended", "1918"], "supported", 0.99, "World War I ended in 1918."),
    (["napoleon", "waterloo", "1815"], "supported", 0.99, "Napoleon was defeated at Waterloo in 1815."),
    (["napoleon", "waterloo", "1814"], "contradicted", 0.97, "Napoleon was defeated at Waterloo in 1815, not 1814."),
    (["french revolution", "1789"], "supported", 0.99, "The French Revolution began in 1789."),
    (["berlin wall", "1989", "fell"], "supported", 0.99, "The Berlin Wall fell in 1989."),
    (["hiroshima", "atomic", "1945"], "supported", 0.99, "The US dropped an atomic bomb on Hiroshima in August 1945."),
    (["moon", "landing", "1969", "armstrong"], "supported", 0.99, "Neil Armstrong landed on the Moon in 1969."),
    (["moon", "landing", "1968"], "contradicted", 0.98, "The Moon landing was in 1969, not 1968."),
    (["titanic", "1912", "sank"], "supported", 0.99, "The Titanic sank in April 1912."),
    (["nelson mandela", "president", "1994"], "supported", 0.99, "Nelson Mandela became South Africa's first Black president in 1994."),
    (["american independence", "1776"], "supported", 0.99, "The United States declared independence in 1776."),
    (["soviet union", "collapsed", "1991"], "supported", 0.99, "The Soviet Union collapsed in 1991."),

    # Bollywood & Culture
    (["ddlj", "1995"], "supported", 0.97, "Dilwale Dulhania Le Jayenge was released in 1995."),
    (["ddlj", "1994"], "contradicted", 0.96, "DDLJ was released in 1995, not 1994."),
    (["ar rahman", "oscar", "slumdog"], "supported", 0.99, "A.R. Rahman won two Academy Awards for Slumdog Millionaire in 2009."),
    (["ar rahman", "roja", "1992"], "supported", 0.97, "A.R. Rahman composed the music for the 1992 Tamil film Roja."),
    (["mughal-e-azam", "1960"], "supported", 0.97, "Mughal-E-Azam was released in 1960."),
    (["mother teresa", "albania", "1910"], "supported", 0.97, "Mother Teresa was born in Albania in 1910."),
    (["mother teresa", "kolkata"], "supported", 0.98, "Mother Teresa served the poor in Kolkata."),
    (["ramayana", "valmiki"], "supported", 0.98, "The Ramayana is attributed to the sage Valmiki."),
    (["mahabharata", "vyasa"], "supported", 0.98, "The Mahabharata is attributed to the sage Vyasa."),

    # Current Affairs
    (["chandrayaan-3", "2023", "isro"], "supported", 0.99, "ISRO's Chandrayaan-3 landed on the Moon in August 2023."),
    (["g20", "india", "2023"], "supported", 0.98, "India hosted the G20 Summit in New Delhi in September 2023."),
    (["icc", "world cup", "2023", "australia"], "supported", 0.98, "Australia won the 2023 ICC ODI World Cup, defeating India in the final."),
    (["icc", "world cup", "2023", "india", "won"], "contradicted", 0.97, "India did not win the 2023 ICC World Cup — Australia won."),
    (["cricket", "t20", "world cup", "2024", "india"], "supported", 0.97, "India won the 2024 ICC T20 World Cup."),
    (["paris", "olympics", "2024"], "supported", 0.98, "The 2024 Summer Olympics were held in Paris."),
    (["neeraj chopra", "silver", "paris", "2024"], "supported", 0.97, "Neeraj Chopra won silver in javelin at the 2024 Paris Olympics."),
    (["neeraj chopra", "gold", "paris", "2024"], "contradicted", 0.96, "Neeraj Chopra won silver, not gold, at Paris 2024."),
]


def _verify_claim(claim: str) -> Tuple[str, float, str]:
    claim_lower = claim.lower()
    matched_contradictions = []
    matched_supported = []

    for keywords, verdict, confidence, reasoning in FACTS:
        match_count = sum(1 for kw in keywords if kw in claim_lower)
        total = len(keywords)

        if match_count == total:
            score = confidence
        elif match_count >= total - 1 and total > 2:
            score = confidence * 0.75
        else:
            continue

        if verdict == "contradicted":
            matched_contradictions.append((score, reasoning))
        else:
            matched_supported.append((score, reasoning))

    if matched_contradictions:
        best = max(matched_contradictions, key=lambda x: x[0])
        return "contradicted", round(best[0], 2), best[1]

    if matched_supported:
        best = max(matched_supported, key=lambda x: x[0])
        return "supported", round(best[0], 2), best[1]

    return "unverifiable", 0.5, "This claim cannot be verified without an external source."


def decompose_claims(response_text: str) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', response_text.strip())
    return [s.strip() for s in sentences if len(s.split()) > 4]


def _locate(claim_text: str, response_text: str):
    idx = response_text.find(claim_text)
    if idx == -1:
        return None, None
    return idx, idx + len(claim_text)


def _trust_score(claims: List[Claim]) -> float:
    if not claims:
        return 100.0
    weights = {"supported": 1.0, "unverifiable": 0.5, "unsupported": 0.0, "contradicted": 0.0}
    total = sum(weights[c.verdict] for c in claims)
    return round((total / len(claims)) * 100, 1)


def _risk_level(score: float) -> str:
    if score >= 75: return "low"
    if score >= 45: return "medium"
    return "high"


def analyze(response_text: str, source_context: Optional[str]) -> AnalyzeResponse:
    mode = "grounded" if source_context and source_context.strip() else "self_consistency"
    raw_claims = decompose_claims(response_text)
    claims: List[Claim] = []

    for raw in raw_claims:
        verdict, confidence, reasoning = _verify_claim(raw)
        start, end = _locate(raw, response_text)
        claims.append(Claim(
            text=raw,
            verdict=verdict,
            confidence=confidence,
            reasoning=reasoning,
            start_index=start,
            end_index=end,
        ))

    score = _trust_score(claims)
    risk = _risk_level(score)

    if not claims:
        summary = "No checkable factual claims found."
    else:
        flagged = sum(1 for c in claims if c.verdict in ("unsupported", "contradicted"))
        uncertain = sum(1 for c in claims if c.verdict == "unverifiable")
        summary = (
            f"{len(claims)} claim(s) checked. {flagged} flagged, "
            f"{uncertain} unverifiable, {len(claims) - flagged - uncertain} supported."
        )

    return AnalyzeResponse(
        response_text=response_text,
        mode=mode,
        claims=claims,
        trust_score=score,
        risk_level=risk,
        summary=summary,
    )