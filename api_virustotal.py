import requests
import base64

def scan_virustotal(url, api_key):
    # เข้ารหัส URL เป็น Base64 ตามกฎของ VirusTotal
    url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
    headers = {"accept": "application/json", "x-apikey": api_key}
    
    try:
        res = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()['data']['attributes']['last_analysis_stats']
        elif res.status_code == 404:
            return "NOT_FOUND"
        else:
            return "ERROR"
    except:
        return "ERROR"