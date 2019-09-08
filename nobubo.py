from copy import copy
import math
import PyPDF2
import pathlib
import sys

import click
import progress.bar

from utils import Factor, PDFProperties


def assemble(input_pdf, input_properties):
    """
    Takes a pattern pdf where one page equals a part of the pattern and assembles it to on huge collage.
    """
    collage = PyPDF2.pdf.PageObject.createBlankPage(None,
                                                    input_properties.columns * input_properties.x_offset,
                                                    input_properties.rows * input_properties.y_offset)
    x_position = 0.0
    y_position = 0.0
    colscount = 0

    print(f"Please be patient, this may take some time.")
    bar = progress.bar.FillingSquaresBar(suffix="assembling page %(index)d of %(max)d, %(elapsed_td)s")
    for pagenumber in bar.iter(range(1, input_properties.number_of_pages)):
    # for pagenumber in tqdm(range(1, input_properties["number_of_pages"])):
    # page 0 in the pdf is typically the overview and not part of the pattern

        if colscount == input_properties.columns:
            x_position = 0.0
            y_position += input_properties.y_offset
            colscount = 0

        collage.mergeTranslatedPage(input_pdf.getPage(pagenumber), x_position, y_position, expand=True)
        x_position += input_properties.x_offset
        colscount += 1
    return collage


def chop_up_for_a0(assembled_collage, input_properties):
    """
    Takes a collage with all assembled pattern pages, divides them up so that they fit on a A0 sheet.
    """

    chopped_up_collage = [assembled_collage for _ in range(0, calculate_pages_needed(input_properties.rows, input_properties.columns))]
    A4 = 4  # 4 A4 fit on 1 A0 page

    # only two points are needed to be cropped, lower left (x, y) and upper right (x, y)
    lowerleft_factor = Factor(x=0, y=0)  # k, l
    upperright_factor = Factor(x=1, y=1)  # m, n

    writer = PyPDF2.PdfFileWriter()

    for elem in chopped_up_collage:
        page = copy(elem)

        # apply transformation to lower left x and y
        x_lowerleft = lowerleft_factor.x * A4 * input_properties.x_offset
        y_lowerleft = lowerleft_factor.y * A4 * input_properties.y_offset

        page.cropBox.lowerLeft = (x_lowerleft, y_lowerleft)

        # apply transformation to upper right, y-value
        rowsleft = input_properties.rows - (upperright_factor.y * A4)
        if rowsleft < 0:
            y_upperright = input_properties.rows * input_properties.y_offset
        else:
            y_upperright = upperright_factor.y * A4 * input_properties.y_offset

        # apply transformation to upper right, x-value
        colselft = input_properties.columns - (upperright_factor.x * A4)
        if colselft > 0:  # still assembling the same horizontal line
            x_upperright = upperright_factor.x * A4 * input_properties.x_offset

            page.cropBox.upperRight = (x_upperright, y_upperright)

            lowerleft_factor.x += 1
            upperright_factor.x += 1
        else:
            if colselft == 0:  # end of line reached, cols % 4 == 0
                x_upperright = upperright_factor.x * A4 * input_properties.x_offset
            if colselft < 0: # end of line reached, but less than 4 pages left for cols
                x_upperright = input_properties.columns * input_properties.x_offset

            page.cropBox.upperRight = (x_upperright, y_upperright)

            lowerleft_factor.x = 0
            lowerleft_factor.y += 1

            upperright_factor.x = 1
            upperright_factor.y += 1

        writer.addPage(page)

    return writer


def write_chops(pypdf2_writer, output_path):

    try:
        with open(output_path, "wb") as output:
            pypdf2_writer.write(output)
    except OSError as e:
        print(f"While writing the file, this error occurred:\n{e}")
        sys.exit(1)


def calculate_pages_needed(rows, cols):
    return math.ceil(rows/4) * math.ceil(cols/4)


@click.command()
@click.argument("rows", type=click.INT)
@click.argument("columns", type=click.INT)
@click.argument("input_path", type=click.STRING)
@click.argument("output_path", type=click.STRING)
@click.option("-c", is_flag=True, help="Only returns a huge collage with all assembled A4 pages.")
def main(rows, columns, input_path, output_path, c):
    """
    Creates a collage from digital pattern pages and then chops it up into a desired format.
    The collage is assembled following an overview sheet of all the assembled pages.
    This overview is usually provided along with the pattern pages in the same pdf.
    It is assumed to be the first page of the pattern pdf.

    Currently, only A4 to A0 is supported, thus nobubo creates A0 pages out of provided A4 pages.

    \t WARNING: In rare cases, the overview doesn't match the true amount and arrangement of pages.
    The resulting collage and pages will thus be mismatching and there's no solution to this yet.

    [ROWS]: The amount of rows you count in the overview page.

    [COLUMNS]: The amount of columns you count in the overview page.

    [INPUT]: Path to the input file, including the filename.

    [OUTPUT]: Path to the output file, including the filename.

    The author does not take any responsibility if you face any fit issues or other problems later on.

    """
    try:
        with open(pathlib.Path(input_path), "rb") as inputfile:
            reader = PyPDF2.PdfFileReader(inputfile, strict=False)
            input_properties = PDFProperties(rows=rows,
                                             columns=columns,
                                             number_of_pages=reader.getNumPages(),
                                             x_offset=float(reader.getPage(1).mediaBox[2]),  # X_OFFSET: # 483.307
                                             y_offset=float(reader.getPage(1).mediaBox[3]))  # Y_OFFSET: # 729.917
            if c:
                collage = assemble(reader, input_properties)
                print(f"Successfully assembled collage from {input_path}.")
                writer = PyPDF2.PdfFileWriter()
                writer.addPage(collage)
                write_chops(writer, output_path)
                print(f"-c flag set, only collage written to {output_path}.\nEnjoy your beautiful collage :)")
            else:
                collage = assemble(reader, input_properties)
                print(f"Successfully assembled collage from {input_path}.\n")

                written_chops = chop_up_for_a0(collage, input_properties)
                print(f"Successfully chopped up the collage.\n")

                write_chops(written_chops, output_path)
                print(f"Final pdf written to {output_path}.\nEnjoy your sewing :)")
    except OSError as e:
        print(f"While reading the file, this error occurred:\n{e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

