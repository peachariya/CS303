import { useState } from "react";
import { api } from "../services/api";
import RiskBadge from "./RiskBadge";

const SAMPLE_SMS = [
  "แจ้งเตือนด่วน: บัญชีของท่านถูกระงับ กรุณายืนยันตัวตนภายใน 24 ชั่วโมง คลิก http://kbank-verify.xyz/confirm",
  "ยินดีด้วยคุณได้รับรางวัลจากกรมสรรพากร 50,000 บาท กดรับรางวัล http://rd-reward.top",
  "ธนาคารกสิกรไทย: ยอดใช้จ่ายบัตรเครดิตของท่านเมื่อวานนี้ 2,500.00 บาท",
];

export default function SMSAnalyzer() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAnalyze() {
    if (!text.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await api.analyzeSMS(text);
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
        <h2 className="text-xl font-bold mb-1">📩 วิเคราะห์ข้อความ SMS หลอกลวง</h2>
        <p className="text-gray-400 text-sm">
          วางข้อความ SMS ที่ต้องการตรวจสอบ ระบบจะวิเคราะห์ด้วย NLP ภาษาไทย
        </p>
      </div>

      {/* Sample buttons */}
      <div className="flex flex-wrap gap-2">
        <span className="text-xs text-gray-500 self-center">ตัวอย่าง:</span>
        {SAMPLE_SMS.map((s, i) => (
          <button
            key={i}
            onClick={() => setText(s)}
            className="text-xs px-3 py-1 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-full border border-gray-700 transition"
          >
            ตัวอย่าง {i + 1}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="space-y-3">
        <textarea
          rows={5}
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder="วางข้อความ SMS ที่ต้องการวิเคราะห์..."
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none"
        />
        <button
          onClick={handleAnalyze}
          disabled={loading || !text.trim()}
          className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium rounded-lg transition text-sm"
        >
          {loading ? "กำลังวิเคราะห์..." : "🔍 วิเคราะห์"}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-900/40 border border-red-700 rounded-lg text-red-300 text-sm">
          ❌ {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
            <span className="font-semibold">ผลการวิเคราะห์</span>
            <RiskBadge level={result.risk_level} />
          </div>

          <div className="px-6 py-5 space-y-4">
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

            {/* Explanation */}
            <div className="p-3 bg-gray-900 rounded-lg text-sm text-gray-300">
              {result.explanation}
            </div>

            {/* Patterns */}
            {result.detected_patterns.length > 0 && (
              <div>
                <p className="text-xs text-gray-400 mb-2">รูปแบบที่พบ</p>
                <div className="flex flex-wrap gap-2">
                  {result.detected_patterns.map(p => (
                    <span key={p} className="px-2 py-1 bg-orange-900/50 text-orange-300 text-xs rounded border border-orange-800">
                      {p}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Keywords */}
            {result.suspicious_keywords.length > 0 && (
              <div>
                <p className="text-xs text-gray-400 mb-2">คำ/ลิงก์ที่น่าสงสัย</p>
                <div className="flex flex-wrap gap-2">
                  {result.suspicious_keywords.map((kw, i) => (
                    <code key={i} className="px-2 py-0.5 bg-gray-900 text-red-300 text-xs rounded font-mono">
                      {kw}
                    </code>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
