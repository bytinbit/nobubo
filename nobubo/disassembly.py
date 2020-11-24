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
import pathlib
import subprocess

import PyPDF2

from nobubo import pdf, calc, output


def create_output_files(temp_collage_paths: [pathlib.Path],
                        input_properties: pdf.InputProperties,
                        output_properties: pdf.OutputProperties):
    for counter, collage_path in enumerate(temp_collage_paths):
        with collage_path.open("rb") as collagefile:
            reader = PyPDF2.PdfFileReader(collagefile, strict=False)
            collage = reader.getPage(0)
            new_outputpath = calc.generate_new_outputpath(output_properties.output_path, counter)
            print(f"\nChopping up the collage...")
            chopped_up_files = _create_output_files(collage, input_properties, input_properties.layout[counter], output_properties.output_layout)
            print(f"Successfully chopped up the collage.\n")
            output.write_chops(chopped_up_files, new_outputpath)
            print(f"Final pdf written to {new_outputpath}. Enjoy your sewing :)")


def _create_output_files(assembled_collage: PyPDF2.pdf.PageObject,
                         input_properties: pdf.InputProperties,
                         current_layout: pdf.Layout,
                         output_layout: [int]) -> PyPDF2.PdfFileWriter:
    """
    Chops up the collage that consists of all the pattern pages to individual pages of the desired output size.
    :param assembled_collage: One pdf page that contains all assembled pattern pages.
    :param input_properties: Properties of the pdf.
    :param output_layout: The desired output layout.
    :return: The pdf with several pages, ready to write to disk.
    """
    n_up_factor = calc.calculate_nup_factors(input_properties, output_layout)
    return _chop_up(assembled_collage, input_properties, current_layout, n_up_factor)


def _chop_up(assembled_collage: PyPDF2.pdf.PageObject,
             input_properties: pdf.InputProperties,
             current_layout: pdf.Layout,
             n_up_factor: calc.Factor) -> PyPDF2.PdfFileWriter:
    """
    Takes a collage with all assembled pattern pages, divides it up so that they fit on a previously specified page size.
    """
    # only two points are needed to be cropped, lower left (x, y) and upper right (x, y)
    lowerleft_factor = calc.Factor(x=0, y=0)
    upperright_factor = calc.Factor(x=1, y=1)

    writer = PyPDF2.PdfFileWriter()
    for x in range(0, calc.calculate_pages_needed(current_layout, n_up_factor)):
        page = copy(assembled_collage)
        # cf. https://stackoverflow.com/questions/52315259/pypdf2-cant-add-multiple-cropped-pages#

        # TODO refactor: not needed to pass full input_properties to functions, only pagesize needed
        lowerleft: pdf.Point = _calculate_lowerleft_point(lowerleft_factor, n_up_factor, input_properties)
        upperright: pdf.Point = _calculate_upperright_point(upperright_factor, n_up_factor, current_layout, input_properties)

        # adjust multiplying factor
        colsleft = _calculate_colsrows_left(current_layout.columns, upperright_factor.x, n_up_factor.x)
        lowerleft_factor, upperright_factor = _adjust_factors(lowerleft_factor, upperright_factor, colsleft)

        page.cropBox.lowerLeft = (lowerleft.x, lowerleft.y)
        page.cropBox.upperRight = (upperright.x, upperright.y)
        writer.addPage(page)

    return writer


def _calculate_colsrows_left(layout_element: int, factor: int, nup_factor: int) -> int:
    return layout_element - (factor * nup_factor)


def _calculate_lowerleft_point(lowerleft_factor: calc.Factor,
                               n_up_factor: calc.Factor,
                               input_properties: pdf.InputProperties) -> pdf.Point:
    return pdf.Point(x=lowerleft_factor.x * n_up_factor.x * input_properties.pagesize.width,
                     y=lowerleft_factor.y * n_up_factor.y * input_properties.pagesize.height)


def _calculate_upperright_point(upperright_factor: calc.Factor,
                                n_up_factor: calc.Factor,
                                current_layout: pdf.Layout,
                                input_properties: pdf.InputProperties) -> pdf.Point:
    upperright = pdf.Point(x=0, y=0)
    # Manage ROWS: apply transformation to upper right, y-value
    rowsleft = _calculate_colsrows_left(current_layout.rows, upperright_factor.y, n_up_factor.y)  # FIX
    if rowsleft < 0:  # end of pattern reached  (full amount of rows reached)
        upperright.y = current_layout.rows * input_properties.pagesize.height
    else:
        upperright.y = upperright_factor.y * n_up_factor.y * input_properties.pagesize.height

    # Manage COLS: apply transformation to upper right, x-value
    colsleft = _calculate_colsrows_left(current_layout.columns, upperright_factor.x, n_up_factor.x)  # COLS
    if colsleft > 0:  # still assembling the same horizontal line
        upperright.x = upperright_factor.x * n_up_factor.x * input_properties.pagesize.width

    else:  # end of line reached, need to go 1 row up
        if colsleft == 0:  # cols % n_up_factor == 0
            upperright.x = upperright_factor.x * n_up_factor.x * input_properties.pagesize.width
        if colsleft < 0:  # remainder pages left for COLS
            upperright.x = current_layout.columns * input_properties.pagesize.width
    return upperright


def _adjust_factors(lowerleft_factor: calc.Factor, upperright_factor: calc.Factor, colsleft: int) -> (
        calc.Factor, calc.Factor):
    if colsleft > 0:  # still assembling the same horizontal line
        return _advance_horizontally(lowerleft_factor, upperright_factor)
    else:  # end of line reached, need to go 1 row up
        return _advance_vertically(lowerleft_factor, upperright_factor)


def _advance_horizontally(lowerleft_factor: calc.Factor, upperright_factor: calc.Factor) -> (
        calc.Factor, calc.Factor):
    lowerleft_factor.x += 1
    upperright_factor.x += 1
    return lowerleft_factor, upperright_factor


def _advance_vertically(lowerleft_factor: calc.Factor, upperright_factor: calc.Factor) -> (calc.Factor, calc.Factor):
    lowerleft_factor.x = 0
    lowerleft_factor.y += 1

    upperright_factor.x = 1
    upperright_factor.y += 1
    return lowerleft_factor, upperright_factor