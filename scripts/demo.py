"""Run the paper's distinction without a model, server or API key."""
import json
from verification import owner_record, verify
from baseline.recipe import canonical_checksum

reference = b'{"units":34}'
record = owner_record(reference)
for label, candidate, owner in [
    ('equivalent re-encoding', b'{"units":34.0}', record),
    ('altered content', b'{"units":43}', record),
    ('unavailable reference', b'{"units":34.0}', None),
    ('unsupported precision', b'{"units":34.000000000000001}', record),
]:
    result = verify(candidate, owner)
    baseline_match = None if owner is None else canonical_checksum(json.loads(reference)) == canonical_checksum(json.loads(candidate))
    print(json.dumps({'case': label, 'baseline_checksum_match': baseline_match, **result}))
