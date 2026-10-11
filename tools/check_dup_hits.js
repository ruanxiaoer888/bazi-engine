// 检测：同一盘是否同时命中"同文案/近似文案"规则（面板会重复显示）
// 2026-10 修复：
//   ① 原脚本**没有任何退出码** → CI/人工跑都恒"绿"，属假门禁；
//   ② 原 12 组里有 6 组引用了已删除的规则 id（health_jin / health_mu / health_shui /
//      marriage_bijie_qiang / marriage_caiguan_strong / wealth_shenruo_caiwang），这些组恒报"双命中 0"，
//      看起来"很干净"其实什么都没检测。
//   现在：规则 id 不存在直接以退出码 2 报错（防止再次静默失效）；双命中率超阈值以退出码 1 报错。
const fs = require('fs');
const html = fs.readFileSync(__dirname + '/../ui/index.html', 'utf8');
const code = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const stub = 'var document={getElementById:()=>({value:"",innerHTML:"",style:{},classList:{add(){},remove(){}}}),querySelectorAll:()=>[],querySelector:()=>null};var alert=()=>{};';
eval(stub + code + ';globalThis.matchRules=matchRules;globalThis.paipan=paipan;globalThis.RULES=RULES;');

const RULE_IDS = new Set(RULES.map(r => r.id));

// 阈值：同一盘同时命中一对"近似文案"规则的比例上限（%），超过即需人工复核
const THRESHOLD = Number(process.env.DUP_HIT_THRESHOLD || 15);

// 仅保留**当前真实存在**的规则对；已删除的旧对不再列入（脚本会在下方校验 id 有效性）
const groups = [
  ['marriage_caiguan_he', 'marriage_caiguan_weak'],
  ['pattern_zhengguan_cheng', 'pattern_正官格'],
  ['pattern_qisha_zhi', 'pattern_七杀格'],
  ['pattern_cong', 'pattern_cong_sp'],
  ['pattern_zhuanwang', 'pattern_zhuanwang_sp'],
  ['pattern_shangguan_yin', 'combo_伤官_正印'],
  ['health_金_wang', 'health_金_ruo'],
  ['health_木_wang', 'health_木_ruo'],
  ['health_水_wang', 'health_水_ruo'],
];

// 门禁①：id 有效性（防脚本再次静默失效）
const missing = new Set();
for (const [a, b] of groups) {
  if (!RULE_IDS.has(a)) missing.add(a);
  if (!RULE_IDS.has(b)) missing.add(b);
}
if (missing.size) {
  console.error('❌ 以下规则 id 在 rules.json 中不存在，脚本已失效，请更新 groups：');
  console.error('   ' + [...missing].join(', '));
  process.exit(2);
}

const hit = (c, id) => {
  const cats = matchRules(c);
  for (const cat in cats) {
    if (cats[cat].some(r => r.id === id)) return true;
  }
  return false;
};

const stats = {};
for (const [a, b] of groups) { stats[a + '||' + b] = { both: 0, total: 0, aOnly: 0, bOnly: 0, neither: 0 }; }
let total = 0;
const seeds = [1978, 1981, 1984, 1987, 1990, 1993, 1996, 1999, 2002, 2005];
for (let si = 0; si < 10; si++) {
  for (let i = 0; i < 120; i++) {
    const y = seeds[si] + (i % 22), m = 1 + (i * 7) % 12, d = 1 + (i * 13) % 28, hh = i % 24, mm = (i * 17) % 60;
    const c = paipan('测', '男', y, m, d, hh, mm, '广州', 'no');
    if (!c) continue;
    total++;
    for (const [a, b] of groups) {
      const ra = hit(c, a), rb = hit(c, b);
      const s = stats[a + '||' + b];
      if (ra && rb) s.both++;
      else if (ra) s.aOnly++;
      else if (rb) s.bOnly++;
      else s.neither++;
    }
  }
}

console.log(`共 ${total} 盘（阈值 ${THRESHOLD}%）\n`);
const over = [];
for (const [a, b] of groups) {
  const s = stats[a + '||' + b];
  const pct = total ? (s.both / total * 100) : 0;
  const flag = pct > THRESHOLD ? '  ⚠️ 超阈值' : '';
  console.log(`${a} × ${b}: 双命中 ${s.both} (${pct.toFixed(1)}%) | 仅a=${s.aOnly} 仅b=${s.bOnly} 都无=${s.neither}${flag}`);
  if (pct > THRESHOLD) over.push(`${a} × ${b} (${pct.toFixed(1)}%)`);
}

// 门禁②：双命中率
if (over.length) {
  console.error('\n❌ 双命中率超过阈值，需人工复核（合并文案或差异化 condition）：');
  over.forEach(x => console.error('   ' + x));
  process.exit(1);
}
console.log('\n✅ 无规则对超过双命中阈值；规则 id 全部有效。');
process.exit(0);
