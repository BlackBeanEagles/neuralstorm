"""QR sharing for sourced rules profiles."""

from __future__ import annotations

import io
from urllib.parse import urlencode, urlsplit

import segno

from binwise.rules import load_locations


def qr_payload(location_id: str, base_url: str) -> dict[str, str]:
    location = next((item for item in load_locations() if item["id"] == location_id), None)
    if location is None or not location.get("qr_shareable"):
        raise ValueError("No shareable QR guide for this profile")

    parsed = urlsplit(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("BINWISE_PUBLIC_URL must be an HTTP or HTTPS base URL")
    if (
        parsed.username
        or parsed.password
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("BINWISE_PUBLIC_URL must be an origin without a path or parameters")

    share_url = f"{base_url.rstrip('/')}/?{urlencode({'site': location_id})}"
    image = segno.make_qr(share_url, error="h")
    output = io.BytesIO()
    image.save(output, kind="svg", scale=7, border=4, dark="#102b27", light="#ffffff")
    return {
        "share_url": share_url,
        "svg": output.getvalue().decode("utf-8"),
        "location": location["name"],
        "location_hi": location.get("name_hi", ""),
        "note": location.get("qr_note", ""),
        "note_hi": location.get("qr_note_hi", ""),
    }
