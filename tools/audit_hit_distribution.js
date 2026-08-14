#!/usr/bin/env node
// 断语库大样本命中分布审查工具（全类别覆盖版）
// 用法：
//   node audit_hit_distribution.js                 # 默认 80 个随机盘全量审查（全16类别）
//   node audit_hit_distribution.js --sample=200    # 自定义样本数
//   node audit_hit_distribution.js --rules=combo_全无财星,pattern_tiaohou  # 深挖指定规则
//   node audit_hit_distribution.js --cat=性格,财运  # 只看指定类别
//
// 判定标准：
//   - 命中率 100% 的规则 = 坏规则（条件过宽/字段引用错误/存在性判断代替真实判断），必须修复
//   - 命中率 >80% 需人工复核；单盘 0 命中也异常（覆盖缺口或引擎短路）
//   - 无 condition 的规则 = 始终命中（若非故意设计则需补条件）
const fs = require('fs');
const path = require('path');

// ---- 参数解析 ----
const args = process.argv.slice(2);
const sampleN = (args.find(a => a.startsWith('--sample=')) || '--sample=80').split('=')[1] | 0;
const rulesArg = (args.find(a => a.startsWith('--rules=')) || '').split('=')[1];
const catsArg = (args.find(a => a.startsWith('--cat=')) || '').split('=')[1];
const watchRules = rulesArg ? rulesArg.split(',').map(s => s.trim()).filter(Boolean) : null;
const watchCats = catsArg ? catsArg.split(',').map(s => s.trim()).filter(Boolean) : null;

// ---- 从 index.html 提取 JS 并在 vm 中执行 ----
const html = fs.readFileSync(path.join(__dirname, '..', 'ui', 'index.html'), 'utf8');
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error('未找到 <script> 块'); process.exit(1); }
const stub = 'var document={getElementById:()=>({value:"",innerHTML:"",style:{},classList:{add(){},remove(){}}}),querySelectorAll:()=>[]};var alert=()=>{};';
const exp = ';globalThis.paipan=paipan;globalThis.matchRules=matchRules;globalThis.RULES=RULES;globalThis.tenGod=tenGod;globalThis.GAN_WX=GAN_WX;globalThis.CANG=CANG;';
eval(stub + m[1] + exp);

// ---- 全 16 类别 ----
const ALL_CATS = ['性格','事业','财运','婚姻','健康','格局','用神喜忌','十神组合','学业','六亲','神煞','流年','合婚','五行生克','大运','流月'];
let activeCats = watchCats || ALL_CATS;

// ---- 随机盘生成 ----
const rand = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
const charts = [];
for (let i = 0; i < sampleN; i++) {
  const y = rand(1950, 2005), mo = rand(1, 12), d = rand(1, 28), hh = rand(0, 23), mm = rand(0, 59);
  const c = paipan('P' + i, i % 2 ? '男' : '女', y, mo, d, hh, mm, '', 'no');
  if (c) charts.push(c);
}
const total = charts.length;
console.log(`样本: ${total} 个随机命盘 (${new Date().toISOString().slice(0, 19)})\n`);

// ---- 逐盘匹配并统计 ----
const hitCount = {};
charts.forEach(c => {
  const cats = matchRules(c);
  activeCats.forEach(cat => {
    (cats[cat] || []).forEach(r => { hitCount[r.id] = (hitCount[r.id] || 0) + 1; });
  });
});

// ---- 无 condition 的规则（始终命中）----
console.log(`== 无 condition 的规则（始终命中，${activeCats.join('/')} 内）==`);
const noCondRules = RULES.filter(r => activeCats.includes(r.category) && (!r.condition || Object.keys(r.condition).length === 0));
if (noCondRules.length === 0) console.log('✅ 无无条件命中规则');
else {
  noCondRules.forEach(r => console.log(`  ℹ️  ${r.id} [${r.category}] → ${r.conclusion.substring(0, 40)}...`));
  console.log(`共 ${noCondRules.length} 条（若为通用评语则正常，若应有条件则需补）`);
}

// ---- 100% 命中规则（坏规则候选）----
console.log(`\n== ${activeCats.join('/')} 类中命中率 100% 的规则（共 ${total} 盘）==`);
let bad = 0;
for (const id in hitCount) {
  if (hitCount[id] === total) {
    // 跳过无condition规则（已在上面报告）
    const r = RULES.find(x => x.id === id);
    if (r && (!r.condition || Object.keys(r.condition).length === 0)) continue;
    bad++;
    console.log(`⚠️  ${id} [${r ? r.category : '?'}] cond=${JSON.stringify(r ? r.condition : null)}`);
    console.log(`    → ${r ? r.conclusion : '(不存在)'}`);
  }
}
console.log(bad === 0 ? '✅ 无 100% 命中规则（排除无条件规则）' : `共 ${bad} 条需修复\n`);

// ---- 命中率分布 ----
console.log('\n== 命中率分布（>80% 需人工复核，排除无条件规则）==');
const over80 = [];
for (const id in hitCount) {
  const r = RULES.find(x => x.id === id);
  if (r && (!r.condition || Object.keys(r.condition).length === 0)) continue; // 跳过无条件规则
  const rate = hitCount[id] / total;
  if (rate > 0.8) over80.push({ id, rate, hit: hitCount[id] });
}
over80.sort((a, b) => b.rate - a.rate);
if (over80.length === 0) console.log('✅ 无 >80% 命中规则');
else over80.forEach(({ id, rate, hit }) => {
  const r = RULES.find(x => x.id === id);
  console.log(`🔎 ${id} ${(rate * 100).toFixed(0)}% (${hit}/${total}) [${r ? r.category : '?'}] → ${r ? r.conclusion.substring(0, 50) : ''}`);
});
const conditionalRules = Object.keys(hitCount).filter(id => {
  const r = RULES.find(x => x.id === id);
  return r && r.condition && Object.keys(r.condition).length > 0;
});
console.log(`有条件规则数: ${conditionalRules.length}（本类别内，不含无条件规则）`);

// ---- 每盘平均命中 ----
const per = charts.map(c => {
  let cnt = 0;
  const cats = matchRules(c);
  activeCats.forEach(cat => { cnt += (cats[cat] || []).length; });
  return cnt;
});
const avg = per.reduce((a, b) => a + b, 0) / total;
console.log(`\n${activeCats.join('/')} 平均命中/盘: ${avg.toFixed(1)} (范围 ${Math.min(...per)} - ${Math.max(...per)})`);

// ---- 深挖指定规则 ----
if (watchRules) {
  watchRules.forEach(id => {
    const r = RULES.find(x => x.id === id);
    console.log(`\n== 深挖 ${id} ==`);
    if (!r) { console.log('  (规则不存在)'); return; }
    console.log(`  condition: ${JSON.stringify(r.condition)}`);
    console.log(`  conclusion: ${r.conclusion}`);
    let hit = 0;
    charts.forEach(c => {
      const cats = matchRules(c);
      const all = Object.values(cats).flat();
      if (all.some(x => x.id === id)) {
        hit++;
        if (hit <= 3) { // 展示前 3 个命中盘的简化上下文
          console.log(`  命中盘 ${c.name}: 日主${c.dayMaster}(${c.dmWx}) 月${c.pillars[1][1]} 五行:${JSON.stringify(c.five)} 喜用:[${c.xiYong}]`);
        }
      }
    });
    console.log(`  命中率: ${hit}/${total} (${(hit / total * 100).toFixed(0)}%)`);
  });
}
