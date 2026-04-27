const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const DEFAULT_USER_ID =
  import.meta.env.VITE_DEFAULT_USER_ID || "00000000-0000-0000-0000-000000000001";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed with ${response.status}`);
  }
  return response.json();
}

export function fetchDashboard(userId = DEFAULT_USER_ID) {
  return request(`/dashboard?user_id=${userId}`);
}

export const getDashboard = fetchDashboard;

export function submitDecision(payload) {
  return request("/decision", {
    method: "POST",
    body: JSON.stringify({ user_id: DEFAULT_USER_ID, ...payload }),
  });
}

export function submitFeedback(payload) {
  return request("/feedback", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getMemory(query, topK = 5, userId = DEFAULT_USER_ID) {
  const params = new URLSearchParams({ user_id: userId, query, top_k: String(topK) });
  return request(`/memory?${params.toString()}`);
}
