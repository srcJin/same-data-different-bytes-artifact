import json
import unittest
from pathlib import Path
from verification import owner_record, verify
from decimal_extension.integrity import canonical_bytes_v2, Reject

ROOT = Path(__file__).resolve().parents[1]

class IntegrityTests(unittest.TestCase):
    def test_all_published_materials(self):
        records = json.loads((ROOT/'data/materials.json').read_text())['records']
        self.assertEqual(len(records), 36)
        for case in records:
            with self.subTest(material=case['id']):
                owner = owner_record(case['reference'].encode())
                self.assertEqual(verify(case['equivalent'].encode(), owner)['status'], 'match')
                self.assertEqual(verify(case['altered'].encode(), owner)['status'], 'mismatch')
                self.assertEqual(verify(case['unavailable_reference_candidate'].encode(), None)['status'], 'unavailable')

    def test_precision_loss_does_not_become_a_mismatch(self):
        result = verify(b'{"x":0.10000000000000001}', owner_record(b'{"x":0.1}'))
        self.assertEqual(result['status'], 'unsupported_input')
        self.assertEqual(result['error'], 'NUMBER_PRECISION_LOSS')
        self.assertIsNone(result['observed'])

    def test_type_and_array_order_matter(self):
        for left, right in [(b'7', b'"7"'), (b'1', b'true'), (b'[1,2]', b'[2,1]')]:
            self.assertEqual(verify(right, owner_record(left))['status'], 'mismatch')

    def test_unicode_and_decimal_equivalence(self):
        self.assertEqual(canonical_bytes_v2(b'{"e\\u0301":15e-1}'), canonical_bytes_v2('{"é":1.50}'.encode()))

    def test_invalid_and_unsupported_reasons(self):
        for raw, reason in [(b'{"x":1,"x":2}', 'DUPLICATE_MEMBER'),
                            (b'{"e\\u0301":1,"\\u00e9":2}', 'NFC_NAME_COLLISION'),
                            (b'NaN', 'NON_FINITE'), (b'"\\ud800"', 'NON_SCALAR_UNICODE'),
                            (b'9007199254740992', 'NUMBER_OUT_OF_RANGE'),
                            (b'['*129+b'0'+b']'*129, 'RESOURCE_LIMIT')]:
            with self.subTest(reason=reason):
                with self.assertRaises(Reject) as error:
                    canonical_bytes_v2(raw)
                self.assertEqual(error.exception.reason, reason)

    def test_reference_checked_before_candidate(self):
        bad_profile = owner_record(b'1')
        bad_profile['canonical_profile'] = 'incompatible'
        self.assertEqual(verify(b'not json', bad_profile)['status'], 'unavailable')
        self.assertEqual(verify(b'1', {'record_id':'wrong'})['error'], 'reference_identity_mismatch')

if __name__ == '__main__':
    unittest.main()
