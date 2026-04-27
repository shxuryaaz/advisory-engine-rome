import { useEffect, useState } from 'react';
import { fetchDashboard } from '../services/api';

export default function Dashboard({ userId }) {
  const [dashboard, setDashboard] = useState(null);

  useEffect(() => {
    fetchDashboard(userId).then(setDashboard).catch(() => setDashboard(null));
  }, [userId]);

  return (
    <section className="grid gap-6 lg:grid-cols-2">
      <div className="card">
        <h2 className="section-title">Behavioral patterns</h2>
        <div className="space-y-3">
          {dashboard?.patterns?.length ? (
            dashboard.patterns.map((pattern) => (
              <div key={pattern.id} className="rounded-xl border border-slate-800 bg-slate-950 p-3">
                <p className="text-sm text-slate-200">{pattern.pattern}</p>
                <p className="mt-1 text-xs text-slate-500">Confidence {Math.round(pattern.confidence_score * 100)}%</p>
              </div>
            ))
          ) : (
            <p className="muted">No learned patterns yet. Submit decisions and feedback to train the model.</p>
          )}
        </div>
      </div>

      <div className="card">
        <h2 className="section-title">Recent decisions</h2>
        <div className="space-y-3">
          {dashboard?.recent_decisions?.length ? (
            dashboard.recent_decisions.map((decision) => (
              <div key={decision.id} className="rounded-xl border border-slate-800 bg-slate-950 p-3">
                <p className="font-medium">{decision.decision_text}</p>
                <p className="text-sm text-emerald-300">Chosen: {decision.chosen_option}</p>
                <p className="mt-1 text-xs text-slate-500">Version {decision.version}</p>
              </div>
            ))
          ) : (
            <p className="muted">No decision history yet.</p>
          )}
        </div>
      </div>
    </section>
  );
}
