import { useState, useEffect } from 'react';

function DraftScreen({ leagueSize, rosterSize, draftPosition, qbStarters, rbStarters, wrStarters, teStarters, flexStarters, benchSlots }) {
  const [activeTab, setActiveTab] = useState('recommendations');
  const [recommendations, setRecommendations] = useState([]);
  const [roster, setRoster] = useState([]);
  const [draftedIds, setDraftedIds] = useState([]);
  const [currentRound, setCurrentRound] = useState(1);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    setLoading(true);
    const response = await fetch('https://fantasy-draft-ai-production.up.railway.app/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        roster: roster,
        round_number: currentRound,
        drafted_ids: draftedIds
      })
    });
    
    const data = await response.json();
    setRecommendations(data.recommendations);
    setLoading(false);
  };

  return (
    <div className="draft-screen">
      <div className="tabs">
        <button onClick={() => setActiveTab('recommendations')}>Recommendations</button>
        <button onClick={() => setActiveTab('roster')}>My Roster</button>
        <button onClick={() => setActiveTab('board')}>Draft Board</button>
        <button onClick={() => setActiveTab('players')}>All Players</button>
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
                </div>
              ))
            )}
          </div>
        )}
        {activeTab === 'roster' && <p>Roster goes here</p>}
        {activeTab === 'board' && <p>Draft board goes here</p>}
        {activeTab === 'players' && <p>All players go here</p>}
      </div>
    </div>
  );
}

export default DraftScreen;