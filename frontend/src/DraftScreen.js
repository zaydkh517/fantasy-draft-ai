import { useState } from 'react';

function DraftScreen() {
  const [activeTab, setActiveTab] = useState('recommendations');

  return (
    <div className="draft-screen">
      <div className="tabs">
        <button onClick={() => setActiveTab('recommendations')}>Recommendations</button>
        <button onClick={() => setActiveTab('roster')}>My Roster</button>
        <button onClick={() => setActiveTab('board')}>Draft Board</button>
        <button onClick={() => setActiveTab('players')}>All Players</button>
      </div>

      <div className="tab-content">
        {activeTab === 'recommendations' && <p>Recommendations go here</p>}
        {activeTab === 'roster' && <p>Roster goes here</p>}
        {activeTab === 'board' && <p>Draft board goes here</p>}
        {activeTab === 'players' && <p>All players go here</p>}
      </div>
    </div>
  );
}

export default DraftScreen;