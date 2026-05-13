import { useState } from "react";
import { api } from "../services/api";
import RiskBadge from "./RiskBadge";

const SAMPLE_URLS = [
  "http://kbank-secure-verify.xyz/login?ref=12345",
  "https://www.kasikornbank.com",
  "http://192.168.1.1/rd-reward/confirm",
];

export default function URLAnalyzer() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAnalyze() {
    if (!url.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await api.analyzeURL(url);
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
        <h2 className="text-xl font-bold mb-1">🔗 วิเคราะห์ URL / Phishing</h2>
        <p className="text-gray-400 text-sm">
          ตรวจสอบว่า URL เป็นเว็บไซต์ตกเบ็ด (Phishing) หรือไม่
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        <span className="text-xs text-gray-500 self-center">ตัวอย่าง:</span>
        {SAMPLE_URLS.map((u, i) => (
          <button
            key={i}
            onClick={() => setUrl(u)}
            className="text-xs px-3 py-1 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-full border border-gray-700 transition truncate max-w-[200px]"
            title={u}
          >
            {u.replace("https://", "").replace("http://", "").slice(0, 30)}...
          </button>
        ))}
      </div>

      <div className="flex gap-3">
        <input
          type="text"
          value={url}
          onChange={e => setUrl(e.target.value)}
          placeholder="https://example.com หรือ URL ที่ต้องการตรวจสอบ"
          className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500 font-mono"
          onKeyDown={e => e.key === "Enter" && handleAnalyze()}
        />
        <button
          onClick={handleAnalyze}
          disabled={loading || !url.trim()}
          className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium rounded-lg transition text-sm whitespace-nowrap"
        >
          {loading ? "กำลังตรวจ..." : "🔍 ตรวจสอบ"}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-900/40 border border-red-700 rounded-lg text-red-300 text-sm">
          ❌ {error}
        </div>
      )}

      {result && (
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
            <code className="text-sm text-gray-300 truncate max-w-md">{result.url}</code>
            <RiskBadge level={result.risk_level} />
          </div>

          <div className="px-6 py-5 space-y-4">
            {/* Phishing verdict */}
            <div className={`flex items-center gap-3 p-3 rounded-lg ${
              result.is_phishing
                ? "bg-red-900/30 border border-red-800"
                : "bg-green-900/30 border border-green-800"
            }`}>
              <span className="text-2xl">{result.is_phishing ? "⚠️" : "✅"}</span>
              <span className="font-semibold text-sm">
                {result.is_phishing
                  ? "ตรวจพบว่าเป็นเว็บไซต์ตกเบ็ด (Phishing) ที่น่าสงสัย"
                  : "URL นี้ดูปลอดภัย ไม่พบรูปแบบ Phishing"}
              </span>
            </div>

            {/* Score bar */}
            <div>
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span>Risk Score</span>
                <span>{(result.risk_score * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${
                    result.risk_score >= 0.75 ? "bg-red-500" :
                    result.risk_score >= 0.50 ? "bg-orange-500" :
                    result.risk_score >= 0.25 ? "bg-yellow-500" : "bg-green-500"
                  }`}
                  style={{ width: `${result.risk_score * 100}%` }}
                />
              </div>
            </div>

            <div className="p-3 bg-gray-900 rounded-lg text-sm text-gray-300">
              {result.explanation}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
