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
from dataclasses import dataclass
from typing import List, Tuple, Optional

import pikepdf

import nobubo.assembly
from nobubo import errors
from nobubo.assembly import Layout, PageSize


@dataclass
class Point:
    """
    Point on a pdf page in user space units.
    """

    x: float
    y: float


@dataclass
class Factor:
    """
    Factor class for multiplication.
    """

    x: int
    y: int


class NobuboOutput:
    """
    Holds all information of the output pdf and is responsible for creating
    the desired output pdf.
    """

    def __init__(self, output_path: pathlib.Path, output_pagesize: Optional[PageSize]):
        """
        :param output_path: path where the output pdf should be saved.
        :param output_pagesize: The desired page size in user space units (can include
        user-defined print margin).
        """
        self.output_path = output_path
        self.output_pagesize = output_pagesize

    def create_output_files(
        self,
        temp_collage_paths: List[pathlib.Path],
        input_properties: nobubo.assembly.NobuboInput,
    ) -> None:
        for counter, collage_path in enumerate(temp_collage_paths):
            try:
                collage = pikepdf.Pdf.open(collage_path)
            except OSError as e:
                raise errors.UsageError(
                    "Could not open collage file for disassembly:" f"\n{e}."
                )
            new_outputpath = self.generate_new_outputpath(self.output_path, counter)
            print("\nChopping up the collage...")
            chopped_up_files = self._create_output_files(
                collage,
                input_properties.pagesize,
                input_properties.layout[counter],
            )
            print("Successfully chopped up the collage.\n")
            self.write_chops(chopped_up_files, new_outputpath)
            print(f"Final pdf written to {new_outputpath}. Enjoy your sewing :)")

    def write_chops(self, collage: pikepdf.Pdf, output_path: pathlib.Path) -> None:
        print("Writing file...")
        try:
            collage.save(output_path)
        except OSError as e:
            raise errors.UsageError(
                f"An error occurred " f"while writing the output file:\n{e}"
            )

    def write_collage(
        self,
        temp_collage_paths: List[pathlib.Path],
    ) -> None:
        for counter, collage_path in enumerate(temp_collage_paths):
            new_outputpath = self.generate_new_outputpath(self.output_path, counter)
            try:
                temp_collage = pikepdf.Pdf.open(collage_path)
                temp_collage.save(new_outputpath)
            except OSError as e:
                raise errors.UsageError(
                    f"An error occurred " f"while writing the collage:\n{e}"
                )
            print(f"Collage written to {new_outputpath}. Enjoy your sewing :)")

    def _create_output_files(
        self,
        collage: pikepdf.Pdf,
        input_pagesize: nobubo.assembly.PageSize,
        current_layout: nobubo.assembly.Layout,
    ) -> pikepdf.Pdf:
        """
        Chops up the collage that consists of all the pattern pages to individual pages
        of the desired output size.
        :param collage: One pdf page that contains all assembled pattern pages.
        :param input_pagesize: size of an input pdf page
        :param current_layout: the current layout of the input pdf
        :return: The pdf with several pages, ready to write to disk.
        """
        assert self.output_pagesize is not None
        n_up_factor = self.nup_factors(input_pagesize, self.output_pagesize)
        # only two points are needed to be cropped, lower left (x, y) and upper right (x, y)
        lowerleft_factor = Factor(x=0, y=0)
        upperright_factor = Factor(x=1, y=1)

        output = pikepdf.Pdf.new()  # type: ignore [call-arg]
        output.copy_foreign(collage.Root)
        # Root must be copied too, not only the page:
        # thanks to https://github.com/cfcurtis/sewingutils
        for i in range(0, self.pages_needed(current_layout, n_up_factor)):
            page = output.copy_foreign(collage.pages[0])

            lowerleft: Point = _calculate_lowerleft_point(
                lowerleft_factor, n_up_factor, input_pagesize
            )
            upperright: Point = _calculate_upperright_point(
                upperright_factor, n_up_factor, current_layout, input_pagesize
            )

            # adjust multiplying factor
            colsleft = _calculate_colsrows_left(
                current_layout.columns, upperright_factor.x, n_up_factor.x
            )
            lowerleft_factor, upperright_factor = _adjust_factors(
                lowerleft_factor, upperright_factor, colsleft
            )

            page.CropBox = [lowerleft.x, lowerleft.y, upperright.x, upperright.y]
            output.pages.append(page)

        return output

    def pages_needed(self, layout: Layout, n_up_factor: Factor) -> int:
        """
        Calculate the pages needed for the required output layout.
        :param layout: layout of the input pdf
        :param n_up_factor: how many pages of the input pdf fit on the desired layout
        :return:
        """
        x = layout.columns / n_up_factor.x
        y = layout.rows / n_up_factor.y
        return math.ceil(x) * math.ceil(y)

    def nup_factors(
        self, input_pagesize: PageSize, output_pagesize: PageSize
    ) -> Factor:
        """
        Calculate the n-up factor for the output pdf, i.e. how many input pages
        fit on the desired output layout.
        :param input_pagesize: Size of a page of the input pdf in user space units
        :param output_pagesize: the output layout in user space units
        :return:
        """
        x_factor = int(output_pagesize.width // input_pagesize.width)
        y_factor = int(output_pagesize.height // input_pagesize.height)
        return Factor(x=x_factor, y=y_factor)

    def generate_new_outputpath(
        self, output_path: pathlib.Path, page_count: int
    ) -> pathlib.Path:
        new_filename = f"{output_path.stem}_{page_count + 1}{output_path.suffix}"
        return output_path.parent / new_filename


def _calculate_colsrows_left(layout_element: int, factor: int, nup_factor: int) -> int:
    return layout_element - (factor * nup_factor)


def _calculate_lowerleft_point(
    lowerleft_factor: Factor, n_up_factor: Factor, pagesize: nobubo.assembly.PageSize
) -> Point:
    return Point(
        x=lowerleft_factor.x * n_up_factor.x * pagesize.width,
        y=lowerleft_factor.y * n_up_factor.y * pagesize.height,
    )


def _calculate_upperright_point(
    upperright_factor: Factor,
    n_up_factor: Factor,
    current_layout: nobubo.assembly.Layout,
    pagesize: nobubo.assembly.PageSize,
) -> Point:
    upperright = Point(x=0, y=0)
    # Manage ROWS: apply transformation to upper right, y-value
    rowsleft = _calculate_colsrows_left(
        current_layout.rows, upperright_factor.y, n_up_factor.y
    )
    if rowsleft < 0:  # end of pattern reached  (full amount of rows reached)
        upperright.y = current_layout.rows * pagesize.height
    else:
        upperright.y = upperright_factor.y * n_up_factor.y * pagesize.height

    # Manage COLS: apply transformation to upper right, x-value
    colsleft = _calculate_colsrows_left(
        current_layout.columns, upperright_factor.x, n_up_factor.x
    )  # COLS
    if colsleft > 0:  # still assembling the same horizontal line
        upperright.x = upperright_factor.x * n_up_factor.x * pagesize.width

    else:  # end of line reached, need to go 1 row up
        if colsleft == 0:  # cols % n_up_factor == 0
            upperright.x = upperright_factor.x * n_up_factor.x * pagesize.width
        if colsleft < 0:  # remainder pages left for COLS
            upperright.x = current_layout.columns * pagesize.width
    return upperright


def _adjust_factors(
    lowerleft_factor: Factor, upperright_factor: Factor, colsleft: int
) -> Tuple[Factor, Factor]:
    if colsleft > 0:  # still assembling the same horizontal line
        return _advance_horizontally(lowerleft_factor, upperright_factor)
    else:  # end of line reached, need to go 1 row up
        return _advance_vertically(lowerleft_factor, upperright_factor)


def _advance_horizontally(
    lowerleft_factor: Factor, upperright_factor: Factor
) -> Tuple[Factor, Factor]:
    lowerleft_factor.x += 1
    upperright_factor.x += 1
    return lowerleft_factor, upperright_factor


def _advance_vertically(
    lowerleft_factor: Factor, upperright_factor: Factor
) -> Tuple[Factor, Factor]:
    lowerleft_factor.x = 0
    lowerleft_factor.y += 1

    upperright_factor.x = 1
    upperright_factor.y += 1
    return lowerleft_factor, upperright_factor
