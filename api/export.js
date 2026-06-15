// api/export.js
// Exports the Resend subscriber audience as a downloadable CSV.
// Protected by a shared secret — visit /api/export?key=YOUR_EXPORT_SECRET

export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' });

  const RESEND_API_KEY = process.env.RESEND_API_KEY;
  const AUDIENCE_ID    = process.env.RESEND_AUDIENCE_ID;
  const EXPORT_SECRET  = process.env.EXPORT_SECRET;

  // Require a secret key to prevent public access to subscriber data
  if (!EXPORT_SECRET || req.query.key !== EXPORT_SECRET) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    const allContacts = [];
    let pageToken = null;

    // Page through all contacts (Resend paginates large audiences)
    do {
      const url = new URL(`https://api.resend.com/audiences/${AUDIENCE_ID}/contacts`);
      if (pageToken) url.searchParams.set('after', pageToken);

      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${RESEND_API_KEY}` },
      });

      if (!response.ok) {
        const err = await response.json();
        console.error('Resend error:', err);
        return res.status(502).json({ error: 'Failed to fetch contacts' });
      }

      const data = await response.json();
      const contacts = data.data || [];
      allContacts.push(...contacts);

      // Resend's contacts list endpoint is not paginated in practice for small
      // audiences, but guard against an unexpected pagination cursor anyway.
      pageToken = data.next_page_token || null;
    } while (pageToken);

    // Build CSV
    const headers = [
      'email', 'first_name', 'last_name', 'organisation', 'role',
      'industry', 'source', 'created_at', 'unsubscribed',
    ];

    const escapeCsv = (val) => {
      const str = String(val ?? '');
      if (/[",\n]/.test(str)) return `"${str.replace(/"/g, '""')}"`;
      return str;
    };

    const rows = allContacts.map((c) => {
      const props = c.properties || {};
      return [
        c.email,
        c.first_name,
        c.last_name,
        props.organisation,
        props.role,
        props.industry,
        props.source,
        c.created_at,
        c.unsubscribed,
      ].map(escapeCsv).join(',');
    });

    const csv = [headers.join(','), ...rows].join('\n');

    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', `attachment; filename="pacific-vector-subscribers-${new Date().toISOString().slice(0, 10)}.csv"`);
    return res.status(200).send(csv);

  } catch (err) {
    console.error('Export error:', err);
    return res.status(500).json({ error: 'Server error' });
  }
}
