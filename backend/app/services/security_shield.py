"""Cybersecurity Shield Layer — Threat detection, rate limiting, and security monitoring."""

import hashlib
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import StrEnum


class ThreatLevel(StrEnum):
    """Threat severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(StrEnum):
    """Types of detected threats."""

    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    BRUTE_FORCE = "brute_force"
    RATE_LIMIT = "rate_limit"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    FRAUD = "fraud"
    DATA_EXFILTRATION = "data_exfiltration"


@dataclass
class ThreatEvent:
    """Detected threat event."""

    threat_type: ThreatType
    threat_level: ThreatLevel
    source_ip: str
    description: str
    timestamp: float = field(default_factory=time.time)
    blocked: bool = False
    user_id: str | None = None
    metadata: dict | None = None


@dataclass
class SecurityReport:
    """Security status report."""

    is_safe: bool
    threats: list[ThreatEvent]
    risk_score: float  # 0-100
    recommendations: list[str]


# SQL Injection patterns
SQL_INJECTION_PATTERNS: list[str] = [
    "' or '1'='1",
    "'; drop table",
    "union select",
    "1=1--",
    "' or 1=1",
    "admin'--",
    "'; exec(",
    "select * from",
    "insert into",
    "delete from",
    "update set",
    "drop table",
    "alter table",
    "exec xp_",
    "execute sp_",
]

# XSS patterns
XSS_PATTERNS: list[str] = [
    "<script>",
    "javascript:",
    "onerror=",
    "onload=",
    "onclick=",
    "onmouseover=",
    "eval(",
    "document.cookie",
    "document.write",
    "innerHTML",
    "<iframe",
    "<object",
    "<embed",
    "expression(",
]

# Suspicious request patterns
SUSPICIOUS_PATTERNS: list[str] = [
    "../",
    "..\\",
    "/etc/passwd",
    "/etc/shadow",
    "cmd.exe",
    "powershell",
    "/bin/sh",
    "/bin/bash",
    "wget ",
    "curl ",
    "nc -e",
    "base64 --decode",
]


class RateLimiter:
    """In-memory rate limiter using sliding window."""

    def __init__(self) -> None:
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        """Check if a key has exceeded the rate limit."""
        now = time.time()
        window_start = now - window_seconds

        # Clean old entries
        self._requests[key] = [ts for ts in self._requests[key] if ts > window_start]

        if len(self._requests[key]) >= max_requests:
            return True

        self._requests[key].append(now)
        return False

    def get_remaining(self, key: str, max_requests: int, window_seconds: int = 60) -> int:
        """Get remaining requests in the current window."""
        now = time.time()
        window_start = now - window_seconds
        current = len([ts for ts in self._requests[key] if ts > window_start])
        return max(0, max_requests - current)


class SecurityShield:
    """Main security shield for threat detection and prevention."""

    def __init__(self) -> None:
        self.rate_limiter = RateLimiter()
        self._threat_log: list[ThreatEvent] = []
        self._blocked_ips: set[str] = set()

    def scan_input(self, text: str, source_ip: str, user_id: str | None = None) -> SecurityReport:
        """Scan user input for security threats."""
        threats: list[ThreatEvent] = []
        text_lower = text.lower()

        # Check SQL injection
        for pattern in SQL_INJECTION_PATTERNS:
            if pattern in text_lower:
                threats.append(
                    ThreatEvent(
                        threat_type=ThreatType.SQL_INJECTION,
                        threat_level=ThreatLevel.HIGH,
                        source_ip=source_ip,
                        description=f"SQL injection pattern detected: '{pattern}'",
                        blocked=True,
                        user_id=user_id,
                    )
                )
                break

        # Check XSS
        for pattern in XSS_PATTERNS:
            if pattern in text_lower:
                threats.append(
                    ThreatEvent(
                        threat_type=ThreatType.XSS,
                        threat_level=ThreatLevel.HIGH,
                        source_ip=source_ip,
                        description=f"XSS pattern detected: '{pattern}'",
                        blocked=True,
                        user_id=user_id,
                    )
                )
                break

        # Check suspicious patterns
        for pattern in SUSPICIOUS_PATTERNS:
            if pattern in text_lower:
                threats.append(
                    ThreatEvent(
                        threat_type=ThreatType.SUSPICIOUS_PATTERN,
                        threat_level=ThreatLevel.MEDIUM,
                        source_ip=source_ip,
                        description=f"Suspicious pattern detected: '{pattern}'",
                        blocked=True,
                        user_id=user_id,
                    )
                )
                break

        # Calculate risk score
        risk_score = self._calculate_risk_score(threats)

        # Generate recommendations
        recommendations = self._generate_recommendations(threats)

        # Log threats
        self._threat_log.extend(threats)

        # Auto-block IP if critical threat
        if risk_score >= 80:
            self._blocked_ips.add(source_ip)

        return SecurityReport(
            is_safe=len(threats) == 0,
            threats=threats,
            risk_score=risk_score,
            recommendations=recommendations,
        )

    def is_ip_blocked(self, ip: str) -> bool:
        """Check if an IP is blocked."""
        return ip in self._blocked_ips

    def check_rate_limit(self, key: str, tier: str = "free") -> bool:
        """Check rate limit based on user tier."""
        limits = {
            "free": 60,
            "pro": 1000,
            "enterprise": 10000,
        }
        max_requests = limits.get(tier, 60)
        return self.rate_limiter.is_rate_limited(key, max_requests)

    def get_rate_limit_remaining(self, key: str, tier: str = "free") -> int:
        """Get remaining rate limit for a key."""
        limits = {
            "free": 60,
            "pro": 1000,
            "enterprise": 10000,
        }
        max_requests = limits.get(tier, 60)
        return self.rate_limiter.get_remaining(key, max_requests)

    def monitor_login_attempt(
        self,
        ip: str,
        success: bool,
        user_id: str | None = None,
    ) -> ThreatEvent | None:
        """Monitor login attempts for brute force detection."""
        key = f"login:{ip}"
        if not success and self.rate_limiter.is_rate_limited(
            key, max_requests=5, window_seconds=300
        ):
            threat = ThreatEvent(
                threat_type=ThreatType.BRUTE_FORCE,
                threat_level=ThreatLevel.HIGH,
                source_ip=ip,
                description="Brute force login attempt detected (5+ failures in 5 minutes)",
                blocked=True,
                user_id=user_id,
            )
            self._threat_log.append(threat)
            self._blocked_ips.add(ip)
            return threat
        return None

    def calculate_fraud_score(self, transaction_data: dict) -> float:
        """Calculate fraud risk score for a transaction (0-100)."""
        score = 0.0

        amount = transaction_data.get("amount", 0)
        if amount > 5000:
            score += 30
        elif amount > 1000:
            score += 15

        # Check for rapid transactions
        if transaction_data.get("transactions_last_hour", 0) > 10:
            score += 25

        # Check for new account
        if transaction_data.get("account_age_days", 0) < 7:
            score += 20

        # Check for unusual location
        if transaction_data.get("unusual_location", False):
            score += 25

        return min(score, 100)

    def generate_request_fingerprint(self, ip: str, user_agent: str, headers: dict) -> str:
        """Generate a fingerprint for request tracking."""
        accept_lang = headers.get("accept-language", "")
        accept_enc = headers.get("accept-encoding", "")
        data = f"{ip}:{user_agent}:{accept_lang}:{accept_enc}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def get_threat_summary(self) -> dict:
        """Get a summary of recent threats."""
        now = time.time()
        recent = [t for t in self._threat_log if now - t.timestamp < 3600]  # Last hour

        summary: dict[str, int] = defaultdict(int)
        for threat in recent:
            summary[threat.threat_type] += 1

        return {
            "total_threats_last_hour": len(recent),
            "blocked_ips": len(self._blocked_ips),
            "threats_by_type": dict(summary),
            "highest_severity": max((t.threat_level for t in recent), default="none"),
        }

    @staticmethod
    def _calculate_risk_score(threats: list[ThreatEvent]) -> float:
        """Calculate overall risk score from detected threats."""
        if not threats:
            return 0.0

        severity_weights = {
            ThreatLevel.LOW: 10,
            ThreatLevel.MEDIUM: 30,
            ThreatLevel.HIGH: 60,
            ThreatLevel.CRITICAL: 100,
        }

        total = sum(severity_weights.get(t.threat_level, 0) for t in threats)
        return min(total, 100.0)

    @staticmethod
    def _generate_recommendations(threats: list[ThreatEvent]) -> list[str]:
        """Generate security recommendations based on detected threats."""
        recommendations: list[str] = []

        threat_types = {t.threat_type for t in threats}

        if ThreatType.SQL_INJECTION in threat_types:
            recommendations.append(
                "Input contains SQL injection patterns. Request has been blocked."
            )
        if ThreatType.XSS in threat_types:
            recommendations.append("Input contains XSS patterns. Content has been sanitized.")
        if ThreatType.BRUTE_FORCE in threat_types:
            recommendations.append(
                "Multiple failed login attempts detected. Account temporarily locked."
            )
        if ThreatType.SUSPICIOUS_PATTERN in threat_types:
            recommendations.append(
                "Suspicious request pattern detected. Request logged for review."
            )

        if not recommendations:
            recommendations.append("No threats detected. Request is safe to process.")

        return recommendations


# Global security shield instance
security_shield = SecurityShield()
