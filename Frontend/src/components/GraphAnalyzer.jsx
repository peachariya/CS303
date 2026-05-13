import { useState, useEffect, useRef } from "react";
import { api } from "../services/api";

// -------- Sample data generator --------
function generateSampleTransactions() {
  return [
    { from_account: "ACC-001", to_account: "ACC-HUB",  amount: 50000,  timestamp: "2024-01-15T09:00:00" },
    { from_account: "ACC-002", to_account: "ACC-HUB",  amount: 35000,  timestamp: "2024-01-15T09:15:00" },
    { from_account: "ACC-003", to_account: "ACC-HUB",  amount: 42000,  timestamp: "2024-01-15T09:30:00" },
    { from_account: "ACC-004", to_account: "ACC-HUB",  amount: 28000,  timestamp: "2024-01-15T09:45:00" },
    { from_account: "ACC-HUB", to_account: "ACC-OUT1", amount: 80000,  timestamp: "2024-01-15T10:00:00" },
    { from_account: "ACC-HUB", to_account: "ACC-OUT2", amount: 60000,  timestamp: "2024-01-15T10:05:00" },
    { from_account: "ACC-OUT1", to_account: "ACC-FINAL", amount: 75000, timestamp: "2024-01-15T11:00:00" },
    { from_account: "ACC-005", to_account: "ACC-OUT2", amount: 15000,  timestamp: "2024-01-15T10:30:00" },
  ];
}

