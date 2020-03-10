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
Contains functions for various output layouts.
"""

from copy import copy
import PyPDF2
import progress.bar

import utils


def assemble_collage(input_pdf: PyPDF2.PdfFileReader,
                     layout: utils.Layout,
                     input_properties: utils.PDFProperties,
                     reverse=False) -> PyPDF2.pdf.PageObject:
    """
    Takes a pattern pdf where one page equals a part of the pattern and assembles it to one huge collage.
    The default assembles it from top left to the bottom right.
    :param input_pdf: The pattern pdf that has been bought by the user.
    :param layout: The layout of the pattern pages, which includes overview pages, columns and rows.
    :param input_properties: Properties of the pdf.
    :param reverse: Indicates order in which collage should be assembled.
    :return The collage with all pattern pages assembled on one single page.

    """
    last_page = layout.overview + (layout.columns * layout.rows)

    collage = PyPDF2.pdf.PageObject.createBlankPage(None,
                                                    layout.columns * input_properties.x_offset,
                                                    layout.rows * input_properties.y_offset)
    if reverse:  # bottom to top
        position: utils.Point = utils.Point(x=0.0, y=0.0)
    else:  # top to bottom
        position: utils.Point = utils.Point(x=0.0, y=((layout.rows-1) * input_properties.y_offset))

    colscount = 0

    bar = progress.bar.FillingSquaresBar(suffix="assembling page %(index)d of %(max)d, %(elapsed_td)s")
    for pagenumber in bar.iter(range(layout.overview, last_page)):

        if colscount == layout.columns:
            position.x = 0.0
            if reverse:
                position.y += input_properties.y_offset
            else:
                position.y -= input_properties.y_offset
            colscount = 0

        collage.mergeTranslatedPage(input_pdf.getPage(pagenumber), position.x, position.y, expand=True)
        position.x += input_properties.x_offset
        colscount += 1
    return collage


def create_output_files(assembled_collage: PyPDF2.pdf.PageObject,
                        layout: utils.Layout,
                        input_properties: utils.PDFProperties,
                        output_layout: [int]) -> PyPDF2.PdfFileWriter:
    """

    :param assembled_collage: One pdf page that contains all assembled pattern pages.
    :param layout: The layout of the pattern pages, which includes overview pages, columns and rows.
    :param input_properties: Properties of the pdf.
    :param output_layout: The desired output layout.
    :return: The pdf with several pages, ready to write to disk.
    """
    n_up_factor = utils.calculate_nup_factors(output_layout, input_properties)
    return _chop_up(assembled_collage, layout, input_properties, n_up_factor)


def _chop_up(assembled_collage: PyPDF2.pdf.PageObject,
             layout: utils.Layout,
             input_properties: utils.PDFProperties,
             n_up_factor: utils.Factor) -> PyPDF2.PdfFileWriter:
    """
    Takes a collage with all assembled pattern pages, divides it up so that they fit on a previously specified sheet.
    """
    # only two points are needed to be cropped, lower left (x, y) and upper right (x, y)
    lowerleft_factor = utils.Factor(x=0, y=0)
    upperright_factor = utils.Factor(x=1, y=1)

    writer = PyPDF2.PdfFileWriter()

    for x in range(0, utils.calculate_pages_needed(layout, n_up_factor)):
        page = copy(assembled_collage)
        # cf. https://stackoverflow.com/questions/52315259/pypdf2-cant-add-multiple-cropped-pages#

        lowerleft: utils.Point = _calculate_lowerleft_point(lowerleft_factor, n_up_factor, input_properties)
        upperright: utils.Point = _calculate_upperright_point(upperright_factor, n_up_factor, input_properties, layout)

        # adjust multiplying factor
        colsleft = _calculate_colsrows_left(layout.columns, upperright_factor.x, n_up_factor.x)
        lowerleft_factor, upperright_factor = _adjust_factors(lowerleft_factor, upperright_factor, colsleft)

        page.cropBox.lowerLeft = (lowerleft.x, lowerleft.y)
        page.cropBox.upperRight = (upperright.x, upperright.y)
        writer.addPage(page)

    return writer


def _calculate_colsrows_left(layout_element: int, factor: int, nup_factor: int) -> int:
    return layout_element - (factor * nup_factor)


def _calculate_lowerleft_point(lowerleft_factor: utils.Factor,
                               n_up_factor: utils.Factor,
                               input_properties: utils.PDFProperties) -> utils.Point:
    return utils.Point(x=lowerleft_factor.x * n_up_factor.x * input_properties.x_offset,
                       y=lowerleft_factor.y * n_up_factor.y * input_properties.y_offset)


def _calculate_upperright_point(upperright_factor: utils.Factor,
                                n_up_factor: utils.Factor,
                                input_properties: utils.PDFProperties,
                                layout: utils.Layout) -> utils.Point:
    upperright = utils.Point(x=0, y=0)
    # Manage ROWS: apply transformation to upper right, y-value
    rowsleft = _calculate_colsrows_left(layout.rows, upperright_factor.y, n_up_factor.y)
    if rowsleft < 0:  # end of pattern reached  (full amount of rows reached)
        upperright.y = layout.rows * input_properties.y_offset
    else:
        upperright.y = upperright_factor.y * n_up_factor.y * input_properties.y_offset

    # Manage COLS: apply transformation to upper right, x-value
    colsleft = _calculate_colsrows_left(layout.columns, upperright_factor.x, n_up_factor.x)  # COLS
    if colsleft > 0:  # still assembling the same horizontal line
        upperright.x = upperright_factor.x * n_up_factor.x * input_properties.x_offset

    else:  # end of line reached, need to go 1 row up
        if colsleft == 0:  # cols % n_up_factor == 0
            upperright.x = upperright_factor.x * n_up_factor.x * input_properties.x_offset
        if colsleft < 0:  # remainder pages left for COLS
            upperright.x = layout.columns * input_properties.x_offset
    return upperright


def _adjust_factors(lowerleft_factor: utils.Factor, upperright_factor: utils.Factor, colsleft: int) -> (
        utils.Factor, utils.Factor):
    if colsleft > 0:  # still assembling the same horizontal line
        return _advance_horizontally(lowerleft_factor, upperright_factor)
    else:  # end of line reached, need to go 1 row up
        return _advance_vertically(lowerleft_factor, upperright_factor)


def _advance_horizontally(lowerleft_factor: utils.Factor, upperright_factor: utils.Factor) -> (
        utils.Factor, utils.Factor):
    lowerleft_factor.x += 1
    upperright_factor.x += 1
    return lowerleft_factor, upperright_factor


def _advance_vertically(lowerleft_factor: utils.Factor, upperright_factor: utils.Factor) -> (utils.Factor, utils.Factor):
    lowerleft_factor.x = 0
    lowerleft_factor.y += 1

    upperright_factor.x = 1
    upperright_factor.y += 1
    return lowerleft_factor, upperright_factor

