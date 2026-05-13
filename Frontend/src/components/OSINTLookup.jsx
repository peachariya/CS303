import { useState } from "react";
import { api } from "../services/api";

export default function OSINTLookup() {
  const [target, setTarget] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleLookup() {
    if (!target.trim()) return;
    setLoading(true); setError(""); setResult(null);
    try {
      const data = await api.osintLookup(target);
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold mb-1">🔍 OSINT Lookup</h2>
        <p className="text-gray-400 text-sm">
          สืบค้นข้อมูลจาก VirusTotal และ WHOIS สำหรับ URL, Domain หรือ IP
        </p>
      </div>

      <div className="flex gap-3">
        <input
          type="text"
          value={target}
          onChange={e => setTarget(e.target.value)}
          placeholder="https://suspicious-domain.xyz หรือ IP address"
          className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500 font-mono"
          onKeyDown={e => e.key === "Enter" && handleLookup()}
        />
        <button
          onClick={handleLookup}
          disabled={loading || !target.trim()}
          className="px-5 py-2.5 bg-purple-600 hover:bg-purple-500 disabled:opacity-40 text-white font-medium rounded-lg transition text-sm whitespace-nowrap"
        >
          {loading ? "กำลังค้นหา..." : "🔍 Lookup"}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-900/40 border border-red-700 rounded-lg text-red-300 text-sm">❌ {error}</div>
      )}

      {result && (
        <div className="space-y-4">
          {/* Summary */}
          <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
            <p className="text-xs text-gray-400 mb-1">สรุปผล</p>
            <p className="text-sm text-gray-200">{result.summary}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* VirusTotal */}
            <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
              <div className="px-4 py-3 border-b border-gray-700 flex items-center gap-2">
                <span>🦠</span>
                <span className="font-semibold text-sm">VirusTotal</span>
              </div>
              <div className="px-4 py-4">
                {result.virustotal?.error ? (
                  <p className="text-yellow-400 text-sm">{result.virustotal.error}</p>
                ) : result.virustotal ? (
                  <div className="space-y-2">
                    {[
                      { label: "Malicious",  key: "malicious",  color: "text-red-400" },
                      { label: "Suspicious", key: "suspicious", color: "text-orange-400" },
                      { label: "Harmless",   key: "harmless",   color: "text-green-400" },
                      { label: "Undetected", key: "undetected", color: "text-gray-400" },
                    ].map(row => (
                      <div key={row.key} className="flex justify-between text-sm">
                        <span className="text-gray-400">{row.label}</span>
                        <span className={`font-bold ${row.color}`}>
                          {result.virustotal[row.key] ?? "-"}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">ไม่มีข้อมูล</p>
                )}
              </div>
            </div>

            {/* WHOIS */}
            <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
              <div className="px-4 py-3 border-b border-gray-700 flex items-center gap-2">
                <span>📋</span>
                <span className="font-semibold text-sm">WHOIS</span>
              </div>
              <div className="px-4 py-4">
                {result.whois?.error ? (
                  <p className="text-yellow-400 text-sm">{result.whois.error}</p>
                ) : result.whois ? (
                  <div className="space-y-2">
                    {[
                      { label: "Domain",      key: "domain_name" },
                      { label: "Registrar",   key: "registrar" },
                      { label: "สร้างเมื่อ", key: "creation_date" },
                      { label: "หมดอายุ",    key: "expiration_date" },
                      { label: "ประเทศ",     key: "country" },
                    ].map(row => (
                      <div key={row.key} className="flex justify-between text-sm gap-2">
                        <span className="text-gray-400 shrink-0">{row.label}</span>
                        <span className="text-gray-200 text-right truncate max-w-[180px]">
                          {result.whois[row.key] ?? "-"}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">ไม่มีข้อมูล</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
