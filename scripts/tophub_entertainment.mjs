import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import crypto from 'node:crypto';

const TOPHUB_URL = process.env.TOPHUB_URL || 'https://tophub.today/c/ent';
const OUTPUT_DIR = process.env.OUTPUT_DIR || 'output';
const REQUEST_TIMEOUT_MS = Number(process.env.REQUEST_TIMEOUT_MS || 20000);

const GEMINI_API_KEY = process.env.GEMINI_API_KEY || process.env.GEMINI;
const GEMINI_MODEL = process.env.GEMINI_MODEL || 'gemini-2.5-flash';

if (!GEMINI_API_KEY) {
  console.error('Missing required env: GEMINI_API_KEY (or GEMINI)');
  process.exit(1);
}

function buildFallbackUrls(url) {
  const stripped = url.replace(/^https?:\/\//, '');
  return [
    url,
    `https://r.jina.ai/http://${stripped}`,
    `https://r.jina.ai/https://${stripped}`,
  ];
}

async function fetchText(url) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const res = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; TophubBot/1.0; +https://github.com)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      },
      signal: controller.signal,
    });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status} for ${url}`);
    }
    return await res.text();
  } finally {
    clearTimeout(timer);
  }
}

async function fetchWithFallback(urls) {
  let lastErr;
  for (const url of urls) {
    try {
      const html = await fetchText(url);
      if (html && html.length > 1000) {
        return { html, url };
      }
      lastErr = new Error(`Empty or short response from ${url}`);
    } catch (err) {
      lastErr = err;
    }
  }
  throw lastErr || new Error('Failed to fetch content');
}

function decodeEntities(str) {
  if (!str) return '';
  return str
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&#x([0-9a-fA-F]+);/g, (_, hex) => {
      try {
        return String.fromCharCode(parseInt(hex, 16));
      } catch {
        return '';
      }
    })
    .replace(/&#(\d+);/g, (_, num) => {
      try {
        return String.fromCharCode(parseInt(num, 10));
      } catch {
        return '';
      }
    });
}

function stripTags(html) {
  return decodeEntities(
    html
      .replace(/<script[\s\S]*?<\/script>/gi, ' ')
      .replace(/<style[\s\S]*?<\/style>/gi, ' ')
      .replace(/<[^>]+>/g, ' ')
  )
    .replace(/\s+/g, ' ')
    .trim();
}

function extractAttr(attrs, name) {
  const re = new RegExp(`${name}\\s*=\\s*(?:\"([^\"]*)\"|'([^']*)'|([^\\s>]+))`, 'i');
  const match = attrs.match(re);
  return match ? (match[1] || match[2] || match[3] || '') : '';
}

const NOISE_WORDS = [
  '登录', '注册', '下载', 'App', 'APP', '帮助', '反馈', '关于', '首页', '分类', '导航',
  '更多', '返回', '上一页', '下一页', '榜单', '热榜', '排行', '排行榜', '最新', '推荐',
  '热门', 'Tophub', 'TOPHUB', '今日热榜', '搜索', '隐私', '条款', '联系我们',
];

function isNoise(text) {
  if (!text) return true;
  const compact = text.replace(/\s+/g, '');
  if (compact.length < 4) return true;
  if (/^\d+$/.test(compact)) return true;
  for (const word of NOISE_WORDS) {
    if (compact.includes(word)) return true;
  }
  return false;
}

