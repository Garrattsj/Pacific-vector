// api/archive.js
// Returns list of all available briefs for the archive page

import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');

  try {
    const briefsDir = path.join(process.cwd(), 'briefs');

    if (!fs.existsSync(briefsDir)) {
      return res.status(200).json([]);
    }

    const files = fs.readdirSync(briefsDir)
      .filter(f => f.endsWith('.json'))
      .sort()
      .reverse(); // Most recent first

    const archive = files.map(file => {
      try {
        const brief = JSON.parse(fs.readFileSync(path.join(briefsDir, file), 'utf8'));
        const slug = file.replace('pacific_vector_', '').replace('.json', '');
        return {
          date: brief.date,
          opening_line: brief.opening_line,
          slug: slug,
        };
      } catch {
        return null;
      }
    }).filter(Boolean);

    res.status(200).json(archive);

  } catch (err) {
    console.error('Archive API error:', err);
    res.status(500).json({ error: 'Server error' });
  }
}
