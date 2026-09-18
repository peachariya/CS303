import React, { useState } from 'react';

export default function App() {
  const [smsText, setSmsText] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // ฟังก์ชันกดปุ่ม "วิเคราะห์" ส่งข้อมูลเข้า Backend API
  const handleAnalyzeSms = async () => {
    if (!smsText.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/check/sms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: smsText }),
      });
      const data = await response.json();
      setAnalysisResult(data); // เก็บผลลัพธ์เพื่อเอาไปแสดงบนหน้าเว็บ
    } catch (error) {
      console.error('Connection error:', error);
      alert('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์วิเคราะห์ได้');
    } finally {
      setLoading(false);
    }
  };

  // กำหนดสีของสถานะตามระดับความเสี่ยง (0=เขียว, 1=เหลือง/ส้ม, 2=แดง)
  const getStatusColor = (level) => {
    if (level === 2) return '#ef4444'; // หลอกลวง (แดง)
    if (level === 1) return '#f59e0b'; // น่าสงสัย (เหลือง/ส้ม)
    return '#22c55e'; // ปลอดภัย (เขียว)
  };

  return (
    <div style={{ padding: '30px', color: '#fff', background: '#0f172a', minHeight: '100vh' }}>
      <h2>🛡️ วิเคราะห์ข้อความ SMS หลอกลวง</h2>
      <p style={{ color: '#94a3b8', fontSize: '14px' }}>วางข้อความ SMS ที่ต้องการตรวจสอบ ระบบจะวิเคราะห์ด้วย Machine Learning (3 ระดับความเสี่ยง)</p>
      
      <div style={{ marginTop: '20px' }}>
        <textarea 
          rows="4"
          style={{ width: '100%', background: '#1e293b', color: '#fff', padding: '12px', borderRadius: '8px', border: '1px solid #475569', fontSize: '15px' }}
          value={smsText} 
          onChange={(e) => setSmsText(e.target.value)} 
          placeholder="วางข้อความ SMS ที่ต้องการตรวจสอบที่นี่..."
        />
      </div>
      
      <br />
      
      <button 
        onClick={handleAnalyzeSms}
        disabled={loading}
        style={{ padding: '10px 24px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', fontSize: '15px' }}
      >
        {loading ? 'กำลังวิเคราะห์...' : 'วิเคราะห์ความเสี่ยง'}
      </button>

      {/* ส่วนแสดง Output ตามรูปแบบ 3 ระดับ */}
      {analysisResult && (
        <div style={{ marginTop: '25px', padding: '20px', background: '#1e293b', borderRadius: '8px', border: '1px solid #475569' }}>
          <h3 style={{ marginTop: 0, borderBottom: '1px solid #475569', paddingBottom: '10px' }}>ผลการวิเคราะห์ (Analysis Output):</h3>
          <p style={{ fontSize: '16px' }}>
            สถานะ: <strong style={{ color: getStatusColor(analysisResult.risk_level) }}>{analysisResult.status}</strong>
          </p>
          <p>
            ระดับความเสี่ยง (Risk Level): <strong>{analysisResult.risk_level}</strong> 
            <span style={{ color: '#94a3b8', marginLeft: '8px' }}>(0 = ปลอดภัย, 1 = น่าสงสัย, 2 = หลอกลวงแน่นอน)</span>
          </p>
          <p style={{ color: '#cbd5e1', background: '#0f172a', padding: '10px', borderRadius: '6px', marginTop: '10px' }}>
            <strong>คำอธิบาย:</strong> {analysisResult.description}
          </p>
        </div>
      )}
    </div>
  );
}