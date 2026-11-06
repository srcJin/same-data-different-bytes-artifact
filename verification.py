"""Standalone Algorithm 1 adapter for the proposed configuration only.

The canonicalization implementation is copied unchanged from the paper's
versioned implementation. This adapter removes dependencies on the unpublished
legacy agent harness; it does not authenticate records or grant access.
"""
import re
from decimal_extension.integrity import canonical_digest_v2, Reject
from decimal_extension.profile import PROFILE, UNSUPPORTED_REASONS


def owner_record(raw: bytes, record_id: str = 'example-owner') -> dict:
    record = {'record_id': record_id, 'canonical_profile': PROFILE}
    try:
        record['canonical_id'] = canonical_digest_v2(raw)
    except Reject as error:
        record['canonical_id_absent'] = error.reason
    return record


def verify(raw: bytes, record: dict | None, record_id: str = 'example-owner') -> dict:
    result = {'status': 'unavailable', 'expected': None, 'observed': None,
              'algorithm': PROFILE, 'reference_record_id': record_id, 'error': None}
    if record is None:
        result['error'] = 'reference_unavailable'
    elif record.get('record_id') != record_id:
        result['error'] = 'reference_identity_mismatch'
    elif record.get('canonical_profile') != PROFILE:
        result['error'] = 'reference_profile_unavailable_or_incompatible'
    elif record.get('canonical_id_absent'):
        reason = record['canonical_id_absent']
        result.update(status='unsupported_input' if reason in UNSUPPORTED_REASONS else 'invalid_input', error=reason)
    elif not isinstance(record.get('canonical_id'), str) or not re.fullmatch('[0-9a-f]{64}', record['canonical_id']):
        result['error'] = 'reference_digest_unavailable'
    else:
        try:
            observed = canonical_digest_v2(raw)
            expected = record['canonical_id']
            result.update(expected=expected, observed=observed,
                          status='match' if observed == expected else 'mismatch')
        except Reject as error:
            result.update(status='unsupported_input' if error.reason in UNSUPPORTED_REASONS else 'invalid_input', error=error.reason)
    return result
