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
import math
import pathlib
from typing import List, Tuple, Optional

import pikepdf

import nobubo.assembly
import nobubo.core
from nobubo import core, errors
from nobubo.assembly import Layout, PageSize
from nobubo.core import Factor


def create_output_files(temp_collage_paths: List[pathlib.Path],
                        input_properties: nobubo.assembly.InputProperties,
                        output_properties: core.OutputProperties) -> None:
    for counter, collage_path in enumerate(temp_collage_paths):
        try:
            collage = pikepdf.Pdf.open(collage_path)
        except OSError as e:
            raise errors.UsageError("Could not open collage file for disassembly:"
                                    f"\n{e}.")
        new_outputpath = generate_new_outputpath(output_properties.output_path, counter)
        print("\nChopping up the collage...")
        chopped_up_files = _create_output_files(collage, input_properties.pagesize,
                                                input_properties.layout[counter],
                                                output_properties.output_layout)
        print("Successfully chopped up the collage.\n")
        write_chops(chopped_up_files, new_outputpath)
        print(f"Final pdf written to {new_outputpath}. Enjoy your sewing :)")


def write_chops(collage: pikepdf.Pdf, output_path: pathlib.Path) -> None:
    print("Writing file...")
    try:
        collage.save(output_path)
    except OSError as e:
        raise errors.UsageError(f"An error occurred "
                                f"while writing the output file:\n{e}")


def write_collage(temp_collage_paths: List[pathlib.Path],
                  output_properties: core.OutputProperties) -> None:
    for counter, collage_path in enumerate(temp_collage_paths):
        new_outputpath = generate_new_outputpath(output_properties.output_path, counter)
        try:
            temp_collage = pikepdf.Pdf.open(collage_path)
            temp_collage.save(new_outputpath)
        except OSError as e:
            raise errors.UsageError(f"An error occurred "
                                    f"while writing the collage:\n{e}")
        print(f"Collage written to {new_outputpath}. Enjoy your sewing :)")


def _create_output_files(collage: pikepdf.Pdf,
                         pagesize: nobubo.assembly.PageSize,
                         current_layout: nobubo.assembly.Layout,
                         output_layout: Optional[List[int]]) -> pikepdf.Pdf:
    """
    Chops up the collage that consists of all the pattern pages to individual pages
    of the desired output size.
    :param collage: One pdf page that contains all assembled pattern pages.
    :param input_properties: Properties of the pdf.
    :param output_layout: The desired output layout.
    :return: The pdf with several pages, ready to write to disk.
    """
    assert output_layout is not None
    n_up_factor = nup_factors(pagesize, output_layout)
    # only two points are needed to be cropped, lower left (x, y) and upper right (x, y)
    lowerleft_factor = nobubo.core.Factor(x=0, y=0)
    upperright_factor = nobubo.core.Factor(x=1, y=1)

    output = pikepdf.Pdf.new()  # type: ignore [call-arg]
    output.copy_foreign(collage.Root)
    # Root must be copied too, not only the page:
    # thanks to https://github.com/cfcurtis/sewingutils
    for i in range(0, pages_needed(current_layout, n_up_factor)):
        page = output.copy_foreign(collage.pages[0])

        lowerleft: core.Point = _calculate_lowerleft_point(lowerleft_factor,
                                                           n_up_factor,
                                                           pagesize)
        upperright: core.Point = _calculate_upperright_point(upperright_factor,
                                                             n_up_factor,
                                                             current_layout,
                                                             pagesize)

        # adjust multiplying factor
        colsleft = _calculate_colsrows_left(current_layout.columns,
                                            upperright_factor.x,
                                            n_up_factor.x)
        lowerleft_factor, upperright_factor = _adjust_factors(lowerleft_factor,
                                                              upperright_factor,
                                                              colsleft)

        page.CropBox = [lowerleft.x, lowerleft.y, upperright.x, upperright.y]
        output.pages.append(page)

    return output


def _calculate_colsrows_left(layout_element: int, factor: int, nup_factor: int) -> int:
    return layout_element - (factor * nup_factor)


def _calculate_lowerleft_point(lowerleft_factor: nobubo.core.Factor,
                               n_up_factor: nobubo.core.Factor,
                               pagesize: nobubo.assembly.PageSize) -> core.Point:
    return core.Point(x=lowerleft_factor.x * n_up_factor.x * pagesize.width,
                      y=lowerleft_factor.y * n_up_factor.y * pagesize.height)


