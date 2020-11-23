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

"""
Contains functions for various output layouts.
"""

from copy import copy
import pathlib
import subprocess

import PyPDF2

from nobubo import pdf, calc


def assemble_collage(input_properties: pdf.PDFProperties,
                     temp_output_dir: pathlib.Path) -> [pathlib.Path]:
    """
    Takes a pattern pdf where one page equals a part of the pattern and assembles it to one huge collage.
    The default assembles it from top left to the bottom right.
    :param input_properties: Properties of the input pdf.
    :param temp_output_dir: The temporary path where all calculations should happen.
    :return A list of all the path to the collages, each with all pattern pages assembled on one single page.

    """
    all_collages_paths: [pathlib.Path] = []
    for counter, layout in enumerate(input_properties.layout):
        print(f"Assembling overview {counter + 1} of {len(input_properties.layout)}\n")
        print(f"Creating collage... Please be patient, this may take some time.")
        all_collages_paths.append(_assemble(input_properties, temp_output_dir, layout))
    return all_collages_paths

def _assemble(input_properties: pdf.PDFProperties,
              temp_output_dir: pathlib.Path,
              current_layout: pdf.Layout,  # TODO: input here is 1 layout_elem, but input_property contains already list of all layout elems
              ) -> pathlib.Path:

    page_width = input_properties.pagesize.width
    page_height = input_properties.pagesize.height
    collage_width = page_width * input_properties.layout.columns
    collage_height = page_height * current_layout.rows

    if input_properties.reverse_assembly:
        start, end, step = calc.calculate_pagerange_reverse(input_properties)
        l = list(reversed([(x+1, x+current_layout.columns) for x in range(start, end, step)]))
        tuples = ["-".join(map(str, i)) for i in l]
        page_range = ",".join(tuples)
    else:
        if current_layout.overview == 0:  # file has no overview page
            page_range = f"1-{current_layout.columns*current_layout.rows}"
        else:
            begin = current_layout.overview + 1
            end = current_layout.overview + (current_layout.columns * current_layout.rows)
            page_range = f"{begin}-{end}"

    file_content = [
        "\\batchmode\n",
        "\\documentclass[a4paper,]{article}\n",
        f"\\usepackage[papersize={{{collage_width}pt,{collage_height}pt}}]{{geometry}}\n",  # include vars
        "\\usepackage[utf8]{inputenc}\n",
        "\\usepackage{pdfpages}\n",
        "\\begin{document}\n",
        f"\\includepdfmerge[nup={current_layout.columns}x{current_layout.rows}, noautoscale=true, scale=1.0]{{{str(input_properties.input_filepath)},{page_range} }}\n",
        "\\end{document}\n",
    ]

    input_filepath = temp_output_dir / "texfile.tex"
    output_filepath = temp_output_dir / "output.pdf"

    with input_filepath.open("w") as f:  # pathlib has its own open method
        f.writelines(file_content)

    command = ["pdflatex",
               "-interaction=nonstopmode",
               f"-jobname=output",
               f"-output-directory={temp_output_dir}",
               input_filepath]

    try:
        _ = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"Error while calling pdflatex:\n{e.output}")

    return output_filepath





def create_output_files(assembled_collage: PyPDF2.pdf.PageObject,
                        input_properties: pdf.PDFProperties,
                        output_layout: [int]) -> PyPDF2.PdfFileWriter:
    """
    Chops up the collage that consists of all the pattern pages to individual pages of the desired output size.
    :param assembled_collage: One pdf page that contains all assembled pattern pages.
    :param input_properties: Properties of the pdf.
    :param output_layout: The desired output layout.
    :return: The pdf with several pages, ready to write to disk.
    """
    n_up_factor = calc.calculate_nup_factors(output_layout, input_properties)
    return _chop_up(assembled_collage, input_properties, n_up_factor)


