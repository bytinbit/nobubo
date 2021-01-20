# Copyright 2021, Méline Sieber
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
import pathlib

import pikepdf

import nobubo.core
from nobubo import core, calc, errors


def create_output_files(temp_collage_paths: [pathlib.Path],
                        input_properties: core.InputProperties,
                        output_properties: core.OutputProperties):
    for counter, collage_path in enumerate(temp_collage_paths):
        try:
            collage = pikepdf.Pdf.open(collage_path)
        except OSError as e:
            raise errors.UsageError(f"Could not open collage file for disassembly:\n{e}.")
        new_outputpath = calc.new_outputpath(output_properties.output_path, counter)
        print(f"\nChopping up the collage...")
        chopped_up_files = _create_output_files(collage, input_properties.pagesize,
                                                input_properties.layout[counter], output_properties.output_layout)
        print(f"Successfully chopped up the collage.\n")
        write_chops(chopped_up_files, new_outputpath)
        print(f"Final pdf written to {new_outputpath}. Enjoy your sewing :)")


def write_chops(collage: pikepdf.Pdf, output_path: pathlib.Path):
    print("Writing file...")
    try:
        collage.save(output_path)
    except OSError as e:
        raise errors.UsageError(f"An error occurred while writing the output file:\n{e}")


def write_collage(temp_collage_paths: [pathlib.Path], output_properties: core.OutputProperties):
    for counter, collage_path in enumerate(temp_collage_paths):
        new_outputpath = calc.new_outputpath(output_properties.output_path, counter)
        try:
            temp_collage = pikepdf.Pdf.open(collage_path)
            temp_collage.save(new_outputpath)
        except OSError as e:
            raise errors.UsageError(f"An error occurred while writing the collage:\n{e}")
        print(f"Collage written to {new_outputpath}. Enjoy your sewing :)")


def _create_output_files(collage: pikepdf.Pdf,
                         pagesize: core.PageSize,
                         current_layout: core.Layout,
                         output_layout: [int]) -> pikepdf.Pdf:
    """
    Chops up the collage that consists of all the pattern pages to individual pages of the desired output size.
    :param collage: One pdf page that contains all assembled pattern pages.
    :param input_properties: Properties of the pdf.
    :param output_layout: The desired output layout.
    :return: The pdf with several pages, ready to write to disk.
    """
    n_up_factor = calc.nup_factors(pagesize, output_layout)
    # only two points are needed to be cropped, lower left (x, y) and upper right (x, y)
    lowerleft_factor = nobubo.core.Factor(x=0, y=0)
    upperright_factor = nobubo.core.Factor(x=1, y=1)

    output = pikepdf.Pdf.new()
    output.copy_foreign(collage.Root)
    # Root must be copied too, not only the page: thanks to https://github.com/cfcurtis/sewingutils for this!
    for i in range(0, calc.pages_needed(current_layout, n_up_factor)):
        page = output.copy_foreign(collage.pages[0])

        lowerleft: core.Point = _calculate_lowerleft_point(lowerleft_factor, n_up_factor, pagesize)
        upperright: core.Point = _calculate_upperright_point(upperright_factor, n_up_factor, current_layout, pagesize)

        # adjust multiplying factor
        colsleft = _calculate_colsrows_left(current_layout.columns, upperright_factor.x, n_up_factor.x)
        lowerleft_factor, upperright_factor = _adjust_factors(lowerleft_factor, upperright_factor, colsleft)

        page.CropBox = [lowerleft.x, lowerleft.y, upperright.x, upperright.y]
        output.pages.append(page)

    return output


def _calculate_colsrows_left(layout_element: int, factor: int, nup_factor: int) -> int:
    return layout_element - (factor * nup_factor)


def _calculate_lowerleft_point(lowerleft_factor: nobubo.core.Factor,
                               n_up_factor: nobubo.core.Factor,
                               pagesize: core.PageSize) -> core.Point:
    return core.Point(x=lowerleft_factor.x * n_up_factor.x * pagesize.width,
                     y=lowerleft_factor.y * n_up_factor.y * pagesize.height)


def _calculate_upperright_point(upperright_factor: nobubo.core.Factor,
                                n_up_factor: nobubo.core.Factor,
                                current_layout: core.Layout,
                                pagesize: core.PageSize) -> core.Point:
    upperright = core.Point(x=0, y=0)
    # Manage ROWS: apply transformation to upper right, y-value
    rowsleft = _calculate_colsrows_left(current_layout.rows, upperright_factor.y, n_up_factor.y)
    if rowsleft < 0:  # end of pattern reached  (full amount of rows reached)
        upperright.y = current_layout.rows * pagesize.height
    else:
        upperright.y = upperright_factor.y * n_up_factor.y * pagesize.height

    # Manage COLS: apply transformation to upper right, x-value
    colsleft = _calculate_colsrows_left(current_layout.columns, upperright_factor.x, n_up_factor.x)  # COLS
    if colsleft > 0:  # still assembling the same horizontal line
        upperright.x = upperright_factor.x * n_up_factor.x * pagesize.width

    else:  # end of line reached, need to go 1 row up
        if colsleft == 0:  # cols % n_up_factor == 0
            upperright.x = upperright_factor.x * n_up_factor.x * pagesize.width
        if colsleft < 0:  # remainder pages left for COLS
            upperright.x = current_layout.columns * pagesize.width
    return upperright


def _adjust_factors(lowerleft_factor: nobubo.core.Factor, upperright_factor: nobubo.core.Factor, colsleft: int) -> (
        nobubo.core.Factor, nobubo.core.Factor):
    if colsleft > 0:  # still assembling the same horizontal line
        return _advance_horizontally(lowerleft_factor, upperright_factor)
    else:  # end of line reached, need to go 1 row up
        return _advance_vertically(lowerleft_factor, upperright_factor)


def _advance_horizontally(lowerleft_factor: nobubo.core.Factor, upperright_factor: nobubo.core.Factor) -> (
        nobubo.core.Factor, nobubo.core.Factor):
    lowerleft_factor.x += 1
    upperright_factor.x += 1
    return lowerleft_factor, upperright_factor


def _advance_vertically(lowerleft_factor: nobubo.core.Factor, upperright_factor: nobubo.core.Factor) -> (
nobubo.core.Factor, nobubo.core.Factor):
    lowerleft_factor.x = 0
    lowerleft_factor.y += 1

    upperright_factor.x = 1
    upperright_factor.y += 1
    return lowerleft_factor, upperright_factor