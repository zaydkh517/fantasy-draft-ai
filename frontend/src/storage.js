// Saves league settings and the in-progress draft so a refresh doesn't lose them.
// Storage can be unavailable (private mode, blocked site data), so every access is
// guarded and the app works the same without it, just without saving.

const SETTINGS_KEY = 'draftEngine.settings.v1';
const DRAFT_KEY = 'draftEngine.draft.v1';

function read(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function write(key, value) {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // ignore: quota exceeded or storage blocked
  }
}

export const loadSettings = () => read(SETTINGS_KEY);
export const saveSettings = (settings) => write(SETTINGS_KEY, settings);

// A saved draft only applies to the league settings it was started with
export const loadDraft = (settings) => {
  const saved = read(DRAFT_KEY);
  return saved && JSON.stringify(saved.settings) === JSON.stringify(settings) ? saved.state : null;
};
export const saveDraft = (settings, state) => write(DRAFT_KEY, { settings, state });
export const clearDraft = () => write(DRAFT_KEY, null);
export const hasDraft = () => read(DRAFT_KEY) !== null;

export function getFlag(key) {
  try { return localStorage.getItem(key); } catch { return null; }
}
export function setFlag(key, value) {
  try { localStorage.setItem(key, value); } catch { /* ignore */ }
}
