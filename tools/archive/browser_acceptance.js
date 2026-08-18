// 浏览器端到端走查脚本（修正版：用真实 id 与按钮文本选择器）
const pw = require('C:/Users/34743/.workbuddy/binaries/node/workspace/node_modules/playwright');
const fs = require('fs');

(async()=>{
  const findings = [];
  const log = (k,v) => { findings.push(k+': '+v); console.log(k+': '+v); };

  const b = await pw.chromium.launch({headless:true, args:['--no-sandbox']});
  const ctx = await b.newContext({viewport:{width:1440,height:900}});
  const p = await ctx.newPage();
  p.on('console', msg => { if(msg.type()==='error') log('CONSOLE_ERROR', msg.text()); });
  p.on('pageerror', err => log('PAGE_ERROR', err.message));

  await p.goto('http://127.0.0.1:8765/index.html');
  await p.waitForTimeout(500);

  // === A. 排盘（1990-05-15 10:00 男 广州 真太阳时）===
  log('A1', '开始填表');
  await p.fill('#name', '测试甲');
  await p.selectOption('#gender', '男');
  await p.fill('#date', '1990-05-15');
  await p.fill('#time', '10:00');
  await p.fill('#birthplace', '广州市');
  await p.selectOption('#truesun', 'yes');
  await p.getByRole('button', {name: /排盘并分析/}).click();
  await p.waitForTimeout(1500);
  await p.screenshot({path:'assets/screenshots/02_paipan_done.png', fullPage:true});

  const body = await p.textContent('body');
  log('A2_yz_庚午', /庚午/.test(body));
  log('A2_yz_辛巳', /辛巳/.test(body));
  log('A2_yz_丙辰', /丙辰/.test(body));
  log('A2_hz_癸巳', /癸巳/.test(body));
  log('A2_身弱_喜用', /身弱|喜用|用神/.test(body));

  // 检查错误元素
  const errCount = await p.locator('.error, .alert-danger').count();
  log('A3_error_els', errCount);

  // === B. 流日 tab ===
  log('B1', '流日 tab');
  await p.fill('#liuDayYear', '2026');
  await p.selectOption('#liuDayMonth', '8');
  await p.getByRole('button', {name: /展开逐日运势/}).click();
  await p.waitForTimeout(800);
  await p.screenshot({path:'assets/screenshots/03_liuri.png', fullPage:true});

  // === C. 六亲 ===
  log('C1', '六亲 tab');
  await p.getByRole('button', {name: /展开六亲详解/}).click();
  await p.waitForTimeout(800);
  await p.screenshot({path:'assets/screenshots/04_liuqin.png', fullPage:true});
  const bodyQin = await p.textContent('body');
  log('C2_qin_4sections', /父母/.test(bodyQin) && /配偶/.test(bodyQin) && /子女/.test(bodyQin) && /兄弟/.test(bodyQin));

  // === D. 流年 ===
  log('D1', '流年 tab');
  await p.fill('#liuYear', '2026');
  await p.getByRole('button', {name: /分析该流年/}).click();
  await p.waitForTimeout(800);
  await p.screenshot({path:'assets/screenshots/05_liunian.png', fullPage:true});

  // === E. 流月 ===
  log('E1', '流月 tab');
  await p.fill('#liuMonthYear', '2026');
  await p.getByRole('button', {name: /展开十二流月/}).click();
  await p.waitForTimeout(800);
  await p.screenshot({path:'assets/screenshots/05b_liuyue.png', fullPage:true});

  // === F. 窄屏 375x812 ===
  await p.setViewportSize({width:375, height:812});
  await p.waitForTimeout(500);
  await p.screenshot({path:'assets/screenshots/06_mobile_375.png', fullPage:false});
  const overflow = await p.evaluate(()=>{
    return { docW: document.documentElement.scrollWidth, winW: window.innerWidth, hasH: document.documentElement.scrollWidth>window.innerWidth+2 };
  });
  log('F1_mobile_overflow', JSON.stringify(overflow));

  // === G. 边界盘 1895-01-03 ===
  await p.setViewportSize({width:1440, height:900});
  await p.getByRole('button', {name: /返回重新排盘/}).click();
  await p.waitForTimeout(400);
  await p.fill('#name', '1895边界');
  await p.selectOption('#gender', '男');
  await p.fill('#date', '1895-01-03');
  await p.fill('#time', '10:00');
  await p.fill('#birthplace', '广州市');
  await p.selectOption('#truesun', 'yes');
  await p.getByRole('button', {name: /排盘并分析/}).click();
  await p.waitForTimeout(1200);
  await p.screenshot({path:'assets/screenshots/07_edge_1895.png', fullPage:true});
  const bodyEdge = await p.textContent('body');
  log('G1_1895_yz_甲午', /甲午/.test(bodyEdge));
  log('G1_1895_mz_丙子', /丙子/.test(bodyEdge));

  // === H. 无效日期 2/30 ===
  await p.getByRole('button', {name: /返回重新排盘/}).click();
  await p.waitForTimeout(400);
  await p.fill('#name', '无效');
  await p.fill('#date', '2024-02-30');
  await p.fill('#time', '10:00');
  await p.fill('#birthplace', '北京市');
  await p.getByRole('button', {name: /排盘并分析/}).click();
  await p.waitForTimeout(500);
  const alertTxt = await p.evaluate(()=>globalThis._alerts?globalThis._alerts.slice(-3):[]).catch(()=>[]);
  log('H1_invalid_alert', JSON.stringify(alertTxt));

  // === I. 合婚：填两盘后提交 ===
  log('I1', '合婚');
  await p.fill('#hNameA', '甲'); await p.selectOption('#hSexA', '男'); await p.fill('#hDateA', '1990-05-15'); await p.fill('#hTimeA', '10:00'); await p.fill('#hPlaceA', '广州市');
  await p.fill('#hNameB', '乙'); await p.selectOption('#hSexB', '女'); await p.fill('#hDateB', '1992-08-20'); await p.fill('#hTimeB', '14:00'); await p.fill('#hPlaceB', '上海市');
  const heBtn = p.getByRole('button', {name: /合婚|配对|测算/}).first();
  if(await heBtn.count() > 0){
    await heBtn.click();
    await p.waitForTimeout(800);
    await p.screenshot({path:'assets/screenshots/08_hehun.png', fullPage:true});
  } else {
    log('I1_he_btn', '未找到合婚按钮');
  }

  // === J. 元素引用完整性统计 ===
  const ids = await p.$$eval('[id]', els => els.map(e=>e.id));
  log('J1_total_ids', ids.length);
  const missingInputs = ['#name','#gender','#date','#time','#birthplace','#truesun'];
  for(const sel of missingInputs){
    const exists = await p.locator(sel).count();
    log('J2_'+sel, exists>0?'OK':'MISSING');
  }

  await b.close();
  fs.writeFileSync('assets/screenshots/findings.json', JSON.stringify(findings,null,2));
  console.log('\n=== 完成 ===');
})().catch(e=>{ console.error('FATAL', e.stack); process.exit(1); });