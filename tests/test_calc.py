import pathlib

import pytest

import nobubo.cli
import nobubo.disassembly
import nobubo.init_nobubo
from nobubo.assembly import Layout, PageSize
from nobubo.disassembly import Factor, NobuboOutput
from nobubo.init_nobubo import to_userspaceunits

INPUT_PAGE = PageSize(width=483.307, height=729.917)

nup_factor_a0 = Factor(x=4, y=4)
nup_factor_custom = Factor(x=5, y=4)
nup_factor_us = Factor(x=5, y=4)

one_overview_even = Layout(first_page=2, columns=8, rows=7)
one_overview_uneven = Layout(first_page=2, columns=9, rows=4)
two_overviews = [
    Layout(first_page=2, columns=5, rows=5),
    Layout(first_page=28, columns=5, rows=5),
]

CUSTOM = [920, 1187]
A0 = [841, 1189]
US = [914, 1220]


@pytest.fixture
def test_outputdata():
    return NobuboOutput(output_path=pathlib.Path(""), output_pagesize=None)


class TestOutputCalculations:
    @pytest.mark.parametrize(
        "overview, nup, expected",
        [
            (one_overview_even, nup_factor_a0, 4),
            (one_overview_even, nup_factor_custom, 4),
            (one_overview_uneven, nup_factor_a0, 3),
            (one_overview_uneven, nup_factor_custom, 2),
        ],
    )
    def test_calculate_pages_needed(self, test_outputdata, overview, nup, expected):
        assert test_outputdata.pages_needed(overview, nup) == expected

    @pytest.mark.parametrize(
        "format, expected_width, expected_height",
        [
            (A0, 2383.937, 3370.394),
            (US, 2590.866, 3458.268),
            (CUSTOM, 2607.874, 3364.724),
        ],
    )
    def test_userspaceunits_conversion(self, format, expected_width, expected_height):
        paper = to_userspaceunits(format)
        assert paper.width == expected_width
        assert paper.height == expected_height

    @pytest.mark.parametrize(
        "input_pagesize, output_pagesize, expected_factor",
        [
            (INPUT_PAGE, A0, nup_factor_a0),
            (INPUT_PAGE, US, nup_factor_us),
            (INPUT_PAGE, CUSTOM, nup_factor_custom),
        ],
    )
    def test_calculate_nup_factors(
        self, input_pagesize, output_pagesize, expected_factor, test_outputdata
    ):
        output_in_userspace_units = to_userspaceunits(output_pagesize)
        factor = test_outputdata.nup_factors(input_pagesize, output_in_userspace_units)
        assert factor.x == expected_factor.x
        assert factor.y == expected_factor.y


class TestCliHelpers:
    def test_conversion_to_mm(self):
        mm = nobubo.init_nobubo.to_mm("920x1187")
        assert mm[0] == 920
        assert mm[1] == 1187

    @pytest.mark.parametrize(
        "cli_arg, expected_pagesize",
        [
            ("a0", PageSize(width=2383.937, height=3370.394)),
            ("us", PageSize(width=2590.866, height=3458.268)),
            ("123x456", PageSize(width=348.661, height=1292.598)),
            ("123x456s", PageSize(width=348.661, height=1292.598)),
        ],
    )
    def test_parse_output_layout_a0(self, cli_arg, expected_pagesize):
        assert nobubo.init_nobubo.parse_output_layout(cli_arg) == expected_pagesize

    def test_parse_output_layout_with_margin(self):
        assert nobubo.init_nobubo.parse_output_layout("a0", 20) == PageSize(
            width=2270.551, height=3257.008
        )
