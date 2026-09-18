import React, { useState } from 'react';

export default function App() {
  const [activeTab, setActiveTab] = useState('sms');
  const [smsText, setSmsText] = useState('');
  const [urlText, setUrlText] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // ตัวอย่างข้อความ SMS ที่สอดคล้องกับชุดข้อมูล (Data) ทดสอบ 3 ระดับ
  const sampleSms = [
    { label: "ตัวอย่างที่ 1 (หลอกลวงแน่นอน - ระดับ 2)", text: "ยินดีด้วยคุณได้รับสิทธิ์รับเงินรางวัล 10,000 บาท คลิกลิงก์เพื่อรับเงิน http://scb-lucky.com" },
    { label: "ตัวอย่างที่ 2 (น่าสงสัย - ระดับ 1)", text: "เตือนภัย: บัญชีธนาคารของคุณมีความเสี่ยง กรุณาติดต่อเจ้าหน้าที่ด่วน" },
    { label: "ตัวอย่างที่ 3 (ปลอดภัย - ระดับ 0)", text: "คุณได้ทำการโอนเงินสำเร็จจำนวน 500 บาท เรียบร้อยแล้ว ขอบคุณที่ใช้บริการ" }
  ];

  const handleAnalyzeSms = async () => {
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
      alert('ไม่สามารถเชื่อมต่อกับ Backend ได้ กรุณาตรวจสอบการรัน uvicorn');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeUrl = async () => {
    if (!urlText.trim()) return;
    setLoading(true);
    setAnalysisResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/check/url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: urlText }),
      });
      const data = await response.json();
      setAnalysisResult(data);
    } catch (error) {
      console.error('Connection error:', error);
      alert('ไม่สามารถเชื่อมต่อกับ Backend ได้');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (level) => {
    if (level === 2) return '#ef4444'; // แดง (หลอกลวง/ฟิชชิ่ง)
    if (level === 1) return '#f59e0b'; // ส้ม/เหลือง (น่าสงสัย)
    return '#22c55e'; // เขียว (ปลอดภัย)
  };

  return (
    <div style={{ background: '#0b0f19', minHeight: '100vh', color: '#fff', fontFamily: 'sans-serif' }}>
      {/* Header ตามดีไซน์เดิม */}
      <header style={{ padding: '15px 30px', borderBottom: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            🛡️ Cybercrime Network Analyzer
          </h1>
          <p style={{ margin: '3px 0 0 0', fontSize: '12px', color: '#64748b' }}>
            ระบบวิเคราะห์พฤติกรรมและเครือข่ายความเชื่อมโยงอาชญากรรมออนไลน์
          </p>
        </div>
        <div style={{ background: '#064e3b', color: '#34d399', padding: '5px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 'bold' }}>
          ● ระบบออนไลน์
        </div>
      </header>

      {/* เมนูแท็บด้านบน */}
      <nav style={{ padding: '0 30px', borderBottom: '1px solid #1e293b', display: 'flex', gap: '30px' }}>
        <button 
          onClick={() => { setActiveTab('sms'); setAnalysisResult(null); }}
          style={{ background: 'transparent', border: 'none', borderBottom: activeTab === 'sms' ? '2px solid #3b82f6' : '2px solid transparent', color: activeTab === 'sms' ? '#3b82f6' : '#94a3b8', padding: '15px 0', cursor: 'pointer', fontWeight: 'bold' }}
        >
          📬 วิเคราะห์ SMS
        </button>
        <button 
          onClick={() => { setActiveTab('url'); setAnalysisResult(null); }}
          style={{ background: 'transparent', border: 'none', borderBottom: activeTab === 'url' ? '2px solid #3b82f6' : '2px solid transparent', color: activeTab === 'url' ? '#3b82f6' : '#94a3b8', padding: '15px 0', cursor: 'pointer', fontWeight: 'bold' }}
        >
          🔗 วิเคราะห์ URL
        </button>
        <button 
          onClick={() => { setActiveTab('graph'); setAnalysisResult(null); }}
          style={{ background: 'transparent', border: 'none', borderBottom: activeTab === 'graph' ? '2px solid #3b82f6' : '2px solid transparent', color: activeTab === 'graph' ? '#3b82f6' : '#94a3b8', padding: '15px 0', cursor: 'pointer', fontWeight: 'bold' }}
        >
          🕸️ เครือข่ายบัญชีม้า (เสริม)
        </button>
        <button 
          onClick={() => { setActiveTab('osint'); setAnalysisResult(null); }}
          style={{ background: 'transparent', border: 'none', borderBottom: activeTab === 'osint' ? '2px solid #3b82f6' : '2px solid transparent', color: activeTab === 'osint' ? '#3b82f6' : '#94a3b8', padding: '15px 0', cursor: 'pointer', fontWeight: 'bold' }}
        >
          🔍 OSINT Lookup
        </button>
      </nav>

      {/* เนื้อหาในแต่ละแท็บ */}
      <main style={{ padding: '30px', maxWidth: '900px' }}>
        {activeTab === 'sms' && (
          <div>
            <h2 style={{ fontSize: '16px', margin: '0 0 5px 0' }}>📬 วิเคราะห์ข้อความ SMS หลอกลวง</h2>
            <p style={{ color: '#94a3b8', fontSize: '13px', marginBottom: '20px' }}>
              วางข้อความ SMS ที่ต้องการตรวจสอบ ระบบจะวิเคราะห์ด้วย NLP ภาษาไทย (จำแนก 3 ระดับ)
            </p>

            {/* ปุ่มตัวอย่างข้อความที่สอดคล้องกับดาต้า */}
            <div style={{ marginBottom: '15px', display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '12px', color: '#94a3b8' }}>ตัวอย่างดาต้า:</span>
              {sampleSms.map((item, i) => (
                <button
                  key={i}
                  onClick={() => setSmsText(item.text)}
                  style={{ background: '#1e293b', border: '1px solid #334155', color: '#cbd5e1', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '11px' }}
                >
                  {item.label}
                </button>
              ))}
            </div>

            <textarea 
              rows="5"
              value={smsText}
              onChange={(e) => setSmsText(e.target.value)}
              placeholder="วางข้อความ SMS ที่ต้องการวิเคราะห์..."
              style={{ width: '100%', background: '#1e293b', color: '#fff', padding: '12px', borderRadius: '8px', border: '1px solid #334155', fontSize: '14px', resize: 'vertical' }}
            />
            <br /><br />
            <button 
              onClick={handleAnalyzeSms}
              disabled={loading}
              style={{ padding: '10px 20px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
            >
              {loading ? 'กำลังวิเคราะห์...' : 'วิเคราะห์ความเสี่ยง'}
            </button>
          </div>
        )}

        {activeTab === 'url' && (
          <div>
            <h2 style={{ fontSize: '16px', margin: '0 0 5px 0' }}>🔗 วิเคราะห์ลิงก์ URL ฟิชชิ่ง</h2>
            <p style={{ color: '#94a3b8', fontSize: '13px', marginBottom: '20px' }}>
              กรอกลิงก์เว็บไซต์ที่สงสัย ระบบจะตรวจสอบฟีเจอร์โครงสร้างลิงก์ (3 ระดับความเสี่ยง)
            </p>
            <input 
              type="text"
              value={urlText}
              onChange={(e) => setUrlText(e.target.value)}
              placeholder="https://example.com/login"
              style={{ width: '100%', background: '#1e293b', color: '#fff', padding: '12px', borderRadius: '8px', border: '1px solid #334155', fontSize: '14px' }}
            />
            <br /><br />
            <button 
              onClick={handleAnalyzeUrl}
              disabled={loading}
              style={{ padding: '10px 20px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
            >
              {loading ? 'กำลังตรวจสอบ...' : 'ตรวจสอบ URL'}
            </button>
          </div>
        )}

        {activeTab === 'graph' && (
          <div>
            <h2 style={{ fontSize: '16px', margin: '0 0 5px 0' }}>🕸️ เครือข่ายบัญชีม้า (NetworkX Graph Analysis)</h2>
            <p style={{ color: '#94a3b8', fontSize: '13px' }}>ส่วนเสริมสำหรับแสดงเส้นทางเส้นทางการเงินและระบุ Hub Account (in-degree สูง)</p>
            <div style={{ padding: '30px', background: '#1e293b', borderRadius: '8px', textAlign: 'center', color: '#64748b', marginTop: '15px' }}>
              [ แสดงผลกราฟความเชื่อมโยงบัญชีธนาคาร ]
            </div>
          </div>
        )}

        {activeTab === 'osint' && (
          <div>
            <h2 style={{ fontSize: '16px', margin: '0 0 5px 0' }}>🔍 OSINT Lookup</h2>
            <p style={{ color: '#94a3b8', fontSize: '13px' }}>ค้นหาข้อมูลข่าวกรองและฐานข้อมูลภัยคุกคามออนไลน์</p>
          </div>
        )}

        {/* ส่วนแสดงผลลัพธ์ (Output) สำหรับเจ้าหน้าที่ อ่านง่าย ตัดสินใจได้ทันที */}
        {analysisResult && (
          <div style={{ marginTop: '25px', padding: '20px', background: '#1e293b', borderRadius: '8px', border: '1px solid #334155' }}>
            <h3 style={{ margin: '0 0 12px 0', borderBottom: '1px solid #334155', paddingBottom: '8px', fontSize: '15px' }}>
              📊 ผลการวิเคราะห์จากระบบ ML
            </h3>
            <div style={{ display: 'grid', gap: '8px', fontSize: '14px' }}>
              <div>
                สถานะความเสี่ยง: <strong style={{ color: getStatusColor(analysisResult.risk_level) }}>{analysisResult.status}</strong>
              </div>
              <div>
                ระดับความเสี่ยง (Risk Level): <strong>{analysisResult.risk_level}</strong>{' '}
                <span style={{ color: '#94a3b8', fontSize: '12px' }}>(0 = ปลอดภัย, 1 = น่าสงสัย, 2 = หลอกลวง/ฟิชชิ่ง)</span>
              </div>
              <div style={{ background: '#0b0f19', padding: '12px', borderRadius: '6px', marginTop: '6px', color: '#cbd5e1' }}>
                <strong>คำอธิบายสำหรับเจ้าหน้าที่:</strong> {analysisResult.description}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}