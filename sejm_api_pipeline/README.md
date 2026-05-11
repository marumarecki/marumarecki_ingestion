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
├── pipeline.py            # Main pipeline script
├── sejm_api_ingestion.py  # Standalone ingestion script
├── notebook.ipynb         # Jupyter notebook with examples
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

The `pipeline.py` script is the main entry point. It accepts command-line arguments for flexibility.

#### Basic Usage

Fetch data from the Sejm API and save locally:

```bash
python pipeline.py --api-url "https://api.sejm.gov.pl/sejm/term10/MP" --output-local "sejm_term10_mps.json"
```

#### Upload to R2

Fetch data and upload directly to R2:

```bash
python pipeline.py \
  --api-url "https://api.sejm.gov.pl/sejm/term10/MP" \
  --r2-bucket "my-bucket" \
  --r2-key "data/sejm/term10/mps.json"
```

#### Full Example with SSL Verification

```bash
python pipeline.py \
  --api-url "https://api.sejm.gov.pl/sejm/term10/MP" \
  --verify-ssl \
  --output-local "sejm_term10_mps.json" \
  --r2-bucket "my-bucket" \
  --r2-key "data/sejm/term10/mps.json"
```

#### Command-Line Arguments

- `--api-url`: The API endpoint URL (required)
- `--verify-ssl`: Enable SSL certificate verification (default: False)
- `--output-local`: Path to save JSON locally (optional)
- `--r2-bucket`: R2 bucket name (optional, uses env var if not provided)
- `--r2-key`: Object key in R2 (e.g., "folder/subfolder/file.json")
- `--r2-account-id`: R2 account ID (optional, uses env var)
- `--r2-access-key`: R2 access key ID (optional, uses env var)
- `--r2-secret-key`: R2 secret access key (optional, uses env var)

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

### Adding New API Endpoints

1. Modify `api_fetcher/fetcher.py` to add new fetch functions
2. Update `pipeline.py` to accept new parameters
3. Test with the notebook

### Extending Storage Options

1. Add new upload functions in `storage/`
2. Update `pipeline.py` to support new storage backends

## License

[Add license information here]

## Contributing

[Add contribution guidelines here]