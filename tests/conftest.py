import pathlib
from typing import Dict, Any, List

import pikepdf
import pytest
from pdfminer.high_level import extract_text

import nobubo.disassembly
from nobubo.assembly import NobuboInput


class PdfTester:
    def __init__(self, outputdir: pathlib.Path) -> None:
        self.outputdir = outputdir
        self.readers: Dict[str, Any] = {}  # reader for every generated pdf
        self._files: List[Any] = []  # save file objects

    def read(self):
        for filepath in self.outputdir.glob("*.pdf"):
            file = pikepdf.open(filepath)
            self._files.append(file)
            self.readers[filepath.name] = file
        return sorted(self.readers.keys())

    def pagesize(self, filename: str, pagenumber: int = 0) -> List[float]:
        reader = self.readers[filename]
        page = reader.pages[pagenumber]
        if not hasattr(page, "CropBox"):
            box = page.MediaBox
        else:
            box = page.CropBox
        return [
            round(float(box[2]) - float(box[0]), 2),
            round(float(box[3]) - float(box[1]), 2),
        ]

    def pagecount(self, filename: str) -> int:
        reader = self.readers[filename]
        return len(reader.pages)

    # requires poppler to be installed on the system too
    def pages_order(self, filepath: str) -> List[str]:
        text = extract_text(filepath, codec="utf-8").split("-")
        # remove ascii value '\f' (form feed, \x0c) indicating page break
        res = list(filter(lambda a: a not in "\x0c", text))
        # tests for the first element in the top left corner
        # and the last element in the bottom right corner
        return [res[0], res[-1]]

    def cleanup(self):
        for file in self._files:
            file.close()


@pytest.fixture
def pdftester(tmp_path):
    tester = PdfTester(tmp_path)
    yield tester
    tester.cleanup()  # executed after every test


@pytest.fixture
def testdata() -> pathlib.Path:
    return pathlib.Path(__file__).parent / "testdata"


@pytest.fixture
def pdfproperty() -> NobuboInput:
    return NobuboInput(
        input_filepath=pathlib.Path("test.pdf"),
        number_of_pages=57,
        pagesize=nobubo.assembly.PageSize(width=483.307, height=729.917),
        layout=[nobubo.assembly.Layout(first_page=2, columns=8, rows=7)],
    )
    # 8 cols, 7 rows + 1 overview page = 57