function normalizeTitle(text) {
  return decodeEntities(text)
    .replace(/\s+/g, ' ')
    .replace(/^[#\d\s.、()\[\]-]+/, '')
    .trim();
}

function extractTitlesFromHtml(html) {
  const titles = [];
  const seen = new Set();

  const dataTitleRegex = /\bdata-title\s*=\s*(?:\"([^\"]+)\"|'([^']+)')/gi;
  for (const match of html.matchAll(dataTitleRegex)) {
    const raw = match[1] || match[2] || '';
    const title = normalizeTitle(raw);
    if (!title || isNoise(title)) continue;
    if (!seen.has(title)) {
      seen.add(title);
      titles.push(title);
    }
  }

  const anchorRegex = /<a\b([^>]*)>([\s\S]*?)<\/a>/gi;
  for (const match of html.matchAll(anchorRegex)) {
    const attrs = match[1] || '';
    const inner = match[2] || '';
    const href = extractAttr(attrs, 'href');
    if (href && (/^javascript:/i.test(href) || href === '#' || href.startsWith('#'))) {
      continue;
    }

    const text = normalizeTitle(stripTags(inner));
    if (!text || isNoise(text)) continue;
    if (text.length > 80) continue;

    if (!seen.has(text)) {
      seen.add(text);
      titles.push(text);
    }
  }

  return titles;
}

function extractTitlesFromJinaMarkdown(text) {
  const titles = [];
  const seen = new Set();

  // Jina renders markdown links: [TITLE](URL)
  const linkRe = /\[([^\]]{1,120})\]\((https?:\/\/[^\)]+)\)/g;
  for (const match of text.matchAll(linkRe)) {
    const t = normalizeTitle(match[1] || '');
    if (!t || isNoise(t)) continue;
    if (t.length > 80) continue;
    if (!seen.has(t)) {
      seen.add(t);
      titles.push(t);
    }
  }

  // Also catch lines like "1. 标题" in markdown sections.
  const lines = text.split(/\r?\n/);
  for (const line of lines) {
    const m = line.match(/^\s*(?:\d+\.|[-*])\s+(.+)$/);
    if (!m) continue;
    const t = normalizeTitle(m[1]);
    if (!t || isNoise(t)) continue;
    if (t.length > 80) continue;
    if (!seen.has(t)) {
      seen.add(t);
      titles.push(t);
    }
  }

  return titles;
}

function extractTitlesFromFetchedText(body) {
  if (!body) return [];
  if (body.includes('<a') || body.includes('data-title=')) {
    return extractTitlesFromHtml(body);
  }
  // Likely from r.jina.ai
  return extractTitlesFromJinaMarkdown(body);
}

function formatDateInChina(date) {
  const fmt = new Intl.DateTimeFormat('zh-CN', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
  const parts = fmt.formatToParts(date).reduce((acc, p) => {
    acc[p.type] = p.value;
    return acc;
  }, {});
  return `${parts.year}-${parts.month}-${parts.day}`;
}

function extractJsonObject(text) {
  if (!text) return null;
  // Best-effort: take the first {...} block.
  const match = text.match(/\{[\s\S]*\}/);
  return match ? match[0] : null;
}

function validateResult(parsed) {
  if (!parsed || typeof parsed !== 'object') {
    throw new Error('JSON must be an object');
  }
  if (!Array.isArray(parsed.hot_events) || !Array.isArray(parsed.hot_memes)) {
    throw new Error('JSON must include hot_events and hot_memes arrays');
  }
  if (parsed.hot_events.length !== 5 || parsed.hot_memes.length !== 5) {
    throw new Error('Each array must contain exactly 5 items');
  }

  const norm = (arr) => arr.map((x) => String(x || '').trim()).filter(Boolean);
  parsed.hot_events = norm(parsed.hot_events);
  parsed.hot_memes = norm(parsed.hot_memes);

  if (parsed.hot_events.length !== 5 || parsed.hot_memes.length !== 5) {
    throw new Error('Each array must contain 5 non-empty strings');
  }

  return parsed;
}

async function callGemini(titles) {
  const prompt =
    `你将收到今日娱乐榜单的标题列表。请仅基于这些标题，提炼：\n` +
    `1) 5条“热点事件”短句（必须包含：主体 + 做了什么 + 影响/结果 + 最主要的一个来源链接）。\n` +
    `2) 5个“热门梗词”（流行梗、梗语、标签、短语）。\n` +
    `要求：\n` +
    `- 热点事件短句：尽量 10-24 个汉字（或中英混合短句），不要写长段落；只能基于标题归纳，不要凭空编造具体细节。\n` +
    `- 梗词：2-10 个字/短语，口语化。\n` +
    `- 去重，不要含序号。\n` +
    `- 只输出严格 JSON，不要输出任何多余文本。\n` +
    `- JSON 格式必须为 {"hot_events":["..."x5],"hot_memes":["..."x5]}\n` +
    `标题列表（共${titles.length}条）：\n` +
    titles.map((t, i) => `${i + 1}. ${t}`).join('\n');

  const url = `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(GEMINI_MODEL)}:generateContent?key=${encodeURIComponent(GEMINI_API_KEY)}`;

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [{ role: 'user', parts: [{ text: prompt }] }],
        generationConfig: {
          temperature: 0.2,
          responseMimeType: 'application/json',
        },
      }),
      signal: controller.signal,
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => '');
      throw new Error(`Gemini request failed: HTTP ${res.status} ${errText}`);
    }

    const data = await res.json();
    const text =
      data?.candidates?.[0]?.content?.parts?.map((p) => p.text).filter(Boolean).join('\n') ||
      data?.candidates?.[0]?.content?.parts?.[0]?.text ||
      '';

    const rawText = String(text || '');
    const jsonText = extractJsonObject(rawText) || rawText;

    const tryParse = (s) => {
      try {
        return JSON.parse(s);
      } catch {
        return null;
      }
    };

    const fixCommonJsonMistakes = (s) => {
      let out = s;
      // Common model mistake: closes hot_events array with `}` instead of `]`.
      // Example: "hot_events": [ ...
      //   },
      //   "hot_memes": ...
      out = out.replace(/("hot_events"\s*:\s*\[[\s\S]*?\])\s*}\s*,\s*("hot_memes"\s*:)/, '$1,\n  $2');
      // Remove trailing commas before closing brackets/braces.
      out = out.replace(/,\s*([\]}])/g, '$1');
      return out;
    };

    let parsed = tryParse(jsonText);
    if (!parsed) {
      parsed = tryParse(fixCommonJsonMistakes(jsonText));
    }

    if (!parsed) {
      throw new Error(`Failed to parse JSON from Gemini. Raw: ${rawText.slice(0, 500)}`);
    }

    return validateResult(parsed);
  } finally {
    clearTimeout(timer);
  }
}

