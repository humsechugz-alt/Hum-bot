"""Security monitoring API endpoints."""

from fastapi import APIRouter, Request

from app.services.security_shield import security_shield

router = APIRouter(prefix="/security", tags=["Security"])


@router.post("/scan")
async def scan_input(request: Request, text: str) -> dict:
    """Scan text input for security threats."""
    client_ip = request.client.host if request.client else "unknown"

    report = security_shield.scan_input(text, source_ip=client_ip)

    return {
        "is_safe": report.is_safe,
        "risk_score": report.risk_score,
        "threats_detected": len(report.threats),
        "threats": [
            {
                "type": t.threat_type,
                "level": t.threat_level,
                "description": t.description,
                "blocked": t.blocked,
            }
            for t in report.threats
        ],
        "recommendations": report.recommendations,
    }


@router.get("/status")
async def security_status() -> dict:
    """Get current security status summary."""
    summary = security_shield.get_threat_summary()
    return {
        "status": "monitoring",
        "encryption": {
            "data_at_rest": "AES-256-GCM",
            "data_in_transit": "TLS 1.3",
            "key_management": "HashiCorp Vault (planned)",
        },
        "threat_summary": summary,
        "active_protections": [
            "SQL Injection Prevention",
            "XSS Protection",
            "Rate Limiting",
            "Brute Force Detection",
            "Input Sanitization",
            "Security Headers",
            "CORS Policy",
        ],
    }


@router.post("/fraud-check")
async def fraud_check(transaction_data: dict) -> dict:
    """Check a transaction for fraud indicators."""
    risk_score = security_shield.calculate_fraud_score(transaction_data)

    return {
        "risk_score": risk_score,
        "risk_level": (
            "low"
            if risk_score < 30
            else "medium"
            if risk_score < 60
            else "high"
            if risk_score < 80
            else "critical"
        ),
        "recommendation": (
            "Transaction approved"
            if risk_score < 30
            else "Review recommended"
            if risk_score < 60
            else "Manual verification required"
            if risk_score < 80
            else "Transaction blocked — contact support"
        ),
        "checks_performed": [
            "Amount threshold",
            "Transaction velocity",
            "Account age",
            "Location analysis",
        ],
    }
