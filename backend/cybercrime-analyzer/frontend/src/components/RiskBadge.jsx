const COLORS = {
  low:      "bg-green-900 text-green-300 border-green-700",
  medium:   "bg-yellow-900 text-yellow-300 border-yellow-700",
  high:     "bg-orange-900 text-orange-300 border-orange-700",
  critical: "bg-red-900 text-red-300 border-red-700",
};

const LABELS = {
  low:      "ปลอดภัย",
  medium:   "ความเสี่ยงปานกลาง",
  high:     "ความเสี่ยงสูง",
  critical: "อันตรายมาก",
};

export default function RiskBadge({ level }) {
  return (
    <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${COLORS[level] || COLORS.medium}`}>
      {LABELS[level] || level}
    </span>
  );
}
