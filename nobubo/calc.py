# Copyright 2020, Méline Sieber
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
Helpers for calculations, conversions, generations.
"""
import math
import pathlib
import random
import string
from dataclasses import dataclass

import PyPDF2

from nobubo import pdf


@dataclass
class Factor:
    """
    Factor class for multiplication.
    """
    x: int
    y: int


def parse_output_layout(output_layout_cli: str) -> [int]:
    if output_layout_cli is None:
        return None
    if output_layout_cli == "a0":
        return convert_to_mm("841x1189")
    elif "x" in output_layout_cli:
        return convert_to_mm(output_layout_cli)


def calculate_pages_needed(layout: pdf.Layout, n_up_factor: Factor) -> int:
    return math.ceil(layout.columns/n_up_factor.x) * math.ceil(layout.rows/n_up_factor.y)


def calculate_page_dimensions(page: PyPDF2.pdf.PageObject) -> (float, float):
    """
    Calculates the x, y value for the offset in default user space units as defined in the pdf standard.
    Uses the cropBox value, since this is the area visible to the printer.
    :param page: A pattern page.
    :return: list with x, y value.
    """
    return round(float(page.cropBox[2])-float(page.cropBox[0]), 2), round(float(page.cropBox[3])-float(page.cropBox[1]), 2)


def convert_to_userspaceunits(width_height: [int, int]) -> pdf.PageSize:
    """
    Converts a page's physical width and height from millimeters to default user space unit,
    which are defined in the pdf standard as 1/72 inch.

    :param width_height: Width and height of the physical page in millimeters (mm),
    on which the pattern will be printed.
    :return: Width and height of the physical page in default user space units.
    """
    # 1 mm = 5/127 inches = 0.03937 inches;  1/72 inch = 0.013888889
    # conversion factor = 5/127 / 1/72 = 360/127 = 2.834645669
    conversion_factor = 2.834645669

    return pdf.PageSize(width=(round(width_height[0] * conversion_factor, 3)),
                       height=(round(width_height[1] * conversion_factor, 3)))


def calculate_nup_factors(pagesize: pdf.PageSize, output_layout: [int]) -> Factor:
    output_papersize = convert_to_userspaceunits(output_layout)
    x_factor = int(output_papersize.width // pagesize.width)
    y_factor = int(output_papersize.height // pagesize.height)
    return Factor(x=x_factor, y=y_factor)


def convert_to_mm(output_layout: str) -> [int, int]:
    ol_in_mm = output_layout.split("x")
    return [int(x) for x in ol_in_mm]


def calculate_pagerange_reverse(layout: pdf.Layout) -> (int, int, int):
    return layout.overview, (layout.overview + (layout.columns * layout.rows)), layout.columns


def generate_new_outputpath(output_path: pathlib.Path, page_count: int):
    new_filename = f"{output_path.stem}_{page_count + 1}{output_path.suffix}"
    return output_path.parent / new_filename


def generate_random_string():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k = 7))