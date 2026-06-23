import DraftScreen from './DraftScreen';
import { useState } from 'react';
import './App.css';
import InfoModal from './InfoModal';

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await fetch('https://fantasy-draft-ai-production.up.railway.app/settings', {
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
    }
  );

    const data = await response.json();
    console.log(data);
    setScreen('draft');
  };

  return (
    <div className="App">
      <button onClick={() => setShowModal(true)}>ⓘ</button>
      {showModal && <InfoModal onClose={() => {localStorage.setItem('seenModal', 'true');
      setShowModal(false);
      }} />}
      {screen === 'setup' ? (
        <div>
          <h1>Fantasy Draft Engine</h1>
          <form onSubmit={handleSubmit}>
            <label>
              League Size:
              <input type="number" value={leagueSize} min={2} onChange={(e) => setLeagueSize(Number(e.target.value))} />
            </label>
            <label>
              QB Starters:
              <input type="number" value={qbStarters} min={1} onChange={(e) => setQbStarters(Number(e.target.value))} />
            </label>
            <label>
              RB Starters:
              <input type="number" value={rbStarters} min={1} onChange={(e) => setRbStarters(Number(e.target.value))} />
            </label>
            <label>
              WR Starters:
              <input type="number" value={wrStarters} min={1} onChange={(e) => setWrStarters(Number(e.target.value))} />
            </label>
            <label>
              TE Starters:
              <input type="number" value={teStarters} min={0} onChange={(e) => setTeStarters(Number(e.target.value))} />
            </label>
            <label>
              Flex Starters:
              <input type="number" value={flexStarters} min={0} onChange={(e) => setFlexStarters(Number(e.target.value))} />
            </label>
            <label>
              Bench Slots:
              <input type="number" value={benchSlots} min={0} onChange={(e) => setBenchSlots(Number(e.target.value))} />
            </label>
            <label>
              Your Draft Position:
              <input type="number" value={draftPosition} min={1} max={leagueSize} onChange={(e) => setDraftPosition(Number(e.target.value))} />
            </label>
            <button type="submit">Start Draft</button>
          </form>
        </div>
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
          />
      )}
    </div>
  );
}

export default App;