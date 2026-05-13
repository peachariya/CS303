"""
บริการสืบค้นข้อมูลสาธารณะ (OSINT)
- VirusTotal API: ตรวจสอบ URL/IP/Domain
- WHOIS: ดึงข้อมูลการจดทะเบียนโดเมน
"""

import os
import httpx
import whois
from typing import Optional
from app.models.schemas import OSINTResponse

VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")
VT_BASE_URL = "https://www.virustotal.com/api/v3"


async def query_virustotal(target: str) -> Optional[dict]:
    """ส่ง URL/domain ไปตรวจสอบกับ VirusTotal"""
    if not VIRUSTOTAL_API_KEY:
        return {"error": "ไม่ได้ตั้งค่า VIRUSTOTAL_API_KEY"}

    headers = {"x-apikey": VIRUSTOTAL_API_KEY}

    # แปลง URL เป็น base64 ตาม VirusTotal spec
    import base64
    url_id = base64.urlsafe_b64encode(target.encode()).decode().strip("=")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{VT_BASE_URL}/urls/{url_id}",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                return {
                    "malicious": stats.get("malicious", 0),
                    "suspicious": stats.get("suspicious", 0),
                    "harmless": stats.get("harmless", 0),
                    "undetected": stats.get("undetected", 0),
                    "reputation": data.get("data", {}).get("attributes", {}).get("reputation", 0),
                }
            elif response.status_code == 404:
                # ยังไม่เคย scan → ส่งไป scan ก่อน
                async with httpx.AsyncClient(timeout=10.0) as c2:
                    scan_resp = await c2.post(
                        f"{VT_BASE_URL}/urls",
                        headers=headers,
                        data={"url": target}
                    )
                    if scan_resp.status_code == 200:
                        return {"status": "queued", "message": "URL ถูกส่งไปวิเคราะห์แล้ว กรุณารอสักครู่"}
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def query_whois(domain: str) -> Optional[dict]:
    """ดึงข้อมูล WHOIS ของโดเมน"""
    try:
        # ตัด protocol ออก
        domain_clean = domain.replace("https://", "").replace("http://", "").split("/")[0]
        w = whois.whois(domain_clean)
        return {
            "domain_name": str(w.domain_name) if w.domain_name else None,
            "registrar": w.registrar,
            "creation_date": str(w.creation_date) if w.creation_date else None,
            "expiration_date": str(w.expiration_date) if w.expiration_date else None,
            "country": w.country,
            "name_servers": w.name_servers if isinstance(w.name_servers, list) else [w.name_servers],
        }
    except Exception as e:
        return {"error": str(e)}


def build_summary(vt_result: Optional[dict], whois_result: Optional[dict]) -> str:
    """สร้างสรุปผลการค้นหา OSINT เป็นภาษาไทย"""
    parts = []

    if vt_result and "malicious" in vt_result:
        mal = vt_result["malicious"]
        sus = vt_result["suspicious"]
        if mal > 0:
            parts.append(f"VirusTotal พบว่า {mal} engine ระบุว่าเป็นอันตราย")
        elif sus > 0:
            parts.append(f"VirusTotal พบว่า {sus} engine ระบุว่าน่าสงสัย")
        else:
            parts.append("VirusTotal ไม่พบภัยคุกคาม")

    if whois_result and "error" not in whois_result:
        reg = whois_result.get("registrar", "ไม่ทราบ")
        created = whois_result.get("creation_date", "ไม่ทราบ")
        parts.append(f"จดทะเบียนโดย: {reg} | วันที่สร้าง: {created}")

    return " | ".join(parts) if parts else "ไม่สามารถดึงข้อมูล OSINT ได้"


async def run_osint(target: str) -> OSINTResponse:
    """รัน OSINT pipeline ทั้งหมด"""
    vt_result    = await query_virustotal(target)
    whois_result = query_whois(target)
    summary      = build_summary(vt_result, whois_result)

    return OSINTResponse(
        target=target,
        virustotal=vt_result,
        whois=whois_result,
        summary=summary,
    )
