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


from copy import copy
import math
import PyPDF2
import pathlib
import sys

import click
import progress.bar
import typing

import utils


def assemble(input_pdf: PyPDF2.PdfFileReader,
             layout: utils.Layout,
             input_properties: utils.PDFProperties) -> PyPDF2.pdf.PageObject:
    """
    Takes a pattern pdf where one page equals a part of the pattern and assembles it to on huge collage.
    """
    last_page = layout.overview + (layout.rows * layout.columns)
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


def chop_up_for_a0(assembled_collage: PyPDF2.pdf.PageObject,
                   layout: utils.Layout,
                   input_properties: utils.PDFProperties) -> PyPDF2.PdfFileWriter:
    """
    Takes a collage with all assembled pattern pages, divides them up so that they fit on a A0 sheet.
    """
    print(f"\nChopping up the collage...")
    chopped_up_collage = [assembled_collage for _ in range(0, calculate_pages_needed(layout.rows, layout.columns))]
    A4 = 4  # 4 A4 fit on 1 A0 page

    # only two points are needed to be cropped, lower left (x, y) and upper right (x, y)
    lowerleft_factor = utils.Factor(x=0, y=0)  # k, l
    upperright_factor = utils.Factor(x=1, y=1)  # m, n

    writer = PyPDF2.PdfFileWriter()

    for elem in chopped_up_collage:
        page = copy(elem)  # cf. https://stackoverflow.com/questions/52315259/pypdf2-cant-add-multiple-cropped-pages#

        # apply transformation to lower left x and y
        x_lowerleft = lowerleft_factor.x * A4 * input_properties.x_offset
        y_lowerleft = lowerleft_factor.y * A4 * input_properties.y_offset

        page.cropBox.lowerLeft = (x_lowerleft, y_lowerleft)

        # apply transformation to upper right, y-value
        rowsleft = layout.rows - (upperright_factor.y * A4)
        if rowsleft < 0:
            y_upperright = layout.rows * input_properties.y_offset
        else:
            y_upperright = upperright_factor.y * A4 * input_properties.y_offset

        # apply transformation to upper right, x-value
        colselft = layout.columns - (upperright_factor.x * A4)
        if colselft > 0:  # still assembling the same horizontal line
            x_upperright = upperright_factor.x * A4 * input_properties.x_offset

            page.cropBox.upperRight = (x_upperright, y_upperright)

            lowerleft_factor.x += 1
            upperright_factor.x += 1
        else:  # end of line rechad
            if colselft == 0:  # cols % 4 == 0
                x_upperright = upperright_factor.x * A4 * input_properties.x_offset
            if colselft < 0:  # less than 4 pages left for cols
                x_upperright = layout.columns * input_properties.x_offset

            page.cropBox.upperRight = (x_upperright, y_upperright)

            lowerleft_factor.x = 0
            lowerleft_factor.y += 1

            upperright_factor.x = 1
            upperright_factor.y += 1

        writer.addPage(page)

    return writer


def write_chops(pypdf2_writer: PyPDF2.PdfFileWriter, output_path: pathlib.Path):

    try:
        with open(output_path, "wb") as output:
            pypdf2_writer.write(output)
    except OSError as e:
        print(f"While writing the file, this error occurred:\n{e}")
        sys.exit(1)


def calculate_pages_needed(rows: int, cols: int) -> int:
    return math.ceil(rows/4) * math.ceil(cols/4)


@click.command()
@click.option("-l", "--layout", nargs=3, type=click.INT, multiple=True, required=True, help="Layout of the pdf. Can be used multiple times if more than 1 overview sheets per pdf exists.", metavar="OVERVIEW ROWS COLUMNS")
@click.option("-c", "--collage-only", is_flag=True, help="Only returns a huge collage with all assembled A4 pages that belong to one overview sheet.")
@click.argument("input_path", type=click.STRING)
@click.argument("output_path", type=click.STRING)
def main(layout, collage_only, input_path, output_path):
    """
    Creates a collage from digital pattern pages and then chops it up into a desired format.
    The collage is assembled according to one or several overview sheets.
    These overviews are usually provided along with the pattern pages in the same pdf.
    Nobubo assumes that overview sheets and the pattern pages are in the same pdf.

    Currently, only A4 to A0 is supported, thus Nobubo creates A0 pages out of provided A4 pages.
    In order for Nobubo to run, you need the original pdf pattern.
    Create a backup of the original if you're afraid to have it damaged in any way.
    The author take no responsibility if you face any fit issues or other problems now or later on.

    Explanation of arguments:

    \t-l, -layout:

    \t\tOVERVIEW: page number of overview

    \t\tROWS: amount of rows you count in the overview sheet

    \t\tCOLUMNS: amount of columns you count in the overview sheet

    \t[-c] Optional flag that only creates a huge collage without chopping it up.

    INPUT: Path to the input file, including filename.

    OUTPUT: Path to the output file, including filename.

    The following example has 2 overview sheets at page 1 and 34 with differing layouts:

    python3 nobubo.py -l 1 4 8 -l 34 3 7 -c "home/alice/mypattern.pdf" "home/alice/results/test_collage.pdf"

    """
    try:
        with open(pathlib.Path(input_path), "rb") as inputfile:
            reader = PyPDF2.PdfFileReader(inputfile, strict=False)
            input_properties = utils.PDFProperties(number_of_pages=reader.getNumPages(),
                                             x_offset=float(reader.getPage(1).mediaBox[2]),  # X_OFFSET: # 483.307
                                             y_offset=float(reader.getPage(1).mediaBox[3]),)  # Y_OFFSET: # 729.917
            layout_list = [utils.Layout(overview=data[0], rows=data[1], columns=data[2]) for data in layout]

            output_path = pathlib.Path(output_path)
            overviewcounter = 1
            for layout_elem in layout_list:
                print(f"Assembling overview {overviewcounter} of {len(layout_list)}\n")
                collage = assemble(reader, layout_elem, input_properties)
                print(f"Successfully assembled collage from {input_path}.")

                new_filename = f"{output_path.stem}_{overviewcounter}{output_path.suffix}"
                new_outputpath = output_path.parent / new_filename

                if collage_only:
                    writer = PyPDF2.PdfFileWriter()
                    writer.addPage(collage)
                    write_chops(writer, new_outputpath)
                    print(f"-c flag set, only collage written to {new_outputpath}.\nEnjoy your beautiful collage :)")
                else:
                    written_chops = chop_up_for_a0(collage, layout_elem, input_properties)
                    print(f"Successfully chopped up the collage.\n")

                    write_chops(written_chops, new_outputpath)
                    print(f"Final pdf written to {new_outputpath}.\nEnjoy your sewing :)")
                overviewcounter += 1

    except OSError as e:
        print(f"While reading the file, this error occurred:\n{e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

