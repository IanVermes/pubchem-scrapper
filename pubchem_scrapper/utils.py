import typing as t
import pathlib
from dataclasses import dataclass

from selenium import webdriver
import yaml

t_SupportedWebBrowsers = t.Union[webdriver.Firefox, webdriver.Chrome]


@dataclass
class DataSelectorConstants:
    cid: str
    iupac: str

    @classmethod
    def from_yaml(cls, yaml_data) -> "DataSelectorConstants":
        cid = yaml_data.get("cid", "")
        iupac = yaml_data.get("iupac", "")
        return cls(cid=cid, iupac=iupac)

    def is_valid(self) -> bool:
        return all([self.cid, self.iupac])


@dataclass
class ScrapeConstants:
    name: str
    url: str
    main_selector: str
    fallback_selector: str
    data_selectors: DataSelectorConstants

    @classmethod
    def from_yaml(cls, yaml_data) -> "ScrapeConstants":
        name = yaml_data.get("name", "")
        url = yaml_data.get("url", "")
        main_selector = yaml_data.get("main_selector", "")
        fallback_selector = yaml_data.get("fallback_selector", "")
        data_selectors = DataSelectorConstants.from_yaml(
            yaml_data.get("data_selectors", {})
        )
        obj = cls(
            name=name,
            url=url,
            main_selector=main_selector,
            fallback_selector=fallback_selector,
            data_selectors=data_selectors,
        )
        return obj

    def is_valid(self) -> bool:
        return all(
            [
                self.name,
                self.url,
                self.main_selector,
                self.fallback_selector,
                self.data_selectors.is_valid(),
            ]
        )


@dataclass
class CsvProperties:
    headers: t.List[str]

    @classmethod
    def from_yaml(cls, yaml_data) -> "CsvProperties":
        headers = yaml_data.get("headers", [])
        obj = cls(headers=headers)
        return obj

    def is_valid(self) -> bool:
        return all([len(self.headers)])


@dataclass
class CsvConstants:
    in_file: CsvProperties
    out_file: CsvProperties

    @classmethod
    def from_yaml(cls, yaml_data) -> "CsvConstants":
        in_file = CsvProperties.from_yaml(yaml_data.get("in_file", {}))
        out_file = CsvProperties.from_yaml(yaml_data.get("out_file", {}))
        obj = cls(in_file=in_file, out_file=out_file)
        return obj

    def is_valid(self) -> bool:
        return all([self.in_file.is_valid(), self.out_file.is_valid()])


@dataclass
class Constants:
    target: ScrapeConstants
    csv: CsvConstants

    @classmethod
    def from_yaml(cls, yaml_data) -> "Constants":
        target = ScrapeConstants.from_yaml(yaml_data.get("target", {}))
        csv = CsvConstants.from_yaml(yaml_data.get("csv", {}))
        return cls(target=target, csv=csv)

    def is_valid(self) -> bool:
        return all([self.target.is_valid(), self.csv.is_valid()])


def create_constants(constants_yaml: pathlib.Path) -> "Constants":
    with open(constants_yaml, "r") as handle:
        data = yaml.safe_load(handle)
    return Constants.from_yaml(data)


def get_browser_factory(directory: pathlib.Path):
    files: t.List[pathlib.Path] = [
        file for file in directory.glob("*") if not file.name.startswith(".")
    ]
    if len(files) != 1:
        raise ValueError(f"Expected 1 exectuable, got: {files!r}")
    else:
        exectuable = files.pop()
    if "geckodriver" == exectuable.name:
        OptionsFactory = webdriver.firefox.options.Options
        BrowserFactory = webdriver.Firefox
    elif "chromedriver" == exectuable.name:
        OptionsFactory = webdriver.chrome.options.Options
        BrowserFactory = webdriver.Chrome
    else:
        msg = f"Expected to find either a Firefox 'geckodriver' or Chrome 'chromedriver' binary, got {path.name}"
        raise ValueError(msg)
    return BrowserFactory, OptionsFactory, exectuable


def create_browser(
    directory: pathlib.Path, headless: bool = False
) -> t_SupportedWebBrowsers:

    BrowserFactory, OptionsFactory, exectuable = get_browser_factory(directory)
    options = OptionsFactory()
    options.headless = headless
    path = str(exectuable)
    browser = BrowserFactory(executable_path=path_s, options=options)
    return browser
