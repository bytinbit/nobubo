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
import PyPDF2
import pathlib
import sys

from nobubo import assembly, disassembly, pdf, calc, writer


def write_chops(pypdf2_writer: PyPDF2.PdfFileWriter, output_path: pathlib.Path):
    print("Writing file...")
    try:
        with open(output_path, "wb") as output:
            pypdf2_writer.write(output)
    except OSError as e:
        print(f"While writing the file, this error occurred:\n{e}")
        sys.exit(1)


def write_collage(temp_collage_paths: [pathlib.Path], output_properties: pdf.OutputProperties):
    for counter, collage_path in enumerate(temp_collage_paths):
        writer = PyPDF2.PdfFileWriter()
        with collage_path.open("rb") as collagefile:
            reader = PyPDF2.PdfFileReader(collagefile, strict=False)
            collage = reader.getPage(0)
            new_outputpath = calc.generate_new_outputpath(output_properties, counter)
            writer.addPage(collage)
            write_chops(writer, new_outputpath)
            print(f"Collage written to {new_outputpath}. Enjoy your sewing :)")