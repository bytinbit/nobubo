import PyPDF2
import sys
from copy import copy
import click
import pathlib


@click.command()
@click.argument("rows", type=click.INT)
@click.argument("columns", type=click.INT)
@click.argument("number_of_output_pages", type=click.INT)
@click.argument("input_path", type=click.STRING)
def chop_up_collage(rows, columns, number_of_output_pages, input_path):
    p = pathlib.Path(input_path)
    reader = PyPDF2.PdfFileReader(open(p, "rb"))
    collage = reader.getPage(0)
    ROWS = rows
    COLS = columns
    pages_needed = number_of_output_pages
    X_OFFSET = 483.307
    Y_OFFSET = 729.917

    chopped_up_collage = [collage for i in range(0, pages_needed)]

    pagecounter = 1

    # initial coordinates for 1 A0 page
    x_lowerleft = 0.0
    y_lowerleft = 0.0

    # only two points are needed to crop, lower left (x, y) and upper right (x, y)
    k = 0  # controls lower-left x
    l = 0  # controls lower-left y

    m = 1  # controls upper right x
    n = 1  # controls upper right y

    writer = PyPDF2.PdfFileWriter()

    for elem in chopped_up_collage:
        print(f"------------- page {pagecounter} -------------")
        page = copy(elem)

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
            print(f"\tx_upperright: m {m} * 4 * x_offset = {x_upperright}")
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

        pagecounter = pagecounter + 1
        writer.addPage(page)
        print("----------------------------------")

    try:
        output = open(f"chopped_collage/{p.stem}_choppedup.pdf", "wb")
    except OSError:
        print("Could not write file to disk.")
        sys.exit(1)
    writer.write(output)
    output.close()



if __name__ == '__main__':
    chop_up_collage()

