# Nobubo
Digital sewing patterns are very handy: No shipping costs and cheaper than physical patterns. There is one drawback: Many digital patterns are distributed in A4 size, and it is up to the sewist to assemble it.

A jacket has around 50 A4 pages that must be glued or taped together. This usually results in an apartment covered in A4 pages and a final collage in which printer irregularities lead to ill-matching pattern lines. Many indie pattern companies manage to sell their digital patterns as A4 and A0 in the same purchase, but there are some that still only sell A4.

Nobubo to the rescue! This tool assembles the pages of a digital pdf pattern and chops it into a desired output size. I developed and tested Nobubo with download patterns from Burda, and it currently (and only) assembles A4 to fit one or more A0 pages.

## Prerequisites
* A digital pattern where each page is fit for A4
* Each page is cropped so that only the pattern is visible (no border)
* an overview sheet that shows what the assembled pattern should look like in the end
* some version of Python 3

## Usage Example:
Mock overview sheet:

< SAMPLE IMAGE>

This pattern has a 5x6 format, so 5 rows and 6 columns. This means the final pdf collage will comprise four A0 pages to print, since 16 A4 pages fit on one A0 page.

Command example: 
```
python nobubo.py 5 6 "home/alice/patterns/jacket.pdf" "home/alice/patterns/jacket_a0.pdf" 
```
* `5 6` denote rows and columns
* `"home/alice/patterns/jacket.pdf"` denotes the path to the original digital pattern
* `"home/alice/patterns/jacket_a0.pdf"` denotes the path and name to the final collage


