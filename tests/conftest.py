import pathlib
import PyPDF2
import pytest

import nobubo.utils as utils


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
def n_up_factor_custom() -> utils.Factor:
    return utils.Factor(x=5, y=4)

# factors with 8 cols, 7 rows, edge cases (kleid 2013)

# a4

# custom

# factors with 9 cols, 4 rows, edge cases (kastenjacke)

# a4


# custom
