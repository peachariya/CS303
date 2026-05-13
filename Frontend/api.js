const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function post(path, body) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  analyzeSMS:   (text)         => post("/api/sms/analyze",   { text }),
  analyzeURL:   (url)          => post("/api/url/analyze",   { url }),
  analyzeGraph: (transactions) => post("/api/graph/analyze", { transactions }),
  osintLookup:  (target)       => post("/api/osint/lookup",  { target }),
};
