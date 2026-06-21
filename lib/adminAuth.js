// lib/adminAuth.js
// Minimal cookie-based auth for the single-admin /admin/* pages.
// Not imported from /api directly as a route — Vercel only turns files
// inside /api into endpoints, so this stays a plain helper module.

import crypto from 'crypto';

const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || '';
const COOKIE_NAME = 'pv_admin_session';

function sessionToken() {
  // Derived from the password itself — no extra secret to manage, good
  // enough for a single-admin internal tool. Changing ADMIN_PASSWORD
  // automatically invalidates any existing session.
  return crypto.createHmac('sha256', ADMIN_PASSWORD || 'unset')
    .update('pacific-vector-admin')
    .digest('hex');
}

function parseCookies(header) {
  const out = {};
  if (!header) return out;
  header.split(';').forEach((part) => {
    const idx = part.indexOf('=');
    if (idx === -1) return;
    out[part.slice(0, idx).trim()] = decodeURIComponent(part.slice(idx + 1).trim());
  });
  return out;
}

export function isAuthenticated(req) {
  if (!ADMIN_PASSWORD) return false;
  const cookies = parseCookies(req.headers.cookie);
  return cookies[COOKIE_NAME] === sessionToken();
}

export function checkPassword(password) {
  return Boolean(ADMIN_PASSWORD) && password === ADMIN_PASSWORD;
}

export function setSessionCookie(res) {
  const token = sessionToken();
  res.setHeader(
    'Set-Cookie',
    `${COOKIE_NAME}=${token}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=${60 * 60 * 24 * 7}`
  );
}

export function clearSessionCookie(res) {
  res.setHeader(
    'Set-Cookie',
    `${COOKIE_NAME}=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0`
  );
}
