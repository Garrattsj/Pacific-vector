// api/subscribe.js
// Handles email subscriptions — adds contact to Resend audience

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { name, email } = req.body || {};

  if (!email || !email.includes('@')) {
    return res.status(400).json({ error: 'Valid email required' });
  }

  const RESEND_API_KEY  = process.env.RESEND_API_KEY;
  const AUDIENCE_ID     = process.env.RESEND_AUDIENCE_ID; // Set this in Vercel env vars

  try {
    // Add contact to Resend audience
    const response = await fetch(`https://api.resend.com/audiences/${AUDIENCE_ID}/contacts`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${RESEND_API_KEY}`,
        'Content-Type':  'application/json',
      },
      body: JSON.stringify({
        email:      email,
        first_name: name ? name.split(' ')[0] : '',
        last_name:  name ? name.split(' ').slice(1).join(' ') : '',
        unsubscribed: false,
      }),
    });

    if (!response.ok) {
      const err = await response.json();
      console.error('Resend error:', err);
      // If contact already exists, treat as success
      if (err.name === 'validation_error' && err.message?.includes('already exists')) {
        return res.status(200).json({ success: true, message: 'Already subscribed' });
      }
      return res.status(400).json({ error: 'Subscription failed' });
    }

    // Send welcome email
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${RESEND_API_KEY}`,
        'Content-Type':  'application/json',
      },
      body: JSON.stringify({
        from:    'Pacific Vector <brief@pacific-vector.com>',
        to:      [email],
        subject: 'Welcome to Pacific Vector',
        html:    `
          <div style="font-family: 'IBM Plex Mono', monospace; max-width: 600px; margin: 0 auto; padding: 2rem; color: #0d0d0d;">
            <div style="font-size: 1rem; font-weight: 500; letter-spacing: 0.2em; margin-bottom: 1.5rem;">
              PACIFIC<span style="color: #1a3a5c;">VECTOR</span>
            </div>
            <p style="font-size: 0.85rem; line-height: 1.8; margin-bottom: 1rem;">
              ${name ? `${name.split(' ')[0]},` : 'Hello,'}
            </p>
            <p style="font-size: 0.85rem; line-height: 1.8; margin-bottom: 1rem;">
              You're now subscribed to Pacific Vector — daily Japan geopolitical intelligence.
            </p>
            <p style="font-size: 0.85rem; line-height: 1.8; margin-bottom: 2rem;">
              Your first brief arrives tomorrow morning.
            </p>
            <div style="border-left: 2px solid #1a3a5c; padding-left: 1rem; font-size: 0.78rem; color: #888; line-height: 1.8;">
              Coverage: Japan–China · Japan–US & Security · Indo-Pacific/QUAD · Domestic Politics · Daily Figure Profile
            </div>
            <p style="font-size: 0.68rem; color: #888; margin-top: 2rem;">
              pacific-vector.com
            </p>
          </div>
        `,
      }),
    });

    return res.status(200).json({ success: true });

  } catch (err) {
    console.error('Subscribe error:', err);
    return res.status(500).json({ error: 'Server error' });
  }
}