async function main() {
  const urls = buildFallbackUrls(TOPHUB_URL);
  const { html, url } = await fetchWithFallback(urls);
  const titles = extractTitlesFromFetchedText(html);

  if (!titles.length) {
    throw new Error('No titles extracted from page');
  }

  const result = await callGemini(titles);
  const date = formatDateInChina(new Date());
  const output = {
    date,
    source_url: TOPHUB_URL,
    fetched_from: url,
    titles_count: titles.length,
    hot_events: result.hot_events,
    hot_memes: result.hot_memes,
    model: GEMINI_MODEL,
    generated_at: new Date().toISOString(),
  };

  await fs.mkdir(OUTPUT_DIR, { recursive: true });
  await fs.writeFile(path.join(OUTPUT_DIR, 'titles.txt'), titles.join('\n'), 'utf8');
  const stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\..+$/, '').replace('T', '_');
  const jsonName = `summary_${stamp}.json`;
  const mdName = `summary_${stamp}.md`;

  await fs.writeFile(path.join(OUTPUT_DIR, jsonName), JSON.stringify(output, null, 2), 'utf8');
  await fs.writeFile(path.join(OUTPUT_DIR, mdName),
    `# 今日娱乐热点\n\n` +
      `日期: ${output.date}\n\n` +
      `来源: ${output.source_url}\n\n` +
      `标题数量: ${output.titles_count}\n\n` +
      `## 热点事件（主体-动作-影响）\n` +
      output.hot_events.map((item) => `- ${item}`).join('\n') +
      `\n\n## 热门梗词\n` +
      output.hot_memes.map((item) => `- ${item}`).join('\n') +
      `\n`,
    'utf8'
  );

  // Keep a stable pointer for downstream consumption.
  await fs.writeFile(path.join(OUTPUT_DIR, 'summary.json'), JSON.stringify(output, null, 2), 'utf8');
  await fs.writeFile(path.join(OUTPUT_DIR, 'summary.md'),
    `# 今日娱乐热点\n\n` +
      `日期: ${output.date}\n\n` +
      `来源: ${output.source_url}\n\n` +
      `标题数量: ${output.titles_count}\n\n` +
      `## 热点事件（主体-动作-影响）\n` +
      output.hot_events.map((item) => `- ${item}`).join('\n') +
      `\n\n## 热门梗词\n` +
      output.hot_memes.map((item) => `- ${item}`).join('\n') +
      `\n`,
    'utf8'
  );

  const hash = crypto.createHash('sha256').update(titles.join('\n')).digest('hex').slice(0, 12);
  console.log(`Fetched from: ${url}`);
  console.log(`Titles: ${titles.length}, hash: ${hash}`);
  console.log('Output written to', OUTPUT_DIR);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
