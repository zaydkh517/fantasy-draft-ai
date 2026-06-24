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

  const isMyTurn = () => {
    const pickInRound = ((currentPick - 1) % leagueSize) + 1;
    return pickInRound === draftPosition;
  };

  const fetchAllPlayers = async () => {
    const response = await fetch('https://fantasy-draft-ai-production.up.railway.app/players');
    const data = await response.json();
    setAllPlayers(data.players || []);
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async (currentRoster = roster, currentDraftedIds = draftedIds, round = currentRound) => {
    setLoading(true);
    const response = await fetch('https://fantasy-draft-ai-production.up.railway.app/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        roster: currentRoster,
        round_number: round,
        drafted_ids: currentDraftedIds
      })
    });

    const data = await response.json();
    setRecommendations(data.recommendations);
    setLoading(false);
  };

  const handleDraft = async (player) => {
    const newRoster = [...roster, { position: player.position, player_id: player.player_id, full_name: player.full_name }];
    const newDraftedIds = [...draftedIds, player.player_id];
    const newRound = Math.floor(newDraftedIds.length / leagueSize) + 1;

    setRoster(newRoster);
    setDraftedIds(newDraftedIds);
    setCurrentRound(newRound);
    setCurrentPick(currentPick + 1);

    await fetch('https://fantasy-draft-ai-production.up.railway.app/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: player.player_id })
    });
    
    fetchRecommendations(newRoster, newDraftedIds, newRound);
  };

  const handleLogPick = async (player) => {
    const newDraftedIds = [...draftedIds, player.player_id];
    const newRound = Math.floor(newDraftedIds.length / leagueSize) + 1;

    setDraftedIds(newDraftedIds);
    setCurrentRound(newRound);
    setCurrentPick(currentPick + 1);

    await fetch('https://fantasy-draft-ai-production.up.railway.app/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: player.player_id })
    });
    fetchRecommendations(roster, newDraftedIds, newRound);
  };

  return (
    <div className="draft-screen">
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
                  <p>{player.explanation}</p>
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
        {activeTab === 'roster' && <p>Roster goes here</p>}
        {activeTab === 'board' && <p>Draft board goes here</p>}
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