from progress.bar import FillingSquaresBar


class NobuboError(Exception):
    """Base class for nobubo errors."""


class NobuboBar(FillingSquaresBar):
    suffix = "assembling page %(index)d of %(max)d, %(minutes_passed)d:%(elapsed)d"
    @property
    def minutes_passed(self):
        return self.elapsed // 60