import attr


@attr.s
class PDFProperties:
    rows: int = attr.ib()
    columns: int = attr.ib()
    number_of_pages: int = attr.ib()
    x_offset: float = attr.ib()
    y_offset: float = attr.ib()

@attr.s
class Factor:
    x = attr.ib()
    y = attr.ib()
