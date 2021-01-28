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
Helpers for calculations, conversions, generations.
"""
import math
import pathlib
import random
import re
import string
from typing import List

import click
import pikepdf

from nobubo import core, errors
from nobubo.core import Factor


def parse_cli_input(input_layout: (int, int, int), output_layout_cli: str, print_margin: int,
                    reverse_assembly: bool, input_path: str, output_path: str
                    ) -> (core.InputProperties, core.OutputProperties):
    try:
        with pikepdf.open(pathlib.Path(input_path)) as inputfile:
            # first page (getPage(0)) may contain overview, so get second one
            width, height = page_dimensions(inputfile.pages[1])
            input_properties = core.InputProperties(
                input_filepath=pathlib.Path(input_path),
                output_path=pathlib.Path(output_path),
                number_of_pages=len(inputfile.pages),
                pagesize=core.PageSize(width=width, height=height),
                layout=parse_input_layouts(input_layout),
                reverse_assembly=reverse_assembly)
            output_properties = core.OutputProperties(
                output_path=pathlib.Path(output_path),
                output_layout=parse_output_layout(output_layout_cli, print_margin))
    except OSError as e:
        raise errors.UsageError(f"While reading the input pdf file, this error occurred:\n{e}")
    return input_properties, output_properties


def parse_input_layouts(input_layout: (int, int, int)) ->[core.Layout]:
    return [core.Layout(first_page=data[0], columns=data[1], rows=data[2]) for data in input_layout]


def parse_output_layout(output_layout_cli: str, print_margin: int = None) -> [int]:
    print_size: List[int] = []
    if output_layout_cli is None:
        return None
    if output_layout_cli == "a0":
        print_size = to_mm("841x1189")
    if output_layout_cli == "us":  # Arch E /Arch 6 size of 36 × 48 inches
        print_size = to_mm("914x1220")
    elif "x" in output_layout_cli:
        print_size = to_mm(output_layout_cli)

    if print_margin:
        return [size - (2 * print_margin) for size in print_size]
    else:
        return print_size


def validate_output_layout(ctx, param, value):
    p = re.compile(r"(a0)|(us)|(\d+[x]\d+)")
    try:
        assert value is None or p.match(value)
        return value
    except AssertionError:
        raise click.BadParameter(f"Output layout {value} does not exist. "
                                 f"Have you chosen a0, us or a custom layout, such as 222x444?")


def pages_needed(layout: core.Layout, n_up_factor: Factor) -> int:
    return math.ceil(layout.columns/n_up_factor.x) * math.ceil(layout.rows/n_up_factor.y)


def page_dimensions(page: pikepdf.Page) -> (float, float):
    """
    Calculates the x, y value for the offset in default user space units as defined in the pdf standard.
    :param page: A PDF page.
    :return: list with x, y value.
    """
    if not hasattr(page, "CropBox"):
        box = page.MediaBox
    else:
        box = page.CropBox
    return round(float(box[2])-float(box[0]), 2), round(float(box[3])-float(box[1]), 2)


def to_userspaceunits(width_height: [int, int]) -> core.PageSize:
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

    return core.PageSize(width=(round(width_height[0] * conversion_factor, 3)),
                         height=(round(width_height[1] * conversion_factor, 3)))


def nup_factors(pagesize: core.PageSize, output_layout: [int]) -> Factor:
    output_papersize = to_userspaceunits(output_layout)
    x_factor = int(output_papersize.width // pagesize.width)
    y_factor = int(output_papersize.height // pagesize.height)
    return Factor(x=x_factor, y=y_factor)


def to_mm(output_layout: str) -> [int, int]:
    ol_in_mm = re.compile(r"\d+[x]\d+").findall(output_layout)[0].split("x")
    return [int(x) for x in ol_in_mm]


def pagerange_reverse(layout: core.Layout) -> (int, int, int):
    return layout.first_page, (layout.first_page + (layout.columns * layout.rows)), layout.columns


def new_outputpath(output_path: pathlib.Path, page_count: int):
    new_filename = f"{output_path.stem}_{page_count + 1}{output_path.suffix}"
    return output_path.parent / new_filename


def random_string():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=7))
