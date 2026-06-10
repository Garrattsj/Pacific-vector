// api/brief.js
// Serves the most recent available brief to the website frontend

import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');

  try {
    const briefsDir = path.join(process.cwd(), 'briefs');

    if (!fs.existsSync(briefsDir)) {
      return res.status(404).json({ error: 'No briefs directory found' });
    }

    // Get all JSON files, sort by filename (which is date-based), take the latest
    const files = fs.readdirSync(briefsDir)
      .filter(f => f.startsWith('pacific_vector_') && f.endsWith('.json'))
      .sort()
      .reverse();

    if (files.length === 0) {
      return res.status(404).json({ error: 'No briefs available' });
    }

    // Always serve the most recent brief
    const latestFile = files[0];
    const briefPath = path.join(briefsDir, latestFile);
    const brief = JSON.parse(fs.readFileSync(briefPath, 'utf8'));

    res.status(200).json(brief);

  } catch (err) {
    console.error('Brief API error:', err);
    res.status(500).json({ error: 'Server error' });
  }
}
