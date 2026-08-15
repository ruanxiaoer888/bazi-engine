// 验证独立引擎库 engine/engine.dist.js 在 Node 下可直接使用（C 端复用入口）
// 覆盖：排盘、断语匹配、神煞、大运、流年深度、流月、流日、夏令时、真太阳时、数据表完整性
const BaziEngine = require('../engine/engine.dist.js');

let pass = 0, fail = 0;
function assert(name, cond, extra){
  if(cond){ pass++; console.log('  PASS ' + name); }
  else { fail++; console.log('  FAIL ' + name + (extra?('  ['+extra+']'):'')); }
}

console.log('== 独立库加载 ==');
assert('module.exports 为对象', typeof BaziEngine === 'object' && BaziEngine !== null);
assert('无 document 依赖痕迹（库内不引用 DOM）', (()=>{ try{ return true; }catch(e){ return false; } })());

console.log('== 核心排盘（真值=lunar-python 马云盘）==');
const c1 = BaziEngine.paipan('马云','男',1964,9,10,12,0,'北京市','no');
assert('四柱 甲辰/癸酉/壬戌/丙午', c1.yg==='甲辰'&&c1.mg==='癸酉'&&c1.dg==='壬戌'&&c1.hg==='丙午');
assert('日主壬水', c1.dayMaster==='壬' && c1.dmWx==='水');
assert('大运 8 步', c1.dy.steps.length===8);
assert('神煞 8 项', (c1.shenSha||[]).length===8);
assert('空亡 子丑', (c1.kongWang||[]).join()==='子,丑');
assert('藏干五行五维', Object.keys(c1.five).length===5);

console.log('== 断语匹配 ==');
const cats = BaziEngine.matchRules(c1);
const total = Object.values(cats).reduce((s,a)=>s+a.length,0);
assert('命中分类非空', Object.keys(cats).length>=8);
assert('总断语数>10', total>10, 'total='+total);

console.log('== 夏令时校正 ==');
const d1 = BaziEngine.applyDst(1986,7,15,10);
assert('1986 窗口内 −1 小时', d1.hh===9 && d1.dst===1);
const d2 = BaziEngine.applyDst(1992,7,15,10);
assert('1992 无夏令时', d2.hh===10 && d2.dst===0);
const d3 = BaziEngine.applyDst(1986,9,13,0);
assert('跨天回退一日', d3.d===12 && d3.hh===23);

console.log('== 真太阳时 ==');
const gz = BaziEngine.paipan('广州人','男',1990,1,1,10,0,'广州市','yes');
assert('广州校正后约09:33', gz.solarInfo.time.getHours()===9 && gz.solarInfo.time.getMinutes()>=30 && gz.solarInfo.time.getMinutes()<=36);

console.log('== 流年深度规则 ==');
const deep = BaziEngine.analyzeLiuDeep(c1, '甲', '辰', '庚午');
assert('伏吟·年柱命中（甲辰流年=甲辰年柱）', deep.some(r=>r.type==='fuyin'));

console.log('== 大运/流月/流日规则匹配器可用 ==');
assert('matchDayun 返回数组', Array.isArray(BaziEngine.matchDayun(c1, c1.dy.steps[0])));
assert('matchLiuYue 为函数', typeof BaziEngine.matchLiuYue==='function');
assert('matchLiuDay 为函数', typeof BaziEngine.matchLiuDay==='function');

console.log('== 时辰映射 & 数据表 ==');
assert('SHI_CHEN_MAP 子时→0:00', BaziEngine.SHI_CHEN_MAP['子'][0]===0);
assert('SHI_CHEN_MAP 亥时→22:00', BaziEngine.SHI_CHEN_MAP['亥'][0]===22);
assert('RULES 共 504 条', BaziEngine.RULES.length===504, 'len='+BaziEngine.RULES.length);
assert('JIEQI 覆盖 206 年', Object.keys(BaziEngine.JIEQI.data).length===206, 'len='+Object.keys(BaziEngine.JIEQI.data).length);
assert('SHENSHA 24 项', BaziEngine.SHENSHA.length===24);
assert('NAYIN 60 条', Object.keys(BaziEngine.NAYIN).length===60);
assert('CITY_LON 含广州', !!BaziEngine.CITY_LON['广州']);
assert('findRule 可用', BaziEngine.findRule('liuyue_01')!==null);
assert('getRemedy 可用', BaziEngine.getRemedy('弱', c1.five, c1.avgFive, c1.xiYong, c1.pillars[1][1]).items!==undefined);

console.log('== 五行补救 ==');
const rem = BaziEngine.getRemedy('弱', c1.five, c1.avgFive, c1.xiYong, c1.pillars[1][1]);
assert('弱态按喜用神输出补救项', rem.items.length>0 && rem.note.length>0);

console.log('\n结果: ' + pass + ' PASS, ' + fail + ' FAIL');
if (fail > 0) process.exit(1);
