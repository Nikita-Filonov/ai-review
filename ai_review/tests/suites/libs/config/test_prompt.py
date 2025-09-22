from pathlib import Path

import pytest

from ai_review.libs.config.prompt import PromptConfig


def test_inline_prompt_files_or_default_uses_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    dummy_file = tmp_path / "dummy.md"
    dummy_file.write_text("DUMMY")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: dummy_file)

    config = PromptConfig()
    result = config.inline_prompt_files_or_default

    assert result == [dummy_file]
    assert config.load_inline() == ["DUMMY"]


def test_system_inline_prompts_none_returns_global(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    dummy_file = tmp_path / "global.md"
    dummy_file.write_text("GLOBAL")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: dummy_file)

    config = PromptConfig(system_inline_prompt_files=None)
    result = config.system_inline_prompt_files_or_default

    assert result == [dummy_file]
    assert config.load_system_inline() == ["GLOBAL"]


def test_system_inline_prompts_include_true(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    global_file = tmp_path / "global.md"
    global_file.write_text("GLOBAL")
    custom_file = tmp_path / "custom.md"
    custom_file.write_text("CUSTOM")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: global_file)

    config = PromptConfig(system_inline_prompt_files=[custom_file], include_inline_system_prompts=True)
    result = config.system_inline_prompt_files_or_default

    assert global_file in result and custom_file in result
    assert config.load_system_inline() == ["GLOBAL", "CUSTOM"]


def test_system_inline_prompts_include_false(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    global_file = tmp_path / "global.md"
    global_file.write_text("GLOBAL")
    custom_file = tmp_path / "custom.md"
    custom_file.write_text("CUSTOM")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: global_file)

    config = PromptConfig(system_inline_prompt_files=[custom_file], include_inline_system_prompts=False)
    result = config.system_inline_prompt_files_or_default

    assert result == [custom_file]
    assert config.load_system_inline() == ["CUSTOM"]
