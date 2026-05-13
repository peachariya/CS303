import { useState } from "react";
import SMSAnalyzer from "./components/SMSAnalyzer";
import URLAnalyzer from "./components/URLAnalyzer";
import GraphAnalyzer from "./components/GraphAnalyzer";
import OSINTLookup from "./components/OSINTLookup";

const NAV_ITEMS = [
  { id: "sms",   label: "📩 วิเคราะห์ SMS",        component: SMSAnalyzer },
  { id: "url",   label: "🔗 วิเคราะห์ URL",         component: URLAnalyzer },
  { id: "graph", label: "🕸️ เครือข่ายบัญชีม้า",    component: GraphAnalyzer },
  { id: "osint", label: "🔍 OSINT Lookup",           component: OSINTLookup },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("sms");
  const ActiveComponent = NAV_ITEMS.find(n => n.id === activeTab)?.component || SMSAnalyzer;

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-700 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center gap-3">
          <span className="text-2xl">🛡️</span>
          <div>
            <h1 className="text-lg font-bold text-white leading-tight">
              Cybercrime Network Analyzer
            </h1>
            <p className="text-xs text-gray-400">
              ระบบวิเคราะห์พฤติกรรมและเครือข่ายอาชญากรรมออนไลน์
            </p>
          </div>
          <div className="ml-auto">
            <span className="px-2 py-1 bg-emerald-900 text-emerald-300 text-xs rounded-full border border-emerald-700">
              ● ระบบออนไลน์
            </span>
          </div>
        </div>
      </header>

      {/* Nav Tabs */}
      <nav className="bg-gray-900 border-b border-gray-800 px-6">
        <div className="max-w-7xl mx-auto flex gap-1">
          {NAV_ITEMS.map(item => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
                activeTab === item.id
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-gray-400 hover:text-gray-200"
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <ActiveComponent />
      </main>
    </div>
  );
}
