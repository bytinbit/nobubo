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
import progress.bar

import utils


def assemble_to_collage(input_pdf: PyPDF2.PdfFileReader,
                        layout: utils.Layout,
                        input_properties: utils.PDFProperties) -> PyPDF2.pdf.PageObject:
    """
    Takes a pattern pdf where one page equals a part of the pattern and assembles it to on huge collage.
    It is assembled from bottom left to the top right.
    """
    last_page = layout.overview + (layout.columns * layout.rows)
    collage = PyPDF2.pdf.PageObject.createBlankPage(None,
                                                    layout.columns * input_properties.x_offset,
                                                    layout.rows * input_properties.y_offset)
    x_position = 0.0
    y_position = 0.0
    colscount = 0

    print(f"Creating collage... Please be patient, this may take some time.")
    bar = progress.bar.FillingSquaresBar(suffix="assembling page %(index)d of %(max)d, %(elapsed_td)s")
    for pagenumber in bar.iter(range(layout.overview, last_page)):

        if colscount == layout.columns:
            x_position = 0.0
            y_position += input_properties.y_offset
            colscount = 0

        collage.mergeTranslatedPage(input_pdf.getPage(pagenumber), x_position, y_position, expand=True)
        x_position += input_properties.x_offset
        colscount += 1
    return collage


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

    # only two points are needed to be cropped, lower left (x, y) and upper right (x, y)
    lowerleft_factor = utils.Factor(x=0, y=0)  # k, l
    upperright_factor = utils.Factor(x=1, y=1)  # m, n

    # init points
    upperright = utils.Point(x=0, y=0)

    writer = PyPDF2.PdfFileWriter()

    for x in range(0, utils.calculate_pages_needed(layout, n_up_factor)):
        page = copy(assembled_collage)
        # cf. https://stackoverflow.com/questions/52315259/pypdf2-cant-add-multiple-cropped-pages#

        # apply transformation to lower left x and y
        lowerleft: utils.Point = _calculate_lowerleft_point(lowerleft_factor, n_up_factor, input_properties)

        # upperright: utils.Point = _calculate_upperright_point(upperright_factor, n_up_factor, input_properties, layout)

        # Manage ROWS: apply transformation to upper right, y-value
        rowsleft = _calculate_colsrows_left(layout.rows, upperright_factor.y, n_up_factor.y)  # ROWS
        if rowsleft < 0:  # ROWS y-Factor
            upperright.y = layout.rows * input_properties.y_offset # end of pattern reached  (full amount of rows reached)
        else:
            upperright.y = upperright_factor.y * n_up_factor.y * input_properties.y_offset


        # Manage COLS: apply transformation to upper right, x-value
        colsleft = _calculate_colsrows_left(layout.columns, upperright_factor.x, n_up_factor.x)  # COLS
        if colsleft > 0:  # still assembling the same horizontal line
            upperright.x = upperright_factor.x * n_up_factor.x * input_properties.x_offset

            lowerleft_factor, upperright_factor = _advance_horizontally(lowerleft_factor, upperright_factor)

        else:  # end of line reached, need to go 1 row up
            if colsleft == 0:  # cols % 4 == 0 COLS
                upperright.x = upperright_factor.x * n_up_factor.x * input_properties.x_offset
            if colsleft < 0:  # less than (% n_up_factor) pages left for COLS
                upperright.x = layout.columns * input_properties.x_offset

            lowerleft_factor, upperright_factor = _advance_vertically(lowerleft_factor, upperright_factor)

        page.cropBox.lowerLeft = (lowerleft.x, lowerleft.y)
        page.cropBox.upperRight = (upperright.x, upperright.y)
        writer.addPage(page)

    return writer


def _calculate_colsrows_left(layout_element: int, multiplier: int, nup_factor: int) -> int:
    return layout_element - (multiplier * nup_factor)


def _calculate_lowerleft_point(lowerleft_factor: utils.Factor, n_up_factor: utils.Factor, input_properties: utils.PDFProperties) -> utils.Point:
    return utils.Point(x=lowerleft_factor.x * n_up_factor.x * input_properties.x_offset,  # starts with e.g. 0 * 4 * xoffset
                       y=lowerleft_factor.y * n_up_factor.y * input_properties.y_offset)  # starts with 0 * 4 * yoffset


def _calculate_upperright_point(upperright_factor: utils.Factor, n_up_factor: utils.Factor, input_properties: utils.PDFProperties, input_layout: utils.Layout) -> utils.Point:
    pass


def _advance_horizontally(lowerleft_factor: utils.Point, upperright_factor: utils.Point) -> utils.Point:
    lowerleft_factor.x += 1
    upperright_factor.x += 1
    return lowerleft_factor, upperright_factor


def _advance_vertically(lowerleft_factor: utils.Point, upperright_factor: utils.Point) -> utils.Point:
    lowerleft_factor.x = 0
    lowerleft_factor.y += 1

    upperright_factor.x = 1
    upperright_factor.y += 1
    return lowerleft_factor, upperright_factor

