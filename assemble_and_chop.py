import math
import PyPDF2
import pathlib
import sys

import click
from tqdm import tqdm

def assemble(input_pdf, input_properties):
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

def chop_up(assembled_collage, input_properties):
    collage = assembled_collage.getPage(0)
    chopped_up_collage = [collage for i in range(0, calculate_pages_needed(input_properties["ROWS"], input_properties["COLS"]))]
    ROWS = input_properties["ROWS"]
    COLS = input_properties["COLS"]
    X_OFFSET = input_properties["X_OFFSET"]
    Y_OFFSET = input_properties["Y_OFFSET"]

    pagecounter = 1

    # initial coordinates for 1 A0 page
    x_lowerleft = 0.0
    y_lowerleft = 0.0

    # only two points are needed to crop, lower left (x, y) and upper right (x, y)
    k = 0  # controls lower-left x
    l = 0  # controls lower-left y

    m = 1  # controls upper right x
    n = 1  # controls upper right y

    for page in chopped_up_collage:
        print(f"------------- page {pagecounter} -------------")
        writer = PyPDF2.PdfFileWriter()

        # apply transformation to lower left
        print("positions lower left: ")
        x_lowerleft = k * 4 * X_OFFSET
        y_lowerleft = l * 4 * Y_OFFSET
        print(f"\tx_lowerleft: k {k} * 4 * x_offset = {x_lowerleft}")
        print(f"\ty_lowerleft: l {l} * 4 * y_offset = {y_lowerleft}")

        page.cropBox.lowerLeft = (x_lowerleft, y_lowerleft)
        print(f"values of current lower left of page.cropBox: {page.cropBox.lowerLeft}")
        # --------------------------------------------

        # apply transformation to upper right, y-value
        print(f"\npositions upper right: ")
        if ROWS - (n * 4) < 0:
            y_upperright = ROWS * Y_OFFSET
            print(f"\ty_upperright: n {n} * 4 * y_offset = {y_upperright}")

        else:
            y_upperright = n * 4 * Y_OFFSET
            print(f"\ty_upperright: n {n} * 4 * y_offset = {y_upperright}")

        # apply transformation to upper right, x-value
        if COLS - (m * 4) > 0:  # still on the same horizontal line
            x_upperright = m * 4 * X_OFFSET
            print(f"\tx_upperright: m {m} * 4 * x_offset = {x_upperright}")
            # update new horizontal startpositions (on same horizontal line)
            page.cropBox.upperRight = (x_upperright, y_upperright)
            print(f"values of current upper right of page.cropBox: {page.cropBox.upperRight}\n")
            k = k + 1
            m = m + 1
        elif COLS - (m * 4) == 0:  # end of line reached, colsamount mod 4 == 0
            x_upperright = m * 4 * X_OFFSET
            print(f"\tx_upperrreaderight: m {m} * 4 * x_offset = {x_upperright}")
            page.cropBox.upperRight = (x_upperright, y_upperright)
            print(f"values of current upper right of page.cropBox: {page.cropBox.upperRight}\n")
            k = 0
            m = 1
            n = n + 1
            l = l + 1

        else:  # COLS - (m * 4) < 0:   # end of line reached, but less than 4 pages left for cols
            x_upperright = COLS * X_OFFSET
            print(f"\tx_upperright: {COLS} * x_offset = {x_upperright}")
            page.cropBox.upperRight = (x_upperright, y_upperright)
            print(f"values of current upper right of page.cropBox: {page.cropBox.upperRight}\n")
            k = 0
            m = 1
            n = n + 1
            l = l + 1

        writer.addPage(page)
        print("----------------------------------")

        try:
            output = open(f"chopped_collage/{p.stem}_{pagecounter}.pdf", "wb")
        except OSError:
            print("Could not write file to disk.")
            sys.exit(1)
        writer.write(output)
        output.close()
        pagecounter = pagecounter+1

    return 0


def calculate_pages_needed(rows, cols):
    return math.ceil((cols * rows)/16)


@click.command()
@click.argument("rows", type=click.INT)
@click.argument("columns", type=click.INT)
@click.argument("input_path", type=click.STRING)
@click.argument("output_path", type=click.STRING)
def main(rows, columns, input_path, output_path):
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

    input_properties = {"ROWS": rows,
                      "COLS": columns,
                      "number_of_pages": reader.getNumPages(),
                      "X_OFFSET": float(reader.getPage(1).mediaBox[2]),
                      "Y_OFFSET": float(reader.getPage(1).mediaBox[3]),}
    # X_OFFSET: # 483.307
    # Y_OFFSET: # 729.917

    collage = assemble(reader, input_properties)
    chops = chop_up(collage, input_properties)


if __name__ == '__main__':
    main()

