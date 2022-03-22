import typing as t
from pathlib import Path
from csv import DictReader
from collections import OrderedDict


def read_csv(csv_path: Path, constants) -> t.Dict[str, t.Dict[str, str]]:
    minimum_expected_headers = constants.csv.in_file.headers
    row_key = minimum_expected_headers[0]
    csv_as_rows = OrderedDict()

    with open(csv_path, "r") as handle:
        reader = DictReader(handle)
        for row in reader:
            exposure_name = row[row_key]
            csv_as_rows[exposure_name] = row
    return csv_as_rows
