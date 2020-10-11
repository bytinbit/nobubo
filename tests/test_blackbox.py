from click.testing import CliRunner
from nobubo import nobubo

# Input: 1 overview, normal, collage only
# Input: 1 overview, reversed, collage only

# Input: 1 overview, normal
# Input: 1 overview, reverse

# Input: 2 overviews, normal, collage only=> should result in 2 files

# Input: 2 overviews, reverse, collage only=> should result in 2 files
def test_two_overviews_normal(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_twooverviews_reverse.pdf"
    print(filepath)
    output_filepath = tmp_path / "mock.pdf"
    print(output_filepath)
    runner = CliRunner()
    result = runner.invoke(nobubo.main, ["--il", "1", "8", "4", "--il", "34", "7", "3", "--reverse", str(filepath), str(output_filepath)])
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf", "mock_2.pdf"]
    assert pdftester.pagecount("mock_1.pdf") == 1
    assert pdftester.pagecount("mock_2.pdf") == 1

# Input: 2 overviews, normal => should result in 2 files
# Input: 2 overviews, reverse => should result in 2 files



