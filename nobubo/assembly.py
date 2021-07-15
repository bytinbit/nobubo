# Copyright 2021, Méline Sieber
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
import pathlib
import random
import string
import subprocess
from dataclasses import dataclass
from typing import List, Tuple

from nobubo import errors



@dataclass
class PageSize:
    """
    Page size whose width and height are in user space units.
    """
    width: float = 0
    height: float = 0


@dataclass
class Layout:
    """
    A Pattern layout.

    first_page: The number of the pdf page
    which marks the beginning of the pattern pages
    that are covered by the columns and rows.
    """
    first_page: int
    columns: int
    rows: int

class InputProperties:
    """
    Holds all information of the input pdf.
    """

    def __init__(self,
                 input_filepath: pathlib.Path,
                 number_of_pages: int,
                 pagesize: PageSize,
                 layout: List[Layout],
                 reverse_assembly: bool = False):
        self.input_filepath = input_filepath
        self.number_of_pages = number_of_pages
        self.pagesize = pagesize
        self.layout = layout
        self.reverse_assembly = reverse_assembly

    def assemble_collage(self, temp_output_dir: pathlib.Path) -> List[pathlib.Path]:
        """
        Takes a pattern pdf where one page equals a part of the pattern and
        assembles it to one huge collage.
        The default assembles it from top left to the bottom right.
        :param input_properties: Properties of the input pdf.
        :param temp_output_dir: The temporary path where all calculations should happen.
        :return A list of all the path to the collages, each with all pattern pages
                assembled on one single page.

        """
        all_collages_paths: List[pathlib.Path] = []
        for counter, current_layout in enumerate(self.layout):
            print(f"Assembling overview {counter + 1} of {len(self.layout)}\n")
            print("Creating collage... Please be patient, this may take some time.")
            all_collages_paths.append(self._assemble(temp_output_dir, current_layout))
        return all_collages_paths

    def _assemble(self,
                  temp_output_dir: pathlib.Path,
                  current_layout: Layout) -> pathlib.Path:
        collage_width = self.pagesize.width * current_layout.columns
        collage_height = self.pagesize.height * current_layout.rows

        if self.reverse_assembly:
            start, end, step = pagerange_reverse(current_layout)
            page_range_for_pdflatex = list(reversed([(x, x + current_layout.columns - 1)
                                                     for x in range(start, end, step)]))
            tuples = ["-".join(map(str, i)) for i in page_range_for_pdflatex]
            page_range = ",".join(tuples)
        else:
            begin = current_layout.first_page
            end_of_section = current_layout.columns * current_layout.rows
            end = current_layout.first_page + end_of_section - 1
            page_range = f"{begin}-{end}"

        file_content = [
            "\\batchmode\n",
            "\\documentclass[a4paper,]{article}\n",
            f"\\usepackage[papersize={{{collage_width}pt,"
            f"{collage_height}pt}}]{{geometry}}\n",
            "\\usepackage[utf8]{inputenc}\n",
            "\\usepackage{pdfpages}\n",
            "\\begin{document}\n",
            f"\\includepdfmerge[nup={current_layout.columns}x{current_layout.rows}, "
            f"noautoscale=true, scale=1.0]"
            f"{{{str(self.input_filepath)},{page_range} }}\n",
            "\\end{document}\n",
        ]

        input_filepath = temp_output_dir / "texfile.tex"
        output_filename = f"output_{random_string()}"

        with input_filepath.open("w") as f:  # pathlib has its own open method
            f.writelines(file_content)

        command = ["pdflatex",
                   "-interaction=nonstopmode",
                   f"-jobname={output_filename}",
                   f"-output-directory={temp_output_dir}",
                   str(input_filepath)]

        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise errors.UsageError("Error: pdflatex encountered a problem while "
                                    f"assembling the collage and had to abort:\n{e}")
        except FileNotFoundError as e:
            raise errors.UsageError(f"pdflatex or the output file was not found:\n{e}")

        return temp_output_dir / pathlib.Path(output_filename).with_suffix(".pdf")




def pagerange_reverse(layout: Layout) -> Tuple[int, int, int]:
    return layout.first_page, \
           layout.first_page + (layout.columns * layout.rows) - 1, \
           layout.columns


def random_string():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=7))