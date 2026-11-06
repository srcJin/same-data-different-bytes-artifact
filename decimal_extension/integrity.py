"""Exact-token admission followed by NFC, JCS, and SHA-256.

Decimal equality concerns JSON numeric values, not significant figures. JCS
still uses binary64; only values preserved in its final decimal text pass.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
import hashlib
import json
import math

import rfc8785

from vendor.canon import canon
from .profile import MAX_BYTES, MAX_DEPTH, MAX_NUMBER_CHARS, MAX_ABS_EXPONENT

Reject = canon.Reject
SAFE_INTEGER = canon.SAFE_INTEGER


def _decimal_token(token: str) -> Decimal:
    if len(token) > MAX_NUMBER_CHARS:
        raise Reject("RESOURCE_LIMIT")
    exponent = token.lower().partition("e")[2]
    if exponent and abs(int(exponent)) > MAX_ABS_EXPONENT:
        raise Reject("RESOURCE_LIMIT")
    try:
        return Decimal(token)
    except InvalidOperation:
        raise Reject("MALFORMED_JSON") from None


def _check_depth(text: str) -> None:
    # Check before the recursive JSON decoder; ignore brackets inside strings.
    depth = 0
    in_string = escaped = False
    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char in "[{":
            depth += 1
            if depth > MAX_DEPTH:
                raise Reject("RESOURCE_LIMIT")
        elif char in "]}":
            depth -= 1


def parse_exact(raw: bytes):
    """Parse original UTF-8 JSON without any binary floating-point conversion.

    This parser also serves the independent answer comparator. Numeric profile
    admission happens later, so scoring can distinguish unsupported numbers.
    """
    if not isinstance(raw, bytes):
        raise TypeError("original JSON bytes required")
    if len(raw) > MAX_BYTES:
        raise Reject("RESOURCE_LIMIT")
    text = canon._decode(raw)
    _check_depth(text)
    try:
        value = json.loads(text, object_pairs_hook=canon._reject_duplicates,
                           parse_int=_decimal_token, parse_float=_decimal_token,
                           parse_constant=canon._non_finite)
    except (json.JSONDecodeError, InvalidOperation):
        raise Reject("MALFORMED_JSON") from None
    canon._require_scalar_unicode(value)
    return value


def exact_equal(left, right) -> bool:
    """Structural decimal equality; never equates a Boolean with a number."""
    if isinstance(left, Decimal) or isinstance(right, Decimal):
        return isinstance(left, Decimal) and isinstance(right, Decimal) and left == right
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(exact_equal(v, right[k]) for k, v in left.items())
    if isinstance(left, list):
        return len(left) == len(right) and all(exact_equal(a, b) for a, b in zip(left, right))
    return left == right


def _jcs_input(value):
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            # Compare directly: Decimal abs() can apply the active context.
            if value > SAFE_INTEGER or value < -SAFE_INTEGER:
                raise Reject("NUMBER_OUT_OF_RANGE")
            return int(value)
        result = float(value)
        if not math.isfinite(result):
            raise Reject("NUMBER_OUT_OF_RANGE")
        return result
    if isinstance(value, dict):
        return {key: _jcs_input(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jcs_input(item) for item in value]
    return value


def canonical_bytes_v2(raw: bytes) -> bytes:
    source = canon._fold_nfc(parse_exact(raw))
    candidate = rfc8785.dumps(_jcs_input(source))
    if not exact_equal(source, parse_exact(candidate)):
        raise Reject("NUMBER_PRECISION_LOSS")
    return candidate


def canonical_digest_v2(raw: bytes) -> str:
    return hashlib.sha256(canonical_bytes_v2(raw)).hexdigest()
