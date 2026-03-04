import json
import os
import re
import time
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from dotenv import load_dotenv
from ontology import GraphExtraction

# .env is one level up (project root)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please add it to your .env file.")

client = genai.Client(api_key=api_key)
MODEL = "gemini-2.5-flash"

# Paths relative to this script
DATA_DIR    = os.path.join(os.path.dirname(__file__), "..", "data")
INPUT_FILE  = os.path.join(DATA_DIR, "corpus.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "graph_extractions.json")

MAX_RETRIES = 4


def extract_from_batch(batch_text: str) -> dict:
    prompt = f"""
    Analyze the following batch of GitHub issues and communications, and extract the underlying entities and their relationships.
    For any evidence you extract, use the provided SOURCE_URL that accompanies each issue or comment.

    Batch Data:
    {batch_text}
    """
    error_str = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=GraphExtraction,
                ),
            )
            return json.loads(response.text)

        except genai_errors.ClientError as e:
            error_str = str(e)
            if "429" in error_str:
                wait_seconds = 65
                match = re.search(r"retryDelay[^0-9]+(\d+)", error_str)
                if match:
                    wait_seconds = int(match.group(1)) + 5
                print(f"  [429 Rate limit] Attempt {attempt}/{MAX_RETRIES}. Waiting {wait_seconds}s...")
                time.sleep(wait_seconds)
            else:
                raise

    raise RuntimeError(f"All {MAX_RETRIES} retries exhausted. Last error: {error_str}")


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


if __name__ == "__main__":
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    batch_size = 5
    total_batches = (len(corpus) + batch_size - 1) // batch_size
    print(f"Loaded {len(corpus)} issues. Processing {total_batches} batches of {batch_size}...")

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            try:
                all_extractions = json.load(f)
                if all_extractions:
                    print(f"  Resuming: {len(all_extractions)} batches already done, skipping them.")
            except json.JSONDecodeError:
                all_extractions = []
    else:
        all_extractions = []

    start_batch = len(all_extractions)
    failed_batches = 0

    for batch_index, issue_batch in enumerate(chunks(corpus, batch_size)):
        if batch_index < start_batch:
            continue

        batch_text = ""
        for issue in issue_batch:
            batch_text += f"\n--- ISSUE ID: {issue['id']} ---\n"
            batch_text += f"SOURCE_URL: {issue['url']}\n"
            batch_text += f"Title: {issue['title']}\n"
            batch_text += f"Body: {issue.get('body', '')}\n"
            batch_text += "Comments:\n"
            for comment in issue.get('comments', []):
                comment_url = f"{issue['url']}#issuecomment-{comment['id']}"
                batch_text += f"- SOURCE_URL: {comment_url} | Author: {comment.get('author', 'Unknown')}: {comment.get('body', '')}\n"

        print(f"Extracting batch {batch_index + 1}/{total_batches}...")
        try:
            batch_result = extract_from_batch(batch_text)
            all_extractions.append(batch_result)
            print(f"  OK — {len(batch_result.get('entities', []))} entities, {len(batch_result.get('claims', []))} claims")

            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(all_extractions, f, indent=2)

        except Exception as e:
            failed_batches += 1
            print(f"  FAILED batch {batch_index + 1}: {e}")

        time.sleep(5)

    successful = len(all_extractions)
    print(f"\nDone! {successful}/{total_batches} batches extracted ({failed_batches} failed).")
    print(f"Saved to {OUTPUT_FILE}")
