# GitHub Repo Summary Extractor

A Python tool to fetch and log repositories of any GitHub user into a JSON file.  
It supports both **interactive input** for beginners and **CLI arguments** for advanced usage.

---

## Features
- Fetches repositories owned by a GitHub user using the GitHub REST API.
- Handles pagination (multiple pages of repos).
- Retries failed requests with exponential backoff.
- Gracefully manages API rate limits (shows reset time in IST).
- Outputs clean JSON with repo details:
  - Name
  - Description
  - Stars
  - Language
  - Created date
  - Last updated date
- Hybrid usage:
  - **Interactive mode**: Enter usernames one by one.
  - **CLI mode**: Pass username and output file via arguments.

---

## Requirements
- Python 3.10+
- Libraries:
  - `requests`
  - `urllib3`

Install dependencies:
```bash
pip install requests urllib3
