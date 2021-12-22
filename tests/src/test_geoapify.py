from unittest import TestCase

from app.src.geoapify import get_point_from_address, LowConfidence

valid_addresses = ['Rotermanni 14, 10111 Tallinn, Estonia', 'Maleva põik 1, 11711 Tallinn , Estonia']
invalid_addresses = ['xxxyyyzzz 12, 99999 Rakvere, Estonia', 'Rotermanni 14, 10111 Tallinn, Germany']


class TestGeoCoding(TestCase):

    def test_valid_addresses(self):
        for addr in valid_addresses:
            try:
                get_point_from_address(addr)
            except Exception as e:
                self.fail(f"get_point_from_address() raised {e} unexpectedly!")

    def test_invalid_addresses(self):
        for addr in invalid_addresses:
            with self.assertRaises(LowConfidence):
                get_point_from_address(addr)
