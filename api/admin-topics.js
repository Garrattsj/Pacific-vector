// api/admin-topics.js
// Returns the full topic taxonomy, for populating the topic picker in the
// admin UI. Read-only — topics are managed via migrations, not the UI.

import { isAuthenticated } from '../lib/adminAuth.js';
import { pgRequest } from '../lib/supabaseAdmin.js';

export default async function handler(req, res) {
  if (!isAuthenticated(req)) return res.status(401).json({ error: 'Unauthorized' });
  if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const topics = await pgRequest('/topics?select=id,name&order=name.asc');
    return res.status(200).json({ topics });
  } catch (err) {
    console.error('admin-topics error:', err);
    return res.status(500).json({ error: 'Server error' });
  }
}
