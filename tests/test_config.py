"""Basic config loading tests."""
from pathlib import Path
import pytest
from kiro_multi_agent.config import load_team_config


def test_load_example_config(tmp_path: Path):
    yaml_content = """
instances:
  test-agent:
    working_directory: /tmp/test
    description: "Test agent"
    role: worker
health_port: 9999
"""
    config_file = tmp_path / "team.yaml"
    config_file.write_text(yaml_content)

    config = load_team_config(config_file)
    assert "test-agent" in config.instances
    assert config.health_port == 9999
    assert config.instances["test-agent"].role == "worker"
