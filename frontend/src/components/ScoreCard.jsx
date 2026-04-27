export default function ScoreCard({ title, score, children }) {
  const percentage = Math.round((Number(score) || 0) * 100)

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 shadow-xl shadow-black/20">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-cyan-300">{title}</p>
          <div className="mt-3 h-2 w-48 overflow-hidden rounded-full bg-slate-800">
            <div className="h-full rounded-full bg-cyan-400" style={{ width: `${percentage}%` }} />
          </div>
        </div>
        <span className="text-3xl font-semibold text-white">{percentage}</span>
      </div>
      {children ? <div className="mt-4 text-sm leading-6 text-slate-300">{children}</div> : null}
    </section>
  )
}
