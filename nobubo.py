from copy import copy
import math
import PyPDF2
import pathlib
import sys

import click
from tqdm import tqdm


def assemble(input_pdf, input_properties):
    """
    Takes a pattern pdf where one page equals a part of the pattern and assembles it to on huge collage.
    """
    collage = PyPDF2.pdf.PageObject.createBlankPage(None,
                                                    input_properties["COLS"] * input_properties["X_OFFSET"],
                                                    input_properties["ROWS"] * input_properties["Y_OFFSET"])
    x_position = 0.0
    y_position = 0.0
    colscount = 0

    for pagenumber in tqdm(range(1, input_properties["number_of_pages"])):
        # page 0 in the pdf is typically the overview and not part of the pattern

        if colscount == input_properties["COLS"]:
            x_position = 0.0
            y_position += float(input_properties["Y_OFFSET"])
            colscount = 0

        collage.mergeTranslatedPage(input_pdf.getPage(pagenumber), x_position, y_position, True)
        x_position += float(input_properties["X_OFFSET"])
        colscount = colscount + 1

    return collage


def chop_up_for_a0(assembled_collage, input_properties):
    """
    Takes a collage with all assembled pattern pages, divides them so that they fit on a A0 sheet.
    """

    chopped_up_collage = [assembled_collage for i in range(0, calculate_pages_needed(input_properties["ROWS"], input_properties["COLS"]))]

    ROWS = input_properties["ROWS"]
    COLS = input_properties["COLS"]
    X_OFFSET = input_properties["X_OFFSET"]
    Y_OFFSET = input_properties["Y_OFFSET"]
    A4 = 4  # 4 A4 fit on 1 A0 page

    # only two points are needed to be cropped, lower left (x, y) and upper right (x, y)
    lowerleft_factor = {"x": 0, "y": 0}
    # lower_left_xfactor = 0  # k
    # lower_left_yfactor = 0  # l

    upper_right_factor = {"x": 1, "y": 1}
    # upper_right_xfactor = 1  # m
    # upper_right_yfactor = 1  # n

    writer = PyPDF2.PdfFileWriter()

    for elem in chopped_up_collage:
        page = copy(elem)

        # apply transformation to lower left x and y
        x_lowerleft = lowerleft_factor["x"] * A4 * X_OFFSET
        y_lowerleft = lowerleft_factor["y"] * A4 * Y_OFFSET

        page.cropBox.lowerLeft = (x_lowerleft, y_lowerleft)

        # apply transformation to upper right, y-value
        rowsleft = ROWS - (upper_right_factor["y"] * A4)
        if rowsleft < 0:
            y_upperright = ROWS * Y_OFFSET
        else:
            y_upperright = upper_right_factor["y"] * A4 * Y_OFFSET

        # apply transformation to upper right, x-value
        colselft = COLS - (upper_right_factor["x"] * A4)
        if colselft > 0:  # still on the same horizontal line
            x_upperright = upper_right_factor["x"] * A4 * X_OFFSET

            page.cropBox.upperRight = (x_upperright, y_upperright)

            lowerleft_factor["x"] = lowerleft_factor["x"] + 1
            upper_right_factor["x"] = upper_right_factor["x"] + 1
        else:
            if colselft == 0:  # end of line reached, cols % 4 == 0
                x_upperright = upper_right_factor["x"] * A4 * X_OFFSET
            if colselft < 0: # end of line reached, but less than 4 pages left for cols
                x_upperright = COLS * X_OFFSET

            page.cropBox.upperRight = (x_upperright, y_upperright)

            lowerleft_factor["x"] = 0
            lowerleft_factor["y"] = lowerleft_factor["y"] + 1

            upper_right_factor["x"] = 1
            upper_right_factor["y"] = upper_right_factor["y"] + 1

        writer.addPage(page)

    return writer


def write_chops(pypdf2_writer, output_path):

    try:
        output = open(output_path, "wb")
        print(f"Final pdf written to {output_path}.")
    except IOError:
        print("Could not write file to disk.")
        sys.exit(1)
    pypdf2_writer.write(output)
    output.close()


def calculate_pages_needed(rows, cols):
    return math.ceil(rows/4) * math.ceil(cols/4)


@click.command()
@click.argument("rows", type=click.INT)
@click.argument("columns", type=click.INT)
@click.argument("input_path", type=click.STRING)
@click.argument("output_path", type=click.STRING)
def main(rows, columns, input_path, output_path):
    """
    Creates a collage from single A4 Burda pattern pages.
    The pages are assembled following an overview picture of all the assembled pages.
    This overview is usually provided along with the pattern pages in the same pdf
    and shown on the first page of the pattern pdf.\n

    [ROWS] The amount of rows you count in the overview page.\n
    \t WARNING: In rare cases, the overview doesn't match the true amount and arrangement of pages.
    The resulting collage and pages will thus be mismatching and there's no solution to this yet.
    [COLUMNS] The amount of columns you count in the overview.\n
    [INPUT]: Path to the input file, including the filename.\n
    [OUTPUT]: Path to the output file, including the filename.\n

    """
    try:
        reader = PyPDF2.PdfFileReader(open(pathlib.Path(input_path), "rb"))
    except OSError:
        print(f"Filepath{input_path} not found")
        sys.exit(1)

    input_properties = {"ROWS": rows,
                        "COLS": columns,
                        "number_of_pages": reader.getNumPages(),
                        "X_OFFSET": float(reader.getPage(1).mediaBox[2]),  # X_OFFSET: # 483.307
                        "Y_OFFSET": float(reader.getPage(1).mediaBox[3]),  # Y_OFFSET: # 729.917
                       }

    collage = assemble(reader, input_properties)
    print(f"Successfully assembled collage from {input_path}.")
    written_chops = chop_up_for_a0(collage, input_properties)
    print(f"Successfully chopped up the collage.")
    write_chops(written_chops, output_path)
    print(f"Final pdf written to {output_path}.\nEnjoy your sewing :)")


if __name__ == '__main__':
    main()

