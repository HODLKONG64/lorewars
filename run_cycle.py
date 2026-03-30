def main() -> None:
    print("=" * 60)
    print("LOREWARS CYCLE START")
    print(f"DRY_RUN={DRY_RUN}")
    print("=" * 60)

    print("\n[1/7] Crawling RSS and archive sources...")
    new_urls = rss_crawler.run()
    print(f"      Queue length: {queue.length()}")

    print("\n[2/7] Selecting source URL...")
    source_entry = source_selector.select()
    if source_entry is None:
        print("      No source available — aborting cycle.")
        return
    print(f"      Selected: {source_entry['url']}")

    print("\n[3/7] Generating war log...")
    log_dict = log_generator.generate(source_entry)

    # 🔥 HANDLE SKIPPED CONTENT
    if not log_dict:
        print("      Skipped — weak content")
        return

    print(f"      Slug: {log_dict['slug']}")

    print("\n[4/7] Publishing wiki page...")
    log_path = wiki_publisher.publish(log_dict)
    print(f"      Written: {log_path}")

    print("\n[5/7] Publishing to IPFS...")
    cid = ipfs_publisher.publish(log_dict)
    print(f"      CID: {cid}")

    print("\n[6/7] Building search index...")
    search_index.build()

    print("\n[7/7] Updating memory state...")
    history.add_entry(
        url=source_entry["url"],
        source_name=source_entry["source_name"],
        log_slug=log_dict["slug"],
        date=log_dict["metadata"]["date"],
    )
    _update_world_state(log_dict)
    _update_arc_state(log_dict)

    print("\n" + "=" * 60)
    print("LOREWARS CYCLE COMPLETE")
    print(f"  Log slug  : {log_dict['slug']}")
    print(f"  Source    : {source_entry['source_name']}")
    print(f"  IPFS CID  : {cid}")
    print(f"  New URLs  : {new_urls}")
    print("=" * 60)