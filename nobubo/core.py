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
    """
    overview: int
    columns: int
    rows: int


@dataclass
class Point:
    """
    Point on a pdf page in user space units.
    """
    x: float
    y: float


@dataclass
class InputProperties:
    """
    Holds all information of the input pdf.
    """
    input_filepath: pathlib.Path
    output_path: pathlib.Path
    number_of_pages: int
    pagesize: PageSize
    layout: [Layout]
    reverse_assembly: bool = False


@dataclass
class OutputProperties:
    """
    Holds all information of the output pdf.
    """
    output_path: pathlib.Path
    output_layout: [int]


@dataclass
class Factor:
    """
    Factor class for multiplication.
    """
    x: int
    y: int