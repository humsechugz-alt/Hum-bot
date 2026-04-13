"""Medusa Virus Shield API endpoints."""

from fastapi import APIRouter, status

from app.services.medusa_shield import (
    ThreatCategory,
    medusa_shield,
)

router = APIRouter(prefix="/medusa", tags=["Medusa Virus Shield"])


@router.get("/status")
async def shield_status() -> dict:
    """Get Medusa Virus Shield operational status."""
    return medusa_shield.get_shield_status()


@router.post("/scan")
async def scan_content(
    content: str,
    filename: str = "",
    deep_scan: bool = False,
) -> dict:
    """Scan content for malware and threats using Medusa Shield.

    All 7 detection heads work in parallel:
    - Signature matching
    - Heuristic analysis
    - Sandbox execution
    - Memory scanning
    - Network anomaly detection
    - File integrity monitoring
    - AI-powered zero-day detection
    """
    result = medusa_shield.scan_content(
        content=content,
        filename=filename,
        deep_scan=deep_scan,
    )

    return {
        "scan_id": result.scan_id,
        "status": result.status,
        "risk_score": result.risk_score,
        "threats_found": len(result.threats_found),
        "threats": result.threats_found,
        "heads_activated": [h.value for h in result.heads_activated],
        "files_scanned": result.files_scanned,
        "bytes_scanned": result.bytes_scanned,
        "scan_duration_ms": result.scan_duration_ms,
        "recommendations": result.recommendations,
        "timestamp": result.timestamp.isoformat(),
    }


@router.post("/quarantine", status_code=status.HTTP_201_CREATED)
async def quarantine_threat(
    content_path: str,
    threat_name: str,
    category: str = "malware",
    severity: int = 5,
) -> dict:
    """Quarantine a detected threat."""
    entry = medusa_shield.quarantine_threat(
        content_path=content_path,
        threat_name=threat_name,
        category=ThreatCategory(category),
        severity=severity,
    )

    return {
        "id": entry.id,
        "original_path": entry.original_path,
        "threat_name": entry.threat_name,
        "category": entry.threat_category,
        "severity": entry.severity,
        "quarantined_at": entry.quarantined_at.isoformat(),
        "neutralized": entry.neutralized,
    }


@router.post("/quarantine/{quarantine_id}/neutralize")
async def neutralize_threat(quarantine_id: str) -> dict:
    """Neutralize a quarantined threat."""
    success = medusa_shield.neutralize_threat(quarantine_id)
    return {
        "quarantine_id": quarantine_id,
        "neutralized": success,
        "message": ("Threat neutralized successfully" if success else "Quarantine entry not found"),
    }


@router.get("/quarantine")
async def list_quarantine() -> dict:
    """List all quarantined threats."""
    entries = medusa_shield.get_quarantine_list()
    return {
        "quarantine": [
            {
                "id": e.id,
                "threat_name": e.threat_name,
                "category": e.threat_category,
                "severity": e.severity,
                "quarantined_at": e.quarantined_at.isoformat(),
                "neutralized": e.neutralized,
            }
            for e in entries
        ],
        "total": len(entries),
    }


@router.post("/block-hash")
async def block_hash(file_hash: str) -> dict:
    """Add a known malicious file hash to the block list."""
    medusa_shield.add_blocked_hash(file_hash)
    return {
        "hash": file_hash,
        "status": "blocked",
        "message": "Hash added to Medusa Shield block list",
    }
