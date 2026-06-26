import { useState, useEffect } from 'react';

function DraftScreen({ leagueSize, rosterSize, draftPosition, qbStarters, rbStarters, wrStarters, teStarters, flexStarters, benchSlots }) {
  const [activeTab, setActiveTab] = useState('recommendations');
  const [recommendations, setRecommendations] = useState([]);
  const [roster, setRoster] = useState([]);
  const [draftedIds, setDraftedIds] = useState([]);
  const [currentRound, setCurrentRound] = useState(1);
  const [loading, setLoading] = useState(false);
  const [currentPick, setCurrentPick] = useState(1);
  const [allPlayers, setAllPlayers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [draftBoard, setDraftBoard] = useState([]);

  const isMyTurn = (pick = currentPick) => {
    const pickInRound = ((pick - 1) % leagueSize) + 1;
    const round = Math.floor((pick - 1) / leagueSize) + 1;
    const isEvenRound = round % 2 === 0;
    const effectivePosition = isEvenRound ? leagueSize - draftPosition + 1 : draftPosition;
    return pickInRound === effectivePosition;
  };

  const fetchAllPlayers = async () => {
    const response = await fetch('https://fantasy-draft-ai-production.up.railway.app/players');
    const data = await response.json();
    setAllPlayers(data.players || []);
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async (currentRoster = roster, currentDraftedIds = draftedIds, round = currentRound, myTurn = isMyTurn()) => {
    setLoading(true);
    const response = await fetch('https://fantasy-draft-ai-production.up.railway.app/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        roster: currentRoster,
        round_number: round,
        drafted_ids: currentDraftedIds,
        generate_explanations: myTurn
      })
    });

    const data = await response.json();
    setRecommendations(data.recommendations);
    setLoading(false);
  };

  const handleDraft = async (player) => {
    const slot = assignSlot(player, roster, { qbStarters, rbStarters, wrStarters, teStarters, flexStarters, benchSlots });
    const newRoster = [...roster, { position: player.position, player_id: player.player_id, full_name: player.full_name, slot }];
    const newDraftedIds = [...draftedIds, player.player_id];
    const newRound = Math.floor(newDraftedIds.length / leagueSize) + 1;

    setRoster(newRoster);
    setDraftedIds(newDraftedIds);
    setCurrentRound(newRound);
    setCurrentPick(currentPick + 1);

    setDraftBoard([...draftBoard, {
      pick: currentPick,
      player: player.full_name,
      position: player.position,
      team: 'You'
    }]);

    await fetch('https://fantasy-draft-ai-production.up.railway.app/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: player.player_id })
    });

    fetchRecommendations(newRoster, newDraftedIds, newRound, isMyTurn(currentPick + 1));
  };

  const handleLogPick = async (player) => {
    const newDraftedIds = [...draftedIds, player.player_id];
    const newRound = Math.floor(newDraftedIds.length / leagueSize) + 1;

    setDraftedIds(newDraftedIds);
    setCurrentRound(newRound);
    setCurrentPick(currentPick + 1);

    setDraftBoard([...draftBoard, {
      pick: currentPick,
      player: player.full_name,
      position: player.position,
      team: 'Other'
    }]);

    await fetch('https://fantasy-draft-ai-production.up.railway.app/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: player.player_id })
    });

  console.log('logging pick, newDraftedIds:', newDraftedIds);
  fetchRecommendations(roster, newDraftedIds, newRound, isMyTurn(currentPick + 1));
  };

  const assignSlot = (player, currentRoster, leagueSettings) => {
    const { qbStarters, rbStarters, wrStarters, teStarters, flexStarters, benchSlots } = leagueSettings;

    if (player.position === 'QB') {
      const qbCount = currentRoster.filter(p => p.slot === 'QB').length;
      if (qbCount < qbStarters) return 'QB';
      return 'BENCH';
    } else if (player.position === 'RB') {
      const rbCount = currentRoster.filter(p => p.slot === 'RB').length;
      if (rbCount < rbStarters) return 'RB';
    } else if (player.position === 'WR') {
      const wrCount = currentRoster.filter(p => p.slot === 'WR').length;
      if (wrCount < wrStarters) return 'WR';
    } else if (player.position === 'TE') {
      const teCount = currentRoster.filter(p => p.slot === 'TE').length;
      if (teCount < teStarters) return 'TE';
    }
    const flexCount = currentRoster.filter(p => p.slot === 'FLEX').length;
    if (flexCount < flexStarters) return 'FLEX';

    const benchCount = currentRoster.filter(p => p.slot === 'BENCH').length;
    if (benchCount < benchSlots) return 'BENCH';

    return null;
  };

  return (
    <div className="draft-screen">
      <div className="draft-info">
        <p>Round {currentRound} | Pick {currentPick} | {isMyTurn() ? "Your Pick" : "Waiting..."}</p>
      </div>
      <div className="tabs">
        <button onClick={() => setActiveTab('recommendations')}>Recommendations</button>
        <button onClick={() => setActiveTab('roster')}>My Roster</button>
        <button onClick={() => setActiveTab('board')}>Draft Board</button>
        <button onClick={() => { setActiveTab('players'); fetchAllPlayers(); }}>All Players</button>
      </div>

      <div className="tab-content">
        {activeTab === 'recommendations' && (
          <div>
            {loading ? <p>Loading recommendations...</p> : (
              recommendations.map(player => (
                <div key={player.player_id}>
                  <h3>{player.full_name}</h3>
                  <p>{player.position} | {player.team} | Age {player.age}</p>
                  <p>Overall: {player.overall_score}</p>
                  {isMyTurn() && <p>{player.explanation}</p>}
                  {isMyTurn() ? (
                    <button onClick={() => handleDraft(player)}>Draft</button>
                  ) : (
                    <button onClick={() => handleLogPick(player)}>Log Pick</button>
                  )}
                </div>
              ))
            )}
          </div>
        )}
        {activeTab === 'roster' && (
          <div>
            <h2>My Roster</h2>
            <h3>Starters</h3>
            {Array.from({ length: qbStarters }, (_, i) => {
              const player = roster.filter(p => p.slot === 'QB')[i];
              return <p key={`QB${i}`}>QB: {player ? player.full_name : '—'}</p>;
            })}
            {Array.from({ length: rbStarters }, (_, i) => {
              const player = roster.filter(p => p.slot === 'RB')[i];
              return <p key={`RB${i}`}>RB: {player ? player.full_name : '—'}</p>;
            })}
            {Array.from({ length: wrStarters }, (_, i) => {
              const player = roster.filter(p => p.slot === 'WR')[i];
              return <p key={`WR${i}`}>WR: {player ? player.full_name : '—'}</p>;
            })}
            {Array.from({ length: teStarters }, (_, i) => {
              const player = roster.filter(p => p.slot === 'TE')[i];
              return <p key={`TE${i}`}>TE: {player ? player.full_name : '—'}</p>;
            })}
            {Array.from({ length: flexStarters }, (_, i) => {
              const player = roster.filter(p => p.slot === 'FLEX')[i];
              return <p key={`FLEX${i}`}>FLEX: {player ? player.full_name : '—'}</p>;
            })}
            <h3>Bench</h3>
            {Array.from({ length: benchSlots }, (_, i) => {
              const player = roster.filter(p => p.slot === 'BENCH')[i];
              return <p key={`BENCH${i}`}>Bench: {player ? player.full_name : '—'}</p>;
            })}
          </div>
        )}
        {activeTab === 'board' && (
          <div>
            <h2>Draft Board</h2>
            {draftBoard.length === 0 ? (
              <p>No picks made yet.</p>
            ) : (
              draftBoard.map((entry, i) => (
                <div key={i}>
                  <p>Pick {entry.pick} | {entry.position} | {entry.player} | {entry.team}</p>
                </div>
              ))
            )}
          </div>
        )}
        {activeTab === 'players' && (
          <div>
            <input
              type="text"
              placeholder="Search players..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <div>
              {allPlayers
                .filter(p => !draftedIds.includes(p.player_id) && p.full_name.toLowerCase().includes(searchQuery.toLowerCase()))
                .map(player => (
                  <div key={player.player_id}>
                    <span>{player.full_name} | {player.position} | {player.team}</span>
                    {isMyTurn() ? (
                      <button onClick={() => handleDraft(player)}>Draft</button>
                    ) : (
                      <button onClick={() => handleLogPick(player)}>Log Pick</button>
                    )}
                  </div>
                ))
              }
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default DraftScreen;