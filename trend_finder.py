import feedparser
from pytrends.request import TrendReq

def get_trending_topics(niche="finance money Indonesia"):
    topics = []

    # Source 1: Google Trends (free, no API key needed)
    pytrends = TrendReq(hl='id-ID', tz=420)  # Indonesia timezone
    pytrends.build_payload([niche], timeframe='now 1-d', geo='ID')
    related = pytrends.related_queries()
    
    for key, df in related.items():
        if df and df.get('top') is not None:
            top_queries = df['top']['query'].tolist()[:3]
            topics.extend(top_queries)

    # Source 2: Free RSS feeds (no API key)
    rss_feeds = [
        "https://feeds.finance.yahoo.com/rss/2.0/headline",
        "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    ]
    for url in rss_feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]:
            topics.append(entry.title)

    return topics[:5]  # Return top 5 ideas

if __name__ == "__main__":
    ideas = get_trending_topics()
    print("Today's content ideas:")
    for i, idea in enumerate(ideas, 1):
        print(f"{i}. {idea}")
