#!/usr/bin/env python3
"""Main pipeline for fetching Sejm API data and uploading to R2."""

import argparse
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from api_fetcher.fetcher import fetch_json_from_api, save_payload
from storage.r2_uploader import upload_payload_to_r2, upload_file_to_r2


def main():
    parser = argparse.ArgumentParser(description="Fetch Sejm API data and upload to R2")
    parser.add_argument("--api-url", required=True, help="API URL to fetch data from")
    parser.add_argument("--verify-ssl", action="store_true", default=False, help="Verify SSL certificates")
    parser.add_argument("--output-local", type=str, help="Local file path to save JSON (optional)")
    parser.add_argument("--r2-bucket", type=str, help="R2 bucket name")
    parser.add_argument("--r2-key", type=str, help="R2 object key (path in bucket)")
    parser.add_argument("--r2-account-id", type=str, help="R2 account ID")
    parser.add_argument("--r2-access-key", type=str, help="R2 access key ID")
    parser.add_argument("--r2-secret-key", type=str, help="R2 secret access key")

    args = parser.parse_args()

    # Fetch the payload
    print(f"Fetching data from {args.api_url}...")
    payload = fetch_json_from_api(args.api_url, verify_ssl=args.verify_ssl)
    count = len(payload) if isinstance(payload, (list, tuple)) else None

    print("API payload loaded.")
    print(f"Payload type: {type(payload).__name__}")
    if count is not None:
        print(f"Item count: {count}")

    # Save locally if specified
    if args.output_local:
        saved_path = save_payload(payload, args.output_local)
        print(f"Saved locally to: {saved_path}")

        # If R2 upload is also requested, upload the file
        if args.r2_bucket and args.r2_key:
            print(f"Uploading file to R2: {args.r2_bucket}/{args.r2_key}")
            upload_file_to_r2(
                args.output_local,
                args.r2_bucket,
                args.r2_key,
                account_id=args.r2_account_id,
                access_key=args.r2_access_key,
                secret_key=args.r2_secret_key
            )
            print("Uploaded to R2 successfully.")
    elif args.r2_bucket and args.r2_key:
        # Upload payload directly to R2
        print(f"Uploading payload to R2: {args.r2_bucket}/{args.r2_key}")
        upload_payload_to_r2(
            payload,
            args.r2_bucket,
            args.r2_key,
            account_id=args.r2_account_id,
            access_key=args.r2_access_key,
            secret_key=args.r2_secret_key
        )
        print("Uploaded to R2 successfully.")
    else:
        print("No output destination specified. Payload fetched but not saved.")


if __name__ == "__main__":
    main()