# Copyright 2019, Méline Sieber
#
# This file is part of Nobubo.
#
# Nobubo is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Nobubo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Nobubo.  If not, see <https://www.gnu.org/licenses/>.
"""
Contains all functions for various output layouts.
"""

from copy import copy
import PyPDF2

import utils


def create_output_files(assembled_collage: PyPDF2.pdf.PageObject,
                        layout: utils.Layout,
                        input_properties: utils.PDFProperties,
                        output_layout: str) -> PyPDF2.PdfFileWriter:
    """

    :param assembled_collage: One pdf page that contains all assembled pattern pages.
    :param layout: The layout of the input pattern page.
    :param input_properties: Amount of pdf pages, x- and y-offset.
    :param output_layout: Desired output layout.
    :return: The pdf with several pages, ready to write to disk.
    """
    if output_layout == "a0":
        return _chop_up(assembled_collage, layout, input_properties, utils.Factor(x=4, y=4))

    if output_layout.find("x"):
        # convert output layout to Factors
        n_up_factor = utils.calculate_nup_factors(output_layout, input_properties)
        return _chop_up(assembled_collage, layout, input_properties, n_up_factor)


def _chop_up(assembled_collage: PyPDF2.pdf.PageObject,
             layout: utils.Layout,
             input_properties: utils.PDFProperties,
             n_up_factor: utils.Factor) -> PyPDF2.PdfFileWriter:
    """
    Takes a collage with all assembled pattern pages, divides them up so that they fit on a previously specified sheet.
    """
    print(f"\nChopping up the collage...")
    chopped_up_collage = [assembled_collage for _ in range(0, utils.calculate_pages_needed(layout, n_up_factor))]
    # 4 A4 fit on 1 A0 page

    # only two points are needed to be cropped, lower left (x, y) and upper right (x, y)
    lowerleft_factor = utils.Factor(x=0, y=0)  # k, l
    upperright_factor = utils.Factor(x=1, y=1)  # m, n

    writer = PyPDF2.PdfFileWriter()

    for elem in chopped_up_collage:
        page = copy(elem)  # cf. https://stackoverflow.com/questions/52315259/pypdf2-cant-add-multiple-cropped-pages#

        # apply transformation to lower left x and y
        x_lowerleft = lowerleft_factor.x * n_up_factor.x * input_properties.x_offset
        y_lowerleft = lowerleft_factor.y * n_up_factor.y * input_properties.y_offset

        page.cropBox.lowerLeft = (x_lowerleft, y_lowerleft)

        # apply transformation to upper right, y-value
        rowsleft = layout.rows - (upperright_factor.y * n_up_factor.y)  # ROWS
        if rowsleft < 0:
            y_upperright = layout.rows * input_properties.y_offset
        else:
            y_upperright = upperright_factor.y * n_up_factor.y * input_properties.y_offset

        # apply transformation to upper right, x-value
        colselft = layout.columns - (upperright_factor.x * n_up_factor.x)  # COLS
        if colselft > 0:  # still assembling the same horizontal line
            x_upperright = upperright_factor.x * n_up_factor.x * input_properties.x_offset

            page.cropBox.upperRight = (x_upperright, y_upperright)

            lowerleft_factor.x += 1
            upperright_factor.x += 1
        else:  # end of line reached
            if colselft == 0:  # cols % 4 == 0 COLS
                x_upperright = upperright_factor.x * n_up_factor.x * input_properties.x_offset
            if colselft < 0:  # less than 4 pages left for COLS
                x_upperright = layout.columns * input_properties.x_offset

            page.cropBox.upperRight = (x_upperright, y_upperright)

            lowerleft_factor.x = 0
            lowerleft_factor.y += 1

            upperright_factor.x = 1
            upperright_factor.y += 1

        writer.addPage(page)

    return writer
