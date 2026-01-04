from __future__ import annotations

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
from datetime import datetime, timezone, timedelta
import argparse
import sys


def get_url(user: str) -> str:
    base_url = "https://api.github.com"
    return f"{base_url}/users/{user}/repos"


def convert_reset_to_ist(reset_timestamp: int) -> str:
    utc_time = datetime.fromtimestamp(reset_timestamp, tz=timezone.utc)
    ist_offset = timedelta(hours=5, minutes=30)
    ist_time = utc_time + ist_offset
    return ist_time.strftime("%d-%b-%Y %I:%M:%S %p IST")


def fetcher(username: str) -> list | None:
    try:
        url = get_url(user=username)
        all_items = []
        page = 1

        with requests.Session() as session:
            retry_strategy = Retry(
                total=3,
                backoff_factor=0.5,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET"],
                raise_on_status=False,
                respect_retry_after_header=True
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("https://", adapter)
            session.mount("http://", adapter)

            while True:
                params = {
                    "type": "owner",
                    "sort": "updated",
                    "direction": "desc",
                    "per_page": 30,
                    "page": page
                }

                resp = session.get(url, params=params, timeout=(2, 10))

                if resp.status_code == 403:
                    reset_ts = resp.headers.get("X-RateLimit-Reset")
                    if reset_ts:
                        reset_time = convert_reset_to_ist(int(reset_ts))
                        print(f"Rate limit exceeded. It will reset at: {reset_time}")
                    else:
                        print("Rate limit exceeded. No reset time provided.")
                    return None

                resp.raise_for_status()

                ctype = resp.headers.get("Content-Type", "")
                if "application/json" not in ctype.lower():
                    print("Not JSON")
                    return None

                try:
                    items = resp.json()
                    if not items:
                        break

                    for repo in items:
                        data = {
                            "name": repo.get("name"),
                            "description": repo.get("description"),
                            "stars": repo.get("stargazers_count"),
                            "language": repo.get("language"),
                            "created_at": repo.get("created_at"),
                            "updated_at": repo.get("updated_at"),
                        }
                        all_items.append(data)

                    if len(items) < 30:
                        break

                    page += 1

                except ValueError:
                    print("Invalid JSON")
                    return None
        return all_items

    except requests.exceptions.Timeout:
        print("Request timed out.")
        return None
    except requests.exceptions.ConnectionError:
        print("Connection error")
        return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None
    except Exception as e:
        print(e)
        return None


def write_file(repos: list, output_file: str = "github_repos.json"):
    if repos:
        with open(output_file, "w", encoding="utf-8") as data:
            json.dump(repos, data, indent=4)
    return


def main():
    parser = argparse.ArgumentParser(
        description="GitHub Repo Summary Extractor"
    )
    parser.add_argument(
        "--username", "-u",
        help="GitHub username to fetch repositories for"
    )
    parser.add_argument(
        "--output", "-o", default="github_repos.json",
        help="Output file to save repository data (default: github_repos.json)"
    )

    args = parser.parse_args()

    if args.username:
        # CLI mode
        print(f"Fetching repos for user: {args.username}")
        repos = fetcher(username=args.username)

        if repos:
            print(f"Logging repos to {args.output}...")
            write_file(repos=repos, output_file=args.output)
            print(f"Repos logged to {args.output}")
        elif repos is None:
            print("Error fetching data.")
            sys.exit(1)
        else:
            print("No repos or Invalid account")
            sys.exit(1)

    else:
        # Interactive mode
        print("Welcome to Github Repo Summary Extractor")
        while True:
            try:
                username = input("Enter username (or 'exit' to quit): ")
                if username.lower().strip() == "exit":
                    break

                repos = fetcher(username=username)

                if repos:
                    print("Logging repos to github_repos.json...")
                    write_file(repos=repos)
                    print("Repos logged to github_repos.json")

                elif repos is None:
                    print("Error fetching data.")

                else:
                    print("No repos or Invalid account")

            except ValueError:
                print("Invalid input.")
            except Exception as e:
                print(f"An Unexpected Error Occurred: {e}")


if __name__ == "__main__":
    main()