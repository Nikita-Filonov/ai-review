def decode_git_output(output: bytes) -> str:
    return output.decode("utf-8", errors="replace").replace("\r\n", "\n")
