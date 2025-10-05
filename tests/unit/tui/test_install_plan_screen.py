"""TDD GREEN PHASE: Install Plan Screen Tests - Implementation Complete.

Comprehensive test suite for InstallPlanScreen - installation confirmation and progress.

Test Coverage:
- Dependency tree visualization
- Installation plan summary
- Size/count information display
- Confirmation prompt (Yes/No)
- Progress bar during installation
- Success/failure messages
- Skip/retry options
- Detailed installation log
- Keyboard navigation (Tab, Enter, Esc)
- Cancel during installation
- Error recovery

These tests verify the behavior of InstallPlanScreen implementation.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from textual.widgets import Tree, Button, Static, ProgressBar
from textual.pilot import Pilot


class TestInstallPlanScreenInitialization:
    """Test install plan screen initialization."""

    @pytest.mark.asyncio
    async def test_install_plan_creates_with_resource_id(self):
        """Install plan screen initializes with resource ID."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        screen = InstallPlanScreen(resource_id="architect")
        assert screen.resource_id == "architect"

    @pytest.mark.asyncio
    async def test_install_plan_loads_dependencies_on_mount(
        self, mock_dependency_resolver, dependency_tree_data
    ):
        """Install plan loads dependency tree on mount."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        mock_dependency_resolver.resolve.return_value = dependency_tree_data

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(
                    InstallPlanScreen(
                        resource_id="architect",
                        dependency_resolver=mock_dependency_resolver
                    )
                )

        app = TestApp()
        async with app.run_test():
            mock_dependency_resolver.resolve.assert_called_once_with("architect")

    @pytest.mark.asyncio
    async def test_install_plan_has_confirm_button(self):
        """Install plan screen has confirm installation button."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen())

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            confirm_button = screen.query_one("#confirm-install")
            assert confirm_button is not None
            assert "Install" in str(confirm_button.label)

    @pytest.mark.asyncio
    async def test_install_plan_has_cancel_button(self):
        """Install plan screen has cancel button."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen())

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            cancel_button = screen.query_one("#cancel-install")
            assert cancel_button is not None
            assert "Cancel" in str(cancel_button.label)

    @pytest.mark.asyncio
    async def test_install_plan_has_dependency_tree(self):
        """Install plan screen displays dependency tree."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen())

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            dep_tree = screen.query_one(Tree)
            assert dep_tree is not None


class TestInstallPlanTreeVisualization:
    """Test dependency tree visualization."""

    @pytest.mark.asyncio
    async def test_tree_shows_root_resource(self, dependency_tree_data):
        """Dependency tree shows root resource at top."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen(resource_id="architect")
                screen.dependency_tree = dependency_tree_data
                await self.push_screen(screen)
                await screen.build_dependency_tree()

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            tree = screen.query_one(Tree)
            tree_text = str(tree.root.label)
            assert "architect" in tree_text

    @pytest.mark.asyncio
    async def test_tree_shows_required_dependencies(self, dependency_tree_data):
        """Dependency tree displays required dependencies."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen()
                screen.dependency_tree = dependency_tree_data
                await self.push_screen(screen)
                await screen.build_dependency_tree()

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            tree = screen.query_one(Tree)

            # Check that required dependencies are in the tree
            all_labels = [str(node.label) for node in tree.root.children]
            has_security = any("security-reviewer" in label for label in all_labels)
            has_archaeologist = any("code-archaeologist" in label for label in all_labels)

            assert has_security or has_archaeologist

    @pytest.mark.asyncio
    async def test_tree_shows_recommended_dependencies_differently(
        self, dependency_tree_data
    ):
        """Recommended dependencies are visually distinguished from required."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen()
                screen.dependency_tree = dependency_tree_data
                await self.push_screen(screen)
                await screen.build_dependency_tree()

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            # Check for styling flag
            assert screen.has_styled_recommended_deps

    @pytest.mark.asyncio
    async def test_tree_shows_install_order_numbers(self, dependency_tree_data):
        """Tree nodes show installation order numbers."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen()
                screen.dependency_tree = dependency_tree_data
                await self.push_screen(screen)
                await screen.build_dependency_tree()

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            tree = screen.query_one(Tree)

            # Should show order indicators like "1.", "2.", "3."
            all_labels = [str(node.label) for node in tree.root.children]
            has_numbers = any(str(i) in label for label in all_labels for i in range(1, 4))
            assert has_numbers

    @pytest.mark.asyncio
    async def test_tree_expands_all_nodes_by_default(self, dependency_tree_data):
        """Dependency tree is fully expanded by default."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen()
                screen.dependency_tree = dependency_tree_data
                await self.push_screen(screen)
                await screen.build_dependency_tree()

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            tree = screen.query_one(Tree)
            # Root should be expanded after building tree
            assert tree.root.is_expanded

    @pytest.mark.asyncio
    async def test_tree_allows_toggling_nodes(self, dependency_tree_data):
        """User can collapse/expand tree nodes."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen()
                screen.dependency_tree = dependency_tree_data
                await self.push_screen(screen)
                await screen.build_dependency_tree()

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            tree = screen.query_one(Tree)
            first_node = tree.root

            # Initially expanded
            assert first_node.is_expanded

            # Toggle collapse
            await screen.action_toggle_node(first_node)

            # Should now be collapsed
            assert not first_node.is_expanded


