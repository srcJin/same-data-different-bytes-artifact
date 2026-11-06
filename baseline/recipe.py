"""The digest recipe of the vendored data layer, extracted unmodified.

Both functions are copied byte-for-byte from the source named in PROVENANCE:

  canonical_json_digest   data_layer_gateway/datafacts.py  -- what the gateway
                          computes when a record is published, and what it
                          re-computes to reject a mismatched digest.
  canonical_checksum      experiments/datafact_v2/field_enforcement.py -- what
                          the publishing side writes into a catalogue entry.
                          Same recipe, a second implementation of it.

They are kept apart here for the same reason they are apart there: the paper's
point is that two sides compute the same thing, and only a written-down rule
makes that true by construction rather than by coincidence.
"""
import hashlib
import json
from typing import Any


def canonical_json_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def canonical_checksum(content: Any) -> str:
    """sha256 of canonical JSON — same recipe as the gateway seeder."""
    canon = json.dumps(content, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()
