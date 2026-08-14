// 大样本矛盾断语检测：同一盘命中互为反义的断语
const fs=require('fs');
const html=fs.readFileSync(__dirname+'/../ui/index.html','utf8');
const code=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const stub='var document={getElementById:()=>({value:"",innerHTML:"",style:{},classList:{add(){},remove(){}}}),querySelectorAll:()=>[],querySelector:()=>null};var alert=()=>{};';
eval(stub+code+';globalThis.matchRules=matchRules;globalThis.paipan=paipan;');
// 反义断语对：20 对 强/弱
const pairs=[];
for(const dm of ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']){
  pairs.push(['char_'+dm+'_强','char_'+dm+'_弱']);
  pairs.push(['yongshen_'+dm+['木','木','火','火','土','土','金','金','水','水'][['甲','乙','丙','丁','戊','己','庚','辛','壬','癸'].indexOf(dm)]+'_强','yongshen_'+dm+['木','木','火','火','土','土','金','金','水','水'][['甲','乙','丙','丁','戊','己','庚','辛','壬','癸'].indexOf(dm)]+'_弱']);
}
let total=0, conflicts=0;
const seeds=[1980,1983,1986,1989,1992,1995,1998,2001,2004,2007];
for(let si=0; si<10; si++){
  for(let i=0;i<100;i++){
    const y=seeds[si]+(i%20), m=1+(i*7)%12, d=1+(i*13)%28, hh=i%24, mm=(i*17)%60;
    const c=paipan('测','男',y,m,d,hh,mm,'广州','no');
    if(!c) continue;
    total++;
    for(const [a,b] of pairs){
      const ra=matchRules(c,{id:a}), rb=matchRules(c,{id:b});
      if(ra.length&&rb.length){ conflicts++; console.log(`冲突: 盘${y}-${m}-${d} ${c.dg} 同时命中 ${a}+${b}`); }
    }
  }
}
console.log(`\n共 ${total} 盘，成对规则 ${pairs.length*2} 条，矛盾命中 ${conflicts} 次`);
