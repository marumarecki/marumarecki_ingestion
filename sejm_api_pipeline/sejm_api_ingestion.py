#!/usr/bin/env python3
"""Fetch Sejm term 10 MP data from the public API."""

import json
import os
import ssl
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_URL = "https://api.sejm.gov.pl/sejm/term10/MP"
OUTPUT_FILE = Path(__file__).resolve().parent / "sejm_term10_mps.json"


def get_ssl_context():
    verify_ssl = os.environ.get("SEJM_API_VERIFY_SSL", "1").lower() not in {"0", "false", "no", "off"}
    return ssl.create_default_context() if verify_ssl else ssl._create_unverified_context()


def fetch_sejm_term10_mps():
    """Fetch JSON data from the Sejm term 10 MP endpoint."""
    request = Request(API_URL, headers={"User-Agent": "python-sejm-api-client/1.0"})
    ssl_context = get_ssl_context()

    try:
        with urlopen(request, timeout=30, context=ssl_context) as response:
            body = response.read()
            return json.loads(body.decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"Sejm API request failed: {exc.code} {exc.reason}") from exc
    except URLError as exc:
        if isinstance(exc.reason, ssl.SSLError):
            verify_env = os.environ.get("SEJM_API_VERIFY_SSL", "1")
            if verify_env.lower() in {"0", "false", "no", "off"}:
                raise RuntimeError(
                    "SSL verification failed even though SEJM_API_VERIFY_SSL is disabled. "
                    "Check that your network allows outbound HTTPS traffic."
                ) from exc
            raise RuntimeError(
                "Sejm API SSL error: certificate verification failed. "
                "If your environment uses a self-signed proxy or custom CA, set SEJM_API_VERIFY_SSL=0 "
                "or install the correct CA certificate."
            ) from exc
        raise RuntimeError(f"Sejm API network error: {exc}") from exc
    except ssl.SSLError as exc:
        verify_env = os.environ.get("SEJM_API_VERIFY_SSL", "1")
        if verify_env.lower() in {"0", "false", "no", "off"}:
            raise RuntimeError(
                "SSL verification failed even though SEJM_API_VERIFY_SSL is disabled. "
                "Check that your network allows outbound HTTPS traffic."
            ) from exc
        raise RuntimeError(
            "Sejm API SSL error: certificate verification failed. "
            "If your environment uses a self-signed proxy or custom CA, set SEJM_API_VERIFY_SSL=0 "
            "or install the correct CA certificate."
        ) from exc
    except ValueError as exc:
        raise RuntimeError("Failed to parse JSON response from Sejm API") from exc


def save_payload(payload, path=OUTPUT_FILE):
    """Save the retrieved payload to a JSON file."""
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def main():
    payload = fetch_sejm_term10_mps()
    count = len(payload) if isinstance(payload, (list, tuple)) else None

    print("Sejm term 10 MP payload loaded.")
    print(f"Payload type: {type(payload).__name__}")
    if count is not None:
        print(f"Item count: {count}")

    output_path = save_payload(payload)
    print(f"Saved JSON payload to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
