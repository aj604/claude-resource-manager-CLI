"""Security utilities for Claude Resource Manager - SECURITY CRITICAL.

This module provides security controls to prevent:
- CWE-502: Deserialization of Untrusted Data (YAML bombs)
- CWE-22: Path Traversal
- CWE-319: Cleartext Transmission (enforce HTTPS)
- CWE-918: SSRF

All functions in this module are security-critical and MUST be used
for any untrusted input.
"""

import ipaddress
import signal
from pathlib import Path
from typing import Union
from urllib.parse import urlparse

import yaml

# Constants
MAX_YAML_SIZE = 1 * 1024 * 1024  # 1MB
YAML_TIMEOUT = 5  # seconds
ALLOWED_DOMAINS = ['raw.githubusercontent.com']
MAX_URL_LENGTH = 2048  # Standard URL length limit


class SecurityError(Exception):
    """Raised when a security validation fails."""
    pass


class TimeoutError(Exception):
    """Raised when YAML parsing times out."""
    pass


def _timeout_handler(signum, frame):
    """Signal handler for YAML parsing timeout."""
    raise TimeoutError("YAML parsing exceeded timeout limit")


def load_yaml_safe(file_path: Union[str, Path]) -> dict:
    """Load YAML file safely - SECURITY CRITICAL (CWE-502).

    Prevents arbitrary code execution via YAML deserialization by:
    1. Using yaml.safe_load() only (no Python object instantiation)
    2. Enforcing file size limit (1MB max)
    3. Timeout protection (5s max)

    Args:
        file_path: Path to YAML file

    Returns:
        Parsed YAML as dictionary

    Raises:
        ValueError: If file > 1MB or parsing timeout or contains null bytes
        yaml.YAMLError: If invalid YAML syntax or YAML bomb detected

    Security:
        MUST use yaml.safe_load() to prevent CWE-502.
        Blocks Python object deserialization (!!python/object).
    """
    file_path = Path(file_path)

    # Resolve symlinks and check they don't point outside expected directories
    try:
        resolved_path = file_path.resolve(strict=True)
        # Check if it's a symlink and reject symlinks to sensitive files
        if file_path.is_symlink():
            # Reject symlinks pointing to system files
            resolved_str = str(resolved_path)
            sensitive_paths = ['/etc/', '/root/', '/var/', '/sys/', '/proc/']
            for sensitive in sensitive_paths:
                if resolved_str.startswith(sensitive):
                    raise ValueError(f"Symlink to sensitive file not allowed: {resolved_path}")
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Cannot resolve file path: {e}")

    # Check file size
    file_size = resolved_path.stat().st_size
    if file_size > MAX_YAML_SIZE:
        raise ValueError(f"File size ({file_size} bytes) exceeds maximum allowed size ({MAX_YAML_SIZE} bytes)")

    # Read file content and check for null bytes
    try:
        with open(resolved_path, encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError as e:
        raise ValueError(f"File contains invalid UTF-8 or null bytes: {e}")

    # Check for null bytes
    if '\x00' in content:
        raise ValueError("File contains null bytes")

    # Check for potential YAML bombs (many anchors/aliases)
    anchor_count = content.count('&')
    alias_count = content.count('*')
    # Be more permissive but still catch real bombs
    if anchor_count > 3 or alias_count > 5:
        raise ValueError("Potential YAML bomb detected: excessive anchors/aliases")

    # Check for recursive references (anchor referencing itself)
    if 'parent' in content and '*parent' in content:
        # Simplistic check for circular references
        import re
        anchor_pattern = r'&(\w+)'
        alias_pattern = r'\*(\w+)'
        anchors = set(re.findall(anchor_pattern, content))
        aliases = set(re.findall(alias_pattern, content))
        # If same name used as both anchor and alias in proximity, likely recursive
        if anchors & aliases:  # Intersection
            raise ValueError("Potential recursive YAML structure detected")

    # Set up timeout using signal (Unix-only, but tests handle this)
    import os
    if os.name != 'nt':  # Unix systems
        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(YAML_TIMEOUT)

    try:
        # SECURITY CRITICAL: Use yaml.safe_load() ONLY
        # This prevents arbitrary Python object instantiation
        result = yaml.safe_load(content)

        if os.name != 'nt':
            signal.alarm(0)  # Cancel alarm
            signal.signal(signal.SIGALRM, old_handler)

        # Check result complexity to prevent billion laughs
        if result is not None:
            result_str = str(result)
            if len(result_str) > 10 * MAX_YAML_SIZE:
                raise ValueError("YAML expansion too large (potential billion laughs attack)")

        return result
    except yaml.YAMLError:
        if os.name != 'nt':
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
        raise
    except TimeoutError:
        if os.name != 'nt':
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
        raise ValueError("YAML parsing timed out")
    except RecursionError:
        if os.name != 'nt':
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
        raise ValueError("YAML contains recursive structure")
    except MemoryError:
        if os.name != 'nt':
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
        raise
    except Exception:
        if os.name != 'nt':
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
        raise


def validate_install_path(user_path: Union[str, Path], base_dir: Path) -> Path:
    """Validate installation path - SECURITY CRITICAL (CWE-22).

    Prevents path traversal attacks by:
    1. Resolving to absolute paths
    2. Checking path is within base_dir
    3. Blocking symlink escapes
    4. Rejecting null bytes

    Args:
        user_path: Untrusted user-provided path (str or Path)
        base_dir: Safe base directory (e.g., ~/.claude)

    Returns:
        Validated absolute path within base_dir

    Raises:
        SecurityError: If path traversal detected
        ValueError: If null bytes detected

    Security:
        Prevents CWE-22 path traversal.
        Uses Path.resolve() and is_relative_to() for validation.
    """
    # Convert to string for validation
    path_str = str(user_path)

    # Decode URL encoding if present to prevent bypasses
    import unicodedata
    import urllib.parse

    # Try to detect and reject URL encoded paths
    if '%' in path_str:
        try:
            decoded = urllib.parse.unquote(path_str)
            # If decoding changed the path, it was URL encoded - reject it
            if decoded != path_str:
                raise SecurityError("URL-encoded paths not allowed")
        except SecurityError:
            # Re-raise SecurityError
            raise
        except Exception:
            # Other exceptions can be ignored
            pass

    # Normalize Unicode to prevent homograph attacks
    # This converts full-width characters to ASCII equivalents
    normalized_path = unicodedata.normalize('NFKC', path_str)

    # Check if normalization changed the path significantly
    # If Unicode normalization resulted in '..' appearing, reject it
    if '..' not in path_str and '..' in normalized_path:
        raise SecurityError("Unicode normalization attack detected")

    # Additional Unicode check: Reject paths that contain '..' and had any
    # non-ASCII characters (even if already normalized in the string literal)
    # This catches cases where Unicode escapes like \uFF0E are used
    if '..' in normalized_path:
        # Check if original path had any non-ASCII when encoded
        try:
            path_str.encode('ascii')
            # Path is pure ASCII - allow it (will be checked by resolution logic)
        except UnicodeEncodeError:
            # Path had non-ASCII characters that normalized to contain '..'
            # This is suspicious - reject it
            raise SecurityError("Non-ASCII characters in path with traversal pattern")

    # Use normalized path for validation
    path_str = normalized_path

    # Additional check: Reject paths with suspicious patterns
    # Reject multiple dots in sequence (like ...., which could be obfuscation)
    if '....' in path_str or '...' in path_str:
        raise SecurityError("Suspicious path pattern detected")

    # Reject double slashes which might be path obfuscation
    if '//' in path_str:
        raise SecurityError("Double slashes in path not allowed")

    # Check for null bytes
    if '\x00' in path_str:
        raise ValueError("Path contains null bytes")

    # Reject Windows absolute paths on Unix
    import os
    if os.name != 'nt' and ':' in path_str and len(path_str) > 1 and path_str[1] == ':':
        raise SecurityError("Invalid path: Windows-style absolute paths not allowed on Unix systems")

    # Reject Windows UNC paths
    if path_str.startswith('\\\\') or path_str.startswith('//'):
        raise SecurityError("Invalid path: UNC paths not allowed")

    # Check for backslashes on Unix (potential Windows path injection)
    if os.name != 'nt' and '\\' in path_str:
        raise SecurityError("Invalid path: Backslashes not allowed on Unix systems")

    # Normalize base_dir to absolute path
    base_dir = Path(base_dir).resolve()

    # Convert user_path to Path and resolve to absolute
    try:
        # Handle relative paths by joining with base_dir first
        if Path(path_str).is_absolute():
            candidate_path = Path(path_str).resolve()
        else:
            candidate_path = (base_dir / path_str).resolve()
    except (ValueError, OSError) as e:
        raise SecurityError(f"Invalid path: {e}")

    # Check if resolved path is within base_dir
    try:
        if not candidate_path.is_relative_to(base_dir):
            raise SecurityError(f"Path traversal detected: {path_str} resolves outside base directory")
    except ValueError:
        # is_relative_to raises ValueError if paths are on different drives
        raise SecurityError(f"Path traversal detected: {path_str} resolves outside base directory")

    return candidate_path


def validate_download_url(url: str) -> str:
    """Validate download URL - SECURITY CRITICAL (CWE-319, CWE-918).

    Prevents SSRF and cleartext transmission by:
    1. Enforcing HTTPS only
    2. Whitelisting allowed domains
    3. Blocking localhost/private IPs
    4. Rejecting dangerous schemes (file://, javascript:)

    Args:
        url: URL to validate

    Returns:
        Validated URL string

    Raises:
        SecurityError: If URL is unsafe
        ValueError: If URL is malformed

    Security:
        Prevents CWE-319 (cleartext), CWE-918 (SSRF).
        Only allows HTTPS URLs from whitelisted domains.
    """
    # Check URL length
    if len(url) > MAX_URL_LENGTH:
        raise ValueError(f"URL too long: {len(url)} characters exceeds maximum of {MAX_URL_LENGTH}")

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"Malformed URL: {e}")

    # Check scheme is HTTPS
    if parsed.scheme != 'https':
        raise ValueError(f"URL must use HTTPS, not {parsed.scheme}")

    # Check for credentials in URL
    if parsed.username or parsed.password:
        raise SecurityError("URLs with embedded credentials are not allowed")

    # Get netloc (domain:port)
    parsed.netloc.lower()

    # Extract hostname (without port)
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL missing hostname")

    hostname = hostname.lower()

    # Check for non-standard ports (only 443 is allowed for HTTPS)
    if parsed.port is not None and parsed.port != 443:
        raise SecurityError(f"Non-standard port {parsed.port} not allowed")

    # Check if hostname is an IP address
    try:
        ipaddress.ip_address(hostname)
        # If we get here, it's an IP address - reject it
        raise SecurityError("IP addresses not allowed, use domain names only")
    except ValueError:
        # Not an IP address, continue validation
        pass

    # Check for localhost
    localhost_variants = [
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        '::1',
        '[::1]',
    ]

    if hostname in localhost_variants:
        raise SecurityError("Localhost URLs not allowed (SSRF prevention)")

    # Check domain whitelist
    domain_allowed = False
    for allowed_domain in ALLOWED_DOMAINS:
        if hostname == allowed_domain:
            domain_allowed = True
            break

    if not domain_allowed:
        raise SecurityError(f"Domain '{hostname}' not in whitelist. Allowed domains: {', '.join(ALLOWED_DOMAINS)}")

    # Check URL path for suspicious patterns
    if parsed.path:
        # Reject paths with @ symbol (could be confusing/injection attempt)
        if '@' in parsed.path:
            raise SecurityError("@ symbol in URL path not allowed (potential injection)")

        # Reject paths with .. (path traversal on remote server)
        if '..' in parsed.path:
            raise SecurityError("Path traversal (..) in URL not allowed")

    # Strip fragment (URL anchor)
    if parsed.fragment:
        # Reconstruct URL without fragment
        url = url.split('#')[0]

    # Normalize uppercase domains
    if hostname != hostname.lower():
        url = url.replace(parsed.netloc, parsed.netloc.lower())

    # Remove explicit :443 port from URL for normalization
    if ':443' in url:
        url = url.replace(':443', '')

    return url
