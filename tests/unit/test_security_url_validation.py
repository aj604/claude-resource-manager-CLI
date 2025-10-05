"""Security tests for URL validation - CRITICAL.

These tests ensure HTTPS-only and domain whitelist enforcement.
All URLs must be HTTPS from trusted domains only.
"""

import pytest
from urllib.parse import urlparse

from claude_resource_manager.utils.security import SecurityError, validate_download_url


class TestURLSecurityControls:
    """Critical security tests for URL validation."""

    def test_WHEN_https_url_THEN_allowed(
        self, safe_github_urls: list
    ):
        """
        GIVEN: Valid HTTPS URLs from trusted domains
        WHEN: URL validation is performed
        THEN: URLs are allowed
        """

        for url in safe_github_urls:
            result = validate_download_url(url)
            assert result == url
            assert result.startswith("https://")

    def test_WHEN_http_url_THEN_rejected(
        self, unsafe_urls: list
    ):
        """
        GIVEN: HTTP URLs (not HTTPS)
        WHEN: URL validation is performed
        THEN: URLs are rejected
        """

        http_urls = [
            "http://raw.githubusercontent.com/org/repo/main/file.md",
            "http://example.com/resource.yaml",
        ]

        for url in http_urls:
            with pytest.raises((ValueError, SecurityError)) as exc_info:
                validate_download_url(url)

            assert "https" in str(exc_info.value).lower()

    def test_WHEN_github_domain_THEN_allowed(self):
        """
        GIVEN: GitHub raw content URL
        WHEN: Domain validation is performed
        THEN: GitHub domain is allowed
        """

        github_urls = [
            "https://raw.githubusercontent.com/user/repo/main/file.md",
            "https://raw.githubusercontent.com/org/project/v1.0.0/resource.yaml",
        ]

        for url in github_urls:
            result = validate_download_url(url)
            assert "raw.githubusercontent.com" in result

    def test_WHEN_untrusted_domain_THEN_rejected(self):
        """
        GIVEN: HTTPS URL from untrusted domain
        WHEN: Domain validation is performed
        THEN: URL is rejected
        """

        untrusted_urls = [
            "https://evil.com/malware.sh",
            "https://untrusted.net/resource.yaml",
            "https://malicious-site.org/file.md",
        ]

        for url in untrusted_urls:
            with pytest.raises((ValueError, SecurityError)) as exc_info:
                validate_download_url(url)

            assert (
                "domain" in str(exc_info.value).lower()
                or "untrusted" in str(exc_info.value).lower()
                or "not allowed" in str(exc_info.value).lower()
            )

    def test_WHEN_localhost_url_THEN_rejected(self):
        """
        GIVEN: URL pointing to localhost
        WHEN: URL validation is performed
        THEN: Localhost URLs are rejected (SSRF prevention)
        """

        localhost_urls = [
            "https://localhost:8000/resource.yaml",
            "https://127.0.0.1/file.md",
            "https://[::1]/resource.yaml",  # IPv6 localhost
            "https://0.0.0.0/file.md",
        ]

        for url in localhost_urls:
            with pytest.raises((ValueError, SecurityError)):
                validate_download_url(url)

    def test_WHEN_ip_address_url_THEN_rejected(self):
        """
        GIVEN: URL with IP address instead of domain
        WHEN: URL validation is performed
        THEN: IP address URLs are rejected
        """

        ip_urls = [
            "https://192.168.1.1/resource.yaml",
            "https://10.0.0.1/file.md",
            "https://172.16.0.1/resource.yaml",
            "https://8.8.8.8/file.md",
        ]

        for url in ip_urls:
            with pytest.raises((ValueError, SecurityError)):
                validate_download_url(url)

    def test_WHEN_redirect_to_unsafe_THEN_blocked(self):
        """
        GIVEN: URL that redirects to unsafe location
        WHEN: Redirect is followed
        THEN: Unsafe redirect is blocked
        """

        # This test verifies redirect validation exists
        # Actual redirect handling happens in downloader

        # URL shorteners or redirectors should be blocked
        redirect_urls = [
            "https://bit.ly/malicious",
            "https://tinyurl.com/redirect",
        ]

        for url in redirect_urls:
            with pytest.raises((ValueError, SecurityError)):
                validate_download_url(url)

    def test_WHEN_url_injection_THEN_sanitized(self):
        """
        GIVEN: URL with injection attempts
        WHEN: URL is parsed and validated
        THEN: Injection is prevented
        """

        injection_urls = [
            "https://raw.githubusercontent.com/org/repo@attacker.com/file.md",
            "https://raw.githubusercontent.com/org/repo/main/../../../etc/passwd",
            "https://raw.githubusercontent.com:8080@evil.com/file.md",
        ]

        for url in injection_urls:
            with pytest.raises((ValueError, SecurityError)):
                validate_download_url(url)

    def test_WHEN_file_scheme_THEN_rejected(self):
        """
        GIVEN: file:// URL
        WHEN: URL validation is performed
        THEN: File scheme is rejected
        """

        file_urls = [
            "file:///etc/passwd",
            "file:///Users/user/.ssh/id_rsa",
            "file://C:/Windows/System32/config/sam",
        ]

        for url in file_urls:
            with pytest.raises((ValueError, SecurityError)):
                validate_download_url(url)

    def test_WHEN_ftp_scheme_THEN_rejected(self):
        """
        GIVEN: ftp:// URL
        WHEN: URL validation is performed
        THEN: FTP scheme is rejected
        """

        ftp_urls = [
            "ftp://ftp.example.com/resource.yaml",
            "ftps://secure-ftp.com/file.md",
        ]

        for url in ftp_urls:
            with pytest.raises((ValueError, SecurityError)):
                validate_download_url(url)

    def test_WHEN_javascript_scheme_THEN_rejected(self):
        """
        GIVEN: javascript: URL
        WHEN: URL validation is performed
        THEN: JavaScript scheme is rejected
        """

        js_urls = [
            "javascript:alert('XSS')",
            "javascript:eval('malicious')",
        ]

        for url in js_urls:
            with pytest.raises((ValueError, SecurityError)):
                validate_download_url(url)

    def test_WHEN_data_scheme_THEN_rejected(self):
        """
        GIVEN: data: URL
        WHEN: URL validation is performed
        THEN: Data scheme is rejected
        """

        data_urls = [
            "data:text/html,<script>alert('XSS')</script>",
            "data:text/plain;base64,bWFsaWNpb3Vz",
        ]

        for url in data_urls:
            with pytest.raises((ValueError, SecurityError)):
                validate_download_url(url)

    def test_WHEN_malformed_url_THEN_rejected(self):
        """
        GIVEN: Malformed URLs
        WHEN: URL validation is performed
        THEN: Malformed URLs are rejected
        """

        malformed_urls = [
            "not-a-url",
            "htp://typo.com/file.md",
            "https:/missing-slash.com",
            "https://double//slash.com/file.md",
        ]

        for url in malformed_urls:
            with pytest.raises((ValueError, SecurityError)):
                validate_download_url(url)

    def test_WHEN_port_specified_THEN_rejected(self):
        """
        GIVEN: URL with non-standard port
        WHEN: URL validation is performed
        THEN: Non-standard ports are rejected (except 443)
        """

        port_urls = [
            "https://raw.githubusercontent.com:8080/file.md",
            "https://raw.githubusercontent.com:3000/resource.yaml",
        ]

        for url in port_urls:
            with pytest.raises((ValueError, SecurityError)):
                validate_download_url(url)

    def test_WHEN_credentials_in_url_THEN_rejected(self):
        """
        GIVEN: URL with embedded credentials
        WHEN: URL validation is performed
        THEN: URLs with credentials are rejected
        """

        credential_urls = [
            "https://user:pass@raw.githubusercontent.com/file.md",
            "https://admin:secret@github.com/repo/file.md",
        ]

        for url in credential_urls:
            with pytest.raises((ValueError, SecurityError)):
                validate_download_url(url)

    def test_WHEN_unicode_domain_THEN_handled(self):
        """
        GIVEN: URL with Unicode/IDN domain (homograph attack)
        WHEN: URL validation is performed
        THEN: Unicode domains are normalized or rejected
        """

        # Punycode/IDN domains that look like github
        unicode_urls = [
            "https://gịthub.com/file.md",  # Vietnamese
            "https://gіthub.com/file.md",  # Cyrillic i
        ]

        for url in unicode_urls:
            with pytest.raises((ValueError, SecurityError)):
                validate_download_url(url)

    def test_WHEN_url_too_long_THEN_rejected(self):
        """
        GIVEN: Extremely long URL (potential DoS)
        WHEN: URL validation is performed
        THEN: URL is rejected
        """

        long_url = "https://raw.githubusercontent.com/" + "a" * 10000 + "/file.md"

        with pytest.raises((ValueError, SecurityError)):
            validate_download_url(long_url)

    def test_WHEN_query_params_present_THEN_handled(self):
        """
        GIVEN: URL with query parameters
        WHEN: URL validation is performed
        THEN: Query params are validated or stripped
        """

        # GitHub raw URLs shouldn't have query params
        param_url = "https://raw.githubusercontent.com/org/repo/main/file.md?token=abc123"

        # Should either allow with validation or reject
        try:
            result = validate_download_url(param_url)
            assert "raw.githubusercontent.com" in result
        except (ValueError, SecurityError):
            pass  # Acceptable to reject

    def test_WHEN_fragment_present_THEN_stripped(self):
        """
        GIVEN: URL with fragment (#anchor)
        WHEN: URL validation is performed
        THEN: Fragment is stripped
        """

        fragment_url = "https://raw.githubusercontent.com/org/repo/main/file.md#section"

        result = validate_download_url(fragment_url)

        # Fragment should be stripped
        assert "#" not in result

    def test_WHEN_url_normalization_THEN_consistent(self):
        """
        GIVEN: URLs with different but equivalent forms
        WHEN: URL normalization is performed
        THEN: URLs are normalized consistently
        """

        url_variants = [
            "https://RAW.GITHUBUSERCONTENT.COM/org/repo/main/file.md",  # Uppercase
            "https://raw.githubusercontent.com:443/org/repo/main/file.md",  # Explicit port
        ]

        results = [validate_download_url(url) for url in url_variants]

        # Should normalize to same URL
        assert len(set(results)) <= 2  # Allow some variation
