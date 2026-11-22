import { useState, useEffect } from 'react';

function DraftScreen({ leagueSize, rosterSize, draftPosition, qbStarters, rbStarters, wrStarters, teStarters, flexStarters, benchSlots, onShowInfo }) {
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
  const [positionFilter, setPositionFilter] = useState('ALL');
  const [teamRosters, setTeamRosters] = useState(Array.from({ length: leagueSize }, () => []));
  const [draftComplete, setDraftComplete] = useState(false);
  
  //checks if it's users turn
  const isMyTurn = (pick = currentPick) => {
    const pickInRound = ((pick - 1) % leagueSize) + 1;
    const round = Math.floor((pick - 1) / leagueSize) + 1;
    const isEvenRound = round % 2 === 0;
    const effectivePosition = isEvenRound ? leagueSize - draftPosition + 1 : draftPosition;
    return pickInRound === effectivePosition;
  };

//gets all players
const fetchAllPlayers = async () => {
  const response = await fetch('https://backend-ivory-reed-8288.fly.dev/rank-all', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      roster: roster,
      round_number: currentRound,
      drafted_ids: draftedIds
    })
  });
  const data = await response.json();
  setAllPlayers(data.players || []);
};

  useEffect(() => {
    fetchRecommendations();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  //get recommendations
  const fetchRecommendations = async (currentRoster = roster, currentDraftedIds = draftedIds, round = currentRound, myTurn = isMyTurn()) => {
    setLoading(true);
    const response = await fetch('https://backend-ivory-reed-8288.fly.dev/recommend', {
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

  //assign player to roster spot
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

  //draft a player
  const handleDraft = async (player) => {
    const slot = assignSlot(player, roster, { qbStarters, rbStarters, wrStarters, teStarters, flexStarters, benchSlots });
    const newRoster = [...roster, { position: player.position, player_id: player.player_id, full_name: player.full_name, slot }];
    const newDraftedIds = [...draftedIds, player.player_id];
    const newRound = Math.floor(newDraftedIds.length / leagueSize) + 1;

    setRoster(newRoster);
    setDraftedIds(newDraftedIds);
    setCurrentRound(newRound);
    setCurrentPick(currentPick + 1);

    if (newDraftedIds.length >= leagueSize * rosterSize) {
      setDraftComplete(true);
      return;
}

    setDraftBoard([...draftBoard, {
      pick: currentPick,
      player: player.full_name,
      position: player.position,
      team: 'You'
    }]);

    // fire-and-forget: recommendations use drafted_ids from the request, not this
    fetch('https://backend-ivory-reed-8288.fly.dev/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: player.player_id })
    }).catch(() => {});

    fetchRecommendations(newRoster, newDraftedIds, newRound, isMyTurn(currentPick + 1));
  };

  //log a pick
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

    // fire-and-forget: recommendations use drafted_ids from the request, not this
    fetch('https://backend-ivory-reed-8288.fly.dev/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: player.player_id })
    }).catch(() => {});

  console.log('logging pick, newDraftedIds:', newDraftedIds);
  fetchRecommendations(roster, newDraftedIds, newRound, isMyTurn(currentPick + 1));
  };

const handleAutoDraft = async () => {
  let pick = currentPick;
  let draftedIdsCopy = [...draftedIds];
  let teamRostersCopy = teamRosters.map(r => [...r]);
  let draftBoardCopy = [...draftBoard];
  let round = currentRound;

  while (!isMyTurn(pick)) {
    const pickInRound = ((pick - 1) % leagueSize);
    const isEvenRound = Math.floor((pick - 1) / leagueSize) % 2 === 1;
    const teamIndex = isEvenRound ? leagueSize - 1 - pickInRound : pickInRound;

    const currentTeamRoster = teamRostersCopy[teamIndex];

    const response = await fetch('https://backend-ivory-reed-8288.fly.dev/autodraft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        roster: currentTeamRoster,
        round_number: round,
        drafted_ids: draftedIdsCopy
      })
    });

    const data = await response.json();
    const pickedPlayer = data.pick;

    if (!pickedPlayer) break;

    draftedIdsCopy = [...draftedIdsCopy, pickedPlayer.player_id];
    teamRostersCopy[teamIndex] = [...currentTeamRoster, { position: pickedPlayer.position, player_id: pickedPlayer.player_id, full_name: pickedPlayer.full_name }];
    draftBoardCopy = [...draftBoardCopy, { pick, player: pickedPlayer.full_name, position: pickedPlayer.position, team: `Team ${teamIndex + 1}` }];

    pick++;
    round = Math.floor((pick - 1) / leagueSize) + 1;
  }

  if (draftedIdsCopy.length >= leagueSize * rosterSize) {
  setDraftedIds(draftedIdsCopy);
  setTeamRosters(teamRostersCopy);
  setDraftBoard(draftBoardCopy);
  setCurrentPick(pick);
  setCurrentRound(round);
  setDraftComplete(true);
  return;
}

  setDraftedIds(draftedIdsCopy);
  setTeamRosters(teamRostersCopy);
  setDraftBoard(draftBoardCopy);
  setCurrentPick(pick);
  setCurrentRound(round);
  

  fetchRecommendations(roster, draftedIdsCopy, round, true);
};

