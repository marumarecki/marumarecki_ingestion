# Sejm API Ingestion Pipeline

This repository contains a modular Python pipeline for fetching data from the Sejm (Polish Parliament) API and uploading it to Cloudflare R2 storage.

## Project Structure

```
sejm_api_pipeline/
├── api_fetcher/           # API fetching utilities
│   ├── __init__.py
│   └── fetcher.py         # Contains functions for fetching JSON from APIs
├── storage/               # Storage utilities
│   ├── __init__.py
│   └── r2_uploader.py     # Contains functions for uploading to Cloudflare R2
├── pipeline.py            # Main pipeline script (single & batch processing)
├── sejm_api_ingestion.py  # Standalone ingestion script
├── notebook.ipynb         # Jupyter notebook with examples
├── config.example.json    # Example configuration for batch processing
├── logs/                  # Pipeline execution logs (created on first run)
└── README.md              # This file
```

## Prerequisites

- Python 3.8 or higher
- `boto3` library for R2 uploads
- Access to Cloudflare R2 storage (account ID, access keys, bucket)

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd marumarecki_ingestion/sejm_api_pipeline
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install boto3
```

### 4. Configure Environment Variables

Create a `.env` file or set environment variables for R2 credentials:

```bash
export R2_ACCOUNT_ID="your-account-id"
export R2_ACCESS_KEY_ID="your-access-key-id"
export R2_SECRET_ACCESS_KEY="your-secret-access-key"
export R2_BUCKET_NAME="your-bucket-name"
```

Or load them in your script using `python-dotenv`:

```bash
pip install python-dotenv
```

Then in your scripts:

```python
from dotenv import load_dotenv
load_dotenv()
```

## Usage

### Running the Main Pipeline

The `pipeline.py` script is the main entry point. It supports both single task and batch processing modes.

#### Single Task Mode

Fetch data from the Sejm API and save locally:

```bash
python pipeline.py --api-url "https://api.sejm.gov.pl/sejm/term10/MP" --output-local "sejm_term10_mps.json"
```

Upload to R2:

```bash
python pipeline.py \
  --api-url "https://api.sejm.gov.pl/sejm/term10/MP" \
  --r2-bucket "my-bucket" \
  --r2-key "data/sejm/term10/mps.json"
```

With SSL verification:

```bash
python pipeline.py \
  --api-url "https://api.sejm.gov.pl/sejm/term10/MP" \
  --verify-ssl \
  --output-local "sejm_term10_mps.json" \
  --r2-bucket "my-bucket" \
  --r2-key "data/sejm/term10/mps.json"
```

#### Batch Mode with Configuration File

Process multiple API endpoints in a single run using a config file:

```bash
python pipeline.py --config config.json
```

Create a `config.json` file based on `config.example.json`:

```json
{
  "r2_defaults": {
    "bucket": "my-bucket",
    "account_id": null,
    "access_key": null,
    "secret_key": null
  },
  "tasks": [
    {
      "api_url": "https://api.sejm.gov.pl/sejm/term10/MP",
      "r2_key": "data/sejm/term10/mps.json",
      "verify_ssl": false
    },
    {
      "api_url": "https://api.sejm.gov.pl/sejm/term9/MP",
      "r2_key": "data/sejm/term9/mps.json",
      "verify_ssl": false
    }
  ]
}
```

The script will loop through each task and:
- Fetch data from the API
- Optionally save locally
- Upload to R2 using the specified key (folder structure supported)
- Log results

#### Command-Line Arguments

**Single Task Mode:**
- `--api-url`: The API endpoint URL (required for single task mode)
- `--verify-ssl`: Enable SSL certificate verification (default: False)
- `--output-local`: Path to save JSON locally (optional)
- `--r2-bucket`: R2 bucket name (optional, uses env var if not provided)
- `--r2-key`: Object key in R2 (e.g., "folder/subfolder/file.json")
- `--r2-account-id`: R2 account ID (optional, uses env var)
- `--r2-access-key`: R2 access key ID (optional, uses env var)
- `--r2-secret-key`: R2 secret access key (optional, uses env var)

**Batch Mode:**
- `--config`: Path to configuration JSON file with multiple tasks

### Running the Standalone Script

For simpler use cases, use `sejm_api_ingestion.py`:

```bash
python sejm_api_ingestion.py
```

This fetches from the hardcoded URL and saves locally. For SSL issues, set `SEJM_API_VERIFY_SSL=0`:

```bash
SEJM_API_VERIFY_SSL=0 python sejm_api_ingestion.py
```

### Using the Jupyter Notebook

1. Open `notebook.ipynb` in VS Code or Jupyter Lab
2. Ensure the Python kernel is set to your virtual environment
3. Run the cells step by step

The notebook contains examples of fetching data and uploading to R2.

## Scheduled Execution with GitHub Actions

This repository includes a GitHub Actions workflow that runs the pipeline on schedule.

### Setup

1. **Add repository secrets** in your GitHub repo settings:
   - `R2_ACCOUNT_ID`
   - `R2_ACCESS_KEY_ID`
   - `R2_SECRET_ACCESS_KEY`
   - `R2_BUCKET_NAME`

2. **Create a configuration file** in the repository root (`sejm_api_pipeline/config.json`) with your API tasks.

3. **Review the workflow** in `.github/workflows/scheduled-pipeline.yml`:
   - Default: Runs daily at 2:00 AM UTC
   - Manual trigger: Available via GitHub Actions UI
   - Uses `actions/upload-artifact@v4` for artifact uploads, compatible with the latest GitHub Actions artifacts API
   - Uploads pipeline outputs from `sejm_api_pipeline/artifact/` using the same path structure as the configured R2 key

### Customizing the Schedule

Edit `.github/workflows/scheduled-pipeline.yml` to change the schedule:

```yaml
on:
  schedule:
    # Run daily at 2:00 AM UTC
    - cron: '0 2 * * *'
    # Or run weekly on Monday at 3:00 AM UTC
    # - cron: '0 3 * * 1'
