from ai_review.services.git.tools import decode_git_output


def test_decode_git_output_decodes_utf8() -> None:
    assert decode_git_output("Привет, мир!".encode()) == "Привет, мир!"


def test_decode_git_output_replaces_invalid_utf8() -> None:
    assert decode_git_output(b"valid\x98text") == "valid\ufffdtext"


def test_decode_git_output_normalizes_crlf() -> None:
    assert decode_git_output(b"first\r\nsecond\r\n") == "first\nsecond\n"


def test_decode_git_output_preserves_standalone_carriage_return() -> None:
    assert decode_git_output(b"first\rsecond\n") == "first\rsecond\n"