const myTurn = isMyTurn();
  const picksUntilMine = (() => {
    let n = 0;
    while (!isMyTurn(currentPick + n) && n < leagueSize * 2) n++;
    return n;
  })();
  const pickingTeam = (() => {
    const pickInRound = (currentPick - 1) % leagueSize;
    const isEvenRound = Math.floor((currentPick - 1) / leagueSize) % 2 === 1;
    return (isEvenRound ? leagueSize - 1 - pickInRound : pickInRound) + 1;
  })();
  const pickInRound = ((currentPick - 1) % leagueSize) + 1;
  const pickLabel = `${currentRound}.${String(pickInRound).padStart(2, '0')}`;
  const totalPicks = leagueSize * rosterSize;
  const settings = { qbStarters, rbStarters, wrStarters, teStarters, flexStarters, benchSlots };

  const actionButton = (player, size) => myTurn ? (
    <button className={`btn-primary ${size}`} onClick={() => handleDraft(player)}>Draft</button>
  ) : (
    <button className={`btn-secondary ${size}`} onClick={() => handleLogPick(player)}>Log pick</button>
  );

  if (draftComplete) {
    return (
      <main className="complete">
        <header className="complete-head">
          <span className="eyebrow">Draft complete</span>
          <h1>Your team</h1>
          <p>{roster.length} players drafted across {currentRound > rosterSize ? rosterSize : currentRound} rounds.</p>
        </header>
        <div className="panel">
          <RosterList roster={roster} {...settings} />
        </div>
      </main>
    );
  }

  return (
    <div className="draft">
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <span className="brand-mark" aria-hidden="true" />
            <span className="brand-text">Draft Engine</span>
          </div>

          <div className="clock">
            <div className="clock-pick">
              <span className="clock-label">Pick</span>
              <span className="mono">{pickLabel}</span>
              <span className="clock-sub mono">{currentPick}/{totalPicks}</span>
            </div>
            <div className={`status ${myTurn ? 'status-live' : ''}`}>
              <span className="status-dot" />
              {myTurn ? "You're on the clock" : `Team ${pickingTeam} picking · you in ${picksUntilMine}`}
            </div>
          </div>

          <div className="topbar-actions">
            {!myTurn && <button className="btn-secondary sm" onClick={handleAutoDraft}>Sim to my pick</button>}
            <button className="icon-btn" aria-label="How it works" onClick={onShowInfo}>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.4"><circle cx="8" cy="8" r="6.5" /><path d="M8 7.2v4M8 4.8v.01" strokeLinecap="round" /></svg>
            </button>
          </div>
        </div>
        <div className="progress" aria-hidden="true"><span style={{ width: `${((currentPick - 1) / totalPicks) * 100}%` }} /></div>
      </header>

      <div className="draft-body">
        <main className="draft-main">
          <nav className="tabs" role="tablist">
            {[
              ['recommendations', 'Recommended'],
              ['players', 'All players'],
              ['board', `Board${draftBoard.length ? ` · ${draftBoard.length}` : ''}`],
              ['roster', 'My roster'],
            ].map(([key, label]) => (
              <button
                key={key}
                role="tab"
                aria-selected={activeTab === key}
                className={`tab ${activeTab === key ? 'tab-active' : ''} ${key === 'roster' ? 'tab-roster' : ''}`}
                onClick={() => { setActiveTab(key); if (key === 'players') fetchAllPlayers(); }}
              >
                {label}
              </button>
            ))}
          </nav>

          {activeTab === 'recommendations' && (
            <section>
              {!myTurn && (
                <p className="notice">Not your pick. Log what Team {pickingTeam} takes, or sim ahead to your turn. Reasoning is shown when you're on the clock.</p>
              )}
              {loading ? <SkeletonRows /> : (
                <ol className="rec-list">
                  {recommendations.map((player, i) => (
                    <li key={player.player_id} className="rec">
                      <span className="rec-rank mono">{i + 1}</span>
                      <div className="rec-body">
                        <div className="rec-title">
                          <PosChip pos={player.position} />
                          <h3>{player.full_name}</h3>
                          <span className="meta">{player.team || 'FA'} · {player.age ? `${player.age} yrs` : '—'}</span>
                        </div>
                        {myTurn && player.explanation && <p className="rec-why">{player.explanation}</p>}
                        <ScoreBreakdown player={player} />
                      </div>
                      <div className="rec-side">
                        <div className="score">
                          <span className="mono">{fmt(player.overall_score)}</span>
                          <small>score</small>
                        </div>
                        {actionButton(player, 'sm')}
                      </div>
                    </li>
                  ))}
                </ol>
              )}
            </section>
          )}

          {activeTab === 'players' && (
            <section>
              <div className="toolbar">
                <div className="search">
                  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="7" cy="7" r="5" /><path d="M11 11l3.5 3.5" strokeLinecap="round" /></svg>
                  <input
                    type="text"
                    placeholder="Search players"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <div className="segmented" role="group" aria-label="Filter by position">
                  {['ALL', 'QB', 'RB', 'WR', 'TE'].map(pos => (
                    <button
                      key={pos}
                      className={positionFilter === pos ? 'active' : ''}
                      onClick={() => setPositionFilter(pos)}
                    >
                      {pos === 'ALL' ? 'All' : pos}
                    </button>
                  ))}
                </div>
              </div>
              {allPlayers.length === 0 ? <SkeletonRows /> : (
                <div className="table">
                  <div className="table-head players-grid">
                    <span>#</span><span>Player</span><span className="hide-sm">Team</span><span className="num">Score</span><span />
                  </div>
                  {allPlayers
                    .filter(p =>
                      !draftedIds.includes(p.player_id) &&
                      p.full_name.toLowerCase().includes(searchQuery.toLowerCase()) &&
                      (positionFilter === 'ALL' || p.position === positionFilter)
                    )
                    .slice(0, 200)
                    .map((player, i) => (
                      <div key={player.player_id} className="table-row players-grid">
                        <span className="mono dim">{i + 1}</span>
                        <span className="cell-player"><PosChip pos={player.position} /><span className="name">{player.full_name}</span></span>
                        <span className="dim hide-sm">{player.team || 'FA'}</span>
                        <span className="num mono">{fmt(player.overall_score)}</span>
                        <span className="cell-action">{actionButton(player, 'xs')}</span>
                      </div>
                    ))}
                </div>
              )}
            </section>
          )}

          {activeTab === 'board' && (
            <section>
              {draftBoard.length === 0 ? (
                <div className="empty">
                  <p>No picks yet</p>
                  <small>Picks you draft, log or sim will show up here.</small>
                </div>
              ) : (
                <div className="table">
                  <div className="table-head board-grid">
                    <span>Pick</span><span>Player</span><span>Team</span>
                  </div>
                  {[...draftBoard].reverse().map((entry) => {
                    const r = Math.floor((entry.pick - 1) / leagueSize) + 1;
                    const p = ((entry.pick - 1) % leagueSize) + 1;
                    return (
                      <div key={entry.pick} className={`table-row board-grid ${entry.team === 'You' ? 'row-mine' : ''}`}>
                        <span className="mono dim">{r}.{String(p).padStart(2, '0')}</span>
                        <span className="cell-player"><PosChip pos={entry.position} /><span className="name">{entry.player}</span></span>
                        <span className={entry.team === 'You' ? 'you' : 'dim'}>{entry.team}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </section>
          )}

          {activeTab === 'roster' && (
            <section className="roster-tab">
              <RosterList roster={roster} {...settings} />
            </section>
          )}
        </main>

        <aside className="sidebar">
          <div className="panel">
            <div className="panel-head">
              <h2>My roster</h2>
              <span className="mono dim">{roster.length}/{rosterSize}</span>
            </div>
            <RosterList roster={roster} {...settings} />
          </div>
        </aside>
      </div>
    </div>
  );
}

const fmt = (n) => (typeof n === 'number' ? n.toFixed(1) : '—');

function PosChip({ pos }) {
  return <span className={`pos pos-${(pos || '').toLowerCase()}`}>{pos}</span>;
}

function ScoreBreakdown({ player }) {
  const items = [
    ['Base', player.base_score],
    ['Potential', player.potential_score],
    ['Sleeper', player.sleeper_score],
    ['Need', player.need_score],
  ].filter(([, v]) => typeof v === 'number');
  if (!items.length) return null;
  return (
    <dl className="breakdown">
      {items.map(([label, v]) => (
        <div key={label}>
          <dt>{label}</dt>
          <dd className="mono">{v.toFixed(1)}</dd>
          <span className="bar"><span style={{ width: `${Math.max(0, Math.min(100, v * 10))}%` }} /></span>
        </div>
      ))}
    </dl>
  );
}

function SkeletonRows() {
  return (
    <div className="skeleton" aria-label="Loading">
      {Array.from({ length: 5 }, (_, i) => <div key={i} className="skeleton-row" />)}
    </div>
  );
}

function RosterList({ roster, qbStarters, rbStarters, wrStarters, teStarters, flexStarters, benchSlots }) {
  const group = (slot, count) => Array.from({ length: count }, (_, i) => ({
    slot,
    player: roster.filter(p => p.slot === slot)[i],
  }));
  const starters = [
    ...group('QB', qbStarters),
    ...group('RB', rbStarters),
    ...group('WR', wrStarters),
    ...group('TE', teStarters),
    ...group('FLEX', flexStarters),
  ];
  const bench = group('BENCH', benchSlots);

  const row = ({ slot, player }, i) => (
    <li key={`${slot}${i}`} className={`slot ${player ? '' : 'slot-empty'}`}>
      <span className="slot-label">{slot === 'BENCH' ? 'BN' : slot === 'FLEX' ? 'FLX' : slot}</span>
      {player ? (
        <span className="slot-player">
          <span className="name">{player.full_name}</span>
          {slot !== player.position && <PosChip pos={player.position} />}
        </span>
      ) : <span className="slot-player">Empty</span>}
    </li>
  );

  return (
    <div className="roster">
      <h3>Starters</h3>
      <ul>{starters.map(row)}</ul>
      {benchSlots > 0 && (
        <>
          <h3>Bench</h3>
          <ul>{bench.map(row)}</ul>
        </>
      )}
    </div>
  );
}

export default DraftScreen;
