"""Tests for Security Shield."""

from app.services.security_shield import SecurityShield, ThreatLevel, ThreatType


def test_sql_injection_detection() -> None:
    """Test SQL injection pattern detection."""
    shield = SecurityShield()
    report = shield.scan_input("' or '1'='1", source_ip="1.2.3.4")
    assert not report.is_safe
    assert report.risk_score > 0
    assert any(t.threat_type == ThreatType.SQL_INJECTION for t in report.threats)


def test_xss_detection() -> None:
    """Test XSS pattern detection."""
    shield = SecurityShield()
    report = shield.scan_input("<script>alert('xss')</script>", source_ip="1.2.3.4")
    assert not report.is_safe
    assert any(t.threat_type == ThreatType.XSS for t in report.threats)


def test_safe_input() -> None:
    """Test that normal input passes security scan."""
    shield = SecurityShield()
    report = shield.scan_input("Hello, how are you today?", source_ip="1.2.3.4")
    assert report.is_safe
    assert report.risk_score == 0


def test_rate_limiting() -> None:
    """Test rate limiting functionality."""
    shield = SecurityShield()
    key = "test-user"

    # Should not be rate limited for the first 60 requests
    for _ in range(60):
        assert not shield.check_rate_limit(key, tier="free")

    # The 61st request should be rate limited
    assert shield.check_rate_limit(key, tier="free")


def test_brute_force_detection() -> None:
    """Test brute force login detection."""
    shield = SecurityShield()
    ip = "192.168.1.1"

    # First 5 failed login attempts should not trigger (limit is 5)
    for _ in range(5):
        result = shield.monitor_login_attempt(ip, success=False)
        assert result is None

    # 6th attempt should trigger brute force detection
    result = shield.monitor_login_attempt(ip, success=False)
    assert result is not None
    assert result.threat_type == ThreatType.BRUTE_FORCE
    assert result.threat_level == ThreatLevel.HIGH


def test_fraud_score_calculation() -> None:
    """Test fraud risk score calculation."""
    shield = SecurityShield()

    # Low risk transaction
    low_risk = shield.calculate_fraud_score(
        {
            "amount": 50,
            "transactions_last_hour": 2,
            "account_age_days": 365,
        }
    )
    assert low_risk < 30

    # High risk transaction
    high_risk = shield.calculate_fraud_score(
        {
            "amount": 9999,
            "transactions_last_hour": 15,
            "account_age_days": 1,
            "unusual_location": True,
        }
    )
    assert high_risk >= 80


def test_ip_blocking() -> None:
    """Test IP blocking on critical threat."""
    shield = SecurityShield()
    ip = "10.0.0.1"

    assert not shield.is_ip_blocked(ip)

    # Trigger SQL injection + XSS to exceed risk_score >= 80
    shield.scan_input(
        "' or '1'='1 <script>alert(1)</script> ../etc/passwd",
        source_ip=ip,
    )
    assert shield.is_ip_blocked(ip)


def test_request_fingerprint() -> None:
    """Test request fingerprint generation."""
    shield = SecurityShield()
    fp = shield.generate_request_fingerprint(
        ip="1.2.3.4",
        user_agent="Mozilla/5.0",
        headers={"accept-language": "en-US"},
    )
    assert len(fp) == 16
    # Same input should produce same fingerprint
    fp2 = shield.generate_request_fingerprint(
        ip="1.2.3.4",
        user_agent="Mozilla/5.0",
        headers={"accept-language": "en-US"},
    )
    assert fp == fp2


def test_threat_summary() -> None:
    """Test threat summary generation."""
    shield = SecurityShield()
    # Trigger multiple threats to ensure blocked IPs
    shield.scan_input(
        "<script>alert(1)</script> ' or 1=1-- ../etc/passwd",
        source_ip="1.1.1.1",
    )

    summary = shield.get_threat_summary()
    assert summary["total_threats_last_hour"] >= 1
    assert summary["blocked_ips"] >= 1