def _calculate_upperright_point(upperright_factor: nobubo.core.Factor,
                                n_up_factor: nobubo.core.Factor,
                                current_layout: nobubo.assembly.Layout,
                                pagesize: nobubo.assembly.PageSize) -> core.Point:
    upperright = core.Point(x=0, y=0)
    # Manage ROWS: apply transformation to upper right, y-value
    rowsleft = _calculate_colsrows_left(current_layout.rows,
                                        upperright_factor.y,
                                        n_up_factor.y)
    if rowsleft < 0:  # end of pattern reached  (full amount of rows reached)
        upperright.y = current_layout.rows * pagesize.height
    else:
        upperright.y = upperright_factor.y * n_up_factor.y * pagesize.height

    # Manage COLS: apply transformation to upper right, x-value
    colsleft = _calculate_colsrows_left(current_layout.columns,
                                        upperright_factor.x,
                                        n_up_factor.x)  # COLS
    if colsleft > 0:  # still assembling the same horizontal line
        upperright.x = upperright_factor.x * n_up_factor.x * pagesize.width

    else:  # end of line reached, need to go 1 row up
        if colsleft == 0:  # cols % n_up_factor == 0
            upperright.x = upperright_factor.x * n_up_factor.x * pagesize.width
        if colsleft < 0:  # remainder pages left for COLS
            upperright.x = current_layout.columns * pagesize.width
    return upperright


def _adjust_factors(lowerleft_factor: nobubo.core.Factor,
                    upperright_factor: nobubo.core.Factor,
                    colsleft: int) -> Tuple[
        nobubo.core.Factor, nobubo.core.Factor]:
    if colsleft > 0:  # still assembling the same horizontal line
        return _advance_horizontally(lowerleft_factor, upperright_factor)
    else:  # end of line reached, need to go 1 row up
        return _advance_vertically(lowerleft_factor, upperright_factor)


def _advance_horizontally(lowerleft_factor: nobubo.core.Factor,
                          upperright_factor: nobubo.core.Factor
                          ) -> Tuple[nobubo.core.Factor, nobubo.core.Factor]:
    lowerleft_factor.x += 1
    upperright_factor.x += 1
    return lowerleft_factor, upperright_factor


def _advance_vertically(lowerleft_factor: nobubo.core.Factor,
                        upperright_factor: nobubo.core.Factor
                        ) -> Tuple[nobubo.core.Factor, nobubo.core.Factor]:
    lowerleft_factor.x = 0
    lowerleft_factor.y += 1

    upperright_factor.x = 1
    upperright_factor.y += 1
    return lowerleft_factor, upperright_factor


def pages_needed(layout: Layout, n_up_factor: Factor) -> int:
    x = layout.columns / n_up_factor.x
    y = layout.rows / n_up_factor.y
    return math.ceil(x) * math.ceil(y)


def to_userspaceunits(width_height: List[int]) -> PageSize:
    """
    Converts a page's physical width and height from millimeters to
    default user space unit, which is defined in the pdf standard as 1/72 inch.

    :param width_height: Width and height of the physical page in millimeters (mm),
    on which the pattern will be printed.
    :return: Width and height of the physical page in default user space units.
    """
    # 1 mm = 5/127 inches = 0.03937 inches;  1/72 inch = 0.013888889
    # conversion factor = 5/127 / 1/72 = 360/127 = 2.834645669
    conversion_factor = 2.834645669

    return PageSize(width=(round(width_height[0] * conversion_factor, 3)),
                                    height=(round(width_height[1] * conversion_factor, 3)))


def nup_factors(pagesize: PageSize, output_layout: List[int]) -> Factor:
    output_papersize = to_userspaceunits(output_layout)
    x_factor = int(output_papersize.width // pagesize.width)
    y_factor = int(output_papersize.height // pagesize.height)
    return Factor(x=x_factor, y=y_factor)


def generate_new_outputpath(output_path: pathlib.Path, page_count: int) -> pathlib.Path:
    new_filename = f"{output_path.stem}_{page_count + 1}{output_path.suffix}"
    return output_path.parent / new_filename