```

Cron format: `minute hour day month day-of-week`

### Manual Trigger

Run the pipeline manually from GitHub Actions:
1. Go to your repository's Actions tab
2. Select "Scheduled Sejm API Ingestion"
3. Click "Run workflow"

### Viewing Logs

1. Go to Actions tab in GitHub
2. Select the workflow run
3. View logs for each step
4. Failed runs will have artifacts with pipeline logs available for download

## API Details

- **Base URL**: `https://api.sejm.gov.pl/sejm/`
- **Example Endpoint**: `term10/MP` (Members of Parliament for term 10)
- **Response**: JSON array of MP data

## R2 Storage

- Uses S3-compatible API
- Supports folder structures via the `--r2-key` parameter (e.g., "data/2023/sejm/mps.json")
- Credentials loaded from environment variables or command-line args

## Troubleshooting

### SSL Certificate Errors

If you encounter SSL verification errors:

1. Disable SSL verification: `--verify-ssl` (not recommended for production)
2. Install proper CA certificates on your system
3. Use a proxy that handles SSL

### Module Not Found Errors

Ensure you're running in the correct virtual environment and have installed dependencies:

```bash
source venv/bin/activate
pip install boto3
```

### R2 Upload Failures

- Verify your R2 credentials and bucket name
- Check that the bucket exists and you have write permissions
- Ensure the account ID is correct

## Development

### Adding New API Endpoints to Batch Config

Simply add a new task object to the `tasks` array in your `config.json`:

```json
{
  "tasks": [
    {
      "api_url": "https://api.sejm.gov.pl/sejm/term11/MP",
      "r2_key": "data/sejm/term11/mps.json",
      "verify_ssl": false
    }
  ]
}
```

Optional fields per task:
- `output_local`: Save to a local file before uploading
- `verify_ssl`: Override default SSL verification (default: false)
- `r2_bucket`: Override default bucket per task
- `r2_account_id`, `r2_access_key`, `r2_secret_key`: Override credentials per task

### Extending the Code

1. **Adding New API Endpoints**: Modify `api_fetcher/fetcher.py` to add new fetch functions
2. **Adding New Storage Backends**: Create new upload functions in `storage/`
3. **Adding New Features**: Update `pipeline.py` to support new modes or parameters

### Adding New API Fetcher Functions

Edit `api_fetcher/fetcher.py`:

```python
def fetch_json_from_custom_api(api_url, auth_token=None, timeout=30):
    """Fetch JSON from a custom API with optional authentication."""
    headers = {"User-Agent": "python-api-client/1.0"}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    # Your implementation here
    return fetch_json_from_api(api_url, headers=headers, timeout=timeout)
```

Then use it in `pipeline.py` or batch config.

### Adding New Storage Backends

Create a new file in `storage/` (e.g., `storage/s3_uploader.py`):

```python
def upload_to_aws_s3(payload, bucket, key, region='us-east-1'):
    """Upload to AWS S3 instead of R2."""
    # Implementation here
    pass
```

Import and use in `pipeline.py` as needed.

## License

[Add license information here]

## Contributing

[Add contribution guidelines here]