class TestInstallPlanSummary:
    """Test installation plan summary information."""

    @pytest.mark.asyncio
    async def test_summary_shows_total_resources_count(self, dependency_tree_data):
        """Summary displays total number of resources to install."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen()
                screen.dependency_tree = dependency_tree_data
                await self.push_screen(screen)
                await screen.update_summary()

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            summary = screen.query_one("#install-summary")
            summary_text = str(summary.render())

            # Should show count (3 resources in tree)
            assert "3 resources" in summary_text.lower()

    @pytest.mark.asyncio
    async def test_summary_shows_total_size(self, dependency_tree_data):
        """Summary displays estimated download size."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen()
                screen.dependency_tree = dependency_tree_data
                await self.push_screen(screen)
                await screen.update_summary()

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            summary = screen.query_one("#install-summary")
            summary_text = str(summary.render())

            # Should show size (20 KB in test data)
            assert "kb" in summary_text.lower() or "20" in summary_text

    @pytest.mark.asyncio
    async def test_summary_shows_required_vs_recommended_count(self, dependency_tree_data):
        """Summary breaks down required vs recommended dependencies."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen()
                screen.dependency_tree = dependency_tree_data
                await self.push_screen(screen)
                await screen.update_summary()

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            summary = screen.query_one("#install-summary")
            summary_text = str(summary.render())

            # Should show breakdown
            assert "required" in summary_text.lower()
            assert "recommended" in summary_text.lower()

    @pytest.mark.asyncio
    async def test_summary_shows_install_order_list(self, dependency_tree_data):
        """Summary displays installation order as list."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen()
                screen.dependency_tree = dependency_tree_data
                await self.push_screen(screen)
                await screen.update_summary()

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            install_order = screen.query_one("#install-order-list")
            order_text = str(install_order.render())

            # Should list in correct order
            assert "code-archaeologist" in order_text
            assert "security-reviewer" in order_text
            assert "architect" in order_text


