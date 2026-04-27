import { useState } from "react";
import ScoreCard from "../components/ScoreCard.jsx";
import { submitFeedback } from "../services/api.js";

export default function Results({ result }) {
  if (!result) {
    return (
      <section className="card">
        <h2>No decision result yet</h2>
        <p>Submit a decision to see scored recommendations and agent reasoning.</p>
      </section>
    );
  }

  const agents = Object.values(result.agent_breakdown || {});

  return (
    <section className="stack">
      <div className="card hero">
        <p className="eyebrow">Recommended option</p>
        <h2>{result.recommended_option}</h2>
        <ScoreCard label="Final score" score={result.score} />
        <p>{result.reasoning}</p>
        <p className="muted">
          Decision ID: {result.decision_id} | Version {result.version}
        </p>
      </div>

      <div className="grid">
        {agents.map((agent) => (
          <div className="card" key={agent.agent}>
            <ScoreCard label={agent.agent.replace("_", " ")} score={agent.score} />
            <p>{agent.reasoning}</p>
            {agent.warnings?.length > 0 && (
              <ul className="warnings">
                {agent.warnings.map((warning) => (
                  <li key={warning}>{warning}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>

      <div className="card">
        <h3>Alternatives</h3>
        {result.alternatives?.length ? (
          result.alternatives.map((alt) => (
            <div className="row" key={alt.option_id}>
              <strong>{alt.label}</strong>
              <span>{Math.round(alt.score * 100)}%</span>
            </div>
          ))
        ) : (
          <p>No alternatives supplied.</p>
        )}
      </div>

      <FeedbackForm decisionId={result.decision_id} />
    </section>
  );
}

function FeedbackForm({ decisionId }) {
  const [status, setStatus] = useState("");

  async function submit(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await submitFeedback({
      decision_id: decisionId,
      outcome_summary: form.get("outcome_summary"),
      success_score: Number(form.get("success_score")),
      reflection: form.get("reflection"),
    });
    setStatus("User model updated with outcome and reflection.");
    event.currentTarget.reset();
  }

  return (
    <form className="card stack" onSubmit={submit}>
      <h3>Feedback loop</h3>
      <input name="outcome_summary" placeholder="What happened?" required />
      <input name="success_score" type="number" min="0" max="1" step="0.05" defaultValue="0.7" required />
      <textarea name="reflection" placeholder="Reflection for future decisions" />
      <button type="submit">Update user model</button>
      {status && <p className="muted">{status}</p>}
    </form>
  );
}
