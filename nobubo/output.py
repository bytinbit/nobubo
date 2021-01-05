# Copyright 2020, Méline Sieber
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
from pikepdf import Pdf
import pathlib
import sys

from nobubo import core, calc


def write_chops(collage: Pdf, output_path: pathlib.Path):
    print("Writing file...")
    try:
        collage.save(output_path)
    except OSError as e:
        print(f"While writing the file, this error occurred:\n{e}")
        sys.exit(1)


def write_collage(temp_collage_paths: [pathlib.Path], output_properties: core.OutputProperties):
    for counter, collage_path in enumerate(temp_collage_paths):
        new_outputpath = calc.generate_new_outputpath(output_properties.output_path, counter)
        temp_collage = Pdf.open(collage_path)
        temp_collage.save(new_outputpath)
        print(f"Collage written to {new_outputpath}. Enjoy your sewing :)")