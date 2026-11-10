from athenacli.main import is_mutating


def test_is_mutating_whitespace_only():
    assert is_mutating('   ') is False
    assert is_mutating('\t\n ') is False


def test_is_mutating_keeps_behavior():
    assert is_mutating(None) is False
    assert is_mutating('') is False
    assert is_mutating('insert into foo values (1)') is True
    assert is_mutating('SELECT * FROM foo') is False
