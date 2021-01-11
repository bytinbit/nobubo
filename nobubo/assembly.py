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
import subprocess

from nobubo import core, calc


def assemble_collage(input_properties: core.InputProperties,
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


def _assemble(input_properties: core.InputProperties,
              temp_output_dir: pathlib.Path,
              current_layout: core.Layout) -> pathlib.Path:

    collage_width = input_properties.pagesize.width * current_layout.columns
    collage_height = input_properties.pagesize.height * current_layout.rows

    if input_properties.reverse_assembly:
        start, end, step = calc.calculate_pagerange_reverse(current_layout)
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
        f"\\usepackage[papersize={{{collage_width}pt,{collage_height}pt}}]{{geometry}}\n",
        "\\usepackage[utf8]{inputenc}\n",
        "\\usepackage{pdfpages}\n",
        "\\begin{document}\n",
        f"\\includepdfmerge[nup={current_layout.columns}x{current_layout.rows}, noautoscale=true, scale=1.0]{{{str(input_properties.input_filepath)},{page_range} }}\n",
        "\\end{document}\n",
    ]

    input_filepath = temp_output_dir / "texfile.tex"
    output_filename = f"output_{calc.generate_random_string()}"

    with input_filepath.open("w") as f:  # pathlib has its own open method
        f.writelines(file_content)

    command = ["pdflatex",
               "-interaction=nonstopmode",
               f"-jobname={output_filename}",
               f"-output-directory={temp_output_dir}",
               input_filepath]

    try:
        _ = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"Error while calling pdflatex:\n{e.output}")

    return temp_output_dir / pathlib.Path(output_filename).with_suffix(".pdf")






