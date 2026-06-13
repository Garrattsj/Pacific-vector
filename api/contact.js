// api/contact.js
// Handles contact form submissions — sends an email via Resend

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { name, email, message } = req.body || {};

  if (!name || !email || !email.includes('@') || !message) {
    return res.status(400).json({ error: 'Name, valid email, and message are required' });
  }

  const RESEND_API_KEY = process.env.RESEND_API_KEY;
  const CONTACT_TO     = process.env.CONTACT_TO_EMAIL; // Set this in Vercel env vars

  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${RESEND_API_KEY}`,
        'Content-Type':  'application/json',
      },
      body: JSON.stringify({
        from:    'Pacific Vector <brief@pacific-vector.com>',
        to:      [CONTACT_TO],
        reply_to: email,
        subject: `Pacific Vector contact form — ${name}`,
        html: `
          <div style="font-family: 'IBM Plex Mono', monospace; max-width: 600px; margin: 0 auto; padding: 2rem; color: #0d0d0d;">
            <div style="font-size: 1rem; font-weight: 500; letter-spacing: 0.2em; margin-bottom: 1.5rem;">
              PACIFIC<span style="color: #1a3a5c;">VECTOR</span>
            </div>
            <p style="font-size: 0.85rem; line-height: 1.8; margin-bottom: 0.5rem;"><strong>From:</strong> ${name} (${email})</p>
            <div style="border-left: 2px solid #1a3a5c; padding-left: 1rem; font-size: 0.85rem; line-height: 1.8; margin-top: 1rem; white-space: pre-wrap;">${message}</div>
          </div>
        `,
      }),
    });

    if (!response.ok) {
      const err = await response.json();
      console.error('Resend error:', err);
      return res.status(500).json({ error: 'Failed to send message' });
    }

    return res.status(200).json({ success: true });

  } catch (err) {
    console.error('Contact error:', err);
    return res.status(500).json({ error: 'Server error' });
  }
}
