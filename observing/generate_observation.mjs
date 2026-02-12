import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const REQUEST_TIMEOUT_MS = Number(process.env.REQUEST_TIMEOUT_MS || 20000);

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 1) {
    const key = argv[i];
    if (!key || !key.startsWith('--')) continue;
    const name = key.slice(2);
    const next = argv[i + 1];
    if (next && !next.startsWith('--')) {
      args[name] = next;
      i += 1;
    } else {
      args[name] = true;
    }
  }
  return args;
}

function formatTimestamp(date) {
  const pad = (n) => String(n).padStart(2, '0');
  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
    pad(date.getHours()),
    pad(date.getMinutes()),
    pad(date.getSeconds()),
  ].join('-');
}

function sanitizeFilenamePrefix(text) {
  if (!text) return 'observation';
  const invalid = /[<>:"/\\|?*\x00-\x1F]/g;
  let cleaned = String(text).replace(invalid, '').replace(/\s+/g, '').trim();
  cleaned = cleaned.replace(/[.\s]+$/g, '');
  const visible = Array.from(cleaned).slice(0, 10).join('');
  const withoutPunct = visible.replace(/[\p{P}\p{S}]/gu, '');
  if (!visible || !withoutPunct) return 'observation';
  return visible;
}

function buildPrompt({ observation, scenario, perspective }) {
  const context = [`观察: ${observation}`];
  if (scenario) context.push(`场景: ${scenario}`);
  if (perspective) context.push(`观察者视角: ${perspective}`);

  return (
    '你将把一条日常观察转写为“现状 -> 理想 -> 差距 -> 机会”的结构化观察笔记。\n' +
    '要求：\n' +
    '- 必须使用中文。\n' +
    '- 必须严格按模板输出，保留标题文字与层级，不要添加额外说明或总结。\n' +
    '- 每个板块要具体，避免空话。\n' +
    '- 差距至少覆盖时间、认知负担、情绪/不确定性三类，可补充成本或其他。\n' +
    '- 至少给出 1 条商机假设。\n' +
    '- 不要给出具体解决方案，只写机会方向。\n' +
    '\n' +
    '模板：\n' +
    '观察场景 (time / place / context)\n' +
    '现实状态 (Current State)\n' +
    '- ...\n' +
    '隐含的理想状态 (Ideal State)\n' +
    '- ...\n' +
    '关键差距 (Gap Description)\n' +
    '- 差距体现为:\n' +
    '  - 时间: ...\n' +
    '  - 成本: ...\n' +
    '  - 认知负担: ...\n' +
    '  - 情绪/不确定性: ...\n' +
    '  - 其他: ...\n' +
    '人们的应对方式 (Workarounds / Tolerance)\n' +
    '- ...\n' +
    '商机假设 (Opportunity Hypotheses)\n' +
    '- ...\n' +
    '\n' +
    '输入：\n' +
    context.join('\n')
  );
}

async function callGemini({ apiKey, model, prompt }) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(model)}:generateContent?key=${encodeURIComponent(apiKey)}`;
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
          temperature: 0.4,
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

    if (!text) {
      throw new Error('Gemini response was empty');
    }

    return String(text);
  } finally {
    clearTimeout(timer);
  }
}

function normalizeOutput(text) {
  if (!text) return '';
  let out = String(text).trim();
  const fenced = out.match(/^```(?:\w+)?\n([\s\S]*?)\n```$/);
  if (fenced && fenced[1]) {
    out = fenced[1].trim();
  } else {
    out = out.replace(/```/g, '').trim();
  }

  const headingIndex = out.indexOf('观察场景');
  if (headingIndex > 0) {
    out = out.slice(headingIndex).trim();
  }

  return out.trim() + '\n';
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const observation = args.observation || process.env.OBSERVATION;
  const scenario = args.scenario || process.env.SCENARIO || '';
  const perspective = args.perspective || process.env.PERSPECTIVE || '';
  const outputDir = args['output-dir'] || process.env.OUTPUT_DIR || 'output/observing';

  const apiKey =
    args['gemini-api-key'] ||
    process.env.ACTION_GEMINI_API_KEY ||
    process.env.GEMINI_API_KEY ||
    process.env.GEMINI ||
    '';
  const model = args['gemini-model'] || process.env.ACTION_GEMINI_MODEL || process.env.GEMINI_MODEL || 'gemini-2.5-flash';

  if (!observation) {
    console.error('Missing required observation input. Use --observation or set OBSERVATION.');
    process.exit(1);
  }
  if (!apiKey) {
    console.error('Missing Gemini API key. Use --gemini-api-key or set GEMINI_API_KEY/GEMINI.');
    process.exit(1);
  }

  const prompt = buildPrompt({ observation, scenario, perspective });
  const rawOutput = await callGemini({ apiKey, model, prompt });
  const output = normalizeOutput(rawOutput);

  const prefix = sanitizeFilenamePrefix(observation);
  const timestamp = formatTimestamp(new Date());
  const filename = `${prefix}-${timestamp}.md`;

  const workspace = process.env.GITHUB_WORKSPACE || process.cwd();
  const resolvedOutputDir = path.isAbsolute(outputDir)
    ? outputDir
    : path.join(workspace, outputDir);
  await fs.mkdir(resolvedOutputDir, { recursive: true });

  const filePath = path.join(resolvedOutputDir, filename);
  await fs.writeFile(filePath, output, 'utf8');

  const outputFile = process.env.GITHUB_OUTPUT;
  if (outputFile) {
    const lines = [
      `note_path=${filePath}`,
      `note_dir=${resolvedOutputDir}`,
      `note_filename=${filename}`,
    ].join('\n') + '\n';
    await fs.appendFile(outputFile, lines, 'utf8');
  }

  console.log(`Note written to: ${filePath}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
