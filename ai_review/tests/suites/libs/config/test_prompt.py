from pathlib import Path

import pytest

from ai_review.libs.config.prompt import PromptConfig, resolve_prompt_files, resolve_system_prompt_files


# ---------- resolve_prompt_files ----------

def test_resolve_prompt_files_returns_given_list(tmp_path: Path):
    dummy_file = tmp_path / "file.md"
    result = resolve_prompt_files([dummy_file], "default_inline.md")
    assert result == [dummy_file]


def test_resolve_prompt_files_loads_default_when_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    dummy_file = tmp_path / "inline_default.md"
    dummy_file.write_text("INLINE_DEFAULT")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: dummy_file)

    result = resolve_prompt_files(None, "default_inline.md")
    assert result == [dummy_file]


# ---------- resolve_system_prompt_files ----------

def test_resolve_system_prompt_files_none_returns_global(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    dummy_file = tmp_path / "sys.md"
    dummy_file.write_text("SYS")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: dummy_file)

    result = resolve_system_prompt_files(None, include=True, default_file="default_system_inline.md")
    assert result == [dummy_file]


def test_resolve_system_prompt_files_include_true(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    global_file = tmp_path / "global.md"
    global_file.write_text("GLOBAL")
    custom_file = tmp_path / "custom.md"
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: global_file)

    result = resolve_system_prompt_files([custom_file], include=True, default_file="default_system_inline.md")
    assert result == [global_file, custom_file]


def test_resolve_system_prompt_files_include_false(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    global_file = tmp_path / "global.md"
    global_file.write_text("GLOBAL")
    custom_file = tmp_path / "custom.md"
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: global_file)

    result = resolve_system_prompt_files([custom_file], include=False, default_file="default_system_inline.md")
    assert result == [custom_file]


# ---------- Prompts ---------

def test_load_context_prompts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    dummy_file = tmp_path / "context.md"
    dummy_file.write_text("CTX")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: dummy_file)

    config = PromptConfig()
    assert config.context_prompt_files_or_default == [dummy_file]
    assert config.load_context() == ["CTX"]


def test_load_summary_prompts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    dummy_file = tmp_path / "summary.md"
    dummy_file.write_text("SUM")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: dummy_file)

    config = PromptConfig()
    assert config.summary_prompt_files_or_default == [dummy_file]
    assert config.load_summary() == ["SUM"]


def test_load_inline_reply_prompts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    dummy_file = tmp_path / "inline_reply.md"
    dummy_file.write_text("INL_R")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: dummy_file)

    config = PromptConfig()
    assert config.inline_reply_prompt_files_or_default == [dummy_file]
    assert config.load_inline_reply() == ["INL_R"]


def test_load_summary_reply_prompts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    dummy_file = tmp_path / "summary_reply.md"
    dummy_file.write_text("SUM_R")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: dummy_file)

    config = PromptConfig()
    assert config.summary_reply_prompt_files_or_default == [dummy_file]
    assert config.load_summary_reply() == ["SUM_R"]


# ---------- Agent Prompts ----------

def test_load_agent_prompts_from_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    dummy_file = tmp_path / "agent.md"
    dummy_file.write_text("AGENT")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: dummy_file)

    config = PromptConfig()
    assert config.agent_prompt_files_or_default == [dummy_file]
    assert config.load_agent() == ["AGENT"]


def test_load_agent_prompts_from_custom_files(tmp_path: Path):
    custom_file = tmp_path / "custom_agent.md"
    custom_file.write_text("CUSTOM_AGENT")

    config = PromptConfig(agent_prompt_files=[custom_file])
    assert config.agent_prompt_files_or_default == [custom_file]
    assert config.load_agent() == ["CUSTOM_AGENT"]


# ---------- System Prompts ----------

def test_load_system_context_prompts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    dummy_file = tmp_path / "sys_context.md"
    dummy_file.write_text("SYS_CTX")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: dummy_file)

    config = PromptConfig()
    assert config.system_context_prompt_files_or_default == [dummy_file]
    assert config.load_system_context() == ["SYS_CTX"]


def test_load_system_summary_prompts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    dummy_file = tmp_path / "sys_summary.md"
    dummy_file.write_text("SYS_SUM")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: dummy_file)

    config = PromptConfig()
    assert config.system_summary_prompt_files_or_default == [dummy_file]
    assert config.load_system_summary() == ["SYS_SUM"]


def test_load_system_inline_reply_prompts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    dummy_file = tmp_path / "sys_inline_reply.md"
    dummy_file.write_text("SYS_IR")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: dummy_file)

    config = PromptConfig()
    assert config.system_inline_reply_prompt_files_or_default == [dummy_file]
    assert config.load_system_inline_reply() == ["SYS_IR"]


def test_load_system_summary_reply_prompts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    dummy_file = tmp_path / "sys_summary_reply.md"
    dummy_file.write_text("SYS_SR")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: dummy_file)

    config = PromptConfig()
    assert config.system_summary_reply_prompt_files_or_default == [dummy_file]
    assert config.load_system_summary_reply() == ["SYS_SR"]


def test_load_system_agent_prompts_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    global_file = tmp_path / "global_sys_agent.md"
    global_file.write_text("GLOBAL_SYS_AGENT")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: global_file)

    config = PromptConfig()
    assert config.system_agent_prompt_files_or_default == [global_file]
    assert config.load_system_agent() == ["GLOBAL_SYS_AGENT"]


def test_load_system_agent_prompts_include_true(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    global_file = tmp_path / "global_sys_agent.md"
    global_file.write_text("GLOBAL_SYS_AGENT")
    custom_file = tmp_path / "custom_sys_agent.md"
    custom_file.write_text("CUSTOM_SYS_AGENT")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: global_file)

    config = PromptConfig(system_agent_prompt_files=[custom_file], include_agent_system_prompts=True)
    assert config.system_agent_prompt_files_or_default == [global_file, custom_file]
    assert config.load_system_agent() == ["GLOBAL_SYS_AGENT", "CUSTOM_SYS_AGENT"]


def test_load_system_agent_prompts_include_false(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    global_file = tmp_path / "global_sys_agent.md"
    global_file.write_text("GLOBAL_SYS_AGENT")
    custom_file = tmp_path / "custom_sys_agent.md"
    custom_file.write_text("CUSTOM_SYS_AGENT")
    monkeypatch.setattr("ai_review.libs.config.prompt.load_resource", lambda **_: global_file)

    config = PromptConfig(system_agent_prompt_files=[custom_file], include_agent_system_prompts=False)
    assert config.system_agent_prompt_files_or_default == [custom_file]
    assert config.load_system_agent() == ["CUSTOM_SYS_AGENT"]
