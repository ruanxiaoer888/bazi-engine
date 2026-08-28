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
// 2026-08-19 修复（工具链审计）：原断言 try{return true} 恒真，改真实检查 dist 源码不含 DOM 引用
const fs = require('fs');
const distSrc = fs.readFileSync(__dirname + '/../engine/engine.dist.js', 'utf8');
assert('dist 不引用 DOM（document/getElementById）', !/document\.|getElementById/.test(distSrc));

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
assert('RULES 共 1000 条', BaziEngine.RULES.length===1000, 'len='+BaziEngine.RULES.length);
assert('JIEQI 覆盖 206 年', Object.keys(BaziEngine.JIEQI.data).length===206, 'len='+Object.keys(BaziEngine.JIEQI.data).length);
assert('SHENSHA 24 项', BaziEngine.SHENSHA.length===24);
assert('NAYIN 60 条', Object.keys(BaziEngine.NAYIN).length===60);
assert('CITY_LON 含广州', !!BaziEngine.CITY_LON['广州']);
// 2026-08-28 CITY_LON 扩充至 724 城（345 地级市 + 379 县级市）：关键县级市防回退断言
assert('CITY_LON 共 724 城', Object.keys(BaziEngine.CITY_LON).length===724, 'len='+Object.keys(BaziEngine.CITY_LON).length);
assert('CITY_LON 含黄冈(地级)', BaziEngine.CITY_LON['黄冈']===114.9, '黄冈='+BaziEngine.CITY_LON['黄冈']);
assert('CITY_LON 含义乌市(县级)', BaziEngine.CITY_LON['义乌市']===120.1, '义乌市='+BaziEngine.CITY_LON['义乌市']);
assert('CITY_LON 含昆山市(县级)', BaziEngine.CITY_LON['昆山市']===121, '昆山市='+BaziEngine.CITY_LON['昆山市']);
assert('CITY_LON 含神木市(县级)', BaziEngine.CITY_LON['神木市']===110.3, '神木市='+BaziEngine.CITY_LON['神木市']);
assert('CITY_LON 含喀什(西部)', BaziEngine.CITY_LON['喀什']===75.9, '喀什='+BaziEngine.CITY_LON['喀什']);
// 匹配逻辑：最长名称优先 + 去"市"后缀兼容（填"义乌"命中"义乌市"）
const yw = BaziEngine.paipan('测试','男',1990,6,1,14,0,'义乌','yes');
assert('填"义乌"命中义乌市 120.1°', yw.solarInfo && yw.solarInfo.found && yw.solarInfo.lon===120.1, JSON.stringify(yw.solarInfo));
const yid = BaziEngine.paipan('测试','男',1990,6,1,14,0,'湖北省宜昌市宜都市','yes');
assert('最长匹配:宜都市(111.4)优先于宜昌', yid.solarInfo && yid.solarInfo.found && yid.solarInfo.lon===111.4, JSON.stringify(yid.solarInfo));
assert('findRule 可用', BaziEngine.findRule('liuyue_01')!==null);
assert('getRemedy 可用', BaziEngine.getRemedy('弱', c1.five, c1.avgFive, c1.xiYong, c1.pillars[1][1]).items!==undefined);

console.log('== 五行补救 ==');
const rem = BaziEngine.getRemedy('弱', c1.five, c1.avgFive, c1.xiYong, c1.pillars[1][1]);
assert('弱态按喜用神输出补救项', rem.items.length>0 && rem.note.length>0);

console.log('\n结果: ' + pass + ' PASS, ' + fail + ' FAIL');
if (fail > 0) process.exit(1);
