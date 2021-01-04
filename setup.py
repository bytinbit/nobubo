from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nobubo-bytinbit",
    version="1.1.0",
    description="Nobubo assembles a digital pdf sewing pattern and chops it into a desired output size to be printed.",
    long_description=long_description,
    long_description_content_type="text/markdown",    
    url="https://github.com/bytinbit/nobubo",
    author="Méline Sieber",
    license="AGPLv3",
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    install_requires=["click", "pikepdf"],
    classifiers=[
        "Topic :: Printing",
        "Topic :: Utilities",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "License :: OSI Approved :: GNU Affero General Public License v3",
    ],
    keywords="sewing pdf printing",
)
