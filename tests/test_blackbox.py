from click.testing import CliRunner
from nobubo import nobubo

# Input: 1 overview, normal, collage only

# Input: 1 overview, reversed, collage only

# Input: 1 overview, reverse

# Input: 2 overviews, normal, collage only => should result in 2 files

# Input: 2 overviews, reverse, collage only => should result in 2 files
def test_two_overviews_reverse_collage(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_twooverviews_reverse.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(nobubo.main, ["--il", "1", "8", "4", "--il", "34", "7", "3", "--reverse", str(filepath), str(output_filepath)])
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf", "mock_2.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 1
    assert pdftester.pagecount("mock_2.pdf") == 1

    assert pdftester.pagesize("mock_1.pdf") == [4744.608, 3354.979]
    assert pdftester.pagesize("mock_2.pdf") == [4151.532, 2516.234]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["25A", "8A"]
    assert pdftester.pages_order(tmp_path / "mock_2.pdf") == ["15B", "7B"]

# Input: 2 overviews, normal => should result in 2 files
# Input: 2 overviews, reverse => should result in 2 files