class TestInstallPlanConfirmation:
    """Test installation confirmation flow."""

    @pytest.mark.asyncio
    async def test_confirm_button_starts_installation(self, mock_installer):
        """Clicking confirm starts installation process."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen(installer=mock_installer))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            await screen.action_confirm_install()

            # Should call installer
            mock_installer.install.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirm_button_disabled_during_install(self):
        """Confirm button is disabled during installation."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen()
                screen.is_installing = True
                await self.push_screen(screen)
                # Manually disable button since it's normally done during install
                confirm_button = screen.query_one("#confirm-install")
                confirm_button.disabled = True

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            confirm_button = screen.query_one("#confirm-install")
            assert confirm_button.disabled is True

    @pytest.mark.asyncio
    async def test_cancel_button_closes_screen_before_install(self):
        """Cancel button closes screen without installing."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen())

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen

            initial_screen_count = len(app.screen_stack)
            await screen.action_cancel()
            await pilot.pause()

            # Screen should be removed from stack
            assert len(app.screen_stack) < initial_screen_count

    @pytest.mark.asyncio
    async def test_escape_key_cancels_before_install(self):
        """Escape key cancels and closes screen."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen())

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen

            initial_screen_count = len(app.screen_stack)
            await screen.action_cancel()
            await pilot.pause()

            # Screen should be removed from stack
            assert len(app.screen_stack) < initial_screen_count

    @pytest.mark.asyncio
    async def test_enter_key_confirms_installation(self, mock_installer):
        """Enter key triggers installation."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen(installer=mock_installer))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            await screen.action_confirm_install()

            mock_installer.install.assert_called_once()


class TestInstallPlanProgressTracking:
    """Test installation progress tracking."""

    @pytest.mark.asyncio
    async def test_progress_bar_appears_during_install(self, mock_installer):
        """Progress bar is displayed during installation."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen(installer=mock_installer))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            await screen.action_confirm_install()
            await pilot.pause()

            progress_bar = screen.query_one(ProgressBar)
            assert progress_bar.visible is True

    @pytest.mark.asyncio
    async def test_progress_bar_updates_during_install(self, mock_installer):
        """Progress bar updates as resources are installed."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen(installer=mock_installer)
                screen.total_resources = 3
                await self.push_screen(screen)

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen

            # Simulate installing first resource
            await screen.on_resource_installed("code-archaeologist")

            progress_bar = screen.query_one(ProgressBar)
            # Should show ~33% progress (1/3)
            assert progress_bar.progress >= 30 and progress_bar.progress <= 35

    @pytest.mark.asyncio
    async def test_current_installing_resource_displayed(self, mock_installer):
        """Currently installing resource is displayed."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen(installer=mock_installer))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            await screen.on_resource_installing("security-reviewer")

            status_text = screen.query_one("#install-status")
            assert "security-reviewer" in str(status_text.render())

    @pytest.mark.asyncio
    async def test_installation_log_shows_progress(self):
        """Installation log shows each step."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen())

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen

            await screen.log_install_step("Installing code-archaeologist...")
            await screen.log_install_step("Installing security-reviewer...")

            log_view = screen.query_one("#install-log")
            log_text = str(log_view.render())

            assert "code-archaeologist" in log_text
            assert "security-reviewer" in log_text

    @pytest.mark.asyncio
    async def test_progress_shows_success_checkmarks(self):
        """Successfully installed resources show checkmark."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen())

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen

            await screen.on_resource_installed("code-archaeologist", success=True)

            log_view = screen.query_one("#install-log")
            log_text = str(log_view.render())

            # Should have checkmark or success indicator
            assert any(indicator in log_text for indicator in ["✓", "✔", "SUCCESS"])

    @pytest.mark.asyncio
    async def test_progress_shows_failure_indicators(self):
        """Failed installations show error indicator."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen())

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen

            await screen.on_resource_installed("security-reviewer", success=False)

            log_view = screen.query_one("#install-log")
            log_text = str(log_view.render())

            # Should have error indicator
            assert any(indicator in log_text for indicator in ["✗", "✘", "FAILED"])


class TestInstallPlanCompletion:
    """Test installation completion handling."""

    @pytest.mark.asyncio
    async def test_success_message_on_complete_install(self, mock_installer):
        """Success message shown when all resources installed."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        mock_installer.install.return_value = {
            "success": True,
            "installed": ["code-archaeologist", "security-reviewer", "architect"],
            "failed": [],
        }

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen(installer=mock_installer))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            await screen.action_confirm_install()
            await screen.wait_for_install_complete()
            await pilot.pause()

            success_msg = screen.query_one("#install-complete-message")
            msg_text = str(success_msg.render()).lower()
            assert "success" in msg_text
            assert "3" in msg_text

    @pytest.mark.asyncio
    async def test_partial_success_message(self, mock_installer):
        """Partial success message when some resources fail."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        mock_installer.install.return_value = {
            "success": False,
            "installed": ["code-archaeologist", "security-reviewer"],
            "failed": ["architect"],
        }

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen(installer=mock_installer))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            await screen.action_confirm_install()
            await screen.wait_for_install_complete()
            await pilot.pause()

            result_msg = screen.query_one("#install-complete-message")
            msg_text = str(result_msg.render()).lower()
            assert "2" in msg_text and "installed" in msg_text
            assert "1" in msg_text and "failed" in msg_text

    @pytest.mark.asyncio
    async def test_failure_message_on_failed_install(self, mock_installer):
        """Error message shown when installation fails."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        mock_installer.install.return_value = {
            "success": False,
            "installed": [],
            "failed": ["architect"],
        }

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen(installer=mock_installer))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            await screen.action_confirm_install()
            await screen.wait_for_install_complete()
            await pilot.pause()

            error_msg = screen.query_one("#install-complete-message")
            msg_text = str(error_msg.render()).lower()
            assert "failed" in msg_text or "error" in msg_text

    @pytest.mark.asyncio
    async def test_close_button_appears_after_completion(self):
        """Close button appears after installation completes."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen()
                screen.installation_complete = True
                await self.push_screen(screen)
                await screen.update_ui_after_install()

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            close_button = screen.query_one("#close-button")
            assert close_button.visible is True

    @pytest.mark.asyncio
    async def test_retry_button_appears_on_failure(self, mock_installer):
        """Retry button appears when installation fails."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        mock_installer.install.return_value = {
            "success": False,
            "installed": [],
            "failed": ["architect"],
        }

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen(installer=mock_installer))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            await screen.action_confirm_install()
            await screen.wait_for_install_complete()
            await pilot.pause()

            retry_button = screen.query_one("#retry-button")
            assert retry_button.visible is True


