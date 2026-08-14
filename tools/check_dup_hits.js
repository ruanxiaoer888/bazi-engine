// 检测：同一盘是否同时命中"同文案/近似文案"规则（面板会重复显示）
const fs=require('fs');
const html=fs.readFileSync(__dirname+'/../ui/index.html','utf8');
const code=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const stub='var document={getElementById:()=>({value:"",innerHTML:"",style:{},classList:{add(){},remove(){}}}),querySelectorAll:()=>[],querySelector:()=>null};var alert=()=>{};';
eval(stub+code+';globalThis.matchRules=matchRules;globalThis.paipan=paipan;');
const hit=(c,id)=>{
  const cats=matchRules(c);
  for(const cat in cats){
    if(cats[cat].some(r=>r.id===id)) return true;
  }
  return false;
};
const groups=[
  ['marriage_bijie_duo','marriage_bijie_qiang'],
  ['marriage_caiguan_he','marriage_caiguan_strong'],
  ['wealth_bodyweak_cai','wealth_shenruo_caiwang'],
  ['pattern_zhengguan_cheng','pattern_正官格'],
  ['pattern_qisha_zhi','pattern_七杀格'],
  ['pattern_cong','pattern_cong_sp'],
  ['pattern_zhuanwang','pattern_zhuanwang_sp'],
  ['pattern_shangguan_yin','combo_伤官_正印'],
  ['health_jin','health_金_wang'],
  ['health_jin','health_金_ruo'],
  ['health_mu','health_木_wang'],
  ['health_shui','health_水_wang'],
];
const stats={};
for(const [a,b] of groups){ stats[a+'||'+b]={both:0,total:0,aOnly:0,bOnly:0,neither:0}; }
let total=0;
const seeds=[1978,1981,1984,1987,1990,1993,1996,1999,2002,2005];
for(let si=0; si<10; si++){
  for(let i=0;i<120;i++){
    const y=seeds[si]+(i%22), m=1+(i*7)%12, d=1+(i*13)%28, hh=i%24, mm=(i*17)%60;
    const c=paipan('测','男',y,m,d,hh,mm,'广州','no');
    if(!c) continue;
    total++;
    for(const [a,b] of groups){
      const ra=hit(c,a), rb=hit(c,b);
      const s=stats[a+'||'+b];
      if(ra&&rb) s.both++;
      else if(ra) s.aOnly++;
      else if(rb) s.bOnly++;
      else s.neither++;
    }
  }
}
console.log(`共 ${total} 盘\n`);
for(const [a,b] of groups){
  const s=stats[a+'||'+b];
  const bothPct=(s.both/total*100).toFixed(1);
  console.log(`${a} × ${b}: 双命中 ${s.both} (${bothPct}%) | 仅a=${s.aOnly} 仅b=${s.bOnly} 都无=${s.neither}`);
}
