import pathlib
import PyPDF2
import pytest

import textract

from nobubo import utils


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
        return [float(page.cropBox[2])-float(page.cropBox[0]), float(page.cropBox[3])-float(page.cropBox[1])]

    def pagecount(self, filename: str) -> int:
        reader = self.readers[filename]
        return reader.getNumPages()

    def pages_order(self, filepath: str, pageamount: int=1) -> [str, str]:
        text = str(textract.process(filepath, encoding="utf-8"), "utf-8").split("\n\n")
        # texteract finds ascii value '\f' (form feed) that must be removed
        res = list(filter(lambda a: a != '\x0c' and a != '\x0c1', text))
        # tests for the first element in the top left corner and the last element in the bottom right corner
        return [res[0], res[-1]]
    # [arr[i::count] for i in range(count)]

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
def pdfproperty() -> utils.PDFProperties:
    return utils.PDFProperties(number_of_pages=57, x_offset=483.307, y_offset=729.917)
    # 8 cols, 7 rows + 1 overview page = 57

@pytest.fixture
def one_overview_even() -> utils.Layout:
    return utils.Layout(overview=1, columns=8, rows=7)


@pytest.fixture
def one_overview_uneven() -> utils.Layout:
    return utils.Layout(overview=1, columns=9, rows=4)


@pytest.fixture()
def two_overviews() -> [utils.Layout, utils.Layout]:
    first = utils.Layout(overview=1, columns=5, rows=5)
    second = utils.Layout(overview=27, columns=5, rows=5)
    return [first, second]


@pytest.fixture()
def one_pdf_page_same_boxes() -> PyPDF2.pdf.PageObject:
    return PyPDF2.pdf.PageObject.createBlankPage(None, 483.307, 729.917)


@pytest.fixture()
def n_up_factor_a0() -> utils.Factor:
    return utils.Factor(x=4, y=4)


@pytest.fixture()
def nup_factor_custom() -> utils.Factor:
    return utils.Factor(x=5, y=4)