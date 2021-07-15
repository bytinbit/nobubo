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
import pathlib
import re
import sys
import tempfile
from typing import List, Tuple

import click
import pikepdf

from nobubo import errors
from nobubo.disassembly import OutputProperties
from nobubo.assembly import InputProperties, Layout, PageSize


def validate_output_layout(ctx, param, value):
    p = re.compile(r"(a0)|(us)|(\d+[x]\d+)")
    try:
        assert value is None or p.match(value)
        return value
    except AssertionError:
        raise click.BadParameter(f"Output layout {value} does not exist. "
                                 "Have you chosen a0, us or a custom layout, "
                                 "such as 222x444?")


@click.command()
@click.option("--il", "input_layout_cli", nargs=3, type=click.INT, multiple=True,
              required=True,
              help="Input layout of the pdf. Can be used multiple times.",
              metavar="FIRSTPAGE COLUMNS ROWS")
@click.option("--ol", "output_layout_cli", nargs=1, type=click.STRING,
              callback=validate_output_layout,
              help="Output layout. Supported formats: a0, us, custom. No output "
                   "layout provided creates a huge collage.",
              metavar="a0 | us | mmxmm")
@click.option("--margin", "print_margin", nargs=1, type=click.INT,
              help="Define an optional print margin in mm.",
              metavar="mm")
@click.option("--reverse", "reverse_assembly", is_flag="True",
              help="With reverse flag: collage is assembled from bottom left to top "
                   "right. "
                   "No flag: collage is assembled from top left to bottom right. ")
@click.argument("input_path", type=click.STRING)
@click.argument("output_path", type=click.STRING)
def main(input_layout_cli, output_layout_cli, print_margin, reverse_assembly,
         input_path, output_path):
    """
    Creates a collage from digital pattern pages
    and then chops it up into a desired output layout.
    The collage is assembled according to one or several overview sheets.
    These overviews are usually provided along with the pattern pages
    in the same pdf or in the instructions pdf.

    Note: In order to use nobubo, you need the original pdf pattern.
    Create a backup of the original if you are afraid to have it damaged in any way.
    The author takes no responsibility if you face any fit issues
    or other problems now or later on.

    Example: A digital pattern contains 2 overview sheets
    at page 1 and 34 with different layouts each.
    The output is to be printed on A0 paper:

    $ nobubo --il 2 8 4 -il 35 7 3 --ol a0 "myfolder/mypattern.pdf" "test_collage.pdf"

    See the readme for further information: https://github.com/bytinbit/nobubo

    Arguments:

    INPUT_PATH: Input path to your pdf pattern.

    OUTPUT_PATH: Where the output should be saved.

    """
    try:
        with tempfile.TemporaryDirectory() as td:
            temp_output_dir = pathlib.Path(td)
            input_properties, output_properties = \
                parse_cli_input(input_layout_cli,
                                output_layout_cli,
                                print_margin,
                                reverse_assembly,
                                input_path,
                                output_path)
            temp_collage_paths: List[pathlib.Path] = \
                input_properties.assemble_collage(temp_output_dir)
            print(f"Successfully assembled collage from {input_path}.")

            if output_properties.output_layout is not None:
                output_properties.create_output_files(temp_collage_paths,
                                                input_properties,
                                                )
            else:  # default: no output_layout specified, print collage pdf
                output_properties.write_collage(temp_collage_paths, )
    except (errors.UsageError, click.BadParameter) as e:
        print(e)
        sys.exit(1)


def parse_cli_input(input_layout: List[Tuple[int, int, int]],
                    output_layout_cli: str,
                    print_margin: int,
                    reverse_assembly: bool,
                    input_path: str, output_path: str
                    ) -> Tuple[InputProperties, OutputProperties]:
    try:
        with pikepdf.open(pathlib.Path(input_path)) as inputfile:
            # first page (getPage(0)) may contain overview, so get second one
            width, height = page_dimensions(inputfile.pages[1])
            input_properties = InputProperties(
                input_filepath=pathlib.Path(input_path),
                number_of_pages=len(inputfile.pages),
                pagesize=PageSize(width=width, height=height),
                layout=parse_input_layouts(input_layout),
                reverse_assembly=reverse_assembly)
            output_properties = OutputProperties(
                output_path=pathlib.Path(output_path),
                output_layout=parse_output_layout(output_layout_cli, print_margin)
                if output_layout_cli else None
            )
    except OSError as e:
        raise errors.UsageError(f"While reading the input pdf file, "
                                f"this error occurred:\n{e}")
    return input_properties, output_properties


def parse_input_layouts(input_layout: List[Tuple[int, int, int]]) -> List[
    Layout]:
    return [Layout(first_page=data[0], columns=data[1], rows=data[2])
            for data in input_layout]


def parse_output_layout(output_layout_cli: str, print_margin: int = None) -> List[int]:
    print_size: List[int] = []
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


def page_dimensions(page: pikepdf.Page) -> Tuple[float, float]:
    """
    Calculates the x, y value for the offset in default user space units
    as defined in the pdf standard.
    :param page: A PDF page.
    :return: list with x, y value.
    """
    if not hasattr(page, "CropBox"):
        # page is of type Object, and either MediaBox, CropBox or TrimBox
        # are all of type pikepdf.objects.Object
        # they exist (or not) depending on the pdf itself
        box = page.MediaBox  # type: ignore
    else:
        box = page.CropBox  # type: ignore
    return round(float(box[2]) - float(box[0]), 2), round(float(box[3]) - float(box[1]),
                                                          2)


def to_mm(output_layout: str) -> List[int]:
    ol_in_mm = re.compile(r"\d+[x]\d+").findall(output_layout)[0].split("x")
    return [int(x) for x in ol_in_mm]