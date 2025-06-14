import requests
import os
import json
from datetime import datetime, timezone
from urllib.parse import urljoin

# ========== CONFIGURATION ==========

DISCOURSE_BASE_URL = "https://discourse.onlinedegree.iitm.ac.in/"
CATEGORY_SLUG = "courses/tds-kb"
CATEGORY_ID = 34
START_DATE = "2025-01-01"  # Inclusive
END_DATE = "2025-04-15"    # Inclusive

RAW_COOKIE_STRING = """"""  # Replace with your actual cookie string

OUTPUT_PATH = "app/data/discourse_posts.json"
POST_ID_BATCH_SIZE = 50
MAX_CONSECUTIVE_PAGES_WITHOUT_NEW_TOPICS = 5

# ====================================

def parse_cookie_string(raw_cookie_string):
    cookies = {}
    if not raw_cookie_string.strip():
        print("Warning: RAW_COOKIE_STRING is empty.")
        return cookies
    for cookie_part in raw_cookie_string.strip().split(";"):
        if "=" in cookie_part:
            key, value = cookie_part.strip().split("=", 1)
            cookies[key] = value
    return cookies

def get_topic_ids(base_url, category_slug, category_id, start_date_str, end_date_str, cookies):
    url = urljoin(base_url, f"c/{category_slug}/{category_id}.json")
    topic_ids = []
    page = 0

    start_dt = datetime.fromisoformat(start_date_str + "T00:00:00").replace(tzinfo=timezone.utc)
    end_dt = datetime.fromisoformat(end_date_str + "T23:59:59.999999").replace(tzinfo=timezone.utc)

    print(f"Fetching topic IDs from category between {start_dt} and {end_dt}...")

    consecutive_pages_with_no_new_unique_topics = 0
    last_known_unique_topic_count = 0

    while True:
        paginated_url = f"{url}?page={page}"
        try:
            response = requests.get(paginated_url, cookies=cookies, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Error fetching or decoding page {page}: {e}")
            break

        topics_on_page = data.get("topic_list", {}).get("topics", [])
        if not topics_on_page:
            print(f"No more topics found on page {page}.")
            break

        count_before = len(set(topic_ids))
        for topic in topics_on_page:
            try:
                created_date = datetime.fromisoformat(topic["created_at"].replace("Z", "+00:00"))
                if start_dt <= created_date <= end_dt:
                    topic_ids.append(topic["id"])
            except:
                continue

        current_count = len(set(topic_ids))
        if current_count == last_known_unique_topic_count:
            consecutive_pages_with_no_new_unique_topics += 1
            print(f"No new unique topics on page {page}. Consecutive stale pages: {consecutive_pages_with_no_new_unique_topics}")
        else:
            consecutive_pages_with_no_new_unique_topics = 0

        last_known_unique_topic_count = current_count

        if consecutive_pages_with_no_new_unique_topics >= MAX_CONSECUTIVE_PAGES_WITHOUT_NEW_TOPICS:
            print(f"Stopping after {MAX_CONSECUTIVE_PAGES_WITHOUT_NEW_TOPICS} stale pages.")
            break

        if not data.get("topic_list", {}).get("more_topics_url"):
            print(f"No more_topics_url on page {page}. Ending.")
            break

        print(f"Page {page} done. Unique topics so far: {current_count}")
        page += 1

    return list(set(topic_ids))

def get_full_topic_json(base_url, topic_id, cookies):
    topic_url = urljoin(base_url, f"t/{topic_id}.json")
    try:
        resp = requests.get(topic_url, cookies=cookies, timeout=30)
        resp.raise_for_status()
        topic_data = resp.json()
    except Exception as e:
        print(f"Failed to fetch topic {topic_id}: {e}")
        return None

    stream_ids = topic_data.get("post_stream", {}).get("stream", [])
    loaded_ids = {p["id"] for p in topic_data.get("post_stream", {}).get("posts", [])}
    missing_ids = [pid for pid in stream_ids if pid not in loaded_ids]

    extra_posts = []
    for i in range(0, len(missing_ids), POST_ID_BATCH_SIZE):
        batch = missing_ids[i:i+POST_ID_BATCH_SIZE]
        query = [("post_ids[]", pid) for pid in batch]
        try:
            r = requests.get(urljoin(base_url, f"t/{topic_id}/posts.json"), params=query, cookies=cookies, timeout=60)
            r.raise_for_status()
            extra = r.json()
            if isinstance(extra, list):
                extra_posts.extend(extra)
            elif "post_stream" in extra and "posts" in extra["post_stream"]:
                extra_posts.extend(extra["post_stream"]["posts"])
            elif "posts" in extra:
                extra_posts.extend(extra["posts"])
        except Exception as e:
            print(f"Failed batch for topic {topic_id}, posts {batch}: {e}")

    if extra_posts:
        all_posts = {p["id"]: p for p in topic_data["post_stream"]["posts"]}
        for post in extra_posts:
            all_posts[post["id"]] = post
        topic_data["post_stream"]["posts"] = [all_posts[pid] for pid in stream_ids if pid in all_posts]

    return topic_data

def main():
    print("Starting Discourse scraper...")
    cookies = parse_cookie_string(RAW_COOKIE_STRING)

    topic_ids = get_topic_ids(
        DISCOURSE_BASE_URL, CATEGORY_SLUG, CATEGORY_ID,
        START_DATE, END_DATE, cookies
    )

    if not topic_ids:
        print("No topics found.")
        return

    all_topics = []
    for i, tid in enumerate(topic_ids, 1):
        print(f"[{i}/{len(topic_ids)}] Getting topic {tid}...")
        data = get_full_topic_json(DISCOURSE_BASE_URL, tid, cookies)
        if data:
            all_topics.append(data)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_topics, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Done. {len(all_topics)} topics saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
