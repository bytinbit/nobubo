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
import math


import attr
import PyPDF2

@attr.s
class PDFProperties:
    number_of_pages: int = attr.ib()
    x_offset: float = attr.ib()
    y_offset: float = attr.ib()


@attr.s
class Layout:
    overview: int = attr.ib()
    columns: int = attr.ib()
    rows: int = attr.ib()


@attr.s
class Factor:
    x = attr.ib()
    y = attr.ib()


@attr.s
class PaperSize:
    width = attr.ib()
    height = attr.ib()


def calculate_pages_needed(cols: int, rows: int) -> int:
    return math.ceil(rows/4) * math.ceil(cols/4)


def calculate_offset(page: PyPDF2.pdf.PageObject):
    """
    Calculates the x, y value for the offset in default user space units as defined in the pdf standard.
    :param page: A pattern page.
    :return: list with x, y value.
    """
    return [float(page.mediaBox[2])-float(page.mediaBox[0]), float(page.mediaBox[3])-float(page.mediaBox[1])]


def convert_to_userspaceunits(width, height) -> PaperSize:
    """
    Converts a page's physical width and height from millimeters to default user space unit,
    which are defined in the pdf standard as 1/72 inch.

    :param width: Width of the physical page in millimeters (mm).
    :param: height: Height of the physical page in millimeters (mm).
    :return: Width and height of the physical page in default user space units.
    """
    # 1 mm = 5/127 inches = 0.03937 inches;  1/72 inch = 0.013888889
    # conversion factor = 5/127 / 1/72 = 360/127 = 2.834645669
    conversion_factor = 2.834645669

    return PaperSize(width=(width * conversion_factor), height=(height * conversion_factor))
