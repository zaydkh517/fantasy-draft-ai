import DraftScreen from './DraftScreen';
import { useState } from 'react';
import './App.css';
import InfoModal from './InfoModal';

function Stepper({ label, hint, value, min = 0, max = 99, onChange }) {
  const clamp = (n) => Math.max(min, Math.min(max, n));
  return (
    <div className="field">
      <div className="field-label">
        <span>{label}</span>
        {hint && <small>{hint}</small>}
      </div>
      <div className="stepper">
        <button type="button" aria-label={`Decrease ${label}`} disabled={value <= min} onClick={() => onChange(clamp(value - 1))}>−</button>
        <input
          type="number"
          inputMode="numeric"
          value={value}
          min={min}
          max={max}
          onChange={(e) => onChange(clamp(Number(e.target.value)))}
        />
        <button type="button" aria-label={`Increase ${label}`} disabled={value >= max} onClick={() => onChange(clamp(value + 1))}>+</button>
      </div>
    </div>
  );
}

function App() {
  const [showModal, setShowModal] = useState(!localStorage.getItem('seenModal'));
  const [leagueSize, setLeagueSize] = useState(12);
  const [qbStarters, setQbStarters] = useState(1);
  const [rbStarters, setRbStarters] = useState(2);
  const [wrStarters, setWrStarters] = useState(2);
  const [teStarters, setTeStarters] = useState(1);
  const [flexStarters, setFlexStarters] = useState(1);
  const [benchSlots, setBenchSlots] = useState(7);
  const [draftPosition, setDraftPosition] = useState(1);
  const rosterSize = qbStarters + rbStarters + wrStarters + teStarters + flexStarters + benchSlots;
  const [screen, setScreen] = useState('setup');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    const response = await fetch('https://backend-ivory-reed-8288.fly.dev/settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        league_size: leagueSize,
        roster_size: rosterSize,
        qb_starters: qbStarters,
        rb_starters: rbStarters,
        wr_starters: wrStarters,
        te_starters: teStarters,
        flex_starters: flexStarters,
        bench_slots: benchSlots
      })
    });

    const data = await response.json();
    console.log(data);
    setSubmitting(false);
    setScreen('draft');
  };

  const handleLeagueSize = (n) => {
    setLeagueSize(n);
    if (draftPosition > n) setDraftPosition(n);
  };

  const closeModal = () => {
    localStorage.setItem('seenModal', 'true');
    setShowModal(false);
  };

  return (
    <div className="app">
      {showModal && <InfoModal onClose={closeModal} />}
      {screen === 'setup' ? (
        <main className="setup">
          <header className="setup-header">
            <div className="brand">
              <span className="brand-mark" aria-hidden="true" />
              Draft Engine
            </div>
            <button className="btn-ghost" onClick={() => setShowModal(true)}>How it works</button>
          </header>

          <div className="setup-intro">
            <h1>Set up your league</h1>
            <p>Enter your league's settings. During the draft, the assistant ranks every available player for your roster and explains its top picks.</p>
          </div>

          <form className="setup-form" onSubmit={handleSubmit}>
            <section className="form-section">
              <h2>League</h2>
              <div className="field-grid">
                <Stepper label="Teams" value={leagueSize} min={2} max={32} onChange={handleLeagueSize} />
                <Stepper label="Your pick" hint={`of ${leagueSize}`} value={draftPosition} min={1} max={leagueSize} onChange={setDraftPosition} />
              </div>
            </section>

            <section className="form-section">
              <h2>Roster</h2>
              <div className="field-grid">
                <Stepper label="QB" value={qbStarters} min={1} max={4} onChange={setQbStarters} />
                <Stepper label="RB" value={rbStarters} min={1} max={6} onChange={setRbStarters} />
                <Stepper label="WR" value={wrStarters} min={1} max={6} onChange={setWrStarters} />
                <Stepper label="TE" value={teStarters} min={0} max={4} onChange={setTeStarters} />
                <Stepper label="Flex" hint="RB/WR/TE" value={flexStarters} min={0} max={4} onChange={setFlexStarters} />
                <Stepper label="Bench" value={benchSlots} min={0} max={15} onChange={setBenchSlots} />
              </div>
            </section>

            <footer className="setup-footer">
              <dl className="summary">
                <div><dt>Roster</dt><dd>{rosterSize}</dd></div>
                <div><dt>Rounds</dt><dd>{rosterSize}</dd></div>
                <div><dt>Total picks</dt><dd>{leagueSize * rosterSize}</dd></div>
              </dl>
              <button type="submit" className="btn-primary" disabled={submitting}>
                {submitting ? 'Starting…' : 'Start draft'}
              </button>
            </footer>
          </form>
        </main>
      ) : (
        <DraftScreen
          leagueSize={leagueSize}
          rosterSize={rosterSize}
          draftPosition={draftPosition}
          qbStarters={qbStarters}
          rbStarters={rbStarters}
          wrStarters={wrStarters}
          teStarters={teStarters}
          flexStarters={flexStarters}
          benchSlots={benchSlots}
          onShowInfo={() => setShowModal(true)}
        />
      )}
    </div>
  );
}

export default App;
