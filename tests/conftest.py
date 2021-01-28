import pathlib
import pikepdf
import pytest

import textract

import nobubo.core
from nobubo import core, calc


class PdfTester:
    def __init__(self, outputdir: pathlib.Path) -> None:
        self.outputdir = outputdir
        self.readers = {}  # reader for every generated pdf
        self._files = []  # save file objects

    def read(self):
        for filepath in self.outputdir.glob("*.pdf"):
            file = pikepdf.open(filepath)
            self._files.append(file)
            self.readers[filepath.name] = file
        return sorted(self.readers.keys())

    def pagesize(self, filename: str, pagenumber: int=0) -> [float, float]:
        reader = self.readers[filename]
        page = reader.pages[pagenumber]
        if not hasattr(page, "CropBox"):
            box = page.MediaBox
        else:
            box = page.CropBox
        return [round(float(box[2])-float(box[0]), 2),
                round(float(box[3])-float(box[1]), 2)]

    def pagecount(self, filename: str) -> int:
        reader = self.readers[filename]
        return len(reader.pages)

    # TODO is there a better way to check the order of the pages?
    def pages_order(self, filepath: str) -> [str, str]:
        text = str(textract.process(filepath, encoding="utf-8"), "utf-8").split("\n\n")
        # texteract finds ascii value '\f' (form feed, \x0c) that must be removed
        res = list(filter(lambda a: a not in '\x0c', text))
        # tests for the first element in the top left corner and the last element in the bottom right corner
        return [res[0], res[-1]]

    def cleanup(self):
        for file in self._files:
            file.close()


@pytest.fixture
def pdftester(tmp_path):
    tester = PdfTester(tmp_path)
    yield tester
    tester.cleanup()  # executed after every test


@pytest.fixture
def testdata() -> pathlib.Path:
    return pathlib.Path(__file__).parent / "testdata"


@pytest.fixture
def pdfproperty() -> core.InputProperties:
    return core.InputProperties(input_filepath=pathlib.Path("test.pdf"),
                               output_path=pathlib.Path("output_test.pdf"),
                               number_of_pages=57,
                               pagesize=core.PageSize(width=483.307, height=729.917),
                               layout=[core.Layout(first_page=2, columns=8, rows=7)])
    # 8 cols, 7 rows + 1 overview page = 57

@pytest.fixture
def one_overview_even() -> core.Layout:
    return core.Layout(first_page=2, columns=8, rows=7)


@pytest.fixture
def one_overview_uneven() -> core.Layout:
    return core.Layout(first_page=2, columns=9, rows=4)


@pytest.fixture()
def two_overviews() -> [core.Layout, core.Layout]:
    first = core.Layout(first_page=2, columns=5, rows=5)
    second = core.Layout(first_page=28, columns=5, rows=5)
    return [first, second]


@pytest.fixture()
def n_up_factor_a0() -> nobubo.core.Factor:
    return nobubo.core.Factor(x=4, y=4)


@pytest.fixture()
def nup_factor_custom() -> nobubo.core.Factor:
    return nobubo.core.Factor(x=5, y=4)