import feedparser
from pytrends.request import TrendReq

def get_trending_topics(niche="finance money Indonesia"):
    topics = []
    try:
        pytrends = TrendReq(hl='id-ID', tz=420)
        pytrends.build_payload([niche], timeframe='now 1-d', geo='ID')
        related = pytrends.related_queries()
        for key, df in related.items():
            if df and df.get('top') is not None:
                topics.extend(df['top']['query'].tolist()[:3])
    except Exception as e:
        print(f"Trends error: {e}")

    rss_feeds = [
        "https://feeds.finance.yahoo.com/rss/2.0/headline",
        "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    ]
    for url in rss_feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]:
                topics.append(entry.title)
        except Exception as e:
            print(f"RSS error: {e}")

    fallbacks = [
        "5 cara hemat uang di Indonesia 2025",
        "How to invest your first $100",
        "Morning habits of millionaires",
        "Why most Indonesians don't save money",
        "Passive income ideas for beginners"
    ]
    if not topics:
        topics = fallbacks

    return topics[:5]

if __name__ == "__main__":
    ideas = get_trending_topics()
    print("Today's content ideas:")
    for i, idea in enumerate(ideas, 1):
        print(f"{i}. {idea}")
