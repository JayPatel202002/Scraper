'''Single responsibility: orchestration

Accepts URLs or jobs from the parent app

Controls concurrency

Calls fetch → parse → store

Handles retries & failures

🚫 No scraping logic
🚫 No parsing logic''' 