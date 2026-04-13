"""Kali Linux Security Brick API endpoints."""

from fastapi import APIRouter, Body

from app.services.kali_brick import (
    ScanType,
    ToolCategory,
    kali_brick,
)

router = APIRouter(prefix="/kali", tags=["Kali Security Brick"])


@router.get("/status")
async def brick_status() -> dict:
    """Get Kali Security Brick operational status."""
    return kali_brick.get_brick_status()


@router.get("/tools")
async def list_tools(category: str | None = None) -> dict:
    """List available Kali Linux security tools."""
    cat = ToolCategory(category) if category else None
    tools = kali_brick.get_available_tools(category=cat)
    return {
        "tools": tools,
        "total": len(tools),
        "categories": [c.value for c in ToolCategory],
    }


@router.post("/scan/ports")
async def port_scan(ports: list[int] | None = None) -> dict:
    """Run a defensive port security scan (Nmap-style).

    Checks ports against known vulnerability database.
    """
    report = kali_brick.port_scan(ports=ports)
    return _format_report(report)


@router.post("/scan/web")
async def web_scan(url: str = "") -> dict:
    """Run OWASP Top 10 web vulnerability assessment (ZAP-style)."""
    report = kali_brick.web_vulnerability_scan(url=url)
    return _format_report(report)


@router.post("/scan/password")
async def password_audit(password: str = Body(..., embed=True)) -> dict:
    """Audit password strength (John the Ripper / Hashcat-style).

    Evaluates password entropy, complexity, common patterns,
    and estimated crack time.
    """
    report = kali_brick.password_audit(password=password)
    return _format_report(report)


@router.post("/scan/ssl")
async def ssl_scan(domain: str = "hugzai.com") -> dict:
    """Scan SSL/TLS configuration (SSLScan-style)."""
    report = kali_brick.ssl_scan(domain=domain)
    return _format_report(report)


@router.get("/posture")
async def security_posture() -> dict:
    """Get overall security posture score and grade."""
    return kali_brick.get_security_posture()


@router.get("/scan-types")
async def available_scan_types() -> dict:
    """List available security scan types."""
    return {
        "scan_types": [
            {
                "id": st.value,
                "name": st.value.replace("_", " ").title(),
                "description": _scan_type_description(st),
            }
            for st in ScanType
        ],
    }


def _format_report(report: "SecurityScanReport") -> dict:  # type: ignore[name-defined]  # noqa: F821
    """Format a security scan report for API response."""
    return {
        "scan_id": report.scan_id,
        "scan_type": report.scan_type,
        "target": report.target,
        "status": report.status,
        "findings": [
            {
                "id": f.id,
                "title": f.title,
                "description": f.description,
                "severity": f.severity,
                "category": f.category,
                "affected_component": f.affected_component,
                "cvss_score": f.cvss_score,
                "cve_id": f.cve_id,
                "remediation": f.remediation,
            }
            for f in report.findings
        ],
        "summary": report.summary,
        "tools_used": report.tools_used,
        "scan_duration_ms": report.scan_duration_ms,
        "timestamp": report.timestamp.isoformat(),
    }


def _scan_type_description(scan_type: ScanType) -> str:
    """Get description for a scan type."""
    descriptions = {
        ScanType.PORT_SCAN: "Network port scanning for open/vulnerable ports",
        ScanType.VULN_SCAN: "Comprehensive vulnerability assessment",
        ScanType.WEB_SCAN: "OWASP Top 10 web application security testing",
        ScanType.SSL_SCAN: "SSL/TLS configuration and certificate analysis",
        ScanType.DNS_SCAN: "DNS security configuration assessment",
        ScanType.PASSWORD_AUDIT: "Password strength and policy auditing",
        ScanType.NETWORK_RECON: "Network reconnaissance and discovery",
        ScanType.COMPLIANCE_SCAN: "Compliance standards verification",
    }
    return descriptions.get(scan_type, "Security scan")
