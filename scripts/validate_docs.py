#!/usr/bin/env python3
"""Documentation coverage and quality validation script.

This script validates that all Python modules follow documentation standards:
- All public classes have docstrings with Attributes
- All public functions have docstrings with Args, Returns, Raises
- Security-critical code has explanatory comments
- Complex algorithms have step-by-step comments

Usage:
    # Validate single file
    python scripts/validate_docs.py src/claude_resource_manager/core/catalog_loader.py

    # Validate entire project
    python scripts/validate_docs.py src/claude_resource_manager

    # Generate coverage report
    python scripts/validate_docs.py --report

Example:
    $ python scripts/validate_docs.py src/claude_resource_manager
    ✅ models/resource.py: 100% (5/5)
    ❌ core/search_engine.py: 83% (10/12)
    Overall: 93% (38/41)
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Set
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class DocstringIssue:
    """Represents a documentation issue.

    Attributes:
        file_path: Path to the file with the issue
        item_name: Name of the class/function with the issue
        item_type: Type of item ('class', 'function', 'module')
        issue: Description of the issue
        line_number: Line number where the issue occurs
    """
    file_path: Path
    item_name: str
    item_type: str
    issue: str
    line_number: int


class DocValidator:
    """Validates Python documentation coverage and quality.

    Checks for:
    - Docstring presence on all public items
    - Google-style formatting (Args, Returns, Raises, Attributes)
    - Security comments on critical code
    - Examples in complex functions

    Attributes:
        issues: List of all documentation issues found
        stats: Statistics about documentation coverage
        security_keywords: Keywords that indicate security-critical code
    """

    def __init__(self):
        self.issues: List[DocstringIssue] = []
        self.stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {
            'total': 0,
            'documented': 0,
            'with_examples': 0,
            'with_security': 0
        })
        self.security_keywords = {
            'security', 'validate', 'sanitize', 'safe', 'check',
            'verify', 'password', 'token', 'auth', 'path', 'traversal'
        }

    def validate_file(self, file_path: Path) -> None:
        """Validate documentation in a single Python file.

        Args:
            file_path: Path to Python file to validate

        Raises:
            FileNotFoundError: If file doesn't exist
            SyntaxError: If file has syntax errors
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path) as f:
            try:
                tree = ast.parse(f.read(), filename=str(file_path))
            except SyntaxError as e:
                raise SyntaxError(f"Syntax error in {file_path}: {e}")

        # Check module-level docstring
        self._check_module_docstring(tree, file_path)

        # Check all classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._check_class(node, file_path)
            elif isinstance(node, ast.FunctionDef):
                self._check_function(node, file_path)

    def _check_module_docstring(self, tree: ast.Module, file_path: Path) -> None:
        """Check module-level docstring.

        Args:
            tree: AST tree of the module
            file_path: Path to the file being checked
        """
        docstring = ast.get_docstring(tree)

        if not docstring:
            self.issues.append(DocstringIssue(
                file_path=file_path,
                item_name='<module>',
                item_type='module',
                issue='Missing module-level docstring',
                line_number=1
            ))
        else:
            self.stats[str(file_path)]['documented'] += 1

            # Check if module handles security
            source = ast.get_source_segment(open(file_path).read(), tree)
            if source and any(kw in source.lower() for kw in self.security_keywords):
                if 'security' not in docstring.lower():
                    self.issues.append(DocstringIssue(
                        file_path=file_path,
                        item_name='<module>',
                        item_type='module',
                        issue='Security-related module missing security note in docstring',
                        line_number=1
                    ))

        self.stats[str(file_path)]['total'] += 1

    def _check_class(self, node: ast.ClassDef, file_path: Path) -> None:
        """Check class documentation.

        Args:
            node: AST node for the class
            file_path: Path to the file containing the class
        """
        # Skip private classes
        if node.name.startswith('_'):
            return

        self.stats[str(file_path)]['total'] += 1
        docstring = ast.get_docstring(node)

        if not docstring:
            self.issues.append(DocstringIssue(
                file_path=file_path,
                item_name=node.name,
                item_type='class',
                issue='Missing docstring',
                line_number=node.lineno
            ))
            return

        self.stats[str(file_path)]['documented'] += 1

        # Check for Attributes section
        if 'Attributes:' not in docstring and 'Attributes\n' not in docstring:
            # Check if class has attributes (excluding magic methods)
            has_attributes = any(
                isinstance(child, ast.AnnAssign) or
                (isinstance(child, ast.Assign) and not child.targets[0].id.startswith('_'))
                for child in node.body
                if isinstance(child, (ast.AnnAssign, ast.Assign))
            )

            if has_attributes:
                self.issues.append(DocstringIssue(
                    file_path=file_path,
                    item_name=node.name,
                    item_type='class',
                    issue='Missing Attributes section in docstring',
                    line_number=node.lineno
                ))

        # Check for example
        if 'Example:' in docstring or 'Examples:' in docstring:
            self.stats[str(file_path)]['with_examples'] += 1

    def _check_function(self, node: ast.FunctionDef, file_path: Path) -> None:
        """Check function/method documentation.

        Args:
            node: AST node for the function
            file_path: Path to the file containing the function
        """
        # Skip private functions and magic methods
        if node.name.startswith('_') and not node.name.startswith('__'):
            return

        self.stats[str(file_path)]['total'] += 1
        docstring = ast.get_docstring(node)

        if not docstring:
            self.issues.append(DocstringIssue(
                file_path=file_path,
                item_name=node.name,
                item_type='function',
                issue='Missing docstring',
                line_number=node.lineno
            ))
            return

        self.stats[str(file_path)]['documented'] += 1

        # Check for Args section if function has arguments
        args = [arg.arg for arg in node.args.args if arg.arg != 'self' and arg.arg != 'cls']
        if args and 'Args:' not in docstring and 'Arguments:' not in docstring:
            self.issues.append(DocstringIssue(
                file_path=file_path,
                item_name=node.name,
                item_type='function',
                issue=f'Missing Args section (has {len(args)} arguments)',
                line_number=node.lineno
            ))

        # Check for Returns section if function returns something
        has_return = any(
            isinstance(child, ast.Return) and child.value is not None
            for child in ast.walk(node)
        )
        if has_return and 'Returns:' not in docstring:
            self.issues.append(DocstringIssue(
                file_path=file_path,
                item_name=node.name,
                item_type='function',
                issue='Missing Returns section',
                line_number=node.lineno
            ))

        # Check for Raises section if function raises exceptions
        has_raise = any(
            isinstance(child, ast.Raise)
            for child in ast.walk(node)
        )
        if has_raise and 'Raises:' not in docstring:
            self.issues.append(DocstringIssue(
                file_path=file_path,
                item_name=node.name,
                item_type='function',
                issue='Missing Raises section (function raises exceptions)',
                line_number=node.lineno
            ))

        # Check for security documentation
        if any(kw in node.name.lower() for kw in self.security_keywords):
            if 'security' not in docstring.lower():
                self.issues.append(DocstringIssue(
                    file_path=file_path,
                    item_name=node.name,
                    item_type='function',
                    issue='Security-related function missing security note',
                    line_number=node.lineno
                ))
            else:
                self.stats[str(file_path)]['with_security'] += 1

        # Check for example in complex functions
        if len(docstring) > 200 and 'Example:' not in docstring and 'Examples:' not in docstring:
            self.issues.append(DocstringIssue(
                file_path=file_path,
                item_name=node.name,
                item_type='function',
                issue='Complex function missing Example section',
                line_number=node.lineno
            ))

        if 'Example:' in docstring or 'Examples:' in docstring:
            self.stats[str(file_path)]['with_examples'] += 1

    def print_report(self, verbose: bool = False) -> None:
        """Print documentation coverage report.

        Args:
            verbose: If True, print detailed issues
        """
        print("\n" + "=" * 70)
        print("📚 Documentation Coverage Report")
        print("=" * 70 + "\n")

        # Per-file summary
        total_items = 0
        total_documented = 0

        for file_path, stats in sorted(self.stats.items()):
            rel_path = Path(file_path).relative_to(Path.cwd())
            coverage = (stats['documented'] / stats['total'] * 100) if stats['total'] > 0 else 0

            status = "✅" if coverage == 100 else "🟡" if coverage >= 80 else "❌"
            print(f"{status} {rel_path}: {coverage:.0f}% ({stats['documented']}/{stats['total']})")

            total_items += stats['total']
            total_documented += stats['documented']

        # Overall summary
        print("\n" + "-" * 70)
        overall_coverage = (total_documented / total_items * 100) if total_items > 0 else 0
        print(f"\n📊 Overall Coverage: {overall_coverage:.1f}% ({total_documented}/{total_items})")

        # Statistics
        total_with_examples = sum(stats['with_examples'] for stats in self.stats.values())
        total_with_security = sum(stats['with_security'] for stats in self.stats.values())

        print(f"📝 With Examples: {total_with_examples}")
        print(f"🔒 Security Documented: {total_with_security}")

        # Issues
        if self.issues:
            print(f"\n⚠️  {len(self.issues)} Documentation Issues Found:\n")

            if verbose:
                for issue in sorted(self.issues, key=lambda x: (str(x.file_path), x.line_number)):
                    rel_path = issue.file_path.relative_to(Path.cwd())
                    print(f"  {rel_path}:{issue.line_number}")
                    print(f"    {issue.item_type}: {issue.item_name}")
                    print(f"    Issue: {issue.issue}\n")
            else:
                # Group by file
                by_file = defaultdict(list)
                for issue in self.issues:
                    by_file[issue.file_path].append(issue)

                for file_path in sorted(by_file.keys()):
                    rel_path = file_path.relative_to(Path.cwd())
                    print(f"  {rel_path}: {len(by_file[file_path])} issues")

                print(f"\n  Run with --verbose to see details")

        # Status
        print("\n" + "=" * 70)
        if overall_coverage >= 95:
            print("✅ PASS: Documentation coverage meets 95% target")
            return 0
        elif overall_coverage >= 85:
            print("🟡 WARNING: Documentation coverage below 95% target")
            return 1
        else:
            print("❌ FAIL: Documentation coverage below 85% minimum")
            return 1


def main():
    """Main entry point for documentation validation."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Validate Python documentation coverage and quality'
    )
    parser.add_argument(
        'paths',
        nargs='*',
        default=['src/claude_resource_manager'],
        help='Paths to Python files or directories to validate'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed issue information'
    )
    parser.add_argument(
        '--report', '-r',
        action='store_true',
        help='Generate coverage report'
    )

    args = parser.parse_args()

    validator = DocValidator()

    # Collect all Python files
    python_files = []
    for path_str in args.paths:
        path = Path(path_str)
        if path.is_file():
            if path.suffix == '.py':
                python_files.append(path)
        elif path.is_dir():
            python_files.extend(path.rglob('*.py'))

    # Validate each file
    for file_path in sorted(python_files):
        # Skip __init__.py files if they're empty
        if file_path.name == '__init__.py' and file_path.stat().st_size < 10:
            continue

        try:
            validator.validate_file(file_path)
        except Exception as e:
            print(f"Error validating {file_path}: {e}", file=sys.stderr)

    # Print report
    exit_code = validator.print_report(verbose=args.verbose)

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
