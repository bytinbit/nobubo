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

import click
import progress.bar

import utils
import ols


def assemble_to_collage(input_pdf: PyPDF2.PdfFileReader,
                        layout: utils.Layout,
                        input_properties: utils.PDFProperties) -> PyPDF2.pdf.PageObject:
    """
    Takes a pattern pdf where one page equals a part of the pattern and assembles it to on huge collage.
    It is assembled from bottom left to the top right.
    """
    last_page = layout.overview + (layout.columns * layout.rows)
    collage = PyPDF2.pdf.PageObject.createBlankPage(None,
                                                    layout.columns * input_properties.x_offset,
                                                    layout.rows * input_properties.y_offset)
    x_position = 0.0
    y_position = 0.0
    colscount = 0

    print(f"Creating collage... Please be patient, this may take some time.")
    bar = progress.bar.FillingSquaresBar(suffix="assembling page %(index)d of %(max)d, %(elapsed_td)s")
    for pagenumber in bar.iter(range(layout.overview, last_page)):

        if colscount == layout.columns:
            x_position = 0.0
            y_position += input_properties.y_offset
            colscount = 0

        collage.mergeTranslatedPage(input_pdf.getPage(pagenumber), x_position, y_position, expand=True)
        x_position += input_properties.x_offset
        colscount += 1
    return collage


def write_chops(pypdf2_writer: PyPDF2.PdfFileWriter, output_path: pathlib.Path):
    print("Writing file...")
    try:
        with open(output_path, "wb") as output:
            pypdf2_writer.write(output)
    except OSError as e:
        print(f"While writing the file, this error occurred:\n{e}")
        sys.exit(1)


@click.command()
@click.option("--il", "input_layout", nargs=3, type=click.INT, multiple=True, required=True,
              help="Input layout of the pdf. Can be used multiple times if more than 1 overview sheet per pdf exists.",
              metavar="OVERVIEW COLUMNS ROWS")
@click.option("--ol", "output_layout", nargs=1, type=click.STRING,
              help="Output layout. Supported formats: a0, custom. No output layout provided creates a huge collage.",
              metavar="a0 | mmxmm | collage")
@click.argument("input_path", type=click.STRING)
@click.argument("output_path", type=click.STRING)
def main(input_layout, output_layout, input_path, output_path):
    """
    Creates a collage from digital pattern pages and then chops it up into a desired format.
    The collage is assembled according to one or several overview sheets.
    These overviews are usually provided along with the pattern pages in the same pdf.
    Nobubo assumes that overview sheets and the pattern pages are in the same pdf.
    If no overview sheet is in the pattern pdf itself, write 0 in the arguments given, e.g. -l 0 8 4 (see below).

    Currently, only A4 to A0 is supported, thus Nobubo creates A0 pages out of provided A4 pages.
    In order for Nobubo to run, you need the original pdf pattern.
    Create a backup of the original if you're afraid to have it damaged in any way.
    The author takes no responsibility if you face any fit issues or other problems now or later on.

    Explanation of arguments:

    \t-l, -layout:

    \t\tOVERVIEW: page number of overview

    \t\tCOLUMNS: amount of columns you count in the overview sheet

    \t\tROWS: amount of rows you count in the overview sheet

    \t[-c] Optional flag that only creates a huge collage without chopping it up.

    INPUT: Path to the input file, including filename.

    OUTPUT: Path to the output file, including filename.

    The following example has 2 overview sheets at page 1 and 34 with differing layouts:

    python3 nobubo.py -l 1 8 4 -l 34 7 3 -c "home/alice/mypattern.pdf" "home/alice/results/test_collage.pdf"


    """
    try:
        with open(pathlib.Path(input_path), "rb") as inputfile:
            reader = PyPDF2.PdfFileReader(inputfile, strict=False)
            input_properties = utils.PDFProperties(number_of_pages=reader.getNumPages(),
                                                   x_offset=utils.calculate_offset(reader.getPage(1))[0],
                                                   y_offset=utils.calculate_offset(reader.getPage(1))[1])
            # values of the mediaBox are given according to "user space units", defined as 1/72 inch = 0.013888889
            # upper right: 483.307 user space units * 0.013888889 = 6.712597222 inches = 17.04999694388 cm
            # upper left: 729.917 user space units * 0.013888889 = 10.137736111 inches = 25.74984972194 cm
            # a0 = 841 x 1189 mm =  33.1 × 46.8 inches
            print(utils.calculate_offset(reader.getPage(1)))

            layout_list = [utils.Layout(overview=data[0], columns=data[1], rows=data[2]) for data in input_layout]

            output_path = pathlib.Path(output_path)
            overview_counter = 1

            for layout_elem in layout_list:
                print(f"Assembling overview {overview_counter} of {len(layout_list)}\n")
                collage = assemble_to_collage(reader, layout_elem, input_properties)
                print(f"Successfully assembled collage from {input_path}.")

                new_filename = f"{output_path.stem}_{overview_counter}{output_path.suffix}"
                new_outputpath = output_path.parent / new_filename

                if utils.validate_output_layout(output_layout):
                    chopped_up_files = ols.create_output_files(collage, layout_elem, input_properties, output_layout)
                    # written_chops = ols.chop_up_for_a0(collage, layout_elem, input_properties)
                    print(f"Successfully chopped up the collage.\n")

                    write_chops(chopped_up_files, new_outputpath)
                    print(f"Final pdf written to {new_outputpath}.\nEnjoy your sewing :)")

                else:  # default: no output_layout specified, print collage pdf
                    writer = PyPDF2.PdfFileWriter()
                    writer.addPage(collage)
                    write_chops(writer, new_outputpath)
                    print(f"Collage file(s) written to {new_outputpath}.")
                overview_counter += 1

    except OSError as e:
        print(f"While reading the file, this error occurred:\n{e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
