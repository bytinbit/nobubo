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


def calculate_pages_needed(cols: int, rows: int) -> int:
    return math.ceil(rows/4) * math.ceil(cols/4)


def calculate_offset(page: PyPDF2.pdf.PageObject):
    """
    Calculates the x, y value for the offset in default user space units as defined in the pdf standard.
    :param page: A pattern page.
    :return: list with x, y value.
    """
    return [float(page.mediaBox[2])-float(page.mediaBox[0]), float(page.mediaBox[3])-float(page.mediaBox[1])]