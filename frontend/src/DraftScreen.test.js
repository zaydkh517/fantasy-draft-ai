import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import '@testing-library/jest-dom';
import DraftScreen from './DraftScreen';

// Small fake player pool; the mocked backend ranks them in this order.
const POOL = Array.from({ length: 20 }, (_, i) => ({
  player_id: `p${i + 1}`,
  full_name: `Player ${i + 1}`,
  position: ['RB', 'WR', 'QB', 'TE'][i % 4],
  team: 'TST',
  age: 25,
  overall_score: 10 - i * 0.1,
}));

let calls;

function mockBackend({ failRecommendOnce = false } = {}) {
  calls = [];
  let failNext = failRecommendOnce;
  global.fetch = jest.fn(async (url, opts) => {
    const path = url.replace(/^https?:\/\/[^/]+/, '');
    const body = opts?.body ? JSON.parse(opts.body) : {};
    calls.push({ path, body });
    const available = POOL.filter(p => !(body.drafted_ids || []).includes(p.player_id));
    const json = (data) => ({ ok: true, status: 200, json: async () => data });
    if (path === '/recommend') {
      if (failNext) { failNext = false; return { ok: false, status: 500, json: async () => ({}) }; }
      return json({ recommendations: available.slice(0, 10).map(p => ({ ...p, explanation: body.generate_explanations ? 'why' : null })) });
    }
    if (path === '/autodraft') return json({ pick: available[0] || null });
    if (path === '/rank-all') return json({ players: available });
    return json({});
  });
}

// 2 teams, roster of 3 (QB, RB, WR) => 6 picks. You pick 1st: your picks are 1, 4, 5; Team 2 has 2, 3, 6.
const props = {
  leagueSize: 2, rosterSize: 3, draftPosition: 1,
  qbStarters: 1, rbStarters: 1, wrStarters: 1, teStarters: 0, flexStarters: 0, benchSlots: 0,
  onShowInfo: () => {},
};

// Saved drafts would otherwise leak from one test into the next
beforeEach(() => localStorage.clear());

// First recommendation row, once the list is loaded and clickable
const firstRec = () => waitFor(() => {
  const el = document.querySelector('.rec-list:not(.is-stale) .rec');
  if (!el) throw new Error('recommendations not ready');
  return el;
});

test('full draft: sim stops at the last pick and the draft completes', async () => {
  mockBackend();
  render(<DraftScreen {...props} />);

  // Pick 1 (you)
  fireEvent.click(within(await firstRec()).getByText('Draft'));
  // Picks 2-3 (Team 2) via sim
  fireEvent.click(await screen.findByText('Sim to my pick'));
  await screen.findByText("You're on the clock");
  // Picks 4 and 5 (you, back to back at the turn)
  fireEvent.click(within(await firstRec()).getByText('Draft'));
  await waitFor(() => expect(screen.getByText("You're on the clock")).toBeInTheDocument());
  fireEvent.click(within(await firstRec()).getByText('Draft'));
  // Pick 6 is Team 2's, and the last pick of the draft
  fireEvent.click(await screen.findByText('Sim to the end'));

  await screen.findByText('Your team');
  const autodrafts = calls.filter(c => c.path === '/autodraft');
  expect(autodrafts).toHaveLength(3); // picks 2, 3, 6 only; no phantom round 4
  // league settings travel with every ranking request
  calls.filter(c => c.path !== '/').forEach(c => expect(c.body.league_settings).toMatchObject({ league_size: 2, roster_size: 3 }));
});

test('logging the final pick completes the draft', async () => {
  mockBackend();
  render(<DraftScreen {...props} />);

  fireEvent.click(within(await firstRec()).getByText('Draft'));        // 1 you
  fireEvent.click(within(await firstRec()).getByText('Log pick'));     // 2 team 2
  await waitFor(async () => within(await firstRec()).getByText('Log pick'));
  fireEvent.click(within(await firstRec()).getByText('Log pick'));     // 3 team 2
  await screen.findByText("You're on the clock");
  fireEvent.click(within(await firstRec()).getByText('Draft'));        // 4 you
  await screen.findByText("You're on the clock");
  fireEvent.click(within(await firstRec()).getByText('Draft'));        // 5 you
  await waitFor(async () => within(await firstRec()).getByText('Log pick'));
  fireEvent.click(within(await firstRec()).getByText('Log pick'));     // 6 team 2, last pick

  expect(await screen.findByText('Your team')).toBeInTheDocument();
});

test('a drafted player disappears from recommendations immediately', async () => {
  mockBackend();
  render(<DraftScreen {...props} />);
  const rec = await firstRec();
  const name = within(rec).getByRole('heading').textContent;
  fireEvent.click(within(rec).getByText('Draft'));
  // Before the new recommendations arrive, the drafted player is already gone from the list
  const list = document.querySelector('.rec-list');
  expect(within(list).queryByText(name)).toBeNull();
});

test('sim button is locked while simulating', async () => {
  mockBackend();
  render(<DraftScreen {...props} />);
  fireEvent.click(within(await firstRec()).getByText('Draft'));
  const sim = await screen.findByText('Sim to my pick');
  fireEvent.click(sim);
  fireEvent.click(sim);
  fireEvent.click(sim);
  await screen.findByText("You're on the clock");
  expect(calls.filter(c => c.path === '/autodraft')).toHaveLength(2);
});

test('failed recommendations show a retry instead of loading forever', async () => {
  mockBackend({ failRecommendOnce: true });
  render(<DraftScreen {...props} />);
  expect(await screen.findByRole('alert')).toHaveTextContent("Couldn't load recommendations");
  fireEvent.click(screen.getByText('Retry'));
  await firstRec();
  expect(screen.queryByRole('alert')).toBeNull();
});

test('a draft in progress survives a reload', async () => {
  mockBackend();
  const { unmount } = render(<DraftScreen {...props} />);
  fireEvent.click(within(await firstRec()).getByRole('button', { name: 'Draft' }));
  await waitFor(() => expect(document.querySelector('.clock-sub')).toHaveTextContent('2/6'));
  unmount();

  mockBackend();
  render(<DraftScreen {...props} />);
  expect(document.querySelector('.clock-sub')).toHaveTextContent('2/6');
  // The restored draft's picks go to the backend, so Player 1 isn't recommended again
  await waitFor(() => expect(calls.find(c => c.path === '/recommend')?.body.drafted_ids).toEqual(['p1']));
});

test('a saved draft is not restored under different league settings', async () => {
  mockBackend();
  const { unmount } = render(<DraftScreen {...props} />);
  fireEvent.click(within(await firstRec()).getByRole('button', { name: 'Draft' }));
  await waitFor(() => expect(document.querySelector('.clock-sub')).toHaveTextContent('2/6'));
  unmount();

  mockBackend();
  render(<DraftScreen {...props} draftPosition={2} />);
  expect(document.querySelector('.clock-sub')).toHaveTextContent('1/6');
});
