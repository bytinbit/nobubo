
from nobubo import calc


class TestCalculations:

    def test_calculate_pages_needed_oneoverview_a0_evenlayout(self, one_overview_even, n_up_factor_a0):
        assert calc.pages_needed(one_overview_even, n_up_factor_a0) == 4

    def test_calculate_pages_needed_oneoverview_custom_evenlayout(self, one_overview_even, nup_factor_custom):
        assert calc.pages_needed(one_overview_even, nup_factor_custom) == 4

    def test_calculate_pages_needed_oneoverview_a0_unevenlayout(self, one_overview_uneven, n_up_factor_a0):
        assert calc.pages_needed(one_overview_uneven, n_up_factor_a0) == 3

    def test_calculate_pages_needed_oneoverview_custom_unevenlayout(self, one_overview_uneven, nup_factor_custom):
        assert calc.pages_needed(one_overview_uneven, nup_factor_custom) == 2

    def test_userspaceunits_conversion_a0(self):
        paper = calc.to_userspaceunits([841, 1189])
        assert paper.width == 2383.937
        assert paper.height == 3370.394

    def test_userspaceunits_conversion_custom(self):
        paper = calc.to_userspaceunits([920, 1187])
        assert paper.width == 2607.874
        assert paper.height == 3364.724

    def test_calculate_nup_factors(self, nup_factor_custom, pdfproperty):
        factor = calc.nup_factors(pdfproperty.pagesize, [920, 1187])
        assert factor.x == nup_factor_custom.x
        assert factor.y == nup_factor_custom.y

    def test_conversion_to_mm(self):
        mm = calc.to_mm("920x1187")
        assert mm[0] == 920
        assert mm[1] == 1187

    def test_parse_output_layout(self):
        assert calc.parse_output_layout("a0") == [841, 1189]
        assert calc.parse_output_layout("us") == [914, 1220]
        assert calc.parse_output_layout("123x456") == [123, 456]
        assert calc.parse_output_layout("123x456s") == [123, 456]
        assert calc.parse_output_layout("a0", 20) == [801, 1149]
