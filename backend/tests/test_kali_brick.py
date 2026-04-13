"""Tests for Kali Linux Security Brick service."""

import pytest

from app.services.kali_brick import (
    KaliSecurityBrick,
    ScanType,
    ToolCategory,
    VulnerabilitySeverity,
)


@pytest.fixture
def brick() -> KaliSecurityBrick:
    """Create a fresh Kali Security Brick instance for each test."""
    return KaliSecurityBrick()


class TestPortScanning:
    """Test port security scanning."""

    def test_default_port_scan(self, brick: KaliSecurityBrick) -> None:
        """Scan all known ports in the database."""
        report = brick.port_scan()
        assert report.scan_type == ScanType.PORT_SCAN
        assert report.status == "completed"
        assert len(report.findings) > 0
        assert "nmap" in report.tools_used

    def test_specific_port_scan(self, brick: KaliSecurityBrick) -> None:
        """Scan specific ports."""
        report = brick.port_scan(ports=[22, 443, 3389])
        assert len(report.findings) == 3
        ports_found = [f.affected_component for f in report.findings]
        assert "port:22" in ports_found
        assert "port:443" in ports_found
        assert "port:3389" in ports_found

    def test_critical_port_detection(self, brick: KaliSecurityBrick) -> None:
        """Critical ports are flagged appropriately."""
        report = brick.port_scan(ports=[23])  # Telnet
        telnet_finding = report.findings[0]
        assert telnet_finding.severity == VulnerabilitySeverity.CRITICAL
        assert "Telnet" in telnet_finding.title


class TestWebVulnerabilityScanning:
    """Test OWASP Top 10 web vulnerability assessment."""

    def test_web_scan_owasp(self, brick: KaliSecurityBrick) -> None:
        """Full OWASP Top 10 scan generates findings."""
        report = brick.web_vulnerability_scan(url="https://hugzai.com")
        assert report.scan_type == ScanType.WEB_SCAN
        assert len(report.findings) == 10  # OWASP Top 10
        assert "zap" in report.tools_used

    def test_web_scan_has_injection_check(self, brick: KaliSecurityBrick) -> None:
        """Injection check is included in web scan."""
        report = brick.web_vulnerability_scan()
        titles = [f.title for f in report.findings]
        assert any("Injection" in t for t in titles)

    def test_web_scan_has_auth_check(self, brick: KaliSecurityBrick) -> None:
        """Authentication failures check is included."""
        report = brick.web_vulnerability_scan()
        titles = [f.title for f in report.findings]
        assert any("Auth" in t for t in titles)


class TestPasswordAudit:
    """Test password strength auditing."""

    def test_weak_password(self, brick: KaliSecurityBrick) -> None:
        """Weak passwords are flagged as critical."""
        report = brick.password_audit("abc")
        assert len(report.findings) > 0
        severities = [f.severity for f in report.findings]
        assert VulnerabilitySeverity.CRITICAL in severities
        assert report.summary["strength"] in ("very_weak", "weak")

    def test_common_password_pattern(self, brick: KaliSecurityBrick) -> None:
        """Common passwords are detected."""
        report = brick.password_audit("password123")
        findings_text = [f.title for f in report.findings]
        assert any("Common" in t or "common" in t.lower() for t in findings_text)

    def test_strong_password(self, brick: KaliSecurityBrick) -> None:
        """Strong passwords get fewer findings."""
        report = brick.password_audit("Xk9#mQ$vL2!pR7@nW4")
        # Strong password should have high entropy
        assert report.summary["strength"] in ("strong", "very_strong")

    def test_crack_time_estimation(self, brick: KaliSecurityBrick) -> None:
        """Crack time is estimated for passwords."""
        report = brick.password_audit("test")
        assert "estimated_crack_time" in report.summary


class TestSSLScanning:
    """Test SSL/TLS configuration scanning."""

    def test_ssl_scan(self, brick: KaliSecurityBrick) -> None:
        """SSL scan generates TLS findings."""
        report = brick.ssl_scan(domain="hugzai.com")
        assert report.scan_type == ScanType.SSL_SCAN
        assert len(report.findings) > 0
        assert "sslscan" in report.tools_used

    def test_ssl_checks_tls13(self, brick: KaliSecurityBrick) -> None:
        """SSL scan checks for TLS 1.3 support."""
        report = brick.ssl_scan()
        titles = [f.title for f in report.findings]
        assert any("TLS 1.3" in t for t in titles)


class TestToolRegistry:
    """Test Kali Linux tool registry."""

    def test_list_all_tools(self, brick: KaliSecurityBrick) -> None:
        """List all available tools."""
        tools = brick.get_available_tools()
        assert len(tools) >= 17  # We registered 17+ tools

    def test_filter_by_category(self, brick: KaliSecurityBrick) -> None:
        """Filter tools by category."""
        web_tools = brick.get_available_tools(category=ToolCategory.WEB_APP)
        assert len(web_tools) >= 3  # zap, nikto, sqlmap, wpscan
        assert all(t["category"] == ToolCategory.WEB_APP for t in web_tools)

    def test_password_tools(self, brick: KaliSecurityBrick) -> None:
        """Password tools are registered."""
        pwd_tools = brick.get_available_tools(category=ToolCategory.PASSWORD)
        tool_ids = [t["id"] for t in pwd_tools]
        assert "john" in tool_ids
        assert "hashcat" in tool_ids
        assert "hydra" in tool_ids


class TestSecurityPosture:
    """Test security posture scoring."""

    def test_initial_posture(self, brick: KaliSecurityBrick) -> None:
        """Initial posture is perfect (no scans yet)."""
        posture = brick.get_security_posture()
        assert posture["security_score"] == 100
        assert posture["grade"] == "A+"
        assert posture["total_findings"] == 0

    def test_posture_after_scan(self, brick: KaliSecurityBrick) -> None:
        """Posture degrades after finding vulnerabilities."""
        brick.port_scan(ports=[23, 445, 3389])  # Critical ports
        posture = brick.get_security_posture()
        assert posture["security_score"] < 100
        assert posture["total_findings"] > 0
        assert posture["critical_high_count"] > 0

    def test_brick_status(self, brick: KaliSecurityBrick) -> None:
        """Brick status returns comprehensive info."""
        status = brick.get_brick_status()
        assert status["brick_name"] == "Kali Linux Security Brick"
        assert status["status"] == "active"
        assert status["tools_registered"] >= 17
        assert len(status["capabilities"]) >= 8
