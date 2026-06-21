// api/admin-sources.js
// CRUD for the source registry, backing the /admin/sources UI.
//   GET    /api/admin-sources?country=Japan&language=en&source_type=media&priority=high&active=true
//   POST   /api/admin-sources            { ...fields, topic_ids: [...] }
//   PATCH  /api/admin-sources?id=<uuid>  { ...partial fields, topic_ids?: [...] }

import { isAuthenticated } from '../lib/adminAuth.js';
import { pgRequest } from '../lib/supabaseAdmin.js';

const EDITABLE_FIELDS = [
  'name', 'feed_url', 'website_url', 'source_type', 'country_or_region',
  'language', 'institution', 'priority', 'reliability_tier', 'is_active',
  'notes', 'inclusion_keywords', 'exclusion_keywords',
  'default_relevance_weight', 'max_items_per_run', 'preferred_article_types',
  'requires_ai_review',
];

function pickEditableFields(body) {
  const out = {};
  for (const key of EDITABLE_FIELDS) {
    if (body[key] !== undefined) out[key] = body[key];
  }
  return out;
}

// Flatten the nested PostgREST embed (source_topics -> topics) into a
// simple `topics: [{id, name}]` array on each source for the frontend.
function flattenTopics(sources) {
  return sources.map((s) => {
    const topics = (s.source_topics || [])
      .map((st) => st.topics)
      .filter(Boolean);
    const { source_topics, ...rest } = s;
    return { ...rest, topics };
  });
}

async function replaceSourceTopics(sourceId, topicIds) {
  // Delete-then-insert is simplest and the table is tiny, so this is cheap.
  await pgRequest(`/source_topics?source_id=eq.${sourceId}`, { method: 'DELETE' });
  if (Array.isArray(topicIds) && topicIds.length) {
    await pgRequest('/source_topics', {
      method: 'POST',
      body: topicIds.map((topic_id) => ({ source_id: sourceId, topic_id })),
    });
  }
}

export default async function handler(req, res) {
  if (!isAuthenticated(req)) return res.status(401).json({ error: 'Unauthorized' });

  try {
    if (req.method === 'GET') {
      const { country, language, source_type, priority, active } = req.query;
      const filters = [];
      if (country)     filters.push(`country_or_region=eq.${encodeURIComponent(country)}`);
      if (language)    filters.push(`language=eq.${encodeURIComponent(language)}`);
      if (source_type) filters.push(`source_type=eq.${encodeURIComponent(source_type)}`);
      if (priority)    filters.push(`priority=eq.${encodeURIComponent(priority)}`);
      if (active === 'true')  filters.push('is_active=eq.true');
      if (active === 'false') filters.push('is_active=eq.false');

      const query = filters.length ? `&${filters.join('&')}` : '';
      const sources = await pgRequest(
        `/sources?select=*,source_topics(topics(id,name))&order=name.asc${query}`
      );
      return res.status(200).json({ sources: flattenTopics(sources) });
    }

    if (req.method === 'POST') {
      const body = req.body || {};
      if (!body.name || !body.feed_url || !body.source_type || !body.country_or_region) {
        return res.status(400).json({ error: 'name, feed_url, source_type, and country_or_region are required' });
      }
      const fields = pickEditableFields(body);
      const [created] = await pgRequest('/sources', {
        method: 'POST',
        body: fields,
        prefer: 'return=representation',
      });
      if (Array.isArray(body.topic_ids)) {
        await replaceSourceTopics(created.id, body.topic_ids);
      }
      return res.status(201).json({ source: created });
    }

    if (req.method === 'PATCH') {
      const id = req.query.id;
      if (!id) return res.status(400).json({ error: 'id query param required' });
      const body = req.body || {};
      const fields = pickEditableFields(body);

      let updated = null;
      if (Object.keys(fields).length) {
        const result = await pgRequest(`/sources?id=eq.${id}`, {
          method: 'PATCH',
          body: fields,
          prefer: 'return=representation',
        });
        updated = result[0];
      }
      if (Array.isArray(body.topic_ids)) {
        await replaceSourceTopics(id, body.topic_ids);
      }
      return res.status(200).json({ source: updated });
    }

    return res.status(405).json({ error: 'Method not allowed' });

  } catch (err) {
    console.error('admin-sources error:', err);
    return res.status(500).json({ error: 'Server error' });
  }
}
