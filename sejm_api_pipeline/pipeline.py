#!/usr/bin/env python3
"""Main pipeline for fetching Sejm API data and uploading to R2."""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
import logging

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from api_fetcher.fetcher import fetch_json_from_api, save_payload
from storage.r2_uploader import upload_payload_to_r2, upload_file_to_r2

# Configure logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def process_single_task(api_url, verify_ssl, output_local, r2_bucket, r2_key, r2_account_id, r2_access_key, r2_secret_key):
    """Process a single API fetch and upload task."""
    try:
        logger.info(f"Fetching data from {api_url}...")
        payload = fetch_json_from_api(api_url, verify_ssl=verify_ssl)
        count = len(payload) if isinstance(payload, (list, tuple)) else None

        logger.info("API payload loaded.")
        logger.info(f"Payload type: {type(payload).__name__}")
        if count is not None:
            logger.info(f"Item count: {count}")

        # Save locally if specified
        if output_local:
            saved_path = save_payload(payload, output_local)
            logger.info(f"Saved locally to: {saved_path}")

            # If R2 upload is also requested, upload the file
            if r2_bucket and r2_key:
                logger.info(f"Uploading file to R2: {r2_bucket}/{r2_key}")
                upload_file_to_r2(
                    output_local,
                    r2_bucket,
                    r2_key,
                    account_id=r2_account_id,
                    access_key=r2_access_key,
                    secret_key=r2_secret_key
                )
                logger.info("Uploaded to R2 successfully.")
        elif r2_bucket and r2_key:
            # Upload payload directly to R2
            logger.info(f"Uploading payload to R2: {r2_bucket}/{r2_key}")
            upload_payload_to_r2(
                payload,
                r2_bucket,
                r2_key,
                account_id=r2_account_id,
                access_key=r2_access_key,
                secret_key=r2_secret_key
            )
            logger.info("Uploaded to R2 successfully.")
        else:
            logger.info("No output destination specified. Payload fetched but not saved.")

        return True
    except Exception as e:
        logger.error(f"Error processing {api_url}: {str(e)}")
        return False


def process_batch_config(config_file):
    """Process multiple tasks from a configuration file."""
    logger.info(f"Loading configuration from {config_file}...")
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    tasks = config.get('tasks', [])
    r2_defaults = config.get('r2_defaults', {})
    
    logger.info(f"Found {len(tasks)} tasks to process.")
    
    success_count = 0
    fail_count = 0
    
    for i, task in enumerate(tasks, 1):
        logger.info(f"Processing task {i}/{len(tasks)}: {task.get('api_url')}")
        
        api_url = task.get('api_url')
        if not api_url:
            logger.warning(f"Task {i} missing 'api_url', skipping.")
            continue
        
        verify_ssl = task.get('verify_ssl', False)
        output_local = task.get('output_local')
        r2_bucket = task.get('r2_bucket', r2_defaults.get('bucket'))
        r2_key = task.get('r2_key')
        r2_account_id = task.get('r2_account_id', r2_defaults.get('account_id'))
        r2_access_key = task.get('r2_access_key', r2_defaults.get('access_key'))
        r2_secret_key = task.get('r2_secret_key', r2_defaults.get('secret_key'))
        
        if process_single_task(
            api_url, verify_ssl, output_local,
            r2_bucket, r2_key,
            r2_account_id, r2_access_key, r2_secret_key
        ):
            success_count += 1
        else:
            fail_count += 1
        
        logger.info("-" * 80)
    
    logger.info(f"Batch processing completed: {success_count} succeeded, {fail_count} failed.")
    return fail_count == 0


def main():
    parser = argparse.ArgumentParser(description="Fetch Sejm API data and upload to R2")
    
    # Config file option for batch processing
    parser.add_argument("--config", type=str, help="Config file for batch processing multiple tasks")
    
    # Single task options
    parser.add_argument("--api-url", type=str, help="API URL to fetch data from (single task)")
    parser.add_argument("--verify-ssl", action="store_true", default=False, help="Verify SSL certificates")
    parser.add_argument("--output-local", type=str, help="Local file path to save JSON (optional)")
    parser.add_argument("--r2-bucket", type=str, help="R2 bucket name")
    parser.add_argument("--r2-key", type=str, help="R2 object key (path in bucket)")
    parser.add_argument("--r2-account-id", type=str, help="R2 account ID")
    parser.add_argument("--r2-access-key", type=str, help="R2 access key ID")
    parser.add_argument("--r2-secret-key", type=str, help="R2 secret access key")

    args = parser.parse_args()

    # Check if config file mode or single task mode
    if args.config:
        success = process_batch_config(args.config)
        sys.exit(0 if success else 1)
    elif args.api_url:
        success = process_single_task(
            args.api_url,
            args.verify_ssl,
            args.output_local,
            args.r2_bucket,
            args.r2_key,
            args.r2_account_id,
            args.r2_access_key,
            args.r2_secret_key
        )
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        logger.error("Either --config or --api-url must be provided.")
        sys.exit(1)


if __name__ == "__main__":
    main()
