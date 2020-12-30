import pathlib
import PyPDF2
import pytest

import textract

from nobubo import core, calc


class PdfTester:
    def __init__(self, outputdir: pathlib.Path) -> None:
        self.outputdir = outputdir
        self.readers = {}  # reader for every generated pdf
        self._files = []  # save file objects

    def read(self):
        for filepath in self.outputdir.glob("*.pdf"):
            file = open(filepath, "rb")
            self._files.append(file)
            self.readers[filepath.name] = PyPDF2.PdfFileReader(file)
        return sorted(self.readers.keys())

    def pagesize(self, filename: str, pagenumber: int=0) -> [float, float]:
        reader = self.readers[filename]
        page = reader.getPage(pagenumber)
        return [round(float(page.cropBox[2])-float(page.cropBox[0]), 2), round(float(page.cropBox[3])-float(page.cropBox[1]), 2)]

    def pagecount(self, filename: str) -> int:
        reader = self.readers[filename]
        return reader.getNumPages()

    # TODO is there a better way to check the order of the pages?
    def pages_order(self, filepath: str, pageamount: int=1) -> [str, str]:
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
                               layout=[core.Layout(overview=1, columns=8, rows=7)])
    # 8 cols, 7 rows + 1 overview page = 57

@pytest.fixture
def one_overview_even() -> core.Layout:
    return core.Layout(overview=1, columns=8, rows=7)


@pytest.fixture
def one_overview_uneven() -> core.Layout:
    return core.Layout(overview=1, columns=9, rows=4)


@pytest.fixture()
def two_overviews() -> [core.Layout, core.Layout]:
    first = core.Layout(overview=1, columns=5, rows=5)
    second = core.Layout(overview=27, columns=5, rows=5)
    return [first, second]


@pytest.fixture()
def one_pdf_page_same_boxes() -> PyPDF2.pdf.PageObject:
    return PyPDF2.pdf.PageObject.createBlankPage(None, 483.307, 729.917)


@pytest.fixture()
def n_up_factor_a0() -> calc.Factor:
    return calc.Factor(x=4, y=4)


@pytest.fixture()
def nup_factor_custom() -> calc.Factor:
    return calc.Factor(x=5, y=4)