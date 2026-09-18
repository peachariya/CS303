import React, { useState } from 'react';

export default function SmsAnalysis() {
  const [smsText, setSmsText] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // ตัวอย่างข้อความจำลอง (คลิกเพื่อเติมข้อความอัตโนมัติได้)
  const SAMPLE_SMS = [
  // LOW (score 0.0) - ไม่มีคำในกลุ่ม SCAM_KEYWORDS เลย
  "ธนาคารกสิกรไทย: ยอดใช้จ่ายบัตรเครดิตของท่านเมื่อวานนี้ 2,500.00 บาท",
  // MEDIUM (score 0.3) - เข้าเงื่อนไขกลุ่ม "impersonation" เพียงอย่างเดียว
  "กรมสรรพากรแจ้งเตือนเรื่องภาษีเงินได้ประจำปีของท่าน กรุณาตรวจสอบรายละเอียดในระบบภายในเดือนนี้",
  // HIGH (score 0.65) - เข้ากลุ่ม "urgent" + "link" + มี URL แนบ
  "แจ้งเตือนด่วน: บัญชีของท่านถูกระงับ กรุณายืนยันตัวตนภายใน 24 ชั่วโมง คลิก http://kbank-verify.xyz/confirm",
  // CRITICAL (score 0.9) - เข้ากลุ่ม "urgent" + "impersonation" + "threat" + มีเบอร์โทรฝังในข้อความ
  "เรียน ท่านมีหมายจับจากศาล กรุณาติดต่อกลับด่วนที่ 0891234567 มิฉะนั้นจะถูกดำเนินคดีและบัญชีถูกอายัดทันที",
];

  // ฟังก์ชันยิง API ไปหา Backend ที่เรารันไว้
  const handleAnalyze = async () => {
    if (!smsText.trim()) return;

    setLoading(true);
    setAnalysisResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/check/sms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: smsText }),
      });
      const data = await response.json();
      setAnalysisResult(data);
    } catch (error) {
      console.error('Connection error:', error);
      alert('ไม่สามารถเชื่อมต่อกับ Backend ได้ กรุณาตรวจสอบว่ารัน uvicorn แล้วหรือยัง');
    } finally {
      setLoading(false);
    }
  };

  // กำหนดสีตาม 3 ระดับความเสี่ยง
  const getStatusColor = (level) => {
    if (level === 2) return '#ef4444'; // สีแดง (หลอกลวง)
    if (level === 1) return '#f59e0b'; // สีส้ม/เหลือง (น่าสงสัย)
    return '#22c55e'; // สีเขียว (ปลอดภัย)
  };

  return (
    <div style={{ padding: '20px', color: '#fff' }}>
      <div style={{ marginBottom: '20px' }}>
        <h2 style={{ margin: '0 0 5px 0' }}>📬 วิเคราะห์ข้อความ SMS หลอกลวง</h2>
        <p style={{ color: '#94a3b8', fontSize: '14px', margin: 0 }}>
          วางข้อความ SMS ที่ต้องการตรวจสอบ ระบบจะวิเคราะห์ด้วย Machine Learning ภาษาไทย
        </p>
      </div>

      {/* ปุ่มเลือกข้อความตัวอย่าง */}
      <div style={{ marginBottom: '15px', display: 'flex', gap: '10px', alignItems: 'center' }}>
        <span style={{ fontSize: '13px', color: '#94a3b8' }}>คำถาม:</span>
        {samples.map((sample, idx) => (
          <button
            key={idx}
            onClick={() => setSmsText(sample)}
            style={{
              background: '#1e293b',
              border: '1px solid #475569',
              color: '#cbd5e1',
              padding: '5px 10px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            ตัวอย่าง {idx + 1}
          </button>
        ))}
      </div>

      {/* ช่องกรอกข้อความ (รองรับข้อความยาวๆ เหมือนคำร้องทุกข์จริง) */}
      <div style={{ marginBottom: '15px' }}>
        <textarea
          rows="5"
          value={smsText}
          onChange={(e) => setSmsText(e.target.value)}
          placeholder="วางข้อความ SMS ที่ต้องการตรวจสอบ..."
          style={{
            width: '100%',
            background: '#1e293b',
            color: '#fff',
            padding: '12px',
            borderRadius: '8px',
            border: '1px solid #475569',
            fontSize: '14px',
            resize: 'vertical'
          }}
        />
      </div>

      {/* ปุ่มวิเคราะห์ */}
      <button
        onClick={handleAnalyze}
        disabled={loading}
        style={{
          padding: '10px 24px',
          background: '#3b82f6',
          color: '#fff',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer',
          fontWeight: 'bold',
          fontSize: '14px'
        }}
      >
        {loading ? 'กำลังวิเคราะห์...' : '🔍 วิเคราะห์'}
      </button>

      {/* ส่วนแสดงผลลัพธ์ (Output) ให้เจ้าหน้าที่อ่านง่าย ตัดสินใจได้ทันที */}
      {analysisResult && (
        <div style={{
          marginTop: '25px',
          padding: '20px',
          background: '#1e293b',
          borderRadius: '8px',
          border: '1px solid #475569'
        }}>
          <h3 style={{ margin: '0 0 12px 0', borderBottom: '1px solid #475569', paddingBottom: '8px' }}>
            📊 ผลการวิเคราะห์ความเสี่ยง
          </h3>
          <div style={{ display: 'grid', gap: '8px', fontSize: '15px' }}>
            <div>
              สถานะ: <strong style={{ color: getStatusColor(analysisResult.risk_level) }}>{analysisResult.status}</strong>
            </div>
            <div>
              ระดับความเสี่ยง (Risk Level): <strong>{analysisResult.risk_level}</strong>{' '}
              <span style={{ color: '#94a3b8', fontSize: '13px' }}>(0 = ปลอดภัย, 1 = น่าสงสัย, 2 = หลอกลวงแน่นอน)</span>
            </div>
            <div style={{ background: '#0f172a', padding: '12px', borderRadius: '6px', marginTop: '6px', fontSize: '14px', color: '#cbd5e1' }}>
              <strong>คำอธิบายเพิ่มเติม:</strong> {analysisResult.description}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}