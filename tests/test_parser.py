"""Tests for alias parsing and serialization."""

from al.core.parser import Alias, parse_aliases, serialize_aliases


def test_parse_aliases_simple() -> None:
    """Test parsing a simple alias file."""
    content = """
#[main]
alias foo="echo bar"
"""
    groups = parse_aliases(content)
    assert "main" in groups
    assert len(groups["main"]) == 1
    assert groups["main"][0] == Alias(name="foo", command="echo bar", group="main")


def test_parse_aliases_grouped() -> None:
    """Test parsing an alias file with multiple groups."""
    content = """
#[dev]
alias d="docker"

#[ops]
alias k="kubectl"
"""
    groups = parse_aliases(content)
    assert "dev" in groups
    assert "ops" in groups
    assert groups["dev"][0].name == "d"
    assert groups["ops"][0].name == "k"


def test_serialize_aliases() -> None:
    """Test serializing aliases back to string."""
    groups = {
        "dev": [Alias(name="d", command="docker", group="dev")],
        "main": [Alias(name="ll", command="ls -l", group="main")],
    }
    output = serialize_aliases(groups)
    assert "#[dev]" in output
    assert 'alias d="docker"' in output
    assert "#[main]" in output
    assert 'alias ll="ls -l"' in output


def test_parse_quotes() -> None:
    """Test parsing aliases with quotes in the command."""
    content = """
#[main]
alias gitlog="git log --format='%h %s'"
"""
    groups = parse_aliases(content)
    assert groups["main"][0].command == "git log --format='%h %s'"
