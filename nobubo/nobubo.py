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

import click

from nobubo import assembly, disassembly, calc, output


def validate_output_layout(ctx, param, value):
    p = re.compile(r"(a0)|(us)|(\d+[x]\d+)")
    try:
        assert value is None or p.match(value)
        return value
    except AssertionError:
        raise click.BadParameter(f"Output layout {value} does not exist. "
                                 f"Have you chosen a0, us or a custom layout, such as 222x444?")


@click.command()
@click.option("--il", "input_layout_cli", nargs=3, type=click.INT, multiple=True, required=True,
              help="Input layout of the pdf. Can be used multiple times if there is more than 1 overview sheet per pdf.",
              metavar="OVERVIEW COLUMNS ROWS")
@click.option("--ol", "output_layout_cli", nargs=1, type=click.STRING,
              callback=validate_output_layout,
              help="Output layout. Supported formats: a0, us, custom. No output layout provided creates a huge collage.",
              metavar="a0 | us | mmxmm")
@click.option("--margin", "print_margin", nargs=1, type=click.INT,
              help="Define an optional print margin in mm.",
              metavar="mm")
@click.option("--reverse", "reverse_assembly", is_flag="True",
              help="No reverse flag: collage is assembled from top left to bottom right. With flag: collage "
                   "is assembled from bottom left to top right.")
@click.argument("input_path", type=click.STRING)
@click.argument("output_path", type=click.STRING)
def main(input_layout_cli, output_layout_cli, print_margin, reverse_assembly, input_path, output_path):
    """
    Creates a collage from digital pattern pages and then chops it up into a desired output layout.
    The collage is assembled according to one or several overview sheets.
    These overviews are usually provided along with the pattern pages in the same pdf.
    If no overview sheet is in the pattern pdf itself, write 0 in the arguments given: --il 0 8 4.

    Note: In order to use nobubo, you need the original pdf pattern.
    Create a backup of the original if you are afraid to have it damaged in any way.
    The author takes no responsibility if you face any fit issues or other problems now or later on.

    Example: A digital pattern contains 2 overview sheets at page 1 and 34 with different layouts each.
    The output is to be printed on A0 paper:

    $ nobubo --il 1 8 4 -il 34 7 3 --ol a0 "home/alice/mypattern.pdf" "home/alice/results/test_collage.pdf"

    See the readme for further information: https://github.com/bytinbit/nobubo

    Arguments:

    INPUT_PATH: Input path to your pdf pattern.

    OUTPUT_PATH: Where the output should be saved.

    """
    try:
        with tempfile.TemporaryDirectory() as td:
            temp_output_dir = pathlib.Path(td)
            input_properties, output_properties = calc.parse_cli_input(input_layout_cli, output_layout_cli, print_margin,
                                                                       reverse_assembly, input_path, output_path)
            temp_collage_paths: [pathlib.Path] = assembly.assemble_collage(input_properties, temp_output_dir)
            print(f"Successfully assembled collage from {input_path}.")

            if output_properties.output_layout is not None:
                disassembly.create_output_files(temp_collage_paths, input_properties, output_properties)
            else:  # default: no output_layout specified, print collage pdf
                output.write_collage(temp_collage_paths, output_properties)

    except OSError as e:
        print(f"While reading the file, this error occurred:\n{e}")
        sys.exit(1)