def _chop_up(assembled_collage: PyPDF2.pdf.PageObject,
             input_properties: pdf.PDFProperties,
             n_up_factor: calc.Factor) -> PyPDF2.PdfFileWriter:
    """
    Takes a collage with all assembled pattern pages, divides it up so that they fit on a previously specified page size.
    """
    # only two points are needed to be cropped, lower left (x, y) and upper right (x, y)
    lowerleft_factor = calc.Factor(x=0, y=0)
    upperright_factor = calc.Factor(x=1, y=1)

    writer = PyPDF2.PdfFileWriter()

    for x in range(0, calc.calculate_pages_needed(input_properties.layout, n_up_factor)):  # TODO FIX
        page = copy(assembled_collage)
        # cf. https://stackoverflow.com/questions/52315259/pypdf2-cant-add-multiple-cropped-pages#

        lowerleft: pdf.Point = _calculate_lowerleft_point(lowerleft_factor, n_up_factor, input_properties)
        upperright: pdf.Point = _calculate_upperright_point(upperright_factor, n_up_factor, input_properties)

        # adjust multiplying factor
        colsleft = _calculate_colsrows_left(input_properties.layout.columns, upperright_factor.x, n_up_factor.x)
        lowerleft_factor, upperright_factor = _adjust_factors(lowerleft_factor, upperright_factor, colsleft)

        page.cropBox.lowerLeft = (lowerleft.x, lowerleft.y)
        page.cropBox.upperRight = (upperright.x, upperright.y)
        writer.addPage(page)

    return writer


def _calculate_colsrows_left(layout_element: int, factor: int, nup_factor: int) -> int:
    return layout_element - (factor * nup_factor)


def _calculate_lowerleft_point(lowerleft_factor: calc.Factor,
                               n_up_factor: calc.Factor,
                               input_properties: pdf.PDFProperties) -> pdf.Point:
    return pdf.Point(x=lowerleft_factor.x * n_up_factor.x * input_properties.pagesize.width,
                     y=lowerleft_factor.y * n_up_factor.y * input_properties.pagesize.height)


def _calculate_upperright_point(upperright_factor: calc.Factor,
                                n_up_factor: calc.Factor,
                                input_properties: pdf.PDFProperties) -> pdf.Point:
    upperright = pdf.Point(x=0, y=0)
    # Manage ROWS: apply transformation to upper right, y-value
    rowsleft = _calculate_colsrows_left(input_properties.layout.rows, upperright_factor.y, n_up_factor.y)  # FIX
    if rowsleft < 0:  # end of pattern reached  (full amount of rows reached)
        upperright.y = input_properties.layout.rows * input_properties.pagesize.height
    else:
        upperright.y = upperright_factor.y * n_up_factor.y * input_properties.pagesize.height

    # Manage COLS: apply transformation to upper right, x-value
    colsleft = _calculate_colsrows_left(input_properties.layout.columns, upperright_factor.x, n_up_factor.x)  # COLS
    if colsleft > 0:  # still assembling the same horizontal line
        upperright.x = upperright_factor.x * n_up_factor.x * input_properties.pagesize.width

    else:  # end of line reached, need to go 1 row up
        if colsleft == 0:  # cols % n_up_factor == 0
            upperright.x = upperright_factor.x * n_up_factor.x * input_properties.pagesize.width
        if colsleft < 0:  # remainder pages left for COLS
            upperright.x = input_properties.layout.columns * input_properties.pagesize.width
    return upperright


def _adjust_factors(lowerleft_factor: calc.Factor, upperright_factor: calc.Factor, colsleft: int) -> (
        calc.Factor, calc.Factor):
    if colsleft > 0:  # still assembling the same horizontal line
        return _advance_horizontally(lowerleft_factor, upperright_factor)
    else:  # end of line reached, need to go 1 row up
        return _advance_vertically(lowerleft_factor, upperright_factor)


def _advance_horizontally(lowerleft_factor: calc.Factor, upperright_factor: calc.Factor) -> (
        calc.Factor, calc.Factor):
    lowerleft_factor.x += 1
    upperright_factor.x += 1
    return lowerleft_factor, upperright_factor


def _advance_vertically(lowerleft_factor: calc.Factor, upperright_factor: calc.Factor) -> (calc.Factor, calc.Factor):
    lowerleft_factor.x = 0
    lowerleft_factor.y += 1

    upperright_factor.x = 1
    upperright_factor.y += 1
    return lowerleft_factor, upperright_factor
