from unittest import TestCase

from app.src.geocoding import process_csv_file

csvfile = "../data/testdata.csv" # This file has been removed, please re-create it.

class TestCSVProcessing(TestCase):

    def test_csv_processing(self):
        try:
            process_csv_file(csvfile)
        except Exception as e:
            self.fail(f"get_point_from_address() raised {e} unexpectedly!")


