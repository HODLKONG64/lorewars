from memory import queue
import feedparser


RSS_FEEDS = [
    "https://graffpunks.substack.com/feed",
    "https://medium.com/feed/@iamcharliebuster",
]


def run():
    new_urls = 0

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            url = entry.get("link")
            title = entry.get("title", "")
            source_name = feed.feed.get("title", "Unknown")

            if not url:
                continue

            queue.push({
                "url": url,
                "source_name": source_name,
                "title": title
            })

            new_urls += 1

    print(f"[rss_crawler] Added {new_urls} URLs to queue")
    return new_urls