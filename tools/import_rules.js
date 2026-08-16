#!/usr/bin/env node
/**
 * import_rules.js — 断语批量导入与质检（434→800 流水线的 Step 3→4 工具）
 *
 * 用法：
 *   node tools/import_rules.js --draft 草稿.jsonl [--write] [--stats]
 *
 * 草稿格式（每行一条 JSON，或整个文件为 JSON 数组）：
 *   {"id":"liuri_jia_zi_he","category":"流日","condition":{"组合":"日柱合日支"},"conclusion":"...","source":"《三命通会》xxx","confidence":"高","suggestion":"..."}
 *
 * 校验规则（Step 4 数据红线）：
 *   1. id 必填且全局唯一（与现有库不冲突）
 *   2. category 必填（建议在断语库已有类别内）
 *   3. condition 至少含一个维度（日主/旺衰/十神/五行/状态/性别/位置/组合/格局/神煞/流年）
 *   4. conclusion 非空
 *   5. source 非空且包含书名号《》——可追溯命门，格式不达标一律拒绝
 *   6. confidence 若填写必须是 高/中/低
 *
 * 注意：本脚本只校验"出处格式"，无法验证"出处真伪"。
 * 真实性红线（流水线 Step 2）必须人工逐字核对古籍原文，一条假出处=毁掉全部信誉。
 *
 * 默认 dry-run 只报告不写库；加 --write 才合并写回断语库。
 * 写库后请继续：python tools/build_ui.py && node tools/test_ui.js
 */
const fs = require('fs');
const path = require('path');

const DB_PATH = path.join(__dirname, '..', 'kb', '04-rules-db', 'rules.json');
const VALID_CATS = ['性格','事业','财运','婚姻','格局','用神喜忌','健康','十神组合','学业','六亲','神煞','流年','合婚','五行生克','大运','流月','流日'];
const COND_DIMS = ['日主','旺衰','十神','五行','状态','性别','位置','组合','格局','神煞','流年','流月','流日'];

function parseArgs(argv) {
  const args = { draft: null, write: false, stats: false };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--draft') args.draft = argv[++i];
    else if (a === '--write') args.write = true;
    else if (a === '--stats') args.stats = true;
  }
  return args;
}

function loadDraft(p) {
  const raw = fs.readFileSync(p, 'utf8').trim();
  if (!raw) return [];
  if (raw.startsWith('[')) return JSON.parse(raw);
  return raw.split('\n').filter(l => l.trim()).map(l => JSON.parse(l));
}

function loadDb() {
  return JSON.parse(fs.readFileSync(DB_PATH, 'utf8'));
}

function validate(rule, existingIds) {
  const errs = [];
  if (!rule.id || typeof rule.id !== 'string') errs.push('缺 id');
  else if (existingIds.has(rule.id)) errs.push(`id 与现有库冲突: ${rule.id}`);
  if (!rule.category) errs.push('缺 category');
  else if (VALID_CATS.length && !VALID_CATS.includes(rule.category)) errs.push(`category 不在已知类别: ${rule.category}`);
  const cond = rule.condition || {};
  if (typeof cond !== 'object' || Object.keys(cond).length === 0) errs.push('condition 为空（至少一个维度）');
  else {
    const bad = Object.keys(cond).filter(k => !COND_DIMS.includes(k));
    if (bad.length) errs.push(`condition 含未知维度: ${bad.join(',')}（已知: ${COND_DIMS.join('/')}）`);
  }
  if (!rule.conclusion || typeof rule.conclusion !== 'string') errs.push('缺 conclusion');
  if (!rule.source || !/《[^》]+》/.test(rule.source)) errs.push('source 缺失或未含书名号《》（可追溯命门）');
  if (rule.confidence && !['高','中','低'].includes(rule.confidence)) errs.push(`confidence 非法: ${rule.confidence}（须 高/中/低）`);
  return errs;
}

function main() {
  const args = parseArgs(process.argv);
  if (!args.draft) {
    console.error('用法: node tools/import_rules.js --draft <草稿.jsonl> [--write] [--stats]');
    process.exit(1);
  }
  if (!fs.existsSync(args.draft)) {
    console.error(`草稿文件不存在: ${args.draft}`);
    process.exit(1);
  }

  const db = loadDb();
  const existingIds = new Set(db.rules.map(r => r.id));
  const draft = loadDraft(args.draft);

  console.log(`现有断语库: ${db.rules.length} 条 | 草稿: ${draft.length} 条\n`);

  const ok = [], fail = [];
  for (const r of draft) {
    const errs = validate(r, existingIds);
    if (errs.length) fail.push({ rule: r, errs });
    else { ok.push(r); existingIds.add(r.id); }
  }

  // 草稿内部重复检测（按 conclusion 归一化）
  const byText = new Map();
  for (const r of ok) {
    const t = (r.conclusion || '').trim();
    if (byText.has(t)) fail.push({ rule: r, errs: [`conclusion 与草稿内 ${byText.get(t)} 文案重复`] });
    else byText.set(t, r.id);
  }
  // 去重后重算
  const okFinal = ok.filter(r => !fail.some(f => f.rule === r));

  // 与现有库文案查重
  const dbTexts = new Set(db.rules.map(r => (r.conclusion || '').trim()));
  const okClean = okFinal.filter(r => {
    const dup = dbTexts.has((r.conclusion || '').trim());
    if (dup) fail.push({ rule: r, errs: ['conclusion 与现有断语库文案重复'] });
    return !dup;
  });

  console.log('--- 校验结果 ---');
  console.log(`通过: ${okClean.length} 条 | 拒绝: ${fail.length} 条\n`);
  if (fail.length) {
    console.log('被拒条目明细:');
    for (const { rule, errs } of fail) {
      console.log(`  ✗ ${rule.id || '(无id)'} (${rule.category || '?'}): ${errs.join('; ')}`);
      console.log(`      conclusion: ${String(rule.conclusion || '').slice(0, 40)}`);
    }
    console.log('');
  }

  if (args.stats || args.write) {
    const dist = {};
    for (const r of [...db.rules, ...okClean]) dist[r.category] = (dist[r.category] || 0) + 1;
    console.log('--- 合并后类别分布 ---');
    for (const [cat, n] of Object.entries(dist).sort((a, b) => b[1] - a[1])) {
      console.log(`  ${cat}: ${n}`);
    }
    console.log(`  合计: ${db.rules.length + okClean.length} 条（目标 800，缺口 ${Math.max(0, 800 - db.rules.length - okClean.length)}）`);
    console.log('');
  }

  if (args.write) {
    if (okClean.length === 0) { console.log('没有可通过的条目，未写库。'); return; }
    db.rules.push(...okClean);
    // 同步 description 中的条数说明（若含"规则 N 条"字样）
    db.description = (db.description || '').replace(/规则\s*\d+\s*条/, `规则 ${db.rules.length} 条`);
    fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2) + '\n', 'utf8');
    console.log(`✓ 已合并 ${okClean.length} 条 → rules.json（现共 ${db.rules.length} 条）`);
    console.log('\n后续步骤（流水线 Step 5）:');
    console.log('  python tools/build_ui.py');
    console.log('  node tools/test_ui.js');
    console.log('  node tools/check_dup_hits.js && node tools/check_conflicts.js && node tools/audit_hit_distribution.js');
  } else {
    console.log('(dry-run，未写库。确认无误后加 --write 执行)');
  }
}

main();
