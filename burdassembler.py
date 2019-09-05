import math
import PyPDF2
import pathlib
import sys

import click
from tqdm import tqdm

# Todo: make code nicer
# Todo: Gui


@click.command()
@click.argument("rows", type=click.INT)
@click.argument("columns", type=click.INT)
@click.argument("input_path", type=click.STRING)
@click.argument("output_path", type=click.STRING)
def assemble_pages(rows, columns, input_path, output_path):
    """
    Creates a collage from single A4 Burda pattern pages.
    The pages are assembled to look like an overview picture of all the assembled pages.
    This overview is usually provided along with the pattern pages and shown on the first page of the pattern pdf.\n

    [ROWS] The amount of rows you count in the overview.\n
    [COLUMNS] The amount of columns you count in the overview.\n
    [INPUT]: Path to the input file, including the filename.\n
    [OUTPUT]: Path to the output file, including the filename.\n

    """

    try:
        reader = PyPDF2.PdfFileReader(open(pathlib.Path(input_path), "rb"))
    except OSError:
        print(f"Filepath{input_path} not found")
        sys.exit(1)

    number_of_pages = reader.getNumPages()
    ROWS = rows
    COLS = columns
    X_OFFSET = float(reader.getPage(1).mediaBox[2])  # 483.307
    print(f"X_OFFSET {X_OFFSET}")
    Y_OFFSET = float(reader.getPage(1).mediaBox[3])  # 729.917
    print(f"Y_OFFSET: {Y_OFFSET}")

    x_position = 0.0
    y_position = 0.0
    colscount = 0

# STEP 1: put together a complete pdf with all pages as a collage

    collage = PyPDF2.pdf.PageObject.createBlankPage(None, COLS * X_OFFSET, ROWS * Y_OFFSET)

    for pagenumber in tqdm(range(1, number_of_pages)):
        # page 0 in the pdf is typically the overview and not part of the pattern

        if colscount == COLS:
            x_position = 0.0
            y_position += float(Y_OFFSET)
            colscount = 0

        collage.mergeTranslatedPage(reader.getPage(pagenumber), x_position, y_position, True)
        x_position += float(X_OFFSET)
        colscount = colscount+1

# STEP 2: chop up PDF collage into A0 pages
    chopped_up_collage = [collage for i in range(0, calculate_pages_needed(COLS, ROWS))]
    colsleft = COLS
    rowsleft = ROWS

    # initial coordinates for 1 A0 page
    x_lowerleft = 0.0
    y_lowerleft = 0.0

    x_upperright = X_OFFSET * 4
    y_upperright = Y_OFFSET * 4
    print(f"original x_upperright {x_upperright}")
    print(f"original y_upperright {y_upperright}")

    n = 1
    k = 1

    for page in chopped_up_collage:

        page.cropBox.lowerLeft = (x_lowerleft, y_lowerleft)
        print(f"lower Left of page.cropBox: {page.cropBox.lowerLeft}")
        page.cropBox.upperRight = (x_upperright, y_upperright)
        print(f"upper Right of page.cropBox: {page.cropBox.upperRight}")

        # update new startpositions of next a0 page
        print("update positions: ")
        x_lowerleft = n * 4 * X_OFFSET
        y_lowerleft = 0 * 4 * Y_OFFSET
        print(f"new x_lowerleft {x_lowerleft}")
        print(f"new y_lowerleft {y_lowerleft}")
        # y_lowerleft
        x_upperright = n * 4 * X_OFFSET
        y_upperright = 0 * 4 * Y_OFFSET
        print(f"new x_upperright {x_upperright}")
        print(f"new y_upperright {y_upperright}")
        # y_lowerleft
        n = n+1

        if (colsleft - 4) >= 0:
            colsleft = colsleft - 4
        if (rowsleft - 4) >= 0:
            rowsleft = rowsleft - 4
        print("----------------------")

#     >> > reader = PyPDF2.PdfFileReader(open("notes/pullicollage.pdf", "rb"))
#     >> > page = reader.getPage(0)
#     >> > croppedpage = page
#     >> > croppedpage = page
#     >> > croppedpage.cropBox.upperRight = (483.307, 729.917) is 1 A4 page
#     >> > output = PyPDF2.PdfFileWriter()
#     >> > output.addPage(croppedpage)
#     >> > with open("out.pdf", "wb") as out_f:
#         ...
#         output.write(out_f)

    # STEP 3: Write to disk
    writer = PyPDF2.PdfFileWriter()
    for page in chopped_up_collage:
        writer.addPage(page)
    try:
        output = open(pathlib.Path(output_path), "wb")
    except OSError:
        print("Could not write file to disk.")
        sys.exit(1)
    writer.write(output)
    output.close()


def calculate_pages_needed(cols, rows):
    return math.ceil((cols * rows)/16)


if __name__ == '__main__':
    assemble_pages()
