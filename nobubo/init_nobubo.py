import pathlib
import re
from typing import List, Tuple

import pikepdf

from nobubo import errors
from nobubo.assembly import NobuboInput, PageSize, Layout
from nobubo.disassembly import NobuboOutput


def parse_cli_input_data(
    input_layout: List[Tuple[int, int, int]],
    reverse_assembly: bool,
    input_path: str,
) -> NobuboInput:
    try:
        with pikepdf.open(pathlib.Path(input_path)) as inputfile:
            # first page (getPage(0)) may contain overview, so get second one
            width, height = page_dimensions(inputfile.pages[1])
            input_properties = NobuboInput(
                input_filepath=pathlib.Path(input_path),
                number_of_pages=len(inputfile.pages),
                pagesize=PageSize(width=width, height=height),
                layout=parse_input_layouts(input_layout),
                reverse_assembly=reverse_assembly,
            )
    except OSError as e:
        raise errors.UsageError(
            f"While reading the input pdf file, " f"this error occurred:\n{e}"
        )
    return input_properties


def parse_input_layouts(input_layout: List[Tuple[int, int, int]]) -> List[Layout]:
    return [
        Layout(first_page=data[0], columns=data[1], rows=data[2])
        for data in input_layout
    ]


def parse_cli_output_data(
    output_layout_cli: str,
    print_margin: int,
    output_path: str,
) -> NobuboOutput:
    return NobuboOutput(
        output_path=pathlib.Path(output_path),
        output_pagesize=parse_output_layout(output_layout_cli, print_margin)
        if output_layout_cli
        else None,
    )


def parse_output_layout(output_layout_cli: str, print_margin: int = None) -> PageSize:
    print_size: List[int] = []
    if output_layout_cli == "a0":
        print_size = to_mm("841x1189")
    if output_layout_cli == "us":  # Arch E /Arch 6 size of 36 × 48 inches
        print_size = to_mm("914x1220")
    elif "x" in output_layout_cli:
        print_size = to_mm(output_layout_cli)

    if print_margin:
        return to_userspaceunits([size - (2 * print_margin) for size in print_size])
    else:
        return to_userspaceunits(print_size)


def page_dimensions(page: pikepdf.Page) -> Tuple[float, float]:
    """
    Calculate the x, y value for the offset in default user space units
    as defined in the pdf standard.
    :param page: A PDF page.
    :return: list with x, y value.
    """
    if not hasattr(page, "CropBox"):
        # page is of type Object, and either MediaBox, CropBox or TrimBox
        # are all of type pikepdf.objects.Object
        # they exist (or not) depending on the pdf itself
        box = page.MediaBox  # type: ignore
    else:
        box = page.CropBox  # type: ignore
    return round(float(box[2]) - float(box[0]), 2), round(
        float(box[3]) - float(box[1]), 2
    )


def to_mm(output_layout: str) -> List[int]:
    ol_in_mm = re.compile(r"\d+[x]\d+").findall(output_layout)[0].split("x")
    return [int(x) for x in ol_in_mm]


def to_userspaceunits(width_height: List[int]) -> PageSize:
    """
    Convert a page's physical width and height from millimeters to
    default user space unit, which is defined in the pdf standard as 1/72 inch.

    :param width_height: Width and height of the physical page in millimeters (mm),
    on which the pattern will be printed.
    :return: Width and height of the physical page in default user space units.
    """
    # 1 mm = 5/127 inches = 0.03937 inches;  1/72 inch = 0.013888889
    # conversion factor = 5/127 / 1/72 = 360/127 = 2.834645669
    conversion_factor = 2.834645669

    return PageSize(
        width=(round(width_height[0] * conversion_factor, 3)),
        height=(round(width_height[1] * conversion_factor, 3)),
    )
