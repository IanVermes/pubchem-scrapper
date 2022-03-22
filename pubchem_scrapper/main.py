import argparse
import textwrap
import pathlib

from pubchem_scrapper import guard
from pubchem_scrapper import utils
from pubchem_scrapper import io
from pubchem_scrapper import scrapping

_THIS_FILE = __file__


def main(in_file_csv, constants_yml, webdriver_dir):
    # Check arguments
    guard.guard_contants(constants_yml=constants_yml)
    guard.guard_webdriver(webdriver_dir=webdriver_dir)
    constants = utils.create_constants(constants_yml)
    guard.guard_csv(csv=in_file_csv, constants=constants)

    # Parse the input CSV and get dta out of it
    csv_as_rows = io.read_csv(in_file_csv, constants)
    exposure_names = list(csv_as_rows.keys())

    # Scrape!
    scraped_results = scrapping.scrape(exposure_names, webdriver_dir, constants)


def build_arg_parser():
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(
            """\
        ----------------------------------------------------------------------
        PubChem scraper
        ----------------------------------------------------------------------

        typical usage:
            Backup production environment to localcontainer
                $ %(prog)s --in CSV_FILE
        """
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--in",
        action="store",
        type=pathlib.Path,
        help="the IN file (a csv) to be used in the scrape",
    )
    parser.add_argument(
        "--constants",
        type=pathlib.Path,
        default=(pathlib.Path(_THIS_FILE) / "../../constants.yml").resolve(),
        help="the CONSTANTS (yml) file",
    )
    parser.add_argument(
        "--webdriver",
        type=pathlib.Path,
        default=(pathlib.Path(_THIS_FILE) / "../../webdriver").resolve(),
        help="the WEBDRIVER directory",
    )
    return parser
