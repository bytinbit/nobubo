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
class Point:
    """
    Point on a pdf page in user space units.
    """
    x: float
    y: float


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
