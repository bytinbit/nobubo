from click.testing import CliRunner
from nobubo import nobubo

# Input: 1 overview, normal, collage only
# Input: 1 overview, reversed, collage only

# Input: 1 overview, normal
# Input: 1 overview, reverse

# Input: 2 overviews, normal, collage only=> should result in 2 files

# Input: 2 overviews, reverse, collage only=> should result in 2 files
def test_two_overviews_normal(testdata, tmp_path):
    filepath = testdata / "mock_pattern.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(nobubo.main, ["--il", "1", "8", "4", "--il", "34", "7", "3", "--reverse", str(filepath), str(output_filepath)])
    assert result.exit_code == 0
    assert False, output_filepath


# Input: 2 overviews, normal => should result in 2 files
# Input: 2 overviews, reverse => should result in 2 files



