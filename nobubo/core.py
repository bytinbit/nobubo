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
Data classes for input, output and pdf properties.
"""
from dataclasses import dataclass
import pathlib
from typing import List, Optional


@dataclass
class PageSize:
    """
    Page size whose width and height are in user space units.
    """
    width: float = 0
    height: float = 0


@dataclass
class Layout:
    """
    A Pattern layout.

    first_page: The number of the pdf page
    which marks the beginning of the pattern pages
    that are covered by the columns and rows.
    """
    first_page: int
    columns: int
    rows: int


@dataclass
class Point:
    """
    Point on a pdf page in user space units.
    """
    x: float
    y: float


class InputProperties:
    """
    Holds all information of the input pdf.
    """

    def __init__(self, input_filepath: pathlib.Path, number_of_pages: int, pagesize: PageSize, layout: List[Layout], reverse_assembly: bool = False):
        self.input_filepath = input_filepath
        self.number_of_pages = number_of_pages
        self.pagesize = pagesize
        self.layout = layout
        self.reverse_assembly = reverse_assembly


class OutputProperties:
    """
    Holds all information of the output pdf.
    """

    def __init__(self, output_path: pathlib.Path, output_layout: Optional[List[int]]):
        self.output_path = output_path
        self.output_layout = output_layout


@dataclass
class Factor:
    """
    Factor class for multiplication.
    """
    x: int
    y: int
