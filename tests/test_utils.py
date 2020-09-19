import nobubo.utils as utils


class TestCalculations:

    def test_calculate_pages_needed_oneoverview_a0_evenlayout(self, one_overview_even, n_up_factor_a0):
        assert utils.calculate_pages_needed(one_overview_even, n_up_factor_a0) == 4

    def test_calculate_pages_needed_oneoverview_custom_evenlayout(self, one_overview_even, n_up_factor_custom):
        assert utils.calculate_pages_needed(one_overview_even, n_up_factor_custom) == 4

    def test_calculate_pages_needed_oneoverview_a0_unevenlayout(self, one_overview_uneven, n_up_factor_a0):
        assert utils.calculate_pages_needed(one_overview_uneven, n_up_factor_a0) == 3

    def test_calculate_pages_needed_oneoverview_custom_unevenlayout(self, one_overview_uneven, n_up_factor_custom):
        assert utils.calculate_pages_needed(one_overview_uneven, n_up_factor_custom) == 2

    def test_calculate_offset(self, one_pdf_page_same_boxes):
        assert utils.calculate_offset(one_pdf_page_same_boxes) == [483.307, 729.917]

    def test_userspaceunits_conversion_a0(self):
        paper = utils.convert_to_userspaceunits([841, 1189])
        assert paper.width == 2383.937
        assert paper.height == 3370.394

    def test_userspaceunits_conversion_custom(self):
        paper = utils.convert_to_userspaceunits([920, 1187])
        assert paper.width == 2607.874
        assert paper.height == 3364.724

    def test_calculate_nup_factors(self, pdfproperty, n_up_factor_custom):
        factor = utils.calculate_nup_factors("920x1187", pdfproperty)
        assert factor.x == n_up_factor_custom.x
        assert factor.y == n_up_factor_custom.y

    def test_conversion_to_mm(self):
        mm = utils.convert_to_mm("920x1187")
        assert mm[0] == 920
        assert mm[1] == 1187

