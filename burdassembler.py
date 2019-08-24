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
    X_OFFSET = 483.307
    Y_OFFSET = 729.917

    x_position = 0.0
    y_position = 0.0
    colscount = 0
    rowscount = 0

    # collage = list(PyPDF2.pdf.PageObject.createBlankPage(None, 10, 10)) * calculate_pages_needed(COLS, ROWS)
    collage = PyPDF2.pdf.PageObject.createBlankPage(None, COLS * X_OFFSET, ROWS * Y_OFFSET)

    for pagenumber in tqdm(range(1, number_of_pages)):
        # page 0 in the pdf is typically the overview and not part of the pattern

        if colscount == COLS:
            x_position = 0.0
            y_position += Y_OFFSET
            colscount = 0
            rowscount = rows+1

        collage.mergeTranslatedPage(reader.getPage(pagenumber), x_position, y_position, True)
        x_position += X_OFFSET
        colscount = colscount+1

    writer = PyPDF2.PdfFileWriter()
    writer.addPage(collage)

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
