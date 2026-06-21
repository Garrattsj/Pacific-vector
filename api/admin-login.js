// api/admin-login.js
// Checks the admin password and sets a session cookie on success.

import { checkPassword, setSessionCookie } from '../lib/adminAuth.js';

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { password } = req.body || {};
  if (!checkPassword(password)) {
    return res.status(401).json({ error: 'Invalid password' });
  }

  setSessionCookie(res);
  return res.status(200).json({ success: true });
}
