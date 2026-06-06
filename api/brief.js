// api/brief.js
// Serves today's brief JSON to the website frontend
// Vercel Serverless Function

import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  // Allow CORS
  res.setHeader('Access-Control-Allow-Origin', '*');

  try {
    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    const briefPath = path.join(process.cwd(), 'briefs', `pacific_vector_${today}.json`);

    if (!fs.existsSync(briefPath)) {
      // Try yesterday's brief as fallback
      const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
      const fallbackPath = path.join(process.cwd(), 'briefs', `pacific_vector_${yesterday}.json`);

      if (!fs.existsSync(fallbackPath)) {
        return res.status(404).json({ error: 'No brief available' });
      }

      const brief = JSON.parse(fs.readFileSync(fallbackPath, 'utf8'));
      return res.status(200).json(brief);
    }

    const brief = JSON.parse(fs.readFileSync(briefPath, 'utf8'));
    res.status(200).json(brief);

  } catch (err) {
    console.error('Brief API error:', err);
    res.status(500).json({ error: 'Server error' });
  }
}
