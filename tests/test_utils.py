import pytest
import PyPDF2

from nobubo import utils
# setup: a4 output, custom output  input_properties (PDF Properties)
# 483.307, 729.917


@pytest.fixture
def pdfproperty() -> utils.PDFProperties:
    return utils.PDFProperties(number_of_pages=57, x_offset=483.307, y_offset=729.917)


@pytest.fixture
def one_overview() -> utils.Layout:
    return utils.Layout(overview=1, columns=8, rows=7)


@pytest.fixture()
def two_overviews() -> [utils.Layout, utils.Layout]:
    first = utils.Layout(overview=1, columns=5, rows=5)
    second = utils.Layout(overview=27, columns=5, rows=5)
    return [first, second]


@pytest.fixture()
def one_pdf_page_differing_boxes() -> PyPDF2.pdf.PageObject:
    page = PyPDF2.pdf.PageObject.createBlankPage(None, 595, 842)
    page.cropBox = PyPDF2.generic.RectangleObject([52.41, 106.81, 542.28, 736.05])
    return page


@pytest.fixture()
def one_pdf_page_same_boxes() -> PyPDF2.pdf.PageObject:
    return PyPDF2.pdf.PageObject.createBlankPage(None, 595, 842)


class TestCalculations:

    def test_calculate_pages_needed(self):
        pass

    def test_calculate_offset(self) -> [float, float]:
        pass

    def test_userspaceunits_conversion_a4(self):
        pass

    def test_userspaceunits_conversion_custom(self):
        pass

    def test_calculate_nup_factors(self):
        pass

    def test_conversion_to_mm(self):
        mm = utils.convert_to_mm("920x1187")
        assert mm[0] == 920
        assert mm[1] == 1187




    # test auf landscape und portrait
    # test with 1 overview page, test with 2 overview pages
    # test for a4 output, custom output 920x1187,