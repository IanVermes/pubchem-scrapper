from pathlib import Path
from csv import DictReader

import yaml

from pubchem_scrapper.utils import get_web_browser, create_constants


def guard_csv(csv: Path, constants):
    if not csv.exists():
        msg = f"Cannot find file: '{str(csv)}'"
        raise ValueError(msg)
    with open(csv, "r") as handle:
        sample = handle.read(1024)
        reader = DictReader(handle)
        headers = reader.fieldnames
    has_headers = bool(headers)
    if not has_headers:
        msg = f"CSV '{str(csv)}' has no headers"
        raise ValueError(msg)
    has_expected_headers = set(constants.csv.in_file.headers).issubset(set(headers))
    if not has_expected_headers:
        msg = f"CSV '{str(csv)}' has wrong headers: {headers}"
        raise ValueError(msg)
    return


def guard_contants(constants_yml: Path):
    if not constants_yml.exists():
        msg = f"Cannot find file: '{str(constants_yml)}'"
        raise ValueError(msg)
    with open(constants_yml, "r") as handle:
        _ = yaml.safe_load(handle)
    constants = create_constants(constants_yml)
    if not constants.is_valid():
        msg = f"The parsed yml '{constants_yml}' is not valid"
        raise ValueError(msg)
    return


def guard_webdriver(webdriver_dir: Path):
    get_web_browser(webdriver_dir, headless=False)
    return
