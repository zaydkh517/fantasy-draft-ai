import { useEffect } from 'react';

const SCORES = [
  ['Base', "Consensus ranking from Sleeper."],
  ['Potential', "Projected peak based on age, year-over-year production, starting status, targets, snaps and experience."],
  ['Sleeper', "How undervalued a player looks relative to their potential, plus trending adds."],
  ['Need', "How much your roster still needs the position."],
  ['Overall', "The weighted blend of the four, adjusted by round."],
];

const ROADMAP = [
  ['Next', 'Connect to Sleeper leagues for automatic pick tracking'],
  ['Later', 'ESPN, Yahoo and NFL Fantasy support'],
  ['Ongoing', 'Tuning the scoring model and the interface based on feedback'],
];

function InfoModal({ onClose }) {
  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h2 id="modal-title">How it works</h2>
          <button className="icon-btn" aria-label="Close" onClick={onClose}>
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M2 2l10 10M12 2L2 12" /></svg>
          </button>
        </div>

        <p className="modal-lede">
          Track your draft here as it happens. Log other teams' picks, or let them auto-draft, and when you're on the clock the assistant ranks who's left for your roster and explains its top choices.
        </p>

        <h3>Scoring</h3>
        <dl className="def-list">
          {SCORES.map(([term, desc]) => (
            <div key={term}><dt>{term}</dt><dd>{desc}</dd></div>
          ))}
        </dl>

        <h3>Roadmap</h3>
        <dl className="def-list">
          {ROADMAP.map(([term, desc]) => (
            <div key={term}><dt>{term}</dt><dd>{desc}</dd></div>
          ))}
        </dl>

        <div className="modal-actions">
          <button className="btn-primary" onClick={onClose}>Got it</button>
        </div>
      </div>
    </div>
  );
}

export default InfoModal;
