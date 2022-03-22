import typing as t
from dataclasses import dataclass
from urllib import parse
from pathlib import Path
import logging
import re

RGX_COMPOUND_CID = re.compile(r"(?:compound\scid:\s)(\d+)", re.IGNORECASE)
RGX_COMPOUND_IUPAC = re.compile(
    r"(?:iupac\sname:\s)([\d\w\,\-\s]+?)(?=\s+\n)", re.IGNORECASE
)
WAIT_TIME = 10
LOGGER = logging.getLogger()

from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from pubchem_scrapper import utils

if t.TYPE_CHECKING:
    from selenium import webdriver

    t_SupportedWebBrowsers = t.Union[webdriver.Firefox, webdriver.Chrome]


@dataclass
class ScrapedData:
    name: str
    cid: str
    iupac: str


def scrape(
    exposure_names: t.List[str], webdriver_directory: Path, constants
) -> t.List[ScrapedData]:
    try:
        browser = utils.create_browser(directory=webdriver_directory)
        base_url = constants.target.url

        results = []
        for _, exposure_name in enumerate(exposure_names):
            url = _make_url(base_url, exposure_name)
            result = scrape_compound(browser, url, constants)
            result.name = exposure_name
            LOGGER.info(result)
            results.append(result)
    finally:
        browser.close()
    return results


def scrape_compound(
    browser: "t_SupportedWebBrowsers", url: str, constants
) -> ScrapedData:
    # Get a results card from their search results for a compound
    browser.get(url)
    card_element = get_card_element(browser, constants)

    # However we will want to catch and handle cards that substances not compounds
    card_text = handle_substance_cards(card_element, browser, constants)

    # Finally extract the data
    scraped_data = extract_data_from_element(card_text, constants)
    return scraped_data


def handle_substance_cards(
    card_element: t.Optional[WebElement], browser: "t_SupportedWebBrowsers", constants
) -> str:
    if card_element is None:
        return ""
    orginal_card_text = card_element.text
    is_substance = "Substance SID" in orginal_card_text
    cid = cid = _get_text(orginal_card_text, RGX_COMPOUND_CID)
    if cid and is_substance:
        url = _make_url(constants.target.url, cid)
        browser.get(url)
        alternate_card_element = get_card_element(browser, constants)
        alternate_card_text = (
            alternate_card_element.text if alternate_card_element is not None else ""
        )
        if alternate_card_text:
            return alternate_card_text
    return orginal_card_text


def get_card_element(
    browser: "t_SupportedWebBrowsers", constants
) -> t.Optional[WebElement]:
    card_element = _get_card_element_with_main_selector(browser, constants)
    if card_element is None:
        card_element = _get_card_element_with_fallback_selector(browser, constants)
    if card_element is None:
        card_element = _get_card_element_with_alternate_fallback_selector(
            browser, constants
        )
    return card_element


def extract_data_from_element(element_text: str, constants) -> ScrapedData:
    scraped_data = ScrapedData(name="", cid="", iupac="")
    cid = _get_text(element_text, RGX_COMPOUND_CID)
    iupac = _get_text(element_text, RGX_COMPOUND_IUPAC)
    scraped_data.iupac = iupac
    scraped_data.cid = cid
    return scraped_data


def _get_card_element_with_main_selector(
    browser: "t_SupportedWebBrowsers", constants
) -> t.Optional[WebElement]:
    selector = constants.target.main_selector
    pub_chem_best_match_card = _get_element(browser, selector, label="main")
    return pub_chem_best_match_card


def _get_card_element_with_fallback_selector(
    browser: "t_SupportedWebBrowsers", constants
) -> t.Optional[WebElement]:
    selector = constants.target.fallback_selector
    pub_chem_best_match_card = _get_element(browser, selector, label="fallback")
    return pub_chem_best_match_card


def _get_card_element_with_alternate_fallback_selector(
    browser: "t_SupportedWebBrowsers", constants
) -> t.Optional[WebElement]:
    selector = constants.target.other_fallback_selector
    pub_chem_best_match_card = _get_element(browser, selector, label="alt-fallback")
    return pub_chem_best_match_card


def _make_url(url: str, exposure_name: str) -> str:
    escaped_exposure_name = parse.quote(exposure_name)
    return url + escaped_exposure_name


def _get_element(browser, selector, label: str = "") -> t.Optional[WebElement]:
    try:
        waiting_browser = WebDriverWait(browser, WAIT_TIME, 0.25)
        element = waiting_browser.until(
            lambda x: x.find_element(By.CSS_SELECTOR, selector)
        )
    except (NoSuchElementException, TimeoutException):
        msg = f"{label} selector " if label else "Selector "
        msg += f"could not find the element ('{selector}')."
        LOGGER.warning(msg)
        element = None
    return element


def _get_text(element_text, rgx: t.Pattern) -> str:
    terms = rgx.findall(element_text)
    return terms[0] if terms else ""