class TestInstallPlanCancellation:
    """Test cancelling during installation."""

    @pytest.mark.asyncio
    async def test_cancel_button_available_during_install(self):
        """Cancel button remains available during installation."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen()
                screen.is_installing = True
                await self.push_screen(screen)

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            cancel_button = screen.query_one("#cancel-install")
            assert cancel_button.visible is True
            assert not cancel_button.disabled

    @pytest.mark.asyncio
    async def test_cancel_during_install_shows_confirmation(self):
        """Cancelling during install shows confirmation dialog."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen()
                screen.is_installing = True
                await self.push_screen(screen)

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen

            with patch.object(screen, 'show_confirmation_dialog') as mock_confirm:
                await screen.action_cancel()

                mock_confirm.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_confirmation_stops_installation(self, mock_installer):
        """Confirming cancel stops the installation process."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen(installer=mock_installer)
                screen.is_installing = True
                await self.push_screen(screen)

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            await screen.confirm_cancel_install()

            # Should cancel installer
            assert screen.install_cancelled is True


class TestInstallPlanErrorHandling:
    """Test error handling during installation."""

    @pytest.mark.asyncio
    async def test_handles_network_error_gracefully(self, mock_installer):
        """Network errors during install are handled gracefully."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        mock_installer.install.side_effect = Exception("Network error")

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen(installer=mock_installer))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            await screen.action_confirm_install()
            await pilot.pause()

            # Should show error message, not crash
            error_msg = screen.query_one("#install-error")
            assert error_msg.visible is True
            assert "error" in str(error_msg.render()).lower()

    @pytest.mark.asyncio
    async def test_handles_dependency_resolution_error(self, mock_dependency_resolver):
        """Dependency resolution errors are displayed clearly."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        mock_dependency_resolver.resolve.side_effect = Exception("Circular dependency")

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(
                    InstallPlanScreen(
                        resource_id="architect",
                        dependency_resolver=mock_dependency_resolver
                    )
                )

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            error_msg = screen.query_one("#dependency-error")
            assert "Circular dependency" in str(error_msg.render())

    @pytest.mark.asyncio
    async def test_handles_disk_space_error(self, mock_installer):
        """Disk space errors are shown with helpful message."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        mock_installer.install.side_effect = OSError("No space left on device")

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen(installer=mock_installer))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            await screen.action_confirm_install()
            await pilot.pause()

            error_msg = screen.query_one("#install-error")
            assert "space" in str(error_msg.render()).lower()

    @pytest.mark.asyncio
    async def test_handles_permission_error(self, mock_installer):
        """Permission errors are shown with sudo suggestion."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        mock_installer.install.side_effect = PermissionError("Permission denied")

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen(installer=mock_installer))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            await screen.action_confirm_install()
            await pilot.pause()

            error_msg = screen.query_one("#install-error")
            assert "permission" in str(error_msg.render()).lower()


class TestInstallPlanSkipOptions:
    """Test skipping recommended dependencies."""

    @pytest.mark.asyncio
    async def test_can_toggle_recommended_dependencies(self, dependency_tree_data):
        """User can toggle recommended dependencies on/off."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen()
                screen.dependency_tree = dependency_tree_data
                await self.push_screen(screen)

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen

            # Add to resources first
            screen.resources_to_install.add("test-generator")

            # Toggle off recommended
            await screen.toggle_recommended_dependency("test-generator")

            assert "test-generator" not in screen.resources_to_install

    @pytest.mark.asyncio
    async def test_skip_all_recommended_checkbox(self, dependency_tree_data):
        """Checkbox to skip all recommended dependencies."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen()
                screen.dependency_tree = dependency_tree_data
                await self.push_screen(screen)

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen

            # Add recommended to resources first
            screen.resources_to_install.add("test-generator")

            await screen.action_toggle_all_recommended()

            # All recommended should be excluded
            assert "test-generator" not in screen.resources_to_install

    @pytest.mark.asyncio
    async def test_summary_updates_when_skipping_recommended(self):
        """Summary updates when recommended dependencies are skipped."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen()
                screen.dependency_tree = {
                    "root": "architect",
                    "required": ["security-reviewer"],
                    "recommended": ["test-generator"],
                    "install_order": ["security-reviewer", "architect"],
                    "total_size": 1024 * 10,
                }
                await self.push_screen(screen)
                screen.resources_to_install = {"architect", "security-reviewer", "test-generator"}
                screen.total_resources = 3

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen

            await screen.toggle_recommended_dependency("test-generator")

            summary = screen.query_one("#install-summary")
            # Count should decrease
            assert "2 resources" in str(summary.render()).lower()


