"""Comprehensive integration tests for VHS documentation system.

This module tests the end-to-end VHS (Video Handshake) terminal recording system
that generates animated GIF documentation. Tests cover:

- Tape file execution (.tape scripts)
- GIF output generation and validation
- Demo quality (timing, dimensions, file size)
- Makefile integration targets
- Visual regression testing

Test Coverage: 15 tests
Strategy: RED phase - All tests will FAIL until VHS demos are implemented

VHS Documentation: https://github.com/charmbracelet/vhs
Expected Structure:
    demo/
    ├── quick-start.tape
    ├── fuzzy-search.tape
    ├── multi-select.tape
    ├── categories.tape
    ├── help-system.tape
    └── output/
        ├── quick-start.gif
        ├── fuzzy-search.gif
        ├── multi-select.gif
        ├── categories.gif
        └── help-system.gif

Author: TestMaster (TDD Phase)
"""

import subprocess
from pathlib import Path

import pytest

# Skip all tests if VHS not installed
VHS_INSTALLED = subprocess.run(["which", "vhs"], capture_output=True, text=True).returncode == 0

pytestmark = pytest.mark.skipif(
    not VHS_INSTALLED, reason="VHS not installed. Install with: brew install vhs"
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def demo_dir(project_root: Path) -> Path:
    """Get demo directory path."""
    return project_root / "demo"


@pytest.fixture
def output_dir(demo_dir: Path) -> Path:
    """Get demo output directory path."""
    return demo_dir / "output"


@pytest.fixture
def tape_files() -> dict[str, str]:
    """Map of demo names to tape file names."""
    return {
        "quick-start": "quick-start.tape",
        "fuzzy-search": "fuzzy-search.tape",
        "multi-select": "multi-select.tape",
        "categories": "categories.tape",
        "help-system": "help-system.tape",
    }


@pytest.fixture
def expected_gifs() -> dict[str, str]:
    """Map of demo names to expected GIF output files."""
    return {
        "quick-start": "quick-start.gif",
        "fuzzy-search": "fuzzy-search.gif",
        "multi-select": "multi-select.gif",
        "categories": "categories.gif",
        "help-system": "help-system.gif",
    }


# ============================================================================
# Tape File Execution Tests (5 tests)
# ============================================================================


class TestVHSTapeExecution:
    """Tests for .tape file execution and VHS integration."""

    @pytest.mark.integration
    def test_WHEN_quick_start_tape_executes_THEN_succeeds(
        self, demo_dir: Path, tape_files: dict[str, str]
    ):
        """Quick start demo tape should execute without errors.

        Behavior:
        - VHS processes quick-start.tape successfully
        - Returns exit code 0 (success)
        - No error output to stderr
        """
        # Arrange
        tape_file = demo_dir / tape_files["quick-start"]

        # Act
        result = subprocess.run(
            ["vhs", str(tape_file)], capture_output=True, text=True, timeout=180  # 180 second timeout
        )

        # Assert
        assert result.returncode == 0, (
            f"VHS execution failed for quick-start.tape\n"
            f"STDERR: {result.stderr}\n"
            f"STDOUT: {result.stdout}"
        )

    @pytest.mark.integration
    def test_WHEN_fuzzy_search_tape_executes_THEN_succeeds(
        self, demo_dir: Path, tape_files: dict[str, str]
    ):
        """Fuzzy search demo tape should execute without errors.

        Behavior:
        - VHS processes fuzzy-search.tape successfully
        - Demonstrates fuzzy matching capabilities
        - Returns exit code 0
        """
        # Arrange
        tape_file = demo_dir / tape_files["fuzzy-search"]

        # Act
        result = subprocess.run(["vhs", str(tape_file)], capture_output=True, text=True, timeout=180)

        # Assert
        assert result.returncode == 0, (
            f"VHS execution failed for fuzzy-search.tape\n" f"STDERR: {result.stderr}"
        )

    @pytest.mark.integration
    def test_WHEN_multi_select_tape_executes_THEN_succeeds(
        self, demo_dir: Path, tape_files: dict[str, str]
    ):
        """Multi-select demo tape should execute without errors.

        Behavior:
        - VHS processes multi-select.tape successfully
        - Demonstrates batch selection with checkboxes
        - Returns exit code 0
        """
        # Arrange
        tape_file = demo_dir / tape_files["multi-select"]

        # Act
        result = subprocess.run(["vhs", str(tape_file)], capture_output=True, text=True, timeout=180)

        # Assert
        assert result.returncode == 0, (
            f"VHS execution failed for multi-select.tape\n" f"STDERR: {result.stderr}"
        )

    @pytest.mark.integration
    def test_WHEN_categories_tape_executes_THEN_succeeds(
        self, demo_dir: Path, tape_files: dict[str, str]
    ):
        """Categories demo tape should execute without errors.

        Behavior:
        - VHS processes categories.tape successfully
        - Demonstrates category filtering
        - Returns exit code 0
        """
        # Arrange
        tape_file = demo_dir / tape_files["categories"]

        # Act
        result = subprocess.run(["vhs", str(tape_file)], capture_output=True, text=True, timeout=180)

        # Assert
        assert result.returncode == 0, (
            f"VHS execution failed for categories.tape\n" f"STDERR: {result.stderr}"
        )

    @pytest.mark.integration
    def test_WHEN_help_system_tape_executes_THEN_succeeds(
        self, demo_dir: Path, tape_files: dict[str, str]
    ):
        """Help system demo tape should execute without errors.

        Behavior:
        - VHS processes help-system.tape successfully
        - Demonstrates keybindings and help modal
        - Returns exit code 0
        """
        # Arrange
        tape_file = demo_dir / tape_files["help-system"]

        # Act
        result = subprocess.run(["vhs", str(tape_file)], capture_output=True, text=True, timeout=180)

        # Assert
        assert result.returncode == 0, (
            f"VHS execution failed for help-system.tape\n" f"STDERR: {result.stderr}"
        )


# ============================================================================
# GIF Output Tests (5 tests)
# ============================================================================


class TestVHSGifOutput:
    """Tests for generated GIF files and output validation."""

    @pytest.mark.integration
    def test_WHEN_tape_executes_THEN_gif_created(
        self,
        demo_dir: Path,
        output_dir: Path,
        tape_files: dict[str, str],
        expected_gifs: dict[str, str],
    ):
        """VHS should create GIF output file after tape execution.

        Behavior:
        - Each .tape file generates corresponding .gif
        - GIF files created in demo/output/ directory
        - Files are non-empty (size > 0)
        """
        # Arrange
        tape_file = demo_dir / tape_files["quick-start"]
        expected_gif = output_dir / expected_gifs["quick-start"]

        # Act
        subprocess.run(["vhs", str(tape_file)], check=True, timeout=180)

        # Assert
        assert expected_gif.exists(), (
            f"GIF output file not created: {expected_gif}\n"
            f"Expected location: demo/output/quick-start.gif"
        )
        assert expected_gif.stat().st_size > 0, "GIF file should not be empty"

    @pytest.mark.integration
    def test_WHEN_tape_executes_THEN_gif_under_2mb(
        self,
        demo_dir: Path,
        output_dir: Path,
        tape_files: dict[str, str],
        expected_gifs: dict[str, str],
    ):
        """Individual GIF files should be under 2MB for web performance.

        Behavior:
        - Each demo GIF < 2MB for fast loading
        - Optimized for README embedding
        - Maintains quality while minimizing size
        """
        # Arrange
        tape_file = demo_dir / tape_files["quick-start"]
        expected_gif = output_dir / expected_gifs["quick-start"]

        # Act
        subprocess.run(["vhs", str(tape_file)], check=True, timeout=180)

        # Assert
        file_size_mb = expected_gif.stat().st_size / (1024 * 1024)
        assert file_size_mb < 2.0, (
            f"GIF file too large: {file_size_mb:.2f}MB\n" f"Expected: < 2.0MB for web performance"
        )

    @pytest.mark.integration
    def test_WHEN_tape_executes_THEN_gif_correct_dimensions(
        self,
        demo_dir: Path,
        output_dir: Path,
        tape_files: dict[str, str],
        expected_gifs: dict[str, str],
    ):
        """GIF should have correct dimensions (1000x600) for consistency.

        Behavior:
        - Standard terminal size: 1000x600 pixels
        - Matches VHS Set Width/Height directives
        - Consistent aspect ratio across all demos

        Note: Requires Pillow (PIL) library
        """
        pytest.importorskip("PIL", reason="Pillow required for GIF dimension validation")
        from PIL import Image

        # Arrange
        tape_file = demo_dir / tape_files["quick-start"]
        expected_gif = output_dir / expected_gifs["quick-start"]

        # Act
        subprocess.run(["vhs", str(tape_file)], check=True, timeout=180)

        # Assert
        with Image.open(expected_gif) as img:
            width, height = img.size
            assert width == 1000, f"Expected width 1000px, got {width}px"
            assert height == 600, f"Expected height 600px, got {height}px"

    @pytest.mark.integration
    def test_WHEN_all_tapes_execute_THEN_total_size_under_10mb(
        self,
        demo_dir: Path,
        output_dir: Path,
        tape_files: dict[str, str],
        expected_gifs: dict[str, str],
    ):
        """Total size of all GIF demos should be under 10MB.

        Behavior:
        - All 5 demos combined < 10MB
        - Keeps repository size reasonable
        - Fast clone times for users
        """
        # Arrange & Act
        total_size_bytes = 0
        for demo_name, tape_file_name in tape_files.items():
            tape_file = demo_dir / tape_file_name
            subprocess.run(["vhs", str(tape_file)], check=True, timeout=180)

            gif_file = output_dir / expected_gifs[demo_name]
            if gif_file.exists():
                total_size_bytes += gif_file.stat().st_size

        # Assert
        total_size_mb = total_size_bytes / (1024 * 1024)
        assert total_size_mb < 10.0, (
            f"Total GIF size too large: {total_size_mb:.2f}MB\n"
            f"Expected: < 10.0MB for repository health"
        )

    @pytest.mark.integration
    def test_WHEN_gif_exists_THEN_readable_by_pillow(
        self,
        demo_dir: Path,
        output_dir: Path,
        tape_files: dict[str, str],
        expected_gifs: dict[str, str],
    ):
        """Generated GIF should be valid and readable by image libraries.

        Behavior:
        - GIF format is valid and not corrupted
        - Can be opened by PIL/Pillow
        - Has animation frames (> 1 frame)

        Note: Requires Pillow (PIL) library
        """
        pytest.importorskip("PIL", reason="Pillow required for GIF validation")
        from PIL import Image

        # Arrange
        tape_file = demo_dir / tape_files["quick-start"]
        expected_gif = output_dir / expected_gifs["quick-start"]

        # Act
        subprocess.run(["vhs", str(tape_file)], check=True, timeout=180)

        # Assert
        with Image.open(expected_gif) as img:
            assert img.format == "GIF", f"Expected GIF format, got {img.format}"

            # Check for animation (GIFs should have multiple frames)
            frame_count = 0
            try:
                while True:
                    img.seek(frame_count)
                    frame_count += 1
            except EOFError:
                pass  # End of frames

            assert frame_count > 1, f"GIF should be animated (>1 frame), got {frame_count} frame(s)"


# ============================================================================
# Demo Quality Tests (3 tests)
# ============================================================================


class TestDemoQuality:
    """Tests for demo timing, quality, and user experience."""

    @pytest.mark.integration
    def test_WHEN_quick_start_demo_THEN_duration_30_seconds(
        self,
        demo_dir: Path,
        output_dir: Path,
        tape_files: dict[str, str],
        expected_gifs: dict[str, str],
    ):
        """Quick start demo should be ~30 seconds for comprehensive overview.

        Behavior:
        - Duration: 25-35 seconds (allows 5s tolerance)
        - Covers: launch, search, install workflow
        - Paced for comfortable viewing

        Note: Requires Pillow (PIL) library to read GIF duration
        """
        pytest.importorskip("PIL", reason="Pillow required for GIF duration validation")
        from PIL import Image

        # Arrange
        tape_file = demo_dir / tape_files["quick-start"]
        expected_gif = output_dir / expected_gifs["quick-start"]

        # Act
        subprocess.run(["vhs", str(tape_file)], check=True, timeout=180)

        # Assert
        with Image.open(expected_gif) as img:
            # Calculate total duration from all frames
            total_duration_ms = 0
            frame_count = 0

            try:
                while True:
                    img.seek(frame_count)
                    # Get duration of current frame (in milliseconds)
                    duration = img.info.get("duration", 100)  # Default 100ms if not set
                    total_duration_ms += duration
                    frame_count += 1
            except EOFError:
                pass  # End of frames

            total_duration_sec = total_duration_ms / 1000.0

            # Allow 25-35 second range (30 ± 5 seconds)
            assert 25.0 <= total_duration_sec <= 35.0, (
                f"Quick start demo duration out of range: {total_duration_sec:.1f}s\n"
                f"Expected: 25-35 seconds for comprehensive overview"
            )

    @pytest.mark.integration
    @pytest.mark.slow
    def test_WHEN_feature_demos_THEN_duration_20_seconds(
        self,
        demo_dir: Path,
        output_dir: Path,
        tape_files: dict[str, str],
        expected_gifs: dict[str, str],
    ):
        """Feature-specific demos should be ~20 seconds each.

        Behavior:
        - Duration: 15-25 seconds per demo (allows 5s tolerance)
        - Focused on single feature demonstration
        - Applies to: fuzzy-search, multi-select, categories, help-system

        Note: Requires Pillow (PIL) library to read GIF duration
        """
        pytest.importorskip("PIL", reason="Pillow required for GIF duration validation")
        from PIL import Image

        # Test each feature demo (excluding quick-start)
        feature_demos = ["fuzzy-search", "multi-select", "categories", "help-system"]

        for demo_name in feature_demos:
            # Arrange
            tape_file = demo_dir / tape_files[demo_name]
            expected_gif = output_dir / expected_gifs[demo_name]

            # Act
            subprocess.run(["vhs", str(tape_file)], check=True, timeout=180)

            # Assert
            with Image.open(expected_gif) as img:
                total_duration_ms = 0
                frame_count = 0

                try:
                    while True:
                        img.seek(frame_count)
                        duration = img.info.get("duration", 100)
                        total_duration_ms += duration
                        frame_count += 1
                except EOFError:
                    pass

                total_duration_sec = total_duration_ms / 1000.0

                # Allow 15-25 second range (20 ± 5 seconds)
                assert 15.0 <= total_duration_sec <= 25.0, (
                    f"{demo_name} demo duration out of range: {total_duration_sec:.1f}s\n"
                    f"Expected: 15-25 seconds for focused feature demo"
                )

    @pytest.mark.integration
    @pytest.mark.slow
    def test_WHEN_demo_plays_THEN_all_frames_valid(
        self,
        demo_dir: Path,
        output_dir: Path,
        tape_files: dict[str, str],
        expected_gifs: dict[str, str],
    ):
        """All frames in demo GIFs should be valid and non-corrupted.

        Behavior:
        - Every frame can be read without errors
        - No corrupted or missing frames
        - Smooth playback experience

        Note: Requires Pillow (PIL) library
        """
        pytest.importorskip("PIL", reason="Pillow required for frame validation")
        from PIL import Image

        # Arrange
        tape_file = demo_dir / tape_files["quick-start"]
        expected_gif = output_dir / expected_gifs["quick-start"]

        # Act
        subprocess.run(["vhs", str(tape_file)], check=True, timeout=180)

        # Assert
        with Image.open(expected_gif) as img:
            frame_count = 0
            corrupted_frames = []

            try:
                while True:
                    try:
                        img.seek(frame_count)
                        # Try to load frame data to verify it's not corrupted
                        _ = img.load()
                        frame_count += 1
                    except Exception as e:
                        corrupted_frames.append((frame_count, str(e)))
                        frame_count += 1
            except EOFError:
                pass  # End of frames reached normally

            assert len(corrupted_frames) == 0, (
                f"Found {len(corrupted_frames)} corrupted frame(s):\n" f"{corrupted_frames}"
            )
            assert frame_count > 0, "GIF should contain at least one frame"


# ============================================================================
# Makefile Integration Tests (2 tests)
# ============================================================================


class TestMakefileIntegration:
    """Tests for Makefile targets that orchestrate VHS demos."""

    @pytest.mark.integration
    def test_WHEN_make_demos_THEN_all_gifs_generated(
        self, project_root: Path, output_dir: Path, expected_gifs: dict[str, str]
    ):
        """Running 'make demos' should generate all GIF files.

        Behavior:
        - Executes all .tape files in correct order
        - Generates all 5 GIF outputs
        - Creates output directory if needed
        - Completes successfully (exit code 0)
        """
        # Arrange
        # Clean output directory first
        if output_dir.exists():
            for gif_file in output_dir.glob("*.gif"):
                gif_file.unlink()

        # Act
        result = subprocess.run(
            ["make", "demos"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout for all demos
        )

        # Assert
        assert result.returncode == 0, (
            f"'make demos' failed\n" f"STDERR: {result.stderr}\n" f"STDOUT: {result.stdout}"
        )

        # Verify all GIFs were created
        for demo_name, gif_name in expected_gifs.items():
            gif_path = output_dir / gif_name
            assert gif_path.exists(), f"Expected GIF not created: {gif_name}\n" f"Demo: {demo_name}"

    @pytest.mark.integration
    def test_WHEN_make_demo_clean_THEN_output_removed(
        self,
        project_root: Path,
        output_dir: Path,
        demo_dir: Path,
        tape_files: dict[str, str],
        expected_gifs: dict[str, str],
    ):
        """Running 'make demo-clean' should remove generated GIFs.

        Behavior:
        - Removes all GIF files from output directory
        - Optionally removes output directory itself
        - Does not remove .tape source files
        - Completes successfully (exit code 0)
        """
        # Arrange - Generate at least one GIF first
        tape_file = demo_dir / tape_files["quick-start"]
        subprocess.run(["vhs", str(tape_file)], check=True, timeout=180)

        gif_file = output_dir / expected_gifs["quick-start"]
        assert gif_file.exists(), "Setup: GIF should exist before cleanup"

        # Act
        result = subprocess.run(
            ["make", "demo-clean"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Assert
        assert result.returncode == 0, (
            f"'make demo-clean' failed\n" f"STDERR: {result.stderr}\n" f"STDOUT: {result.stdout}"
        )

        # Verify GIF files removed
        if output_dir.exists():
            remaining_gifs = list(output_dir.glob("*.gif"))
            assert (
                len(remaining_gifs) == 0
            ), f"GIF files still exist after cleanup: {remaining_gifs}"

        # Verify .tape files still exist
        for tape_file_name in tape_files.values():
            tape_path = demo_dir / tape_file_name
            assert tape_path.exists(), f".tape source file should not be deleted: {tape_file_name}"