// -------- Simple force-directed graph using SVG + basic physics --------
function ForceGraph({ nodes, edges, suspectedMules, hubAccounts }) {
  const svgRef = useRef(null);
  const animRef = useRef(null);
  const posRef = useRef({});
  const velRef = useRef({});
  const [, forceUpdate] = useState(0);

  const W = 700, H = 420;
  const REPEL = 4000, ATTRACT = 0.015, DAMP = 0.85, CENTER = 0.008;

  useEffect(() => {
    if (!nodes.length) return;
    // init positions
    nodes.forEach((n, i) => {
      if (!posRef.current[n.id]) {
        const angle = (i / nodes.length) * 2 * Math.PI;
        posRef.current[n.id] = {
          x: W / 2 + Math.cos(angle) * 150,
          y: H / 2 + Math.sin(angle) * 120,
        };
        velRef.current[n.id] = { x: 0, y: 0 };
      }
    });

    let tick = 0;
    function step() {
      tick++;
      const pos = posRef.current;
      const vel = velRef.current;
      const nodeIds = nodes.map(n => n.id);

      // repulsion
      for (let i = 0; i < nodeIds.length; i++) {
        for (let j = i + 1; j < nodeIds.length; j++) {
          const a = nodeIds[i], b = nodeIds[j];
          const dx = pos[b].x - pos[a].x;
          const dy = pos[b].y - pos[a].y;
          const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
          const force = REPEL / (dist * dist);
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;
          vel[a].x -= fx; vel[a].y -= fy;
          vel[b].x += fx; vel[b].y += fy;
        }
      }

      // attraction along edges
      edges.forEach(e => {
        const a = e.source, b = e.target;
        if (!pos[a] || !pos[b]) return;
        const dx = pos[b].x - pos[a].x;
        const dy = pos[b].y - pos[a].y;
        vel[a].x += dx * ATTRACT;
        vel[a].y += dy * ATTRACT;
        vel[b].x -= dx * ATTRACT;
        vel[b].y -= dy * ATTRACT;
      });

      // center gravity
      nodeIds.forEach(id => {
        vel[id].x += (W / 2 - pos[id].x) * CENTER;
        vel[id].y += (H / 2 - pos[id].y) * CENTER;
        vel[id].x *= DAMP;
        vel[id].y *= DAMP;
        pos[id].x = Math.max(30, Math.min(W - 30, pos[id].x + vel[id].x));
        pos[id].y = Math.max(30, Math.min(H - 30, pos[id].y + vel[id].y));
      });

      forceUpdate(t => t + 1);
      if (tick < 200) animRef.current = requestAnimationFrame(step);
    }

    animRef.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(animRef.current);
  }, [nodes.length, edges.length]);

  const pos = posRef.current;

  function nodeColor(id) {
    if (hubAccounts.includes(id)) return "#f97316";       // orange = hub
    if (suspectedMules.includes(id)) return "#ef4444";    // red = mule
    return "#3b82f6";                                     // blue = normal
  }

  return (
    <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} className="w-full rounded-lg bg-gray-900 border border-gray-700">
      <defs>
        <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
          <path d="M0,0 L0,6 L8,3 z" fill="#6b7280" />
        </marker>
      </defs>

      {/* Edges */}
      {edges.map((e, i) => {
        const a = pos[e.source], b = pos[e.target];
        if (!a || !b) return null;
        return (
          <g key={i}>
            <line
              x1={a.x} y1={a.y} x2={b.x} y2={b.y}
              stroke="#374151" strokeWidth="1.5"
              markerEnd="url(#arrow)"
            />
            <text
              x={(a.x + b.x) / 2} y={(a.y + b.y) / 2 - 4}
              fill="#9ca3af" fontSize="9" textAnchor="middle"
            >
              ฿{(e.amount / 1000).toFixed(0)}K
            </text>
          </g>
        );
      })}

      {/* Nodes */}
      {nodes.map(n => {
        const p = pos[n.id];
        if (!p) return null;
        const color = nodeColor(n.id);
        const r = n.is_hub ? 22 : 16;
        return (
          <g key={n.id}>
            <circle
              cx={p.x} cy={p.y} r={r}
              fill={color} fillOpacity={0.25}
              stroke={color} strokeWidth="2"
            />
            <text x={p.x} y={p.y + 4} fill="white" fontSize="8" textAnchor="middle" fontWeight="600">
              {n.id.replace("ACC-", "")}
            </text>
            {n.is_hub && (
              <text x={p.x} y={p.y - r - 4} fill="#f97316" fontSize="9" textAnchor="middle">
                ⚠ Hub
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}

// -------- Main component --------
export default function GraphAnalyzer() {
  const [transactions, setTransactions] = useState(JSON.stringify(generateSampleTransactions(), null, 2));
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAnalyze() {
    setLoading(true); setError(""); setResult(null);
    try {
      const parsed = JSON.parse(transactions);
      const data = await api.analyzeGraph(parsed);
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
        <h2 className="text-xl font-bold mb-1">🕸️ วิเคราะห์เครือข่ายบัญชีม้า</h2>
        <p className="text-gray-400 text-sm">
          อัปโหลดข้อมูลธุรกรรม (JSON) ระบบจะสร้างกราฟความสัมพันธ์และระบุบัญชีม้า
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* JSON Input */}
        <div className="space-y-3">
          <label className="text-sm text-gray-400">ข้อมูลธุรกรรม (JSON)</label>
          <textarea
            rows={14}
            value={transactions}
            onChange={e => setTransactions(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-xs font-mono text-gray-300 focus:outline-none focus:border-blue-500 resize-none"
          />
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white font-medium rounded-lg transition text-sm"
          >
            {loading ? "กำลังวิเคราะห์..." : "🔍 วิเคราะห์เครือข่าย"}
          </button>
        </div>

        {/* Graph */}
        <div className="space-y-2">
          <label className="text-sm text-gray-400">กราฟความสัมพันธ์</label>
          {result ? (
            <ForceGraph
              nodes={result.nodes}
              edges={result.edges}
              suspectedMules={result.suspected_mule_accounts}
              hubAccounts={result.hub_accounts}
            />
          ) : (
            <div className="flex items-center justify-center h-64 bg-gray-900 rounded-lg border border-gray-700 text-gray-600 text-sm">
              กราฟจะแสดงหลังการวิเคราะห์
            </div>
          )}

          {/* Legend */}
          <div className="flex gap-4 text-xs text-gray-400">
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-blue-500 inline-block"/> ปกติ</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-red-500 inline-block"/> บัญชีม้า</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-orange-500 inline-block"/> Hub (ศูนย์กลาง)</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-900/40 border border-red-700 rounded-lg text-red-300 text-sm">❌ {error}</div>
      )}

      {/* Result summary */}
      {result && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <p className="text-xs text-gray-400 mb-1">บัญชีทั้งหมด</p>
            <p className="text-2xl font-bold">{result.nodes.length}</p>
          </div>
          <div className="bg-red-900/30 rounded-lg p-4 border border-red-800">
            <p className="text-xs text-red-400 mb-1">บัญชีม้าที่น่าสงสัย</p>
            <p className="text-2xl font-bold text-red-300">{result.suspected_mule_accounts.length}</p>
            <p className="text-xs text-red-400 mt-1">{result.suspected_mule_accounts.join(", ") || "-"}</p>
          </div>
          <div className="bg-orange-900/30 rounded-lg p-4 border border-orange-800">
            <p className="text-xs text-orange-400 mb-1">Hub Accounts (ศูนย์กลาง)</p>
            <p className="text-2xl font-bold text-orange-300">{result.hub_accounts.length}</p>
            <p className="text-xs text-orange-400 mt-1">{result.hub_accounts.join(", ") || "-"}</p>
          </div>
        </div>
      )}
    </div>
  );
}