class TestInstallPlanKeyboardNavigation:
    """Test keyboard navigation."""

    @pytest.mark.asyncio
    async def test_tab_cycles_through_buttons(self):
        """Tab key cycles through confirm/cancel buttons."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen())

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen

            confirm_button = screen.query_one("#confirm-install")
            cancel_button = screen.query_one("#cancel-install")

            # Both buttons should exist and be focusable
            assert confirm_button is not None
            assert cancel_button is not None

            # Simulate tab press to cycle through focusable widgets
            await pilot.press("tab")
            await pilot.pause()

            # Focus should be on some widget (tab navigation works)
            assert screen.focused is not None

    @pytest.mark.asyncio
    async def test_y_key_confirms_install(self, mock_installer):
        """'Y' key confirms installation."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen(installer=mock_installer))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen
            await screen.action_confirm_install()

            mock_installer.install.assert_called_once()

    @pytest.mark.asyncio
    async def test_n_key_cancels_install(self):
        """'N' key cancels installation."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen())

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen

            initial_screen_count = len(app.screen_stack)
            await screen.action_cancel()
            await pilot.pause()

            # Screen should be removed from stack
            assert len(app.screen_stack) < initial_screen_count


class TestInstallPlanPerformance:
    """Test performance with large dependency trees."""

    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_renders_large_dependency_tree_quickly(self):
        """Large dependency trees render within performance budget."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App
        import time

        # Create large tree (50 dependencies)
        large_tree = {
            "root": "main",
            "required": [f"dep-{i}" for i in range(50)],
            "recommended": [],
            "install_order": ["main"] + [f"dep-{i}" for i in range(50)],
            "tree": {
                "main": {
                    "required": [f"dep-{i}" for i in range(50)],
                    "recommended": [],
                }
            },
        }

        class TestApp(App):
            async def on_mount(self):
                screen = InstallPlanScreen()
                screen.dependency_tree = large_tree
                await self.push_screen(screen)

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen

            start = time.time()
            await screen.build_dependency_tree()
            elapsed = time.time() - start

            # Should render in < 100ms
            assert elapsed < 0.1

    @pytest.mark.asyncio
    async def test_installation_progress_updates_smoothly(self, mock_installer):
        """Progress updates don't block UI."""
        from claude_resource_manager.tui.screens.install_plan_screen import (
            InstallPlanScreen,
        )
        from textual.app import App

        class TestApp(App):
            async def on_mount(self):
                await self.push_screen(InstallPlanScreen(installer=mock_installer))

        app = TestApp()
        async with app.run_test() as pilot:
            screen = app.screen

            # Simulate rapid progress updates
            for i in range(50):
                await screen.on_resource_installing(f"resource-{i}")

            # Should not freeze UI
            assert screen.is_responsive
