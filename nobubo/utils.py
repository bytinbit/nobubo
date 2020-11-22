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
Various helper classes and methods.
"""
import math
from dataclasses import dataclass

import PyPDF2


@dataclass
class PaperSize:
    """
    Paper size where width and height are in user space units.
    """
    width: float = 0
    height: float = 0


@dataclass
class Layout:
    """
    A Pattern layout.
    """
    overview: int
    columns: int
    rows: int


@dataclass
class PDFProperties:
    number_of_pages: int
    papersize: PaperSize
    layout: [Layout]


@dataclass
class Factor:
    """
    Factor class for multiplication.
    """
    x: int
    y: int


@dataclass
class Point:
    """
    Point on a pdf page in user space units.
    """
    x: float
    y: float


def calculate_pages_needed(layout: Layout, n_up_factor: Factor) -> int:
    return math.ceil(layout.columns/n_up_factor.x) * math.ceil(layout.rows/n_up_factor.y)


def calculate_offset(page: PyPDF2.pdf.PageObject) -> [float, float]:
    """
    Calculates the x, y value for the offset in default user space units as defined in the pdf standard.
    Uses mediaBox value, not cropBox.
    :param page: A pattern page.
    :return: list with x, y value.
    """
    return [round(float(page.cropBox[2])-float(page.cropBox[0]), 2), round(float(page.cropBox[3])-float(page.cropBox[1]), 2)]


def convert_to_userspaceunits(width_height: [int, int]) -> PaperSize:
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

    return PaperSize(width=(round(width_height[0] * conversion_factor, 3)),
                     height=(round(width_height[1] * conversion_factor, 3)))


def calculate_nup_factors(output_layout: [int], input_properties: PDFProperties) -> Factor:
    output_papersize = convert_to_userspaceunits(output_layout)
    x_factor = int(output_papersize.width // input_properties.papersize.width)
    y_factor = int(output_papersize.height // input_properties.papersize.height)
    return Factor(x=x_factor, y=y_factor)


def convert_to_mm(output_layout: str) -> [int, int]:
    ol_in_mm = output_layout.split("x")
    return [int(x) for x in ol_in_mm]
