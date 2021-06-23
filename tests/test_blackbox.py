from click.testing import CliRunner

from nobubo import cli


def test_no_overview_normal_collage(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_nooverview_8x4.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--il", "1", "8", "4",
                                      str(filepath), str(output_filepath)])
    print(result.output)
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 1

    assert pdftester.pagesize("mock_1.pdf") == [4744.61, 3354.98]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["1", "32"]


def test_no_overview_reverse_collage(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_nooverview_8x4.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--il", "1", "8", "4", "--reverse",
                                      str(filepath), str(output_filepath)])
    print(result.output)
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 1

    assert pdftester.pagesize("mock_1.pdf") == [4744.61, 3354.98]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["25", "8"]


def test_one_overview_normal_collage(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_oneoverview_8x4.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--il", "2", "8", "4",
                                      str(filepath), str(output_filepath)])
    print(result.output)
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 1

    assert pdftester.pagesize("mock_1.pdf") == [4744.61, 3354.98]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["1", "32"]


def test_one_overview_reverse_collage(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_oneoverview_8x4.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--il", "2", "8", "4", "--reverse",
                                      str(filepath), str(output_filepath)])
    print(result.output)
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 1

    assert pdftester.pagesize("mock_1.pdf") == [4744.61, 3354.98]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["25", "8"]


def test_two_overviews_normal_collage(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_twooverviews_8x4_7x3.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--il", "2", "8", "4", "--il", "35", "7", "3",
                                      str(filepath), str(output_filepath)])
    print(result.output)
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf", "mock_2.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 1
    assert pdftester.pagecount("mock_2.pdf") == 1

    assert pdftester.pagesize("mock_1.pdf") == [4744.61, 3354.98]
    assert pdftester.pagesize("mock_2.pdf") == [4151.53, 2516.23]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["1A", "32A"]
    assert pdftester.pages_order(tmp_path / "mock_2.pdf") == ["1B", "21B"]


def test_two_overviews_reverse_collage(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_twooverviews_8x4_7x3.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--il", "2", "8", "4", "--il", "35", "7", "3",
                                      "--reverse", str(filepath), str(output_filepath)])
    print(result.output)
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf", "mock_2.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 1
    assert pdftester.pagecount("mock_2.pdf") == 1

    assert pdftester.pagesize("mock_1.pdf") == [4744.61, 3354.98]
    assert pdftester.pagesize("mock_2.pdf") == [4151.53, 2516.23]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["25A", "8A"]
    assert pdftester.pages_order(tmp_path / "mock_2.pdf") == ["15B", "7B"]


def test_one_overview_normal_a0(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_oneoverview_8x4.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--il", "2", "8", "4", "--ol", "a0",
                                      str(filepath), str(output_filepath)])
    print(result.output)
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 2

    assert pdftester.pagesize("mock_1.pdf", 0) == [2381.2, 3367.56]
    assert pdftester.pagesize("mock_1.pdf", 1) == [2381.2, 3367.56]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["1", "32"]


def test_one_overview_reverse_a0(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_oneoverview_8x4.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--il", "2", "8", "4", "--ol", "a0", "--reverse",
                                      str(filepath), str(output_filepath)])
    print(result.output)
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 2

    assert pdftester.pagesize("mock_1.pdf", 0) == [2381.2, 3367.56]
    assert pdftester.pagesize("mock_1.pdf", 1) == [2381.2, 3367.56]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["25", "8"]


def test_one_overview_normal_custom(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_oneoverview_8x4.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--il", "2", "8", "4", "--ol", "920x1187",
                                      str(filepath), str(output_filepath)])
    print(result.output)
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 4

    assert pdftester.pagesize("mock_1.pdf", 0) == [2381.2, 2525.67]
    assert pdftester.pagesize("mock_1.pdf", 1) == [2381.2, 2525.67]
    assert pdftester.pagesize("mock_1.pdf", 2) == [2381.2, 841.89]
    assert pdftester.pagesize("mock_1.pdf", 3) == [2381.2, 841.89]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["1", "32"]


def test_one_overview_normal_us(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_oneoverview_8x4.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--il", "2", "8", "4", "--ol", "us",
                                      str(filepath), str(output_filepath)])
    print(result.output)
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 2

    assert pdftester.pagesize("mock_1.pdf", 0) == [2381.2, 3367.56]
    assert pdftester.pagesize("mock_1.pdf", 1) == [2381.2, 3367.56]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["1", "32"]


def test_two_overviews_normal_a0(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_twooverviews_8x4_7x3.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--il", "2", "8", "4", "--il", "35", "7",
                                      "3", "--ol", "a0",
                                      str(filepath), str(output_filepath)])
    print(result.output)
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf", "mock_2.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 2
    assert pdftester.pagecount("mock_2.pdf") == 2

    assert pdftester.pagesize("mock_1.pdf", 0) == [2381.2, 3367.56]
    assert pdftester.pagesize("mock_1.pdf", 1) == [2381.2, 3367.56]
    assert pdftester.pagesize("mock_2.pdf", 0) == [2381.2, 2525.67]
    assert pdftester.pagesize("mock_2.pdf", 1) == [1785.9, 2525.67]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["1A", "32A"]
    assert pdftester.pages_order(tmp_path / "mock_2.pdf") == ["1B", "21B"]


def test_two_overviews_reverse_a0(testdata, tmp_path, pdftester):
    filepath = testdata / "mockpattern_twooverviews_8x4_7x3.pdf"
    output_filepath = tmp_path / "mock.pdf"
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--il", "2", "8", "4", "--il", "35", "7",
                                      "3", "--ol", "a0", "--reverse",
                                      str(filepath), str(output_filepath)])
    print(result.output)
    assert result.exit_code == 0
    assert pdftester.read() == ["mock_1.pdf", "mock_2.pdf"]

    assert pdftester.pagecount("mock_1.pdf") == 2
    assert pdftester.pagecount("mock_2.pdf") == 2

    assert pdftester.pagesize("mock_1.pdf", 0) == [2381.2, 3367.56]
    assert pdftester.pagesize("mock_1.pdf", 1) == [2381.2, 3367.56]
    assert pdftester.pagesize("mock_2.pdf", 0) == [2381.2, 2525.67]
    assert pdftester.pagesize("mock_2.pdf", 1) == [1785.9, 2525.67]

    assert pdftester.pages_order(tmp_path / "mock_1.pdf") == ["25A", "8A"]
    assert pdftester.pages_order(tmp_path / "mock_2.pdf") == ["15B", "7B"]
