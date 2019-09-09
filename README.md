# Nobubo
Digital sewing patterns are very handy: No shipping costs and cheaper than physical patterns. There is one drawback: Many digital patterns are distributed in A4 size, and it is up to the sewist to assemble them.

A jacket has around 50 A4 pages that must be glued or taped together. This usually results in an apartment covered in A4 pages and a final collage in which printer irregularities lead to ill-matching pattern lines. Many indie pattern companies already sell their digital patterns as A4 and A0 in the same pattern purchase, but there are still other companies that only provide A4.

Nobubo to the rescue! This tool assembles the pages of a digital pdf pattern and chops it into a desired output size. I developed and tested Nobubo with several download patterns from Burda, and it currently (and only) assembles A4 to fit one or more A0 pages.

## Prerequisites
* A digital pattern where each page is made to be printed on A4. If you haven't purchased a digital pattern, the tool is useless.
* Each page is cropped already, so that only the pattern is visible (no white borders around the pattern)
* At least one overview sheet that shows what the assembled pattern should look like in the end. Digital Burda patterns have it usually printed on the first page of the pattern pdf. The tool thus assumes that the overview sheet and pattern pages are all in the same pdf.
* Python 3.6

## Usage
`` 
python nobubo.py  -l OVERVIEW ROWS COLUMNS [-c] INPUTPATH OUTPUTPATH]
``

An example pattern has a 5x6 format, so 5 rows and 6 columns in the overview sheet:

```
python nobubo.py 5 6 "home/alice/patterns/jacket.pdf" "home/alice/patterns/jacket_a0.pdf" 
```
* `1` the page on which the overview sheet is located
* `5 6`: rows and columns
* `"home/alice/patterns/jacket.pdf"`: the path to the original digital pattern including filename.
* `"home/alice/patterns/jacket_a0.pdf"`: the path to the output file including filename.
* the optional `-c` flag only creates a huge collage and doesn't chop it up

In our example, the pdf has 5 rows and 6 columns. This means the final pdf collage will comprise four A0 pages to print, since 16 A4 pages fit on one A0 page. This is how the sample overview sheet might look like and how it will be split up:

<img src="img/nobubo.png" alt="sample pattern" width=50%/>

The pattern is built up from the bottom left to the upper right.

## WARNINGS
Please double-check and compare the overview sheet with the amount of pdf pages given. I had two rare cases where the overview sheet did not match the actual amount of pdf pages, e.g. the overview showed 32 A4 pages (4x8), but the actual pdf had 54 pages. Obviously, the pattern vendor did a mistake there. In one case, the final A0 output was surprisingly fine, in the other, the pages not included in the overview were not assembled properly. I have no solution to this problem (yet).

When you print the final pdf pages, please double-check and measure the control square. Don't forget to print "as is", with any scaling or fitting off.

I do not take any responsibility if Nobubo leads to ill-matching garments or any other problems whatsoever. You use this tool at your own risk. Please look at the licence if you want to improve the tool yourself.
