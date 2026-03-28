import { savePreferences } from '../state.js';

export const settingsService = {
  save(preferences) { savePreferences(preferences); return true; },
};
