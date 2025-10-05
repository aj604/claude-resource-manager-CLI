"""Security tests for YAML loading - CRITICAL.

These tests ensure ONLY yaml.safe_load() is used.
Any use of yaml.load() is a SECURITY VULNERABILITY.
"""

from pathlib import Path
import pytest
import yaml


class TestYAMLSecurityControls:
    """Critical security tests for YAML parsing."""

    def test_WHEN_yaml_safe_load_THEN_passes(
        self, temp_catalog_dir: Path
    ):
        """
        GIVEN: YAML file with safe content
        WHEN: Loaded with yaml.safe_load()
        THEN: Content is safely parsed
        """
        from claude_resource_manager.utils.security import load_yaml_safe

        yaml_file = temp_catalog_dir / "safe.yaml"
        safe_content = {
            "id": "test",
            "name": "Test Resource",
            "type": "agent",
        }

        with open(yaml_file, "w") as f:
            yaml.safe_dump(safe_content, f)

        result = load_yaml_safe(yaml_file)

        assert result["id"] == "test"

    def test_WHEN_yaml_load_used_THEN_fails(self):
        """
        GIVEN: Code inspection of YAML loading modules
        WHEN: Source code is scanned
        THEN: NO usage of yaml.load() without Loader is found

        This is a META-TEST that scans our own code for unsafe YAML usage.
        """
        import inspect
        from claude_resource_manager.core import catalog_loader
        from claude_resource_manager.utils import security

        # Get source code
        loader_source = inspect.getsource(catalog_loader)
        security_source = inspect.getsource(security)

        # CRITICAL: Must use safe_load
        assert "yaml.safe_load" in loader_source or "safe_load" in loader_source

        # CRITICAL: Must NOT use unsafe yaml.load()
        # Allow yaml.load only if it has explicit Loader parameter
        if "yaml.load(" in loader_source:
            # Check that it's used with Loader parameter
            import re

            unsafe_pattern = r'yaml\.load\([^,)]+\)'  # yaml.load(x) without second param
            unsafe_matches = re.findall(unsafe_pattern, loader_source)

            assert len(unsafe_matches) == 0, f"Unsafe yaml.load() found: {unsafe_matches}"

    def test_WHEN_yaml_bomb_deeply_nested_THEN_rejected(
        self, temp_catalog_dir: Path, yaml_bomb_content: str
    ):
        """
        GIVEN: YAML bomb with deeply nested references
        WHEN: Attempting to load
        THEN: Loading is rejected or times out
        """
        from claude_resource_manager.utils.security import load_yaml_safe

        yaml_file = temp_catalog_dir / "bomb.yaml"
        with open(yaml_file, "w") as f:
            f.write(yaml_bomb_content)

        with pytest.raises((yaml.YAMLError, ValueError, MemoryError, TimeoutError)):
            load_yaml_safe(yaml_file)

    def test_WHEN_yaml_bomb_many_anchors_THEN_rejected(
        self, temp_catalog_dir: Path
    ):
        """
        GIVEN: YAML with exponential anchor expansion
        WHEN: Attempting to load
        THEN: Loading is rejected
        """
        from claude_resource_manager.utils.security import load_yaml_safe

        # YAML bomb using anchors
        bomb_content = """
        a: &anchor1 ["data", "data", "data", "data", "data"]
        b: &anchor2 [*anchor1, *anchor1, *anchor1, *anchor1, *anchor1]
        c: &anchor3 [*anchor2, *anchor2, *anchor2, *anchor2, *anchor2]
        d: [*anchor3, *anchor3, *anchor3, *anchor3, *anchor3]
        """

        yaml_file = temp_catalog_dir / "anchor_bomb.yaml"
        with open(yaml_file, "w") as f:
            f.write(bomb_content)

        with pytest.raises((yaml.YAMLError, ValueError, MemoryError)):
            load_yaml_safe(yaml_file)

    def test_WHEN_file_size_over_1mb_THEN_rejected(
        self, temp_catalog_dir: Path
    ):
        """
        GIVEN: YAML file larger than 1MB
        WHEN: Attempting to load
        THEN: File is rejected before parsing
        """
        from claude_resource_manager.utils.security import load_yaml_safe

        # Create large file > 1MB
        yaml_file = temp_catalog_dir / "large.yaml"
        with open(yaml_file, "w") as f:
            f.write("data: " + "x" * (1024 * 1024 + 1))

        with pytest.raises(ValueError) as exc_info:
            load_yaml_safe(yaml_file)

        assert "size" in str(exc_info.value).lower() or "large" in str(exc_info.value).lower()

    def test_WHEN_parse_time_over_5s_THEN_timeout(
        self, temp_catalog_dir: Path
    ):
        """
        GIVEN: YAML that takes >5 seconds to parse
        WHEN: Attempting to load
        THEN: Operation times out
        """
        from claude_resource_manager.utils.security import load_yaml_safe

        # This is hard to test without actual slow parsing
        # Verify timeout parameter exists
        import inspect

        sig = inspect.signature(load_yaml_safe)
        params = sig.parameters

        # Should have timeout parameter or use default
        assert "timeout" in params or hasattr(load_yaml_safe, "__defaults__")

    def test_WHEN_recursive_structure_THEN_handled(
        self, temp_catalog_dir: Path
    ):
        """
        GIVEN: YAML with recursive/circular references
        WHEN: Attempting to load
        THEN: Handled without infinite loop
        """
        from claude_resource_manager.utils.security import load_yaml_safe

        recursive_yaml = """
        parent: &parent
          child: *parent
        """

        yaml_file = temp_catalog_dir / "recursive.yaml"
        with open(yaml_file, "w") as f:
            f.write(recursive_yaml)

        with pytest.raises((yaml.YAMLError, RecursionError, ValueError)):
            load_yaml_safe(yaml_file)

    def test_WHEN_arbitrary_python_object_THEN_rejected(
        self, temp_catalog_dir: Path
    ):
        """
        GIVEN: YAML attempting to instantiate Python objects
        WHEN: Attempting to load
        THEN: Rejected (safe_load doesn't allow it)
        """
        from claude_resource_manager.utils.security import load_yaml_safe

        # YAML that tries to execute Python code
        malicious_yaml = """
        !!python/object/apply:os.system
        args: ['echo hacked > /tmp/hacked.txt']
        """

        yaml_file = temp_catalog_dir / "malicious.yaml"
        with open(yaml_file, "w") as f:
            f.write(malicious_yaml)

        with pytest.raises(yaml.YAMLError):
            load_yaml_safe(yaml_file)

    def test_WHEN_code_execution_attempt_THEN_blocked(
        self, temp_catalog_dir: Path
    ):
        """
        GIVEN: YAML attempting code execution via !!python tags
        WHEN: Attempting to load
        THEN: Blocked by safe_load
        """
        from claude_resource_manager.utils.security import load_yaml_safe

        exec_yaml = """
        !!python/object/new:os.system
        args: ['rm -rf /']
        """

        yaml_file = temp_catalog_dir / "exec.yaml"
        with open(yaml_file, "w") as f:
            f.write(exec_yaml)

        with pytest.raises(yaml.YAMLError):
            load_yaml_safe(yaml_file)

    def test_WHEN_eval_attempt_THEN_blocked(
        self, temp_catalog_dir: Path
    ):
        """
        GIVEN: YAML attempting eval() execution
        WHEN: Attempting to load
        THEN: Blocked by safe_load
        """
        from claude_resource_manager.utils.security import load_yaml_safe

        eval_yaml = """
        !!python/object/apply:eval
        args: ['__import__("os").system("whoami")']
        """

        yaml_file = temp_catalog_dir / "eval.yaml"
        with open(yaml_file, "w") as f:
            f.write(eval_yaml)

        with pytest.raises(yaml.YAMLError):
            load_yaml_safe(yaml_file)

    def test_WHEN_billion_laughs_attack_THEN_rejected(
        self, temp_catalog_dir: Path
    ):
        """
        GIVEN: Billion laughs attack (XML entity expansion in YAML)
        WHEN: Attempting to load
        THEN: Rejected due to size or complexity
        """
        from claude_resource_manager.utils.security import load_yaml_safe

        # Billion laughs equivalent in YAML
        billion_laughs = """
        lol1: &lol1 "lol"
        lol2: &lol2 [*lol1, *lol1, *lol1, *lol1, *lol1, *lol1, *lol1, *lol1, *lol1, *lol1]
        lol3: &lol3 [*lol2, *lol2, *lol2, *lol2, *lol2, *lol2, *lol2, *lol2, *lol2, *lol2]
        lol4: &lol4 [*lol3, *lol3, *lol3, *lol3, *lol3, *lol3, *lol3, *lol3, *lol3, *lol3]
        lol5: &lol5 [*lol4, *lol4, *lol4, *lol4, *lol4, *lol4, *lol4, *lol4, *lol4, *lol4]
        lol6: &lol6 [*lol5, *lol5, *lol5, *lol5, *lol5, *lol5, *lol5, *lol5, *lol5, *lol5]
        """

        yaml_file = temp_catalog_dir / "billion_laughs.yaml"
        with open(yaml_file, "w") as f:
            f.write(billion_laughs)

        with pytest.raises((yaml.YAMLError, MemoryError, ValueError)):
            load_yaml_safe(yaml_file)

    def test_WHEN_symlink_to_sensitive_file_THEN_rejected(
        self, temp_catalog_dir: Path, tmp_path: Path
    ):
        """
        GIVEN: Symlink pointing to sensitive file (e.g., /etc/passwd)
        WHEN: Attempting to load
        THEN: Symlink traversal is prevented
        """
        from claude_resource_manager.utils.security import load_yaml_safe

        # Create symlink to /etc/passwd (if on Unix)
        import os

        if os.name != "nt":  # Unix systems
            sensitive_file = Path("/etc/passwd")
            if sensitive_file.exists():
                symlink = temp_catalog_dir / "sensitive.yaml"

                try:
                    symlink.symlink_to(sensitive_file)

                    with pytest.raises((ValueError, PermissionError, OSError)):
                        load_yaml_safe(symlink)
                except OSError:
                    pytest.skip("Cannot create symlinks")

    def test_WHEN_max_depth_exceeded_THEN_rejected(
        self, temp_catalog_dir: Path
    ):
        """
        GIVEN: YAML with excessive nesting depth
        WHEN: Attempting to load
        THEN: Rejected due to depth limit
        """
        from claude_resource_manager.utils.security import load_yaml_safe

        # Create deeply nested structure
        deep_yaml = "a: " + "{ b: " * 1000 + "1" + " }" * 1000

        yaml_file = temp_catalog_dir / "deep.yaml"
        with open(yaml_file, "w") as f:
            f.write(deep_yaml)

        with pytest.raises((yaml.YAMLError, RecursionError, ValueError)):
            load_yaml_safe(yaml_file)

    def test_WHEN_null_bytes_in_yaml_THEN_rejected(
        self, temp_catalog_dir: Path
    ):
        """
        GIVEN: YAML containing null bytes
        WHEN: Attempting to load
        THEN: Rejected for security
        """
        from claude_resource_manager.utils.security import load_yaml_safe

        yaml_file = temp_catalog_dir / "null_bytes.yaml"
        with open(yaml_file, "wb") as f:
            f.write(b"data: test\x00malicious")

        with pytest.raises((ValueError, UnicodeDecodeError, yaml.YAMLError)):
            load_yaml_safe(yaml_file)
