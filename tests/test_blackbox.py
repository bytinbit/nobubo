from click.testing import CliRunner
from nobubo import nobubo


def test_no_overview_normal_collage(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_nooverview_8x4.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(nobubo.main, ["--il", "0", "8", "4", str(filepath), str(output_filepath)])
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 1

    assert pdftester.pagesize("mock_1.pdf") == [4744.608, 3354.979]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["1", "32"]


def test_no_overview_reverse_collage(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_nooverview_8x4.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(nobubo.main, ["--il", "0", "8", "4", "--reverse", str(filepath), str(output_filepath)])
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 1

    assert pdftester.pagesize("mock_1.pdf") == [4744.608, 3354.979]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["25", "8"]

def test_one_overview_normal_collage(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_oneoverview_8x4.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(nobubo.main, ["--il", "1", "8", "4", str(filepath), str(output_filepath)])
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 1

    assert pdftester.pagesize("mock_1.pdf") == [4744.608, 3354.979]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["1", "32"]


def test_one_overview_reverse_collage(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_oneoverview_8x4.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(nobubo.main, ["--il", "1", "8", "4", "--reverse", str(filepath), str(output_filepath)])
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 1

    assert pdftester.pagesize("mock_1.pdf") == [4744.608, 3354.979]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["25", "8"]


def test_two_overviews_normal_collage(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_twooverviews_8x4_7x3.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(nobubo.main, ["--il", "1", "8", "4", "--il", "34", "7", "3", str(filepath), str(output_filepath)])
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf", "mock_2.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 1
    assert pdftester.pagecount("mock_2.pdf") == 1

    assert pdftester.pagesize("mock_1.pdf") == [4744.608, 3354.979]
    assert pdftester.pagesize("mock_2.pdf") == [4151.532, 2516.234]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["1A", "32A"]
    assert pdftester.pages_order(tmp_path / "mock_2.pdf") == ["1B", "21B"]


def test_two_overviews_reverse_collage(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_twooverviews_8x4_7x3.pdf"
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


# 1 overview, normal, output a0
def test_one_overview_normal_a0(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_oneoverview_8x4.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(nobubo.main, ["--il", "1", "8", "4", "--ol", "a0", str(filepath), str(output_filepath)])
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 2

    assert pdftester.pagesize("mock_1.pdf", 0) == [2381.2, 3367.56]
    assert pdftester.pagesize("mock_1.pdf", 1) == [2381.2, 3367.56]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["1", "32"]
    # TODO check size of each page - how



# 1 overview, reverse



# Input: 2 overviews, normal => should result in 2 files

# Input: 2 overviews, reverse => should result in 2 files



