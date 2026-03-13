from log_parser import identify_log_level
from log_parser import count_log_levels
from log_parser import filter_lines


def test_identify_info():
    line = "2024-01-01 INFO This is an info message"
    assert identify_log_level(line) == 'INFO'


def test_identify_error():
    line = "2024-01-01 ERROR This is an error message"
    assert identify_log_level(line) == 'ERROR'


def test_identify_warning():
    line = "2024-01-01 WARNING This is a warning message"
    assert identify_log_level(line) == 'WARNING'


def test_identify_unknown():
    line = "2024-01-01 UNKNOWN This is an unknown message"
    assert identify_log_level(line) == 'UNKNOWN'


def test_count_log_levels():
    lines = [
        "2024-01-01 INFO This is an info message",
        "2024-01-01 ERROR This is an error message",
        "2024-01-01 ERROR This is another error message",
        "2024-01-01 WARNING This is a warning message",
    ]
    counts = count_log_levels(lines)
    assert counts['INFO'] == 1
    assert counts['ERROR'] == 2
    assert counts['WARNING'] == 1


def test_count_log_levels_empty():
    lines = []
    counts = count_log_levels(lines)
    assert counts['INFO'] == 0
    assert counts['ERROR'] == 0
    assert counts['WARNING'] == 0


def test_filter_lines_by_error():
    lines = [
        "2024-01-01 INFO This is an info message",
        "2024-01-01 ERROR This is an error message",
        "2024-01-01 ERROR This is another error message",
        "2024-01-01 WARNING This is a warning message",
    ]
    result = filter_lines(lines, 'ERROR')
    assert len(result) == 2


def test_filter_lines_invalid_level():
    lines = ["2024-01-01 INFO This is an info message"]
    result = filter_lines(lines, 'INVALID')
    assert result is None


def test_filter_lines_no_matches():
    lines = ["2024-01-01 INFO This is an info message"]
    result = filter_lines(lines, 'ERROR')
    assert result == []
