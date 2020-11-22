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
import PyPDF2
import pathlib
import sys
import tempfile

import click

from nobubo import assembly
from nobubo import utils


def write_chops(pypdf2_writer: PyPDF2.PdfFileWriter, output_path: pathlib.Path):
    print("Writing file...")
    try:
        with open(output_path, "wb") as output:
            pypdf2_writer.write(output)
    except OSError as e:
        print(f"While writing the file, this error occurred:\n{e}")
        sys.exit(1)


def validate_output_layout(ctx, param, value):
    try:
        value is not None and (value == "a0" or utils.convert_to_mm(value))
        return value
    except ValueError:
        raise click.BadParameter(f"If custom layout was chosen, have you written it as 'mmxmm', e.g. 222x444?.")


@click.command()
@click.option("--il", "input_layout", nargs=3, type=click.INT, multiple=True, required=True,
              help="Input layout of the pdf. Can be used multiple times if more than 1 overview sheet per pdf exists.",
              metavar="OVERVIEW COLUMNS ROWS")
@click.option("--ol", "output_layout_cli", nargs=1, type=click.STRING,
              callback=validate_output_layout,
              help="Output layout. Supported formats: a0, custom. No output layout provided creates a huge collage.",
              metavar="a0 | mmxmm")
@click.option("--reverse", "reverse_assembly", is_flag="True",
              help="No reverse flag: collage is assembled from top left to bottom right. With reverse flag: collage "
                   "is assembled from bottom left to top right.")
@click.argument("input_path", type=click.STRING)
@click.argument("output_path", type=click.STRING)
def main(input_layout, output_layout_cli, reverse_assembly, input_path, output_path):
    """
    Creates a collage from digital pattern pages and then chops it up into a desired output layout.
    The collage is assembled according to one or several overview sheets.
    These overviews are usually provided along with the pattern pages in the same pdf.
    If no overview sheet is in the pattern pdf itself, write 0 in the arguments given: --il 0 8 4.

    In order for Nobubo to function, you need the original pdf pattern.

    Create a backup of the original if you are afraid to have it damaged in any way.

    The author takes no responsibility if you face any fit issues or other problems now or later on.

    Example usage:

    2 overview sheets at page 1 and 34 with differing layouts, which are then assembled to be printed on a0 paper:

    python nobubo.py --il 1 8 4 -il 34 7 3 --ol a0 "home/alice/mypattern.pdf" "home/alice/results/test_collage.pdf"

    Further information and the readme can be found on https://github.com/bytinbit/nobubo

    """
    # TODO refactor code amount in with whole function
    try:
        with tempfile.TemporaryDirectory() as td:
            temp_output_dir = pathlib.Path(td)
            with open(pathlib.Path(input_path), "rb") as inputfile:
                reader = PyPDF2.PdfFileReader(inputfile, strict=False)
                cropBox_values = utils.calculate_offset(reader.getPage(1))  # first page (getPage(0)) may contain overview
                input_papersize = utils.PaperSize(width=cropBox_values[0], height=cropBox_values[1])
                input_properties = utils.PDFProperties(number_of_pages=reader.getNumPages(),
                                                       papersize=input_papersize, layout=input_layout)
                layout_list = [utils.Layout(overview=data[0], columns=data[1], rows=data[2]) for data in input_properties.layout]

                output_path = pathlib.Path(output_path)

                for counter, layout_elem in enumerate(layout_list):
                    print(f"Assembling overview {counter+1} of {len(layout_list)}\n")
                    print(f"Creating collage... Please be patient, this may take some time.")
                    tempcollagepath = assembly.assemble_collage(pathlib.Path(input_path), temp_output_dir, layout_elem, input_properties, reverse=reverse_assembly)
                    with tempcollagepath.open("rb") as collagefile:
                        reader = PyPDF2.PdfFileReader(collagefile, strict=False)
                        collage = reader.getPage(0)

                        print(f"Successfully assembled collage from {input_path}.")

                        new_filename = f"{output_path.stem}_{counter+1}{output_path.suffix}"
                        new_outputpath = output_path.parent / new_filename

                        if output_layout_cli:
                            print(f"\nChopping up the collage...")
                            if output_layout_cli == "a0":  # TODO move calculation to top, here it's done for every page, not needed
                                output_layout = utils.convert_to_mm("841x1189")
                            if "x" in output_layout_cli:
                                output_layout = utils.convert_to_mm(output_layout_cli)
                            chopped_up_files = assembly.create_output_files(collage, layout_elem, input_properties, output_layout)
                            print(f"Successfully chopped up the collage.\n")

                            write_chops(chopped_up_files, new_outputpath)
                            print(f"Final pdf written to {new_outputpath}. Enjoy your sewing :)")

                        else:  # default: no output_layout specified, print collage pdf
                            writer = PyPDF2.PdfFileWriter()
                            writer.addPage(collage)
                            write_chops(writer, new_outputpath)
                            print(f"Collage written to {new_outputpath}. Enjoy your sewing :)")

    except OSError as e:
        print(f"While reading the file, this error occurred:\n{e}")
        sys.exit(1)