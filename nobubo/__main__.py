"""
Entry point module for the execution of `python -m nobubo`
See:
https://docs.python.org/3/using/cmdline.html#cmdoption-m
https://www.python.org/dev/peps/pep-0338/

"""
from nobubo import cli
if __name__ == '__main__':
    # https://github.com/pallets/click/issues/1399
    cli.main(prog_name="python -m nobubo")
