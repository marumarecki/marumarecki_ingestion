import json
import ssl
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def get_ssl_context(verify_ssl=True):
    """Return an SSL context based on verification preference."""
    return ssl.create_default_context() if verify_ssl else ssl._create_unverified_context()


def fetch_json_from_api(api_url, headers=None, timeout=30, verify_ssl=True):
    """Fetch JSON data from a configurable API endpoint."""
    headers = headers or {"User-Agent": "python-sejm-api-client/1.0"}
    request = Request(api_url, headers=headers)
    ssl_context = get_ssl_context(verify_ssl)

    try:
        with urlopen(request, timeout=timeout, context=ssl_context) as response:
            body = response.read()
            return json.loads(body.decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"API request failed: {exc.code} {exc.reason}") from exc
    except URLError as exc:
        if isinstance(exc.reason, ssl.SSLError):
            if not verify_ssl:
                raise RuntimeError(
                    "SSL verification failed even though verify_ssl is disabled. "
                    "Check if outbound HTTPS traffic is allowed."
                ) from exc
            raise RuntimeError(
                "SSL error: certificate verification failed. "
                "If your environment uses a self-signed proxy or custom CA, disable verification "
                "with verify_ssl=False or install the correct CA certificate."
            ) from exc
        raise RuntimeError(f"API network error: {exc}") from exc
    except ssl.SSLError as exc:
        if not verify_ssl:
            raise RuntimeError(
                "SSL verification failed even though verify_ssl is disabled. "
                "Check if outbound HTTPS traffic is allowed."
            ) from exc
        raise RuntimeError(
            "SSL error: certificate verification failed. "
            "If your environment uses a self-signed proxy or custom CA, disable verification "
            "with verify_ssl=False or install the correct CA certificate."
        ) from exc
    except ValueError as exc:
        raise RuntimeError("Failed to parse JSON response from API") from exc


def save_payload(payload, path):
    """Save the retrieved payload to a JSON file."""
    output_path = Path(path)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path