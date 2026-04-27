import { useEffect, useState } from "react";
import Dashboard from "./pages/Dashboard.jsx";
import DecisionInput from "./pages/DecisionInput.jsx";
import Results from "./pages/Results.jsx";
import { submitFeedback } from "./services/api.js";

const DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001";

export default function App() {
  const [view, setView] = useState("dashboard");
  const [latestResult, setLatestResult] = useState(null);
  const [userId] = useState(DEFAULT_USER_ID);

  useEffect(() => {
    document.title = "PDIS Advisory Engine";
  }, []);

  function handleDecisionResult(result) {
    setLatestResult(result);
    setView("results");
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-950/90">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Personal Decision Intelligence</p>
            <h1 className="text-2xl font-semibold">Advisory Engine Rome</h1>
          </div>
          <nav className="flex gap-2">
            <button className="nav-button" onClick={() => setView("dashboard")}>Dashboard</button>
            <button className="nav-button" onClick={() => setView("decision")}>New Decision</button>
            {latestResult && <button className="nav-button" onClick={() => setView("results")}>Results</button>}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">
        {view === "dashboard" && <Dashboard userId={userId} />}
        {view === "decision" && <DecisionInput userId={userId} onResult={handleDecisionResult} />}
        {view === "results" && (
          <Results
            result={latestResult}
            userId={userId}
            onFeedback={(payload) => submitFeedback(payload).then(() => setView("dashboard"))}
          />
        )}
      </main>
    </div>
  );
}
