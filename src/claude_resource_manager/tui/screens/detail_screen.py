"""DetailScreen - Resource detail viewer for Textual TUI.

This screen provides a comprehensive view of a single resource, including:
- Metadata (name, type, version, author, description)
- Source information (repository, file path, URL)
- Dependency tree visualization
- Installation controls
- Related resources
- Clipboard operations

The screen supports keyboard navigation and provides multiple actions
for interacting with the resource.
"""

from typing import Any, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Markdown, Static, Tree


class DetailScreen(Screen):
    """Resource detail viewer screen.

    Displays comprehensive information about a Claude resource including
    metadata, dependencies, source information, and installation options.

    Attributes:
        resource: The resource data dictionary
        dependency_resolver: Optional dependency resolver for loading dependency info
        search_engine: Optional search engine for finding related resources
        is_installed: Whether the resource is already installed

    Bindings:
        escape: Return to previous screen
        i: Install resource
        c: Copy resource ID to clipboard
        shift+c: Copy install command to clipboard
    """

    BINDINGS = [
        Binding("escape", "cancel", "Back"),
        Binding("i", "install", "Install"),
        Binding("c", "copy_id", "Copy ID"),
        Binding("shift+c", "copy_install_command", "Copy Command"),
    ]

    def __init__(
        self,
        resource: Optional[dict[str, Any]] = None,
        dependency_resolver: Optional[Any] = None,
        search_engine: Optional[Any] = None,
        is_installed: bool = False,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ):
        """Initialize DetailScreen.

        Args:
            resource: Resource data dictionary
            dependency_resolver: DependencyResolver instance for loading dependencies
            search_engine: SearchEngine instance for finding related resources
            is_installed: Whether resource is already installed
            name: Optional screen name
            id: Optional screen ID
            classes: Optional CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.resource = resource or {}
        self.dependency_resolver = dependency_resolver
        self.search_engine = search_engine
        self.is_installed = is_installed
        self._dependency_data: Optional[dict[str, Any]] = None
        self._related_resources: list = []

    def compose(self) -> ComposeResult:
        """Compose the detail screen layout.

        Yields:
            Widgets for the detail screen
        """
        # Header with title
        yield Static(
            self.resource.get("name", "Resource Details"), id="resource-title", classes="title"
        )

        # Main content container
        with ScrollableContainer(id="detail-container"):
            # Metadata section
            with Container(id="metadata-section", classes="section"):
                yield Static(
                    self.resource.get("name", "Unknown"),
                    id="resource-name",
                    classes="resource-name",
                )

                yield Static(
                    self.resource.get("type", "unknown").upper(),
                    id="resource-type",
                    classes="resource-type",
                )

                yield Static(
                    self.resource.get("version", "v0.0.0"),
                    id="resource-version",
                    classes="resource-version",
                )

                yield Static(
                    self.resource.get("author", "Unknown"),
                    id="resource-author",
                    classes="resource-author",
                )

                yield Static(
                    self.resource.get("summary", ""),
                    id="resource-summary",
                    classes="resource-summary",
                )

                install_path = self.resource.get("install_path", "")
                if install_path:
                    install_path = install_path.replace("~", "")
                    if not install_path.startswith("/"):
                        install_path = install_path
                yield Static(
                    install_path or "No install path", id="install-path", classes="install-path"
                )

            # Tags section
            if self.resource.get("metadata", {}).get("tags"):
                with Container(id="resource-tags", classes="section"):
                    tags = self.resource["metadata"]["tags"]
                    tags_text = ", ".join(tags)
                    yield Static(f"Tags: {tags_text}", classes="tags-display")

            # Description section
            with ScrollableContainer(id="description-container", classes="section scrollable"):
                description = self.resource.get("description", "No description available")
                yield Markdown(description, id="resource-description")

            # Metadata tools and model section
            metadata = self.resource.get("metadata", {})
            if metadata:
                with Container(id="metadata-info", classes="section"):
                    if "tools" in metadata:
                        tools_text = ", ".join(metadata["tools"])
                        yield Static(
                            f"Tools: {tools_text}", id="metadata-tools", classes="metadata-item"
                        )

                    if "model" in metadata:
                        yield Static(
                            f"Model: {metadata['model']}",
                            id="metadata-model",
                            classes="metadata-item",
                        )

            # Source information section
            source = self.resource.get("source", {})
            if source:
                with Container(id="source-info", classes="section"):
                    yield Static("Source Information:", classes="section-title")

                    if "url" in source:
                        yield Static(source["url"], id="source-url", classes="source-item")
                        yield Button("Open URL", id="source-url-link", variant="default")

                    if "repo" in source:
                        yield Static(
                            f"Repository: {source['repo']}", id="repository", classes="source-item"
                        )

                    if "path" in source:
                        yield Static(
                            f"Path: {source['path']}", id="file-path", classes="source-item"
                        )

            # Dependency section - will be populated on mount
            with Container(id="dependency-section", classes="section"):
                yield Static("Dependencies:", classes="section-title")
                dep_loading = Static(
                    "Loading dependencies...", id="dependency-loading", classes="loading-message"
                )
                yield dep_loading

                dep_error = Static(
                    "Error loading dependencies", id="dependency-error", classes="error-message"
                )
                dep_error.visible = False
                yield dep_error

                dep_tree = Tree("Dependencies", id="dependency-tree")
                dep_tree.visible = False
                yield dep_tree

                no_deps = Static(
                    "No dependencies required", id="no-dependencies-message", classes="info-message"
                )
                no_deps.visible = False
                yield no_deps

                install_order = Static("", id="install-order", classes="install-order")
                install_order.visible = False
                yield install_order

            # Related resources section
            with Container(id="related-resources", classes="section"):
                yield Static("Related Resources:", classes="section-title")

        # Action buttons
        with Horizontal(id="action-buttons", classes="button-row"):
            yield Button("Back", id="back-button", variant="default")

            install_label = "Installed" if self.is_installed else "Install"
            yield Button(
                install_label, id="install-button", variant="primary", disabled=self.is_installed
            )

    async def on_mount(self) -> None:
        """Handle screen mount - load dependencies and related resources.

        This method is called when the screen is mounted. It loads:
        - Dependency information via the dependency resolver
        - Related resources via the search engine
        """
        # Load dependencies
        if self.dependency_resolver and self.resource.get("id"):
            try:
                self._dependency_data = self.dependency_resolver.resolve(self.resource["id"])
                await self._render_dependencies()
                self.query_one("#dependency-loading").visible = False
            except Exception as e:
                self.query_one("#dependency-loading").visible = False
                error_widget = self.query_one("#dependency-error")
                error_widget.update(f"Error loading dependencies: {str(e)}")
                error_widget.visible = True
        else:
            # No dependency resolver - show no dependencies
            self.query_one("#dependency-loading").visible = False
            self.query_one("#no-dependencies-message").visible = True

    async def _render_dependencies(self) -> None:
        """Render the dependency tree visualization.

        Creates a tree widget showing required and recommended dependencies,
        and displays the installation order.
        """
        if not self._dependency_data:
            self.query_one("#no-dependencies-message").visible = True
            return

        required = self._dependency_data.get("required", [])
        recommended = self._dependency_data.get("recommended", [])
        install_order = self._dependency_data.get("install_order", [])

        # If no dependencies, show message
        if not required and not recommended:
            self.query_one("#no-dependencies-message").visible = True
            return

        # Build dependency tree
        tree = self.query_one("#dependency-tree", Tree)
        tree.visible = True
        tree.clear()

        # Add root
        root = tree.root
        root.label = self.resource.get("name", "Resource")

        # Add required dependencies
        if required:
            req_node = root.add("Required Dependencies")
            for dep in required:
                req_node.add_leaf(dep)

        # Add recommended dependencies
        if recommended:
            rec_node = root.add("Recommended Dependencies")
            for dep in recommended:
                rec_node.add_leaf(dep)

        root.expand()

        # Show installation order
        if install_order and len(install_order) > 1:
            order_widget = self.query_one("#install-order")
            order_text = "Install order: " + " → ".join(install_order)
            order_widget.update(order_text)
            order_widget.visible = True

        # Update install button with count
        if not self.is_installed:
            install_button = self.query_one("#install-button", Button)
            total_count = len(install_order) if install_order else 1
            install_button.label = f"Install ({total_count})"

    async def load_related_resources(self) -> None:
        """Load and display related resources based on tags.

        Uses the search engine to find resources with similar tags
        and displays them in the related resources section.
        """
        if not self.search_engine:
            return

        tags = self.resource.get("metadata", {}).get("tags", [])
        if not tags:
            return

        # Search for resources with similar tags
        # This is a simplified implementation
        try:
            related = self.search_engine.search(" ".join(tags))
            self._related_resources = [r for r in related if r.get("id") != self.resource.get("id")]

            # Display related resources
            related_container = self.query_one("#related-resources")
            for resource in self._related_resources[:5]:  # Limit to 5
                btn = Button(resource.get("name", "Unknown"), classes="related-resource-button")
                related_container.mount(btn)
        except Exception:
            pass  # Silently fail for related resources

    async def action_back(self) -> None:
        """Return to previous screen (back button action)."""
        self.app.pop_screen()

    async def action_cancel(self) -> None:
        """Return to previous screen (escape key action)."""
        self.app.pop_screen()

    async def action_install(self) -> None:
        """Open install plan screen for this resource.

        Creates and pushes an InstallPlanScreen to show the user
        what will be installed and confirm the installation.
        """
        # Import here to avoid circular dependency
        from claude_resource_manager.tui.screens.install_plan_screen import InstallPlanScreen

        install_screen = InstallPlanScreen(
            resource=self.resource, dependency_data=self._dependency_data
        )
        self.app.push_screen(install_screen)

    async def action_copy_id(self) -> None:
        """Copy resource ID to clipboard.

        Requires pyperclip library to be installed.
        """
        try:
            import pyperclip

            resource_id = self.resource.get("id", "")
            pyperclip.copy(resource_id)
        except ImportError:
            pass  # Silently fail if pyperclip not available

    async def action_copy_install_command(self) -> None:
        """Copy installation command to clipboard.

        Creates a CLI install command for the resource and copies it
        to the clipboard using pyperclip.
        """
        try:
            import pyperclip

            resource_id = self.resource.get("id", "")
            command = f"crm install {resource_id}"
            pyperclip.copy(command)
        except ImportError:
            pass  # Silently fail if pyperclip not available

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: Button press event
        """
        button_id = event.button.id

        if button_id == "back-button":
            await self.action_back()
        elif button_id == "install-button":
            await self.action_install()
        elif button_id == "source-url-link":
            # Open URL in browser (simplified - would need webbrowser module)
            pass

    async def on_dependency_clicked(self, dependency_id: str) -> None:
        """Handle clicking on a dependency in the tree.

        Opens a new DetailScreen for the clicked dependency.

        Args:
            dependency_id: ID of the dependency resource
        """
        # Would need to load the full resource data for the dependency
        # For now, create a new DetailScreen
        dep_screen = DetailScreen(
            resource={"id": dependency_id, "name": dependency_id},
            dependency_resolver=self.dependency_resolver,
            search_engine=self.search_engine,
        )
        self.app.push_screen(dep_screen)

    async def on_related_resource_clicked(self, resource_id: str) -> None:
        """Handle clicking on a related resource.

        Opens a new DetailScreen for the clicked related resource.

        Args:
            resource_id: ID of the related resource
        """
        # Find the full resource data
        related_resource = next(
            (r for r in self._related_resources if r.get("id") == resource_id), None
        )

        if related_resource:
            related_screen = DetailScreen(
                resource=related_resource,
                dependency_resolver=self.dependency_resolver,
                search_engine=self.search_engine,
            )
            self.app.push_screen(related_screen)
