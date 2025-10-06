"""Security tests for path validation - CRITICAL.

These tests prevent path traversal attacks.
All paths must stay within ~/.claude/ directory.
"""

from pathlib import Path

import pytest

from claude_resource_manager.utils.security import SecurityError, validate_install_path


class TestPathSecurityControls:
    """Critical security tests for path validation."""

    def test_WHEN_path_traversal_attempt_THEN_blocked(
        self, temp_install_dir: Path, path_traversal_attempts: list
    ):
        """
        GIVEN: Various path traversal attack vectors
        WHEN: Path validation is performed
        THEN: All attempts are blocked
        """

        for malicious_path in path_traversal_attempts:
            with pytest.raises((ValueError, SecurityError)) as exc_info:
                validate_install_path(malicious_path, temp_install_dir)

            assert (
                "traversal" in str(exc_info.value).lower()
                or "invalid" in str(exc_info.value).lower()
                or "path" in str(exc_info.value).lower()
            )

    def test_WHEN_absolute_path_outside_base_THEN_blocked(self, temp_install_dir: Path):
        """
        GIVEN: Absolute path outside base directory
        WHEN: Path validation is performed
        THEN: Path is rejected
        """

        malicious_paths = [
            "/etc/passwd",
            "/tmp/malicious.sh",
            "/Users/other/sensitive.txt",
            "C:\\Windows\\System32\\config",
        ]

        for path in malicious_paths:
            with pytest.raises((ValueError, SecurityError)):
                validate_install_path(path, temp_install_dir)

    def test_WHEN_symlink_escape_THEN_blocked(self, temp_install_dir: Path, tmp_path: Path):
        """
        GIVEN: Symlink pointing outside base directory
        WHEN: Path resolution is performed
        THEN: Symlink escape is detected and blocked
        """
        import os

        if os.name != "nt":  # Unix systems
            # Create symlink pointing outside
            outside_dir = tmp_path / "outside"
            outside_dir.mkdir()

            symlink = temp_install_dir / "agents" / "escape_link"

            try:
                symlink.parent.mkdir(exist_ok=True)
                symlink.symlink_to(outside_dir)

                with pytest.raises((ValueError, SecurityError)):
                    validate_install_path(symlink, temp_install_dir)
            except OSError:
                pytest.skip("Cannot create symlinks")

    def test_WHEN_valid_path_THEN_allowed(self, temp_install_dir: Path):
        """
        GIVEN: Valid path within base directory
        WHEN: Path validation is performed
        THEN: Path is allowed
        """

        valid_paths = [
            "agents/architect.md",
            "commands/review.md",
            "hooks/pre-commit.sh",
            "templates/readme.md",
        ]

        for path in valid_paths:
            result = validate_install_path(path, temp_install_dir)
            assert result.is_relative_to(temp_install_dir)

    def test_WHEN_install_path_normalized_THEN_safe(self, temp_install_dir: Path):
        """
        GIVEN: Path with redundant elements (., .., etc.)
        WHEN: Path is normalized
        THEN: Resolved path is safe and within base
        """

        paths_to_normalize = [
            "agents/./architect.md",  # Redundant .
            "agents/../agents/architect.md",  # Redundant ..
            "agents/subdir/../architect.md",  # Redundant traversal
        ]

        for path in paths_to_normalize:
            result = validate_install_path(path, temp_install_dir)
            assert result.is_relative_to(temp_install_dir)
            assert ".." not in str(result)

    def test_WHEN_dot_dot_in_path_THEN_rejected(self, temp_install_dir: Path):
        """
        GIVEN: Path containing .. that escapes base
        WHEN: Path validation is performed
        THEN: Path is rejected
        """

        malicious_paths = [
            "../../etc/passwd",
            "agents/../../secret.txt",
            "agents/../../../root/.ssh/id_rsa",
        ]

        for path in malicious_paths:
            with pytest.raises((ValueError, SecurityError)):
                validate_install_path(path, temp_install_dir)

    def test_WHEN_null_byte_in_path_THEN_rejected(self, temp_install_dir: Path):
        """
        GIVEN: Path containing null byte
        WHEN: Path validation is performed
        THEN: Path is rejected (null byte injection attack)
        """

        malicious_paths = [
            "agents/test\x00.md",
            "agents/\x00../../etc/passwd",
        ]

        for path in malicious_paths:
            with pytest.raises((ValueError, SecurityError)):
                validate_install_path(path, temp_install_dir)

    def test_WHEN_windows_path_on_unix_THEN_handled(self, temp_install_dir: Path):
        """
        GIVEN: Windows-style path on Unix system
        WHEN: Path validation is performed
        THEN: Path is correctly handled or rejected
        """
        import os

        if os.name != "nt":  # Unix system
            windows_paths = [
                "C:\\Users\\test\\file.txt",
                "..\\..\\..\\etc\\passwd",
                "agents\\..\\..\\sensitive",
            ]

            for path in windows_paths:
                with pytest.raises((ValueError, SecurityError)):
                    validate_install_path(path, temp_install_dir)

    def test_WHEN_relative_path_THEN_resolved_safely(self, temp_install_dir: Path):
        """
        GIVEN: Relative path
        WHEN: Path is resolved
        THEN: Resolved to absolute path within base
        """

        relative_path = "agents/architect.md"

        result = validate_install_path(relative_path, temp_install_dir)

        assert result.is_absolute()
        assert result.is_relative_to(temp_install_dir)

    def test_WHEN_hidden_files_THEN_allowed_in_base(self, temp_install_dir: Path):
        """
        GIVEN: Path to hidden file (starting with .)
        WHEN: File is within base directory
        THEN: Path is allowed
        """

        hidden_paths = [
            ".clauderc",
            "agents/.config.yaml",
        ]

        for path in hidden_paths:
            result = validate_install_path(path, temp_install_dir)
            assert result.is_relative_to(temp_install_dir)

    def test_WHEN_case_sensitivity_exploited_THEN_blocked(self, temp_install_dir: Path):
        """
        GIVEN: Path using case sensitivity to bypass checks
        WHEN: Path validation is performed
        THEN: Case variations are handled correctly
        """

        # On case-insensitive systems, these could be problematic
        case_paths = [
            "AGENTS/../../../etc/passwd",
            "Agents/../../secret.txt",
        ]

        for path in case_paths:
            with pytest.raises((ValueError, SecurityError)):
                validate_install_path(path, temp_install_dir)

    def test_WHEN_long_path_THEN_handled(self, temp_install_dir: Path):
        """
        GIVEN: Very long path (potential DoS)
        WHEN: Path validation is performed
        THEN: Path is handled or rejected gracefully
        """

        # Create very long path
        long_path = "agents/" + ("a" * 10000) + ".md"

        # Should either validate or reject gracefully
        try:
            result = validate_install_path(long_path, temp_install_dir)
            assert result.is_relative_to(temp_install_dir)
        except (ValueError, OSError):
            pass  # Acceptable to reject

    def test_WHEN_special_device_files_THEN_rejected(self, temp_install_dir: Path):
        """
        GIVEN: Path to special device files
        WHEN: Path validation is performed
        THEN: Device files are rejected
        """
        import os

        if os.name != "nt":  # Unix systems
            device_files = [
                "/dev/null",
                "/dev/random",
                "/dev/urandom",
            ]

            for path in device_files:
                with pytest.raises((ValueError, SecurityError)):
                    validate_install_path(path, temp_install_dir)

    def test_WHEN_unicode_normalization_attack_THEN_blocked(self, temp_install_dir: Path):
        """
        GIVEN: Path with Unicode characters that normalize differently
        WHEN: Path validation is performed
        THEN: Normalization attacks are prevented
        """

        # Unicode characters that normalize to .. (path traversal)
        unicode_paths = [
            "agents/\ufe52\ufe52/secret.txt",  # Small full stop (normalizes to ..)
            "agents/\uff0e\uff0e/secret.txt",  # Full-width dots (normalizes to ..)
        ]

        for path in unicode_paths:
            with pytest.raises((ValueError, SecurityError)):
                validate_install_path(path, temp_install_dir)

    def test_WHEN_double_encoding_attack_THEN_blocked(self, temp_install_dir: Path):
        """
        GIVEN: Path with double-encoded characters
        WHEN: Path validation is performed
        THEN: Double-encoding bypass is prevented
        """

        encoded_paths = [
            "agents/%252e%252e/secret.txt",  # Double URL encoded ../
            "agents/..%2F..%2Fetc%2Fpasswd",  # Mixed encoding
        ]

        for path in encoded_paths:
            # Should reject or safely decode
            try:
                result = validate_install_path(path, temp_install_dir)
                assert result.is_relative_to(temp_install_dir)
            except (ValueError, SecurityError):
                pass  # Acceptable to reject
