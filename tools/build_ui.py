# -*- coding: utf-8 -*-
"""构建单文件八字排盘 UI：把节气表(jieqi.json)与断语库(rules)内联进 HTML 模板，
输出 ui/index.html（完全离线、零外部依赖）。

功能：
- 精确四柱（年/月/时柱按节气精确时刻切分、晚子时）
- 真太阳时校正
- 大运推算
- 藏干加权五行分布 + 身强身弱(帮扶/克泄耗比例) + 喜用神 + 月令取格
- 断语库匹配（性格/事业/财运/婚姻/健康/格局/用神喜忌/十神组合/学业/六亲）
- 流年分析（流年干支、十神、与原局生克冲合、与大运关系；含岁运并临/伏吟/反吟深度规则、空亡判断、十二长生状态）
- 流月分析（十二流月柱、纳音、十神、与命局合冲、调候月运简述）
- 合婚配对（七大维度评分）
- 神煞（24 项吉凶星曜，按年/月/日干支查法计算并显示实际出现者）
- 五行补救（基于喜用神 + 调候法的颜色/方位/数字/行业/饰品/饮食建议）
- 胎元/命宫/身宫三式宫位
- 特殊格局细分（专旺：曲直/炎上/稼穑/从革/润下；从格：从财/从杀/从儿/从势）
"""

import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
jieqi = json.load(open(os.path.join(ROOT, "ui", "jieqi.json"), encoding="utf-8"))
rules = json.load(
    open(
        os.path.join(ROOT, "knowledge-base", "04-断语库", "断语库.json"),
        encoding="utf-8",
    )
)["rules"]

TPL = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>八字命盘 · 赛博命理师</title>
<style>
  :root{
    --bg:#07070d; --bg2:#0d0d15; --card:#12121e; --card2:#161627;
    --ink:#e6dfcf; --ink2:#f2ecdf; --muted:#8f8774; --muted2:#5d574a;
    --gold:#c9a35f; --gold2:#dfc088; --gold3:#9c7a3f;
    --line:#23232f; --line2:#1c1c28; --line3:#34344c;
    --red:#e06060; --green:#52b083; --accent:#c9a35f;
    --wood:#63c08c; --fire:#e06060; --earth:#d6a94e; --metal:#b6c2cc; --water:#63a3d9;
    --wood-bg:rgba(99,192,140,0.08); --fire-bg:rgba(224,96,96,0.08); --earth-bg:rgba(214,169,78,0.08);
    --metal-bg:rgba(182,194,204,0.08); --water-bg:rgba(99,163,217,0.08);
    --shadow:0 8px 32px rgba(0,0,0,0.35);
    --radius:14px; --radius2:8px;
    --font-heading:"Songti SC","STSong","SimSun","Noto Serif SC",serif;
    --font-body:system-ui,-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{
    font-family:var(--font-body); background:var(--bg); color:var(--ink);
    line-height:1.8; padding:28px 20px; min-height:100vh;
    background-image:
      radial-gradient(ellipse at 50% -5%, rgba(201,163,95,0.06) 0%, transparent 55%),
      radial-gradient(ellipse at 15% 90%, rgba(99,163,217,0.03) 0%, transparent 45%),
      radial-gradient(ellipse at 85% 35%, rgba(224,96,96,0.025) 0%, transparent 45%);
  }
  .wrap{max-width:980px;margin:0 auto}
  /* ===== 品牌头部 ===== */
  .brand{text-align:center;padding:6px 0 26px}
  .brand-rings{
    width:52px;height:52px;margin:0 auto 14px;border-radius:50%;
    border:1px solid rgba(201,163,95,0.55);position:relative;
    display:flex;align-items:center;justify-content:center;
    background:radial-gradient(circle, rgba(201,163,95,0.08) 0%, transparent 70%);
  }
  .brand-rings::before{
    content:'';position:absolute;inset:7px;border-radius:50%;
    border:1px dashed rgba(201,163,95,0.35);
  }
  .brand-rings::after{
    content:'';width:10px;height:10px;border-radius:50%;
    background:var(--gold);box-shadow:0 0 14px rgba(201,163,95,0.6);
  }
  h1{
    font-family:var(--font-heading); font-size:32px; font-weight:900; text-align:center;
    color:var(--gold2); letter-spacing:10px; margin-bottom:8px; text-indent:10px;
    text-shadow:0 0 40px rgba(201,163,95,0.18);
  }
  .sub{text-align:center;color:var(--muted);font-size:12.5px;letter-spacing:2px}
  .sub em{font-style:normal;color:var(--gold3);padding:0 6px}
  .rule{max-width:420px;height:1px;margin:18px auto 0;
    background:linear-gradient(90deg,transparent,rgba(201,163,95,0.4),transparent);
    position:relative}
  .rule::after{content:'';position:absolute;left:50%;top:-2.5px;width:5px;height:5px;
    transform:translateX(-50%) rotate(45deg);background:var(--gold3);opacity:0.8}
  /* ===== 卡片 ===== */
  .card{
    background:linear-gradient(180deg,var(--card),var(--card2));
    border:1px solid var(--line);border-radius:var(--radius);
    padding:26px;margin-bottom:20px;box-shadow:var(--shadow);
    position:relative;transition:border-color 0.3s;
  }
  .card::before{
    content:'';position:absolute;inset:6px;border:1px solid rgba(201,163,95,0.07);
    border-radius:10px;pointer-events:none;
  }
  .card:hover{border-color:var(--line3)}
  .card h2{
    font-family:var(--font-heading);font-size:16px;color:var(--gold2);
    display:flex;align-items:center;gap:10px;margin-bottom:18px;letter-spacing:2px;
  }
  .card h2 .num{
    flex:none;width:26px;height:26px;border-radius:50%;font-size:12px;
    border:1px solid var(--gold3);color:var(--gold);
    display:inline-flex;align-items:center;justify-content:center;
    font-family:var(--font-body);letter-spacing:0;
  }
  .card h2::after{
    content:'';flex:1;height:1px;
    background:linear-gradient(90deg,rgba(201,163,95,0.35),transparent);
  }
  /* ===== 表单 ===== */
  .form-card{max-width:100%;margin-bottom:20px}
  label{display:block;font-size:12.5px;color:var(--muted);margin:14px 0 6px;letter-spacing:1px}
  input,select{
    width:100%;padding:11px 14px;border:1px solid var(--line);border-radius:var(--radius2);
    font-size:14px;background:var(--bg2);color:var(--ink);font-family:var(--font-body);
    transition:border-color 0.2s,box-shadow 0.2s;
  }
  input::placeholder{color:var(--muted2)}
  input:focus,select:focus{border-color:var(--gold);outline:none;box-shadow:0 0 0 3px rgba(201,163,95,0.08)}
  .row{display:flex;gap:14px;flex-wrap:wrap}
  .row>div{flex:1;min-width:140px}
  .date-group{display:flex;gap:8px}
  .date-group select{flex:1;min-width:0}
  .time-group{display:flex;gap:8px;align-items:center}
  .time-group select{flex:1;min-width:0}
  .time-group select#timeMode,.time-group select#hTimeModeA,.time-group select#hTimeModeB{width:auto;flex:0 0 auto;min-width:96px}
  .time-group select#shichen,.time-group select#hShichenA,.time-group select#hShichenB{flex:1}
  .time-hint{font-size:11px;color:var(--muted);margin-top:4px;min-height:18px}
.cal-toggle{display:flex;gap:0;margin-bottom:0}
  .cal-toggle button{flex:1;padding:2px 16px;border:1px solid var(--line);background:var(--bg2);color:var(--muted);font-size:12.5px;cursor:pointer;margin-top:0;letter-spacing:1px;font-weight:400;font-family:var(--font-body);border-radius:0}
  .cal-toggle button:first-child{border-radius:6px 0 0 6px;border-right:none}
  .cal-toggle button:last-child{border-radius:0 6px 6px 0;border-left:none}
  .cal-toggle button.active{background:var(--gold);color:#0a0a0f;border-color:var(--gold);font-weight:700}
  .cal-toggle button:hover:not(.active){border-color:var(--gold3);color:var(--ink)}
  button{
    background:linear-gradient(135deg,var(--gold2),var(--gold) 45%,var(--gold3));
    color:#0a0a0f;border:none;padding:12px 34px;border-radius:var(--radius2);font-size:14.5px;
    cursor:pointer;margin-top:20px;letter-spacing:3px;font-weight:700;
    font-family:var(--font-heading);transition:all 0.25s;
    box-shadow:0 4px 18px rgba(201,163,95,0.18);
  }
  button:hover{transform:translateY(-1px);box-shadow:0 6px 22px rgba(201,163,95,0.3)}
  button:active{transform:translateY(0)}
  button.ghost{
    background:transparent;color:var(--gold);border:1px solid var(--gold3);
    box-shadow:none;
  }
  button.ghost:hover{background:rgba(201,163,95,0.07);border-color:var(--gold)}
  /* ===== 四柱表 ===== */
  table{width:100%;border-collapse:separate;border-spacing:0;margin-top:6px}
  th,td{
    border:1px solid var(--line);padding:10px 6px;text-align:center;font-size:14px
  }
  th{background:var(--bg2);color:var(--muted);font-weight:600;font-size:12px;letter-spacing:2px}
  .pillar{font-size:22px;font-weight:700;color:var(--ink2);font-family:var(--font-heading)}
  .tg{color:var(--gold)}
  .dz{color:var(--ink2)}
  .ten{font-size:12px;color:var(--muted)}
  /* 四柱专业命盘样式 */
  .phead{font-size:13px;letter-spacing:3px;color:var(--gold2);background:var(--bg2)}
  .prow{width:64px;font-size:12px}
  .pgz{padding:14px 6px 12px!important;line-height:1.35}
  .ptg{display:block;font-size:26px;font-weight:800;color:var(--gold2);font-family:var(--font-heading);letter-spacing:2px}
  .pdz{display:block;font-size:26px;font-weight:800;color:var(--ink2);font-family:var(--font-heading);letter-spacing:2px;margin-top:2px}
  .pgz.cur{background:rgba(201,163,95,0.07);border-color:var(--gold3)!important;box-shadow:inset 0 0 24px rgba(201,163,95,0.05)}
  .hidden{display:none}
  /* ===== 五行 ===== */
  .five{display:flex;gap:12px;flex-wrap:wrap;margin-top:12px}
  .five .el{
    flex:1;min-width:88px;text-align:center;border:1px solid var(--line);
    border-radius:var(--radius);padding:16px 10px 14px;background:var(--bg2);
    transition:transform 0.2s,border-color 0.2s;position:relative;overflow:hidden;
  }
  .five .el::after{
    content:'';position:absolute;left:0;right:0;bottom:0;height:3px;opacity:0.55;
  }
  .five .el:has(.w-wood)::after{background:var(--wood)}
  .five .el:has(.w-fire)::after{background:var(--fire)}
  .five .el:has(.w-earth)::after{background:var(--earth)}
  .five .el:has(.w-metal)::after{background:var(--metal)}
  .five .el:has(.w-water)::after{background:var(--water)}
  .five .el:hover{transform:translateY(-2px)}
  .five .el .nm{font-size:13px;font-weight:700;font-family:var(--font-heading);letter-spacing:2px}
  .five .el .sc{font-size:24px;font-weight:800;margin-top:5px;font-variant-numeric:tabular-nums}
  .w-wood{color:var(--wood)} .w-fire{color:var(--fire)} .w-earth{color:var(--earth)}
  .w-metal{color:var(--metal)} .w-water{color:var(--water)}
  .five .el:has(.w-wood){border-color:rgba(99,192,140,0.22)}.five .el:has(.w-wood):hover{border-color:rgba(99,192,140,0.45)}
  .five .el:has(.w-fire){border-color:rgba(224,96,96,0.22)}.five .el:has(.w-fire):hover{border-color:rgba(224,96,96,0.45)}
  .five .el:has(.w-earth){border-color:rgba(214,169,78,0.22)}.five .el:has(.w-earth):hover{border-color:rgba(214,169,78,0.45)}
  .five .el:has(.w-metal){border-color:rgba(182,194,204,0.22)}.five .el:has(.w-metal):hover{border-color:rgba(182,194,204,0.45)}
  .five .el:has(.w-water){border-color:rgba(99,163,217,0.22)}.five .el:has(.w-water):hover{border-color:rgba(99,163,217,0.45)}
  /* ===== 综合解读 tab ===== */
  .report-tab{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
  .report-tab span{
    padding:6px 16px;border:1px solid var(--line);border-radius:20px;
    font-size:12.5px;cursor:pointer;color:var(--muted);transition:all 0.25s;letter-spacing:1px
  }
  .report-tab span:hover{border-color:var(--gold3);color:var(--gold)}
  .report-tab span.on{
    background:linear-gradient(135deg,var(--gold2),var(--gold) 50%,var(--gold3));
    color:#0a0a0f;border-color:var(--gold);font-weight:700;
    box-shadow:0 3px 12px rgba(201,163,95,0.25);
  }
  .rc{display:none}
  .rc.on{display:block;animation:fadeIn 0.35s ease}
  @keyframes fadeIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
  .rc p{
    font-size:13.5px;line-height:1.9;margin-bottom:10px;padding:9px 4px 9px 14px;
    border-left:2px solid rgba(201,163,95,0.25);
    border-bottom:1px dashed var(--line);color:var(--ink)
  }
  .rc p:last-child{border-bottom:none}
  .src{
    display:inline-block;font-size:10px;color:var(--gold2);
    border:1px solid var(--gold3);border-radius:4px;
    padding:1px 8px;margin-left:8px;vertical-align:middle;
    letter-spacing:0.5px;background:rgba(201,163,95,0.07);white-space:nowrap
  }
  .note{font-size:12px;color:var(--muted);text-align:center;margin-top:20px;line-height:2}
  /* ===== 流月表 ===== */
  .month-table{width:100%;border-collapse:collapse;font-size:13px;margin-top:8px}
  .month-table th{
    background:linear-gradient(180deg,#232334,#1a1a28);
    color:var(--gold2);font-weight:600;font-size:12px;padding:9px 5px;letter-spacing:1px;
    border-bottom:1px solid var(--gold3)
  }
  .month-table td{padding:9px 5px;border-bottom:1px solid var(--line);text-align:center}
  .month-table tr:hover td{background:rgba(201,163,95,0.035)}
  .month-table .mz{font-size:16px;font-weight:700;color:var(--ink2);font-family:var(--font-heading);letter-spacing:1px}
  .ml-good{color:var(--green)} .ml-warn{color:var(--red)} .ml-neu{color:var(--muted)}
  /* ===== 流日表 ===== */
  .ld-table td{padding:7px 4px}
  .ld-table .mz{font-size:15px}
  .ld-legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;margin-top:10px;padding:8px 10px;border:1px dashed var(--gold3);border-radius:6px}
  .ld-hot{color:var(--gold2);font-weight:600}
  .ld-he{color:var(--green);font-weight:600}
  .ld-hot-row td{background:rgba(201,163,95,0.06)}
  .ld-rule{color:var(--gold);opacity:.75}
  /* ===== 六亲详解 ===== */
  .qin-sec{border:1px solid var(--gold3);border-radius:10px;padding:12px 14px;margin-bottom:10px;background:rgba(201,163,95,0.03)}
  .qin-hd{font-size:14px;font-weight:700;color:var(--gold2);margin-bottom:6px;letter-spacing:.5px}
  .qin-meta{font-size:12px;color:var(--muted);line-height:1.7}
  .qin-star{font-size:12.5px;color:var(--ink2);margin-top:6px;line-height:1.7}
  .qin-note{font-size:12px;color:var(--muted);margin-top:5px;padding-left:8px;border-left:2px solid var(--gold3);line-height:1.6}
  /* ===== 图表 ===== */
  .chart-wrap{max-width:680px;margin:14px auto 0}
  .chart-wrap svg{width:100%;height:auto}
  .chart-legend{display:flex;gap:18px;flex-wrap:wrap;justify-content:center;margin-top:12px;font-size:13px}
  .chart-legend span{display:flex;align-items:center;gap:6px}
  .chart-legend i{display:inline-block;width:12px;height:12px;border-radius:3px}
  .chart-tabs{display:flex;gap:4px;margin-bottom:12px}
  .chart-tabs span{
    padding:5px 16px;border:1px solid var(--line);border-radius:16px;
    font-size:12px;cursor:pointer;color:var(--muted);transition:all 0.2s
  }
  .chart-tabs span:hover{border-color:var(--gold)}
  .chart-tabs span.on{background:var(--gold3);color:#0a0a0f;border-color:var(--gold3);font-weight:600}
  .chart-panel{display:none}
  .chart-panel.on{display:block;animation:fadeIn 0.3s ease}
  .chart-note{font-size:11px;color:var(--muted);text-align:center;margin-top:8px}
  /* ===== 结果头部 ===== */
  .result-head{text-align:center;margin-bottom:10px;padding:6px 0 12px;position:relative}
  .result-head::after{
    content:'';position:absolute;left:50%;bottom:0;transform:translateX(-50%);
    width:200px;height:1px;background:linear-gradient(90deg,transparent,rgba(201,163,95,0.45),transparent)
  }
  .result-head .name{font-size:22px;font-weight:700;font-family:var(--font-heading);color:var(--gold2);letter-spacing:3px}
  .result-head .meta{font-size:12.5px;color:var(--muted);letter-spacing:0.5px;margin-top:4px}
  .solar-note{
    font-size:12px;color:var(--muted);background:var(--bg2);
    border:1px dashed var(--line);border-radius:var(--radius2);padding:10px 14px;margin-top:12px
  }
  /* ===== 大运 ===== */
  .dayun{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
  .dayun .step{
    flex:1;min-width:88px;text-align:center;border:1px solid var(--line);
    border-radius:var(--radius);padding:13px 4px 11px;background:var(--bg2);
    transition:transform 0.2s,border-color 0.2s;position:relative
  }
  .dayun .step:hover{transform:translateY(-2px);border-color:var(--gold3)}
  .dayun .step .gz{font-size:18px;font-weight:700;color:var(--gold2);font-family:var(--font-heading);letter-spacing:1px}
  .dayun .step .age{font-size:12px;color:var(--muted);margin-top:5px}
  /* ===== 标签/徽章 ===== */
  .tag{
    display:inline-block;font-size:11px;padding:2px 10px;border-radius:12px;
    background:rgba(201,163,95,0.13);color:var(--gold2);margin-left:6px;
    font-weight:500;letter-spacing:0.5px;vertical-align:middle
  }
  .info-chips{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
  .chip{
    font-size:12.5px;padding:6px 14px;border-radius:20px;
    background:var(--bg2);border:1px solid var(--line);color:var(--ink);
    letter-spacing:0.5px;transition:border-color 0.2s
  }
  .chip:hover{border-color:var(--gold3)}
  .chip b{color:var(--gold2);font-weight:600}
  /* ===== 流年 ===== */
  .liu-box{margin-top:8px;font-size:14px}
  .liu-box .li{margin-bottom:12px;padding:11px 4px 11px 14px;border-left:2px solid rgba(201,163,95,0.22);
    border-bottom:1px dashed var(--line);color:var(--ink)}
  .liu-box .li:last-child{border-bottom:none}
  /* ===== 合婚 ===== */
  .he-dim{margin-bottom:14px}
  .he-dim .top{display:flex;justify-content:space-between;font-size:14px;margin-bottom:5px}
  .he-dim .bar{height:8px;background:var(--line);border-radius:6px;overflow:hidden}
  .he-dim .bar>i{display:block;height:100%;background:linear-gradient(90deg,var(--gold3),var(--gold2));
    border-radius:6px;transition:width 0.6s ease}
  .he-dim .desc{font-size:12px;color:var(--muted);margin-top:3px}
  .score-big{text-align:center;font-size:38px;font-weight:800;color:var(--gold2);margin:12px 0;font-family:var(--font-heading);letter-spacing:1px}
  .score-big small{font-size:13px;color:var(--muted)}
  .two-col{display:flex;gap:16px;flex-wrap:wrap}
  .two-col>div{flex:1;min-width:280px}
  /* ===== 神煞 ===== */
  .ssh-group{margin-top:10px}
  .ssh-group .gt{font-size:12.5px;font-weight:700;display:block;margin-bottom:8px;color:var(--muted);letter-spacing:1.5px}
  .ssh-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:4px}
  .ssh{
    font-size:13px;padding:10px 14px;border-radius:var(--radius2);
    border:1px solid var(--line);background:var(--bg2);
    display:flex;flex-direction:column;gap:3px;min-width:128px;transition:transform 0.2s;
    position:relative;overflow:hidden
  }
  .ssh::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--line3)}
  .ssh:hover{transform:translateY(-2px)}
  .ssh .nm{font-weight:700;font-size:14px;font-family:var(--font-heading);letter-spacing:1px}
  .ssh .pos{font-size:11px;color:var(--muted)}
  .ssh-j{border-color:rgba(82,176,131,0.3);background:rgba(82,176,131,0.06)}
  .ssh-j::before{background:var(--green)}
  .ssh-x{border-color:rgba(224,96,96,0.3);background:rgba(224,96,96,0.06)}
  .ssh-x::before{background:var(--red)}
  .ssh-z{border-color:rgba(201,163,95,0.22);background:rgba(201,163,95,0.04)}
  .ssh-z::before{background:var(--gold3)}
  .tp-j{color:var(--green);font-weight:700}
  .tp-x{color:var(--red);font-weight:700}
  .tp-z{color:var(--gold2);font-weight:700}
  /* ===== 五行补救 ===== */
  .remedy-grid{display:flex;gap:14px;flex-wrap:wrap;margin-top:6px}
  .remedy{
    flex:1;min-width:210px;border:1px solid var(--line);border-radius:var(--radius);
    padding:15px;background:var(--bg2);transition:transform 0.2s,border-color 0.2s
  }
  .remedy:hover{transform:translateY(-2px);border-color:var(--gold3)}
  .remedy .wm{font-size:16px;font-weight:800;margin-bottom:8px;display:flex;align-items:center;gap:8px;font-family:var(--font-heading);letter-spacing:2px}
  .remedy .sw{width:16px;height:16px;border-radius:4px;display:inline-block}
  .remedy dl{margin:0;font-size:13px}
  .remedy dt{color:var(--muted);font-weight:600;margin-top:9px;font-size:12px;letter-spacing:0.5px}
  .remedy dd{margin:2px 0 0;color:var(--ink)}
  .he-advice-box{
    background:linear-gradient(135deg,rgba(201,163,95,0.09),rgba(201,163,95,0.02));
    border:1px solid var(--gold3);border-radius:var(--radius);
    padding:16px 18px;margin-top:16px
  }
  .he-advice-box h4{
    font-family:var(--font-heading);font-size:15px;color:var(--gold2);
    letter-spacing:2px;margin-bottom:10px
  }
  .he-advice-box p{font-size:13px;color:var(--ink);margin-bottom:6px}
  ::-webkit-scrollbar{width:6px}
  ::-webkit-scrollbar-track{background:var(--bg)}
  ::-webkit-scrollbar-thumb{background:var(--line3);border-radius:3px}
  /* ===== 响应式 ===== */
  @media (max-width:640px){
    body{padding:20px 12px}
    h1{font-size:26px;letter-spacing:6px;text-indent:6px}
    .card{padding:20px}
    .form-card{max-width:100%}
    .rc p{font-size:13px}
    .dayun .step{min-width:78px}
    /* iOS Safari: select 字号 <16px 聚焦时自动放大页面，移动端统一 16px 防误触 */
    select{font-size:16px}
  }
</style>
</head>
<body>
<div class="wrap">
  <header class="brand">
    <div class="brand-rings"></div>
    <h1>八字命盘</h1>
    <div class="sub">子平推演<em>·</em>古籍溯源<em>·</em>排盘精确至节气时刻<em>·</em>论断附出处</div>
    <div class="rule"></div>
  </header>

  <div class="card form-card" id="formCard">
    <h2><span class="num">壹</span>填写出生信息</h2>
    <div class="row">
      <div><label>姓名</label><input id="name" placeholder="如：张三"></div>
      <div><label>性别</label>
        <select id="gender"><option value="">请选择</option><option value="男">男</option><option value="女">女</option></select>
      </div>
    </div>
    <div class="row">
      <div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin:14px 0 6px">
          <label id="dateLabel" style="margin:0">阳历生日</label>
          <div class="cal-toggle" id="calToggle">
            <button class="active" data-cal="solar" onclick="switchCal('solar')">阳历</button>
            <button data-cal="lunar" onclick="switchCal('lunar')">农历</button>
          </div>
        </div>
        <div class="date-group">
          <select id="year"><option value="">年份</option></select>
          <select id="month"><option value="">月份</option></select>
          <select id="day"><option value="">日期</option></select>
        </div>
      </div>
      <div>
        <label>出生时间</label>
        <div class="time-group">
          <select id="timeMode" onchange="toggleTimeMode()">
            <option value="exact">精确时间</option>
            <option value="shichen">只知时辰</option>
          </select>
          <select id="hour" class="hidden"><option value="">时</option></select>
          <select id="minute" class="hidden"><option value="0">00分</option></select>
          <select id="shichen" class="hidden">
            <option value="">选时辰</option>
            <option value="子">子时（23:00-01:00）</option>
            <option value="丑">丑时（01:00-03:00）</option>
            <option value="寅">寅时（03:00-05:00）</option>
            <option value="卯">卯时（05:00-07:00）</option>
            <option value="辰">辰时（07:00-09:00）</option>
            <option value="巳">巳时（09:00-11:00）</option>
            <option value="午">午时（11:00-13:00）</option>
            <option value="未">未时（13:00-15:00）</option>
            <option value="申">申时（15:00-17:00）</option>
            <option value="酉">酉时（17:00-19:00）</option>
            <option value="戌">戌时（19:00-21:00）</option>
            <option value="亥">亥时（21:00-23:00）</option>
          </select>
        </div>
        <div id="timeHint" class="time-hint"></div>
      </div>
    </div>
    <div class="row">
      <div><label>出生城市（用于真太阳时校正）</label><input id="birthplace" placeholder="如：广东省广州市（县级市请填到县）"></div>
      <div><label>是否校正真太阳时</label>
        <select id="truesun"><option value="yes">是（按经度校正，推荐）</option><option value="no">否（用北京时间）</option></select>
      </div>
    </div>
    <button onclick="generate()">排盘并分析 →</button>
  </div>

  <div id="result" class="hidden">
    <div class="card">
      <div class="result-head">
        <div class="name" id="rName"></div>
        <div class="meta" id="rMeta"></div>
      </div>
      <h2><span class="num">贰</span>四柱命盘</h2>
      <table id="pillarTable"></table>
      <div id="threeHouse"></div>
      <div style="margin-top:12px;font-size:13px;color:var(--muted)">
        日主（代表你自己）：<span id="rDay" class="pillar"></span>
        <span id="rStrength" style="margin-left:10px"></span>
      </div>
      <div class="info-chips" id="rChips"></div>
      <div class="solar-note" id="rSolar"></div>
    </div>

    <div class="card">
      <h2><span class="num">叁</span>五行分布（藏干加权）</h2>
      <div class="five" id="fiveBox"></div>
      <div style="margin-top:8px;font-size:12px;color:var(--muted)">注：五行分数为藏干加权统计（天干计1.0；地支本气1.0/中气0.5/余气0.25；月令×1.5），据以判定身强身弱，仅供参考。</div>
      <div class="chart-wrap">
        <div class="chart-tabs">
          <span class="on" onclick="switchChart('wxbar')">五行力量</span>
          <span onclick="switchChart('balance')">身强身弱</span>
          <span onclick="switchChart('dayunTrend')">大运趋势</span>
        </div>
        <div class="chart-panel on" id="chart-wxbar"></div>
        <div class="chart-panel" id="chart-balance"></div>
        <div class="chart-panel" id="chart-dayunTrend"></div>
        <div class="chart-note">点击上图切换视图。大运趋势基于各步大运干支对命局五行的增损估算，仅供参考。</div>
      </div>
    </div>

    <div class="card">
      <h2><span class="num">肆</span>神煞（吉凶星曜）</h2>
      <div id="sshBox"></div>
      <div style="margin-top:10px;font-size:12px;color:var(--muted)">注：神煞为辅助参考，须先论格局旺衰与用神，再参看神煞；吉神被冲减力、凶神被冲亦减力。仅列命局中实际出现的神煞。</div>
    </div>

    <div class="card">
      <h2><span class="num">伍</span>五行补救建议</h2>
      <div id="remedyBox"></div>
    </div>

    <div class="card">
      <h2><span class="num">附</span>调候用神 &amp; 病药论</h2>
      <div id="tiaohouBox"></div>
    </div>

    <div class="card">
      <h2><span class="num">陆</span>综合解读</h2>
      <div class="report-tab" id="tabs">
        <span class="on" data-t="char">性格</span>
        <span data-t="career">事业</span>
        <span data-t="wealth">财运</span>
        <span data-t="marriage">婚姻</span>
        <span data-t="health">健康</span>
        <span data-t="pattern">格局</span>
        <span data-t="yongshen">用神</span>
        <span data-t="combo">十神</span>
        <span data-t="qinqin">六亲</span>
        <span data-t="edu">学业</span>
        <span data-t="wuxing">五行</span>
        <span data-t="dayun">大运</span>
      </div>
      <div class="rc on" id="rc-char"></div>
      <div class="rc" id="rc-career"></div>
      <div class="rc" id="rc-wealth"></div>
      <div class="rc" id="rc-marriage"></div>
      <div class="rc" id="rc-health"></div>
      <div class="rc" id="rc-pattern"></div>
      <div class="rc" id="rc-yongshen"></div>
      <div class="rc" id="rc-combo"></div>
      <div class="rc" id="rc-qinqin"></div>
      <div class="rc" id="rc-edu"></div>
      <div class="rc" id="rc-wuxing"></div>
      <div class="rc" id="rc-dayun"></div>
    </div>

    <div class="card">
      <h2><span class="num">柒</span>流年分析</h2>
      <div class="row">
        <div><label>流年（公历年份）</label><input id="liuYear" type="number" value="2026"></div>
        <div><label>对应大运</label><select id="liuDayun"></select></div>
      </div>
      <button class="ghost" id="btnLiu" onclick="runLiu()">分析该流年 →</button>
      <div class="liu-box" id="liuResult"></div>
    </div>

    <div class="card" id="liuMonthCard">
      <h2><span class="num">捌</span>流月分析</h2>
      <div class="row">
        <div><label>目标年份</label><input id="liuMonthYear" type="number" value="2026"></div>
        <div style="display:flex;align-items:flex-end;flex-wrap:wrap"><button class="ghost" id="btnLiuYue" onclick="runLiuYue()" style="margin-top:0;white-space:normal;max-width:100%">展开十二流月 →</button></div>
      </div>
      <div id="liuMonthResult"></div>
    </div>

    <div class="card" id="liuDayCard">
      <h2><span class="num">玖⁺</span>流日分析（单月逐日）</h2>
      <div class="row">
        <div><label>目标年份</label><input id="liuDayYear" type="number" value="2026"></div>
        <div><label>目标月份</label><select id="liuDayMonth">
          <option value="1">1 月</option><option value="2">2 月</option><option value="3">3 月</option>
          <option value="4">4 月</option><option value="5">5 月</option><option value="6">6 月</option>
          <option value="7">7 月</option><option value="8">8 月</option><option value="9">9 月</option>
          <option value="10">10 月</option><option value="11">11 月</option><option value="12">12 月</option>
        </select></div>
        <div style="display:flex;align-items:flex-end;flex-wrap:wrap"><button class="ghost" id="btnLiuDay" onclick="runLiuDay()" style="margin-top:0;white-space:normal;max-width:100%">展开逐日运势 →</button></div>
      </div>
      <div id="liuDayResult"></div>
    </div>

    <div class="card" id="liuQinCard">
      <h2><span class="num">拾</span>六亲详解</h2>
      <div style="color:var(--muted);font-size:12px;margin-top:2px">父母 · 配偶 · 子女 · 兄弟 —— 以宫位为体、十神为用，参合喜忌旺衰与神煞</div>
      <div style="margin-top:10px;max-width:100%"><button class="ghost" id="btnLiuQin" onclick="runLiuQin()" style="margin-top:0;white-space:normal;max-width:100%">展开六亲详解 →</button></div>
      <div id="liuQinResult"></div>
    </div>

    <div class="note">
      命理分析仅供传统文化学习与自我探索参考，不构成任何决策依据。<br>
      涉及健康、财务、婚姻等重大事项，请以专业机构意见为准。<br>
      命理是地图，走路的是你自己。
    </div>
    <button class="ghost" onclick="backToForm()" style="margin:14px auto 0;display:block">← 返回重新排盘</button>
  </div>

  <div class="card" id="heCard">
    <h2><span class="num">玖</span>八字合婚（双盘对比）</h2>
    <div class="two-col">
      <div>
        <h3 style="font-size:14px;color:var(--gold);margin:6px 0">甲方</h3>
        <div class="row">
          <div><label>姓名</label><input id="hNameA" placeholder="甲方"></div>
          <div><label>性别</label><select id="hSexA"><option value="">请选择</option><option value="男">男</option><option value="女">女</option></select></div>
        </div>
        <div class="row">
          <div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin:14px 0 6px">
              <label id="hDateLabelA" style="margin:0">阳历生日</label>
              <div class="cal-toggle" id="hCalToggleA">
                <button class="active" data-cal="solar" onclick="switchHeCal('A','solar')">阳历</button>
                <button data-cal="lunar" onclick="switchHeCal('A','lunar')">农历</button>
              </div>
            </div>
            <div class="date-group">
              <select id="hYearA"><option value="">年份</option></select>
              <select id="hMonthA"><option value="">月份</option></select>
              <select id="hDayA"><option value="">日期</option></select>
            </div>
          </div>
          <div>
            <label>出生时间</label>
            <div class="time-group">
              <select id="hTimeModeA" onchange="toggleHeTimeMode('A')">
                <option value="exact">精确时间</option>
                <option value="shichen">只知时辰</option>
              </select>
              <select id="hHourA" class="hidden"><option value="">时</option></select>
              <select id="hMinuteA" class="hidden"><option value="0">00分</option></select>
              <select id="hShichenA" class="hidden">
                <option value="">选时辰</option>
                <option value="子">子时（23:00-01:00）</option>
                <option value="丑">丑时（01:00-03:00）</option>
                <option value="寅">寅时（03:00-05:00）</option>
                <option value="卯">卯时（05:00-07:00）</option>
                <option value="辰">辰时（07:00-09:00）</option>
                <option value="巳">巳时（09:00-11:00）</option>
                <option value="午">午时（11:00-13:00）</option>
                <option value="未">未时（13:00-15:00）</option>
                <option value="申">申时（15:00-17:00）</option>
                <option value="酉">酉时（17:00-19:00）</option>
                <option value="戌">戌时（19:00-21:00）</option>
                <option value="亥">亥时（21:00-23:00）</option>
              </select>
            </div>
          </div>
        </div>
        <div><label>出生城市</label><input id="hPlaceA" placeholder="如：广东省广州市（县级市请填到县）"></div>
      </div>
      <div>
        <h3 style="font-size:14px;color:var(--gold);margin:6px 0">乙方</h3>
        <div class="row">
          <div><label>姓名</label><input id="hNameB" placeholder="乙方"></div>
          <div><label>性别</label><select id="hSexB"><option value="">请选择</option><option value="女">女</option><option value="男">男</option></select></div>
        </div>
        <div class="row">
          <div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin:14px 0 6px">
              <label id="hDateLabelB" style="margin:0">阳历生日</label>
              <div class="cal-toggle" id="hCalToggleB">
                <button class="active" data-cal="solar" onclick="switchHeCal('B','solar')">阳历</button>
                <button data-cal="lunar" onclick="switchHeCal('B','lunar')">农历</button>
              </div>
            </div>
            <div class="date-group">
              <select id="hYearB"><option value="">年份</option></select>
              <select id="hMonthB"><option value="">月份</option></select>
              <select id="hDayB"><option value="">日期</option></select>
            </div>
          </div>
          <div>
            <label>出生时间</label>
            <div class="time-group">
              <select id="hTimeModeB" onchange="toggleHeTimeMode('B')">
                <option value="exact">精确时间</option>
                <option value="shichen">只知时辰</option>
              </select>
              <select id="hHourB" class="hidden"><option value="">时</option></select>
              <select id="hMinuteB" class="hidden"><option value="0">00分</option></select>
              <select id="hShichenB" class="hidden">
                <option value="">选时辰</option>
                <option value="子">子时（23:00-01:00）</option>
                <option value="丑">丑时（01:00-03:00）</option>
                <option value="寅">寅时（03:00-05:00）</option>
                <option value="卯">卯时（05:00-07:00）</option>
                <option value="辰">辰时（07:00-09:00）</option>
                <option value="巳">巳时（09:00-11:00）</option>
                <option value="午">午时（11:00-13:00）</option>
                <option value="未">未时（13:00-15:00）</option>
                <option value="申">申时（15:00-17:00）</option>
                <option value="酉">酉时（17:00-19:00）</option>
                <option value="戌">戌时（19:00-21:00）</option>
                <option value="亥">亥时（21:00-23:00）</option>
              </select>
            </div>
          </div>
        </div>
        <div><label>出生城市</label><input id="hPlaceB" placeholder="如：广东省广州市（县级市请填到县）"></div>
      </div>
    </div>
    <button onclick="runHe()">开始合婚 →</button>
    <div id="heResult" style="margin-top:10px"></div>
  </div>
</div>

<script>
// [ENGINE:BEGIN]
const JIEQI = __JIEQI__;
const RULES = __RULES__;

// ===== 基础数据 =====
const GAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸'];
const ZHI = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥'];
const GAN_WX = {甲:'木',乙:'木',丙:'火',丁:'火',戊:'土',己:'土',庚:'金',辛:'金',壬:'水',癸:'水'};
const ZHI_WX = {子:'水',丑:'土',寅:'木',卯:'木',辰:'土',巳:'火',午:'火',未:'土',申:'金',酉:'金',戌:'土',亥:'水'};
const WUHU = {甲:'丙',己:'丙',乙:'戊',庚:'戊',丙:'庚',辛:'庚',丁:'壬',壬:'壬',戊:'甲',癸:'甲'};
const WUSHU = {甲:'甲',己:'甲',乙:'丙',庚:'丙',丙:'戊',辛:'戊',丁:'庚',壬:'庚',戊:'壬',癸:'壬'};
const JIE_ZHI = {'立春':2,'惊蛰':3,'清明':4,'立夏':5,'芒种':6,'小暑':7,'立秋':8,'白露':9,'寒露':10,'立冬':11,'大雪':0,'小寒':1};
const JIE_ORDER = JIEQI.order;
const WX_NAMES = ['木','火','土','金','水'];
const SHENG = {木:0,火:1,土:2,金:3,水:4};
// 藏干表：本气1.0 / 中气0.5 / 余气0.25
const CANG = {
  '子':[['癸',1.0]], '丑':[['己',1.0],['癸',0.5],['辛',0.25]],
  '寅':[['甲',1.0],['丙',0.5],['戊',0.25]], '卯':[['乙',1.0]],
  '辰':[['戊',1.0],['乙',0.5],['癸',0.25]], '巳':[['丙',1.0],['庚',0.5],['戊',0.25]],
  '午':[['丁',1.0],['己',0.5]], '未':[['己',1.0],['丁',0.5],['乙',0.25]],
  '申':[['庚',1.0],['壬',0.5],['戊',0.25]], '酉':[['辛',1.0]],
  '戌':[['戊',1.0],['辛',0.5],['丁',0.25]], '亥':[['壬',1.0],['甲',0.5]]
};
const SHENGX = ['鼠','牛','虎','兔','龙','蛇','马','羊','猴','鸡','狗','猪'];
// 地支关系
const CHONG = {子:'午',午:'子',丑:'未',未:'丑',寅:'申',申:'寅',卯:'酉',酉:'卯',辰:'戌',戌:'辰',巳:'亥',亥:'巳'};
const LIUHE = [['子','丑'],['寅','亥'],['卯','戌'],['辰','酉'],['巳','申'],['午','未']];
const SANHE = [['申','子','辰'],['亥','卯','未'],['寅','午','戌'],['巳','酉','丑']];
const XING_PAIRS = [['寅','巳'],['巳','申'],['申','寅'],['丑','戌'],['戌','未'],['未','丑'],['子','卯'],['卯','子']];
const HAI_PAIRS = [['子','未'],['未','子'],['丑','午'],['午','丑'],['寅','巳'],['巳','寅'],['卯','辰'],['辰','卯'],['申','亥'],['亥','申'],['酉','戌'],['戌','酉']];
const WU_HE = {甲:'己',己:'甲',乙:'庚',庚:'乙',丙:'辛',辛:'丙',丁:'壬',壬:'丁',戊:'癸',癸:'戊'};
// 天干相冲（用于反吟/天克地冲判定）
// 天干相冲（传统只有四组：甲庚/乙辛/丙壬/丁癸，戊己同为土不冲）
const WU_CHONG = {甲:'庚',庚:'甲',乙:'辛',辛:'乙',丙:'壬',壬:'丙',丁:'癸',癸:'丁'};
// 纳音（六十甲子）
const NAYIN = {'甲子':'海中金','乙丑':'海中金','丙寅':'炉中火','丁卯':'炉中火','戊辰':'大林木','己巳':'大林木','庚午':'路旁土','辛未':'路旁土','壬申':'剑锋金','癸酉':'剑锋金','甲戌':'山头火','乙亥':'山头火','丙子':'涧下水','丁丑':'涧下水','戊寅':'城头土','己卯':'城头土','庚辰':'白蜡金','辛巳':'白蜡金','壬午':'杨柳木','癸未':'杨柳木','甲申':'泉中水','乙酉':'泉中水','丙戌':'屋上土','丁亥':'屋上土','戊子':'霹雳火','己丑':'霹雳火','庚寅':'松柏木','辛卯':'松柏木','壬辰':'长流水','癸巳':'长流水','甲午':'沙中金','乙未':'沙中金','丙申':'山下火','丁酉':'山下火','戊戌':'平地木','己亥':'平地木','庚子':'壁上土','辛丑':'壁上土','壬寅':'金箔金','癸卯':'金箔金','甲辰':'覆灯火','乙巳':'覆灯火','丙午':'天河水','丁未':'天河水','戊申':'大驿土','己酉':'大驿土','庚戌':'钗钏金','辛亥':'钗钏金','壬子':'桑柘木','癸丑':'桑柘木','甲寅':'大溪水','乙卯':'大溪水','丙辰':'沙中土','丁巳':'沙中土','戊午':'天上火','己未':'天上火','庚申':'石榴木','辛酉':'石榴木','壬戌':'大海水','癸亥':'大海水'};
const NAYIN_WX = {}; for(const k in NAYIN){ NAYIN_WX[k]=NAYIN[k].slice(-1); }
// 六十甲子顺序数组（索引与 NAYIN 的 key 一致：GAN[i%10]+ZHI[i%12]）
const G60 = []; for(let i=0;i<60;i++) G60.push(GAN[i%10]+ZHI[i%12]);
// 十二长生名称（阳干顺行、阴干逆行）
const CS_NAME = ['长生','沐浴','冠带','临官','帝旺','衰','病','死','墓','绝','胎','养'];
// 各天干长生地支位（阳干顺排、阴干逆排）
const CS_BASE = {甲:'亥',乙:'午',丙:'寅',丁:'酉',戊:'寅',己:'酉',庚:'巳',辛:'子',壬:'申',癸:'卯'};
// 空亡（旬空）：基于日柱干支在六十甲子中的旬，返回空亡的两个地支
function calcKongWang(dayPillar){
  const idx=G60.indexOf(dayPillar); if(idx<0) return null;
  const xun=Math.floor(idx/10)*10;
  return [ZHI[(xun+10)%12], ZHI[(xun+11)%12]];
}
// 十二长生：日干在某地支的十二长生状态
function calcChangSheng(dayGan, zhi){
  const base=CS_BASE[dayGan]; if(!base) return null;
  const baseI=ZHI.indexOf(base), ziI=ZHI.indexOf(zhi);
  const off=yang(dayGan) ? ((ziI-baseI+12)%12) : ((baseI-ziI+12)%12);
  return CS_NAME[off];
}
// 主要城市经度（东经）
const CITY_LON = {北京:116.4,上海:121.5,广州:113.3,深圳:114.1,成都:104.1,重庆:106.5,哈尔滨:126.6,
  乌鲁木齐:87.6,杭州:120.2,南京:118.8,武汉:114.3,西安:108.9,天津:117.2,沈阳:123.4,长春:125.3,
  济南:117.0,郑州:113.6,长沙:112.9,福州:119.3,南昌:115.9,昆明:102.7,贵阳:106.7,南宁:108.3,
  海口:110.3,兰州:103.8,西宁:101.8,银川:106.3,呼和浩特:111.7,拉萨:91.1,太原:112.5,石家庄:114.5,
  青岛:120.4,大连:121.6,厦门:118.1,宁波:121.5,无锡:120.3,苏州:120.6,东莞:113.8,佛山:113.1,
  珠海:113.5,温州:120.7,烟台:119.0,常州:119.9,南通:120.9,徐州:117.2,合肥:117.3,香港:114.2,
  澳门:113.5,台北:121.5,绍兴:120.6,嘉兴:120.8,金华:119.6,台州:121.4,泉州:118.6,漳州:117.6,
  洛阳:112.4,开封:114.3,唐山:118.2,保定:115.5,潍坊:119.2,临沂:118.3,淄博:118.1,威海:122.1,
  汕头:116.7,湛江:110.4,中山:113.4,惠州:114.4,江门:113.1,三亚:109.5,桂林:110.3,柳州:109.4};
const PATTERN_NAME = {'比肩':'建禄格','劫财':'月劫格','食神':'食神格','伤官':'伤官格','正财':'正财格','偏财':'偏财格','正官':'正官格','七杀':'七杀格','正印':'正印格','偏印':'偏印格'};

// ===== 五行补救数据（来源：knowledge-base/02-规则手册/五行补救方案.md）=====
const REMEDY = {
  '木':{color:'绿色、青色、翠色', dir:'东、东南', num:'3、8', industry:'教育、医疗、环保、出版、设计、文化、中医药、农业、园艺', jewelry:'绿松石、翡翠、绿水晶、木制饰品', diet:'绿色蔬果、绿茶、绿豆、青菜', basis:'木主仁，其性直，其情和；补木可增仁慈与创造力。'},
  '火':{color:'红色、橙色、紫色、粉色', dir:'南', num:'2、7', industry:'能源、电子、餐饮、娱乐、美容、互联网前端、演艺、市场、销售', jewelry:'红玛瑙、石榴石、红纹石、红水晶', diet:'红枣、红豆、番茄、辣椒、草莓、红酒', basis:'火主礼，其性急，其情恭；补火可增感染力与行动力。'},
  '土':{color:'黄色、棕色、咖啡色、米色', dir:'中、西南、东北', num:'5、10', industry:'地产、建筑、农业、土木工程、仓储、矿产、酒店、保险、信托', jewelry:'黄水晶、蜜蜡、琥珀、陶瓷、黄玉', diet:'小米、玉米、土豆、南瓜、山药、红薯', basis:'土主信，其性重，其情厚；补土可增稳定感与诚信度。'},
  '金':{color:'白色、金色、银色', dir:'西、西北', num:'4、9', industry:'金融、银行、会计、五金、机械、法律、军警、精密制造、珠宝', jewelry:'金银首饰、金属手表、白水晶', diet:'白萝卜、百合、银耳、梨、牛奶、白肉', basis:'金主义，其性刚，其情烈；补金可增决断力与原则性。'},
  '水':{color:'黑色、蓝色、深灰色', dir:'北', num:'1、6', industry:'IT互联网、物流、旅游、渔业、传媒、出版、咨询、教育、哲学', jewelry:'黑曜石、黑水晶、海蓝宝、珍珠', diet:'黑豆、黑芝麻、黑木耳、海带、紫菜', basis:'水主智，其性聪，其情善；补水可增智慧与适应力。'}
};

// ===== 神煞查法表（来源：knowledge-base/01-基础表/神煞速查表.md）=====
// 天乙贵人（年干/日干）
const TIANYI = {甲:['丑','未'],戊:['丑','未'],庚:['丑','未'],乙:['子','申'],己:['子','申'],丙:['亥','酉'],丁:['亥','酉'],壬:['巳','卯'],癸:['巳','卯'],辛:['午','寅']};
// 文昌（年干/日干）
const WENCHANG = {甲:'巳',乙:'午',丙:'申',丁:'酉',戊:'申',己:'酉',庚:'亥',辛:'子',壬:'寅',癸:'卯'};
// 禄神（日干，临官位）
const LUSHEN = {甲:'寅',乙:'卯',丙:'巳',丁:'午',戊:'巳',己:'午',庚:'申',辛:'酉',壬:'亥',癸:'子'};
// 学堂（日干，长生位）
const XUETANG = {甲:'亥',乙:'午',丙:'寅',丁:'酉',戊:'寅',己:'酉',庚:'巳',辛:'子',壬:'申',癸:'卯'};
// 金舆（日干）
const JINYU = {甲:'辰',乙:'巳',丙:'未',丁:'申',戊:'未',己:'申',庚:'戌',辛:'亥',壬:'丑',癸:'寅'};
// 驿马（年支/日支，三合局长生对冲）
const YIMA = {申:'寅',子:'寅',辰:'寅',亥:'巳',卯:'巳',未:'巳',寅:'申',午:'申',戌:'申',巳:'亥',酉:'亥',丑:'亥'};
// 桃花/咸池（年支/日支，三合局沐浴位）
const TAOHUA = {申:'酉',子:'酉',辰:'酉',亥:'子',卯:'子',未:'子',寅:'卯',午:'卯',戌:'卯',巳:'午',酉:'午',丑:'午'};
// 华盖（年支/日支，三合局墓库位）
const HUAGAI = {申:'辰',子:'辰',辰:'辰',亥:'未',卯:'未',未:'未',寅:'戌',午:'戌',戌:'戌',巳:'丑',酉:'丑',丑:'丑'};
// 红鸾（年支）
const HONGLUAN = {子:'卯',丑:'寅',寅:'丑',卯:'子',辰:'亥',巳:'戌',午:'酉',未:'申',申:'未',酉:'午',戌:'巳',亥:'辰'};
// 将星（年支/日支，三合局帝旺位）
const JIANGXING = {申:'子',子:'子',辰:'子',亥:'卯',卯:'卯',未:'卯',寅:'午',午:'午',戌:'午',巳:'酉',酉:'酉',丑:'酉'};
// 天德（月支，干支混合）
const TIANDE = {寅:'丁',卯:'申',辰:'壬',巳:'辛',午:'亥',未:'甲',申:'癸',酉:'寅',戌:'丙',亥:'乙',子:'巳',丑:'庚'};
// 月德（月支）
const YUEDE = {寅:'丙',午:'丙',戌:'丙',申:'壬',子:'壬',辰:'壬',亥:'甲',卯:'甲',未:'甲',巳:'庚',酉:'庚',丑:'庚'};
// 龙德（月支）
const LONGDE = {寅:'未',卯:'申',辰:'酉',巳:'戌',午:'亥',未:'子',申:'丑',酉:'寅',戌:'卯',亥:'辰',子:'巳',丑:'午'};
// 羊刃（日干，帝旺位）
const YANGBLADE = {甲:'卯',乙:'寅',丙:'午',丁:'巳',戊:'午',己:'巳',庚:'酉',辛:'申',壬:'子',癸:'亥'};
// 劫煞（年支/日支，三合局绝地）
const JIESHA = {申:'巳',子:'巳',辰:'巳',亥:'申',卯:'申',未:'申',寅:'亥',午:'亥',戌:'亥',巳:'寅',酉:'寅',丑:'寅'};
// 亡神（年支/日支）
const WANGSHEN = {申:'亥',子:'亥',辰:'亥',亥:'寅',卯:'寅',未:'寅',寅:'巳',午:'巳',戌:'巳',巳:'申',酉:'申',丑:'申'};
// 灾煞（年支/日支，三合局冲位）
const ZAISHA = {申:'午',子:'午',辰:'午',亥:'酉',卯:'酉',未:'酉',寅:'子',午:'子',戌:'子',巳:'卯',酉:'卯',丑:'卯'};
// 孤辰（年支，三会局前一辰）
const GUCHEN = {亥:'寅',子:'寅',丑:'寅',寅:'巳',卯:'巳',辰:'巳',巳:'申',午:'申',未:'申',申:'亥',酉:'亥',戌:'亥'};
// 寡宿（年支，三会局后一辰）
const GUASU = {亥:'戌',子:'戌',丑:'戌',寅:'丑',卯:'丑',辰:'丑',巳:'辰',午:'辰',未:'辰',申:'未',酉:'未',戌:'未'};
// 岁破（年支，六冲位）
const SUIPO = {子:'午',丑:'未',寅:'申',卯:'酉',辰:'戌',巳:'亥',午:'子',未:'丑',申:'寅',酉:'卯',戌:'辰',亥:'巳'};
// 血刃（月支）
const XUEREN = {寅:'丑',卯:'未',辰:'寅',巳:'申',午:'卯',未:'酉',申:'辰',酉:'戌',戌:'巳',亥:'亥',子:'午',丑:'子'};
// 流霞（日干）
const LIUXIA = {甲:'酉',乙:'戌',丙:'未',丁:'申',戊:'巳',己:'午',庚:'辰',辛:'卯',壬:'亥',癸:'寅'};

// 神煞配置：name 名称 / type 吉凶中 / meaning 释义 / get(pillars[,gender])→目标token数组
// token: {kind:'z',v} 地支匹配, {kind:'g',v} 天干匹配, {kind:'e',v} 干支皆可
function z(v){return {kind:'z',v};}
function gv(v){return {kind:'g',v};}
function ge(v){return {kind:'e',v};}
const SHENSHA = [
  {name:'天乙贵人',type:'吉',meaning:'逢凶化吉，贵人提携',get:p=>[z(TIANYI[p[0][0]][0]),z(TIANYI[p[0][0]][1]),z(TIANYI[p[2][0]][0]),z(TIANYI[p[2][0]][1])]},
  {name:'文昌',type:'吉',meaning:'聪明好学，文才出众',get:p=>[z(WENCHANG[p[0][0]]),z(WENCHANG[p[2][0]])]},
  {name:'禄神',type:'吉',meaning:'福禄根基，衣禄丰足',get:p=>[z(LUSHEN[p[2][0]])]},
  {name:'学堂',type:'吉',meaning:'学业有成，悟性高',get:p=>[z(XUETANG[p[2][0]])]},
  {name:'金舆',type:'吉',meaning:'财帛车马，安逸富贵',get:p=>[z(JINYU[p[2][0]])]},
  {name:'天德',type:'吉',meaning:'上天之德，解厄消灾',get:p=>[ge(TIANDE[p[1][1]])]},
  {name:'月德',type:'吉',meaning:'月令之德，化凶为吉',get:p=>[ge(YUEDE[p[1][1]])]},
  {name:'龙德',type:'吉',meaning:'贵人提携，转危为安',get:p=>[z(LONGDE[p[1][1]])]},
  {name:'将星',type:'吉',meaning:'领导才能，主掌权柄',get:p=>[z(JIANGXING[p[0][1]]),z(JIANGXING[p[2][1]])]},
  {name:'红鸾',type:'吉',meaning:'姻缘喜庆，桃花正缘',get:p=>[z(HONGLUAN[p[0][1]])]},
  {name:'华盖',type:'中',meaning:'艺术宗教，孤独清高',get:p=>[z(HUAGAI[p[0][1]]),z(HUAGAI[p[2][1]])]},
  {name:'驿马',type:'中',meaning:'走动迁移，变动奔波',get:p=>[z(YIMA[p[0][1]]),z(YIMA[p[2][1]])]},
  {name:'桃花',type:'中',meaning:'异性才艺，情感酒色',get:p=>[z(TAOHUA[p[0][1]]),z(TAOHUA[p[2][1]])]},
  {name:'羊刃',type:'凶',meaning:'刚烈争斗，防血光争执',get:p=>[z(YANGBLADE[p[2][0]])]},
  {name:'劫煞',type:'凶',meaning:'破财灾祸，谋事多阻',get:p=>[z(JIESHA[p[0][1]]),z(JIESHA[p[2][1]])]},
  {name:'亡神',type:'凶',meaning:'心神不安，官非纠缠',get:p=>[z(WANGSHEN[p[0][1]]),z(WANGSHEN[p[2][1]])]},
  {name:'灾煞',type:'凶',meaning:'意外灾祸，防突发',get:p=>[z(ZAISHA[p[0][1]]),z(ZAISHA[p[2][1]])]},
  {name:'孤辰',type:'凶',meaning:'孤独六亲，缘份较薄',get:p=>[z(GUCHEN[p[0][1]])]},
  {name:'寡宿',type:'凶',meaning:'孤寡之象，婚姻需经营',get:p=>[z(GUASU[p[0][1]])]},
  {name:'岁破',type:'凶',meaning:'破财变动，宜守不宜攻',get:p=>[z(SUIPO[p[0][1]])]},
  {name:'血刃',type:'凶',meaning:'血光之灾，注意安全',get:p=>[z(XUEREN[p[1][1]])]},
  {name:'流霞',type:'凶',meaning:'意外流血，防患未然',get:p=>[z(LIUXIA[p[2][0]])]},
  {name:'勾绞',type:'凶',meaning:'口舌是非，纠缠不清',get:p=>{const i=ZHI.indexOf(p[0][1]);const yang=(i%2===0);return [z(ZHI[(yang?i-1:i+1+12)%12]),z(ZHI[(yang?i+2:i-2+12)%12])];}},
  {name:'天罗地网',type:'凶',meaning:'困顿不顺（男忌天罗戌亥／女忌地网辰巳）',needGender:true,get:(p,gd)=>{return gd==='男'?[z('戌'),z('亥')]:[z('辰'),z('巳')];}}
];

// 神煞出现位置：扫描四柱，返回宫位名（年/月/日/时柱）
function posOfToken(pillars,token){
  const names=['年柱','月柱','日柱','时柱'];
  for(let i=0;i<4;i++){
    if((token.kind==='z'||token.kind==='e') && pillars[i][1]===token.v) return names[i];
    if((token.kind==='g'||token.kind==='e') && pillars[i][0]===token.v) return names[i];
  }
  return null;
}
// 计算命局实际出现的神煞
function calcShenSha(pillars, gender){
  const out=[];
  SHENSHA.forEach(s=>{
    const toks = s.needGender ? s.get(pillars, gender) : s.get(pillars);
    const pos=new Set();
    toks.forEach(t=>{ const p=posOfToken(pillars,t); if(p) pos.add(p); });
    if(pos.size) out.push({name:s.name, type:s.type, meaning:s.meaning, pos:[...pos].join('、')});
  });
  return out;
}
// 五行补救方案（基于喜用神 + 调候法）
function getRemedy(strength, five, avgFive, xiYong, monthZhi){
  let items=[], note='';
  // 调候法：根据月令季节补充
  const tiaoHouWx={};
  if(['亥','子','丑'].includes(monthZhi)) tiaoHouWx['火']=true;       // 冬补火
  else if(['巳','午','未'].includes(monthZhi)) tiaoHouWx['水']=true;    // 夏补水
  else if(['申','酉','戌'].includes(monthZhi)) tiaoHouWx['木']=true;     // 秋补木（含戌燥土月）
  else if(['寅','卯','辰'].includes(monthZhi)) tiaoHouWx['金']=true;     // 春补金（含辰湿土月）
  if(strength!=='中和'){
    xiYong.forEach(w=>{ if(REMEDY[w]) items.push(Object.assign({wx:w}, REMEDY[w])); });
    note='以喜用神为准（非"缺什么补什么"）：命局偏弱喜 '+xiYong.join('、')+'，可对应加强；';
    // 调候提示：若喜用神中未含调候五行，作为补充说明
    const thKeys=Object.keys(tiaoHouWx);
    const needTH=thKeys.filter(w=>tiaoHouWx[w]&&!xiYong.includes(w));
    if(needTH.length) note+='调候建议补充：'+needTH.join('、')+'（季节所需，可做辅助）。';
    else note+='行业选择仍须结合个人能力与市场需求。';
  } else {
    const weak=WX_NAMES.filter(w=>five[w]<avgFive*0.9).sort((a,b)=>five[a]-five[b]);
    if(weak.length){
      weak.slice(0,2).forEach(w=>{ if(REMEDY[w]) items.push(Object.assign({wx:w}, REMEDY[w])); });
      note='身中和，五行较平衡，无需全面补救；仅对偏弱项（'+weak.slice(0,2).join('、')+'）做适度微调即可。';
    } else {
      note='身中和，五行分布均衡，日常保持环境调和即可，无需刻意补救。';
    }
  }
  return {items, note};
}

function parseItem(s){const p=s.split(' ');const d=p[0].split('-');const t=p[1].split(':');return [+d[0],+d[1],+t[0],+t[1]];}
function num(y,m,d,hh,mm){return y*10000+m*100+d+(hh||0)/100+(mm||0)/10000;}
function yang(g){return GAN.indexOf(g)%2===0;}

// 日柱：公历天数差 + 基准(1900-01-01=甲戌)
function dayGZ(y,m,d){
  const base=Date.UTC(1900,0,1), cur=Date.UTC(y,m-1,d);
  const diff=Math.round((cur-base)/86400000);
  return GAN[(diff%10+10)%10]+ZHI[((diff+10)%12+12)%12];
}
// 年柱：立春精确时刻为界
function yearGZ(y,m,d,hh,mm){
  const arr=JIEQI.data[String(y)];
  if(!arr){ console.warn('年份 '+y+' 超出节气库范围('+JIEQI.range[0]+'-'+JIEQI.range[1]+')'); return null; }
  const j=parseItem(arr[0]);
  const born=num(y,m,d,hh,mm), lichun=num(y,j[0],j[1],j[2],j[3]);
  const yy=(born>=lichun)?y:(y-1);
  const idx=((yy-4)%60+60)%60;
  return GAN[idx%10]+ZHI[idx%12];
}
// 月柱：十二节精确时刻 + 五虎遁
function monthGZ(y,m,d,hh,mm,ygan){
  const born=num(y,m,d,hh,mm);
  let cands=[];
  [y-1,y].forEach(yy=>{
    const arr=JIEQI.data[String(yy)];
    if(!arr) return; // 跳过超出范围年份
    JIE_ORDER.forEach((name,i)=>{const p=parseItem(arr[i]);cands.push([num(yy,p[0],p[1],p[2],p[3]),JIE_ZHI[name]]);});
  });
  cands.sort((a,b)=>a[0]-b[0]);
  let zhi=2;
  if(m===1) zhi=0; // 兜底：数据起点年（缺 y-1 数据）时 1 月在小寒前属子月（大雪之后），正常年份会被下方 cands 覆盖
  cands.forEach(c=>{if(born>=c[0])zhi=c[1];});
  const si=GAN.indexOf(WUHU[ygan]);
  const off=(zhi-2+12)%12;
  return GAN[(si+off)%10]+ZHI[zhi];
}
// 时柱：五鼠遁 + 晚子时
function hourGZ(dgan,hh){
  let zhi,dg;
  if(hh>=23){zhi=0;dg=GAN[(GAN.indexOf(dgan)+1)%10];}
  else{zhi=((hh+1)/2|0)%12;dg=dgan;}
  return GAN[(GAN.indexOf(WUSHU[dg])+zhi)%10]+ZHI[zhi];
}
function tenGod(otherGan, dmWx, dmYin){
  const ow=GAN_WX[otherGan], oy=yang(otherGan);
  const dm=SHENG[dmWx];
  const owi=SHENG[ow];
  let rel;
  if(owi===dm) rel='同我';
  else if(owi===(dm+1)%5) rel='我生';
  else if(owi===(dm+2)%5) rel='我克';
  else if(owi===(dm+3)%5) rel='克我';
  else rel='生我';
  // 阴阳定名：同阴阳取"比肩/食神/偏财/七杀/偏印"，异阴阳取"劫财/伤官/正财/正官/正印"
  const same=(dmYin===oy);
  const m={'同我':same?'比肩':'劫财','我生':same?'食神':'伤官','我克':same?'偏财':'正财','克我':same?'七杀':'正官','生我':same?'偏印':'正印'};
  return m[rel];
}
function solarCorrection(place, bjTime){
  if(!place) return null;
  let lon=null;
  for(const c in CITY_LON){ if(place.indexOf(c)>=0){lon=CITY_LON[c];break;} }
  if(lon===null) return {found:false};
  const diffMin=(lon-120)*4;
  const total=bjTime.getTime()+diffMin*60000;
  return {found:true, lon:lon, diffMin:diffMin, time:new Date(total)};
}
// 五行分布（藏干加权，月令×1.5）
function computeFive(pillars){
  const five={木:0,火:0,土:0,金:0,水:0};
  pillars.forEach((p,idx)=>{
    five[GAN_WX[p[0]]]+=1.0;
    const zhi=p[1];
    const mult=(idx===1)?1.5:1.0;
    CANG[zhi].forEach(([tg,w])=>{ five[GAN_WX[tg]]+=w*mult; });
  });
  return five;
}
// 大运
function getDaYun(y,m,d,hh,mm,yg,mg,gender){
  const male=(gender==='男');
  const shun=((male&&yang(yg[0]))||(!male&&!yang(yg[0])));
  const born=num(y,m,d,hh,mm);
  let cands=[];
  [y-1,y,y+1].forEach(yy=>{
    const arr=JIEQI.data[String(yy)];
    if(!arr) return; // 跳过超出范围年份
    JIE_ORDER.forEach((name,i)=>{const p=parseItem(arr[i]);cands.push([num(yy,p[0],p[1],p[2],p[3]),JIE_ZHI[name]]);});
  });
  cands.sort((a,b)=>a[0]-b[0]);
  let target=null;
  if(shun){for(const c of cands){if(c[0]>born){target=c[0];break;}}}
  else{for(let i=cands.length-1;i>=0;i--){if(cands[i][0]<born){target=cands[i][0];break;}}}
  if(target===null) target=born;
  // 含时刻的精确天数差：target 是 num 格式 YYYYMMDD.HHMM
  const tY=Math.floor(target/10000), tM=Math.floor(target/100)%100-1;
  const tD=Math.floor(target%100), tFrac=target-Math.floor(target);
  const tH=Math.floor(tFrac*100), tMin=Math.round((tFrac*100-tH)*100);
  const d1=new Date(y,m-1,d,hh,mm);
  const d2=new Date(tY,tM,tD,tH||0,tMin||0);
  const days=Math.abs((d2-d1)/86400000);
  const startAge=days/3;
  const mi=GAN.indexOf(mg[0]), zi=ZHI.indexOf(mg[1]);
  const steps=[];
  for(let k=1;k<=8;k++){
    const step=shun?k:-k;
    steps.push(GAN[((mi+step)%10+10)%10]+ZHI[((zi+step)%12+12)%12]);
  }
  return {startAge:startAge, shun:shun, steps:steps};
}
// 月令取格（《子平真诠》：透干取格优先；不透干则以月令本气定格）
function getPattern(monthZhi, pillars, dmWx, dmYin){
  const tianGan=[pillars[0][0],pillars[1][0],pillars[2][0],pillars[3][0]];
  for(const [tg,w] of CANG[monthZhi]){
    if(tianGan.includes(tg)){
      const ten=tenGod(tg, dmWx, dmYin);
      if(PATTERN_NAME[ten]) return PATTERN_NAME[ten];
    }
  }
  // 不透干时以月令本气定格（"有格而不透"）
  const tg2=CANG[monthZhi][0][0];
  const ten2=tenGod(tg2, dmWx, dmYin);
  return PATTERN_NAME[ten2]||null;
}
// 胎元：月柱天干顺一位，地支顺三位（以月柱为母体，怀胎十月之根基）
function calcTaiYuan(mg){const gi=GAN.indexOf(mg[0]),zi=ZHI.indexOf(mg[1]);return GAN[(gi+1)%10]+ZHI[(zi+3)%12];}
// 命宫：月支逆数至生时，子为正月起点；天干用五虎遁从年干推算
function calcMingGong(yg,mg,hg){
  const mz=mg[1],hz=hg[1];
  const mNum=((ZHI.indexOf(mz)-2+12)%12)+1, hNum=ZHI.indexOf(hz)+1;
  let mgNum=(14-mNum+hNum)%12; if(mgNum===0) mgNum=12;
  const mgzIdx=(mgNum+1)%12, ygIdx=GAN.indexOf(yg[0]);
  return GAN[(ygIdx*2+mgNum-1)%10]+ZHI[mgzIdx];
}
// 身宫：月支顺数至生时，午为正月起点；公式对称命宫取反
function calcShenGong(yg,mg,hg){
  const mz=mg[1],hz=hg[1];
  const mNum=((ZHI.indexOf(mz)-2+12)%12)+1, hNum=ZHI.indexOf(hz)+1;
  let sgNum=(mNum+hNum)%12; if(sgNum===0) sgNum=12;
  const sgzIdx=(sgNum+1)%12, ygIdx=GAN.indexOf(yg[0]);
  return GAN[(ygIdx*2+sgNum-1)%10]+ZHI[sgzIdx];
}
// 完整排盘，返回 ctx
function paipan(name,gender,y,m,d,hh,mm,place,truesun){
  // 输入校验：类型/范围/日期真实性
  y=Number(y); m=Number(m); d=Number(d); hh=Number(hh); mm=Number(mm);
  if(!Number.isFinite(y)||!Number.isFinite(m)||!Number.isFinite(d)||!Number.isFinite(hh)||!Number.isFinite(mm)){
    alert('请输入有效的出生日期时间'); return null;
  }
  if(y<JIEQI.range[0]||y>JIEQI.range[1]){ alert('出生年份超出支持范围（'+JIEQI.range[0]+'-'+JIEQI.range[1]+'）'); return null; }
  if(m<1||m>12||Math.floor(m)!==m){ alert('月份需为 1-12'); return null; }
  if(hh<0||hh>23||Math.floor(hh)!==hh){ alert('小时需为 0-23'); return null; }
  if(mm<0||mm>59||Math.floor(mm)!==mm){ alert('分钟需为 0-59'); return null; }
  const dv=new Date(y,m-1,d);
  if(dv.getFullYear()!==y||dv.getMonth()!==m-1||dv.getDate()!==d){ alert('日期无效（如 2 月没有 30/31 日）'); return null; }
  if(gender!=='男'&&gender!=='女'){ alert('性别需为男或女'); return null; }
  let solarInfo=null, useY=y,useM=m,useD=d,useH=hh,useMin=mm;
  if(truesun==='yes'){
    const bj=new Date(y,m-1,d,hh,mm);
    const corr=solarCorrection(place,bj);
    if(corr && corr.found){ solarInfo=corr; const t=corr.time; useY=t.getFullYear();useM=t.getMonth()+1;useD=t.getDate();useH=t.getHours();useMin=t.getMinutes(); }
    else if(corr && !corr.found){ solarInfo={found:false}; }
  }
  const yg=yearGZ(useY,useM,useD,useH,useMin);
  const mg=monthGZ(useY,useM,useD,useH,useMin,yg[0]);
  const dg=dayGZ(useY,useM,useD);
  const hg=hourGZ(dg[0],useH);
  const pillars=[yg,mg,dg,hg];
  const dayMaster=dg[0];
  const dmWx=GAN_WX[dayMaster], dmYin=yang(dayMaster);
  const dayMasterFull=dayMaster+dmWx;
  const tens=pillars.map(p=>tenGod(p[0],dmWx,dmYin));
  const five=computeFive(pillars);
  const sumFive=WX_NAMES.reduce((a,w)=>a+five[w],0);
  const avgFive=sumFive/5;
  const dmIdx=SHENG[dmWx];
  const shengWo=(dmIdx+4)%5, woSheng=(dmIdx+1)%5, woKe=(dmIdx+2)%5, keWo=(dmIdx+3)%5;
  const support=five[WX_NAMES[dmIdx]]+five[WX_NAMES[shengWo]];
  const drain=five[WX_NAMES[woSheng]]+five[WX_NAMES[woKe]]+five[WX_NAMES[keWo]];
  const total=sumFive;
  const ratio=support/(support+drain||1);
  let strength, special={zhuanwang:false,cong:false,tiaohou:false};
  if(ratio>0.6) strength='强';
  else if(ratio<0.4) strength='弱';
  else strength='中和';
  const maxWx=Math.max.apply(null, WX_NAMES.map(w=>five[w]));
  if(maxWx>0.55*total) special.zhuanwang=true;
  if(support<0.18*total) special.cong=true;
  const monthZhi=pillars[1][1], dayZhi=pillars[2][1];
  if(['亥','子','丑','巳','午','未'].includes(monthZhi)) special.tiaohou=true;
  // 调候用神：日干×月令季节 → 调候五行（来源：《穷通宝鉴》）
  const seasonMap={寅:'春',卯:'春',辰:'春',巳:'夏',午:'夏',未:'夏',申:'秋',酉:'秋',戌:'秋',亥:'冬',子:'冬',丑:'冬'};
  const season=seasonMap[monthZhi]||'春';
  const TIAOHOU_MAP={
    甲:{春:['火'],夏:['水'],秋:['水'],冬:['火']},
    乙:{春:['火'],夏:['水'],秋:['水'],冬:['火']},
    丙:{春:['水'],夏:['水','金'],秋:['木'],冬:['木']},
    丁:{春:['木'],夏:['水','金'],秋:['木'],冬:['木','火']},
    戊:{春:['木'],夏:['水'],秋:['火'],冬:['火']},
    己:{春:['木'],夏:['水'],秋:['火'],冬:['火']},
    庚:{春:['火'],夏:['水'],秋:['火'],冬:['火']},
    辛:{春:['水'],夏:['水'],秋:['水'],冬:['火']},
    壬:{春:['火','土'],夏:['金','水'],秋:['木','火'],冬:['火','土']},
    癸:{春:['火','土'],夏:['金','水'],秋:['木','火'],冬:['火','土']},
  };
  special.tiaohouEls=TIAOHOU_MAP[dayMaster]?TIAOHOU_MAP[dayMaster][season]||[]:[];
  special._season=season;
  if(special.tiaohouEls.length) special.tiaohou=true;
  // 病药理论：五行偏枯 → 病药分析
  const avg=sumFive/5; let bing=null,yao=[];
  const maxExcess=Math.max.apply(null,WX_NAMES.map(w=>five[w]/avg));
  if(maxExcess>1.3){
    bing=WX_NAMES.reduce((a,b)=>five[a]>five[b]?a:b);
    const sk=WX_SK[bing]; if(sk){ yao.push(sk.被克, sk.生); /* 克病者+泄病者 */ }
  }
  special.bingyao=bing?{bing,yao}:null;
  // 专旺格细分：按主导五行 → 曲直格(木)/炎上格(火)/稼穑格(土)/从革格(金)/润下格(水)
  const ZHW_MAP={木:'曲直格',火:'炎上格',土:'稼穑格',金:'从革格',水:'润下格'};
  const CONG_DETAIL_MAP={正财:'从财格',偏财:'从财格',正官:'从杀格',七杀:'从杀格',食神:'从儿格',伤官:'从儿格'};
  let specialDetail=null;
  if(special.zhuanwang){
    const domWx=WX_NAMES.reduce((a,b)=>five[a]>five[b]?a:b);
    specialDetail='专旺·'+ZHW_MAP[domWx];
  } else if(special.cong){
    // 统计全柱十神频次，找出主导从格类型
    const tenCount={};for(const t of tens){tenCount[t]=(tenCount[t]||0)+1;}
    let domTen=null,maxC=0;
    for(const t in tenCount){if(tenCount[t]>maxC){maxC=tenCount[t];domTen=t;}}
    if(CONG_DETAIL_MAP[domTen]) specialDetail='从格·'+CONG_DETAIL_MAP[domTen];
    else if(maxC>=2) specialDetail='从格·从势格（多神并存）';
    else specialDetail='从格';
  }
  // 喜用神
  let xiYong=[], jiYong=[];
  if(strength==='强'){ xiYong=[WX_NAMES[keWo],WX_NAMES[woKe],WX_NAMES[woSheng]]; jiYong=[WX_NAMES[dmIdx],WX_NAMES[shengWo]]; }
  else if(strength==='弱'){ xiYong=[WX_NAMES[dmIdx],WX_NAMES[shengWo]]; jiYong=[WX_NAMES[keWo],WX_NAMES[woKe],WX_NAMES[woSheng]]; }
  else { xiYong=WX_NAMES.slice(); }
  // 日支十神
  const dayZhiTG=CANG[dayZhi][0][0];
  const dayZhiTG_ten=tenGod(dayZhiTG, dmWx, dmYin);
  const dayZhiTai=['子','午','卯','酉'].includes(dayZhi);
  // 财官位置（天干或地支本气）
  function pillarTenFull(i){
    const zhiTg=CANG[pillars[i][1]][0][0];
    return [tenGod(pillars[i][0],dmWx,dmYin), tenGod(zhiTg,dmWx,dmYin)];
  }
  const caiGuan=['正财','偏财','正官','七杀'];
  let hasYM=false,hasDH=false;
  [0,1].forEach(i=>{ if(pillarTenFull(i).some(t=>caiGuan.includes(t))) hasYM=true; });
  [2,3].forEach(i=>{ if(pillarTenFull(i).some(t=>caiGuan.includes(t))) hasDH=true; });
  const caiGuanPos=(hasYM&&hasDH)?'双':(hasYM?'年月':(hasDH?'日时':'无'));
  const pattern=getPattern(monthZhi, pillars, dmWx, dmYin);
  const dy=getDaYun(useY,useM,useD,useH,useMin,yg,mg,gender);
  const shenSha=calcShenSha(pillars, gender);
  const remedy=getRemedy(strength, five, avgFive, xiYong, monthZhi);
  const kongWang=calcKongWang(dg);
  const taiYuan=calcTaiYuan(mg), mingGong=calcMingGong(yg,mg,hg), shenGong=calcShenGong(yg,mg,hg);
  return {name,gender,y,m,d,hh,mm,place,truesun,
    yg,mg,dg,hg,pillars,dayMaster,dmWx,dmYin,dayMasterFull,tens,
    five,sumFive,avgFive,strength,support,drain,ratio,special,specialDetail,
    monthZhi,dayZhi,dayZhiTG,dayZhiTG_ten,dayZhiTai,caiGuanPos,
    xiYong,jiYong,pattern,dy,solarInfo,
    naYinYear:NAYIN[yg], shenSha:shenSha, remedy:remedy, kongWang:kongWang,
    taiYuan:taiYuan, mingGong:mingGong, shenGong:shenGong,
    useH:useH, useMin:useMin};
}

// 五行生克关系
const WX_SK={木:{生:'火',克:'土',被生:'水',被克:'金'},火:{生:'土',克:'金',被生:'木',被克:'水'},土:{生:'金',克:'水',被生:'火',被克:'木'},金:{生:'水',克:'木',被生:'土',被克:'火'},水:{生:'木',克:'火',被生:'金',被克:'土'}};

// 断语库匹配
function findRule(id){ return RULES.find(r=>r.id===id)||null; }
// [ENGINE:END]
function fmtRule(r){ if(!r) return ''; return `<div style="margin-top:4px;font-size:12px;color:var(--gold)">【古籍断语】${r.conclusion}（出处：${r.source}）${r.suggestion?` → ${r.suggestion}`:''}</div>`; }

// [ENGINE:BEGIN]
// 状态条件运行时评估：为"状态"条件提供真实判断（十神/五行/喜忌/格局上下文）
function evalState(st, c, ctx){
  const avg=ctx.avgFive||1;
  const allTens=[...ctx.tens];
  ctx.pillars.forEach(p=>{ const tg=CANG[p[1]][0][0]; allTens.push(tenGod(tg,ctx.dmWx,ctx.dmYin)); });
  const cnt=(arr,t)=>{ let n=0; arr.forEach(x=>{ if(x===t) n++; }); return n; };
  const wxOf=t=>GAN_WX_OfTen(t,ctx);
  const tg=Array.isArray(c['十神'])?c['十神']:(c['十神']?[c['十神']]:null);
  const countTen=()=>{ if(!tg) return 0; let n=0; allTens.forEach(x=>{ if(tg.includes(x)) n++; }); return n; };
  switch(st){
    case '桃花': {
      const th=ctx.shenSha&&ctx.shenSha.find(s=>s.name==='桃花');
      if(!th) return false;
      if(c['位置']==='日支') return th.pos.indexOf('日')>=0; // 日支坐桃花
      return true;
    }
    case '调候': {
      // 真正的调候需求：寒月（亥子丑）需暖、暑月（巳午未）需润
      const mz=ctx.pillars[1][1];
      return ['亥','子','丑'].includes(mz)||['巳','午','未'].includes(mz);
    }
    case '偏枯有药': {
      // 真正偏枯：某行极旺(≥1.8×avg)且另一行极弱(≤0.4×avg) 旺弱并存（"病"），
      // 且喜用神（"药"）存在感 ≥0.5×avg。
      // 大样本标定（300盘）：此阈值命中率约 28%，避免"人人偏枯"的无区分度断语。
      let mx=0, mn=Infinity;
      for(const w of WX_NAMES){ const v=ctx.five[w]||0; if(v>mx) mx=v; if(v<mn) mn=v; }
      if(!(mx>=avg*1.8 && mn<=avg*0.4)) return false;
      return ctx.xiYong.some(w=>ctx.five[w]>=avg*0.5);
    }
    case '为用神有力': {
      if(!tg) return false;
      return tg.some(t=>ctx.xiYong.includes(wxOf(t))&&ctx.five[wxOf(t)]>=avg);
    }
    case '有制化': {
      const dm=SHENG[ctx.dmWx];
      const yin=WX_NAMES[(dm+4)%5], shiShang=WX_NAMES[(dm+1)%5], guanSha=WX_NAMES[(dm+3)%5];
      const isShangGuan=!!(tg&&tg.includes('伤官'));
      const target=isShangGuan?wxOf('伤官'):guanSha;
      if(ctx.five[target]<avg*0.4) return false;               // 官杀/伤官本身须存在
      if(isShangGuan) return ctx.five[yin]>=avg*0.5;           // 印制伤官
      return ctx.five[shiShang]>=avg*0.5||ctx.five[yin]>=avg*0.5; // 食伤制杀 / 印化杀
    }
    case '多而有力': {
      if(!tg) return false;
      return countTen()>=2&&tg.some(t=>ctx.five[wxOf(t)]>=avg);
    }
    case '多位': {
      if(!tg) return false;
      return countTen()>=2;
    }
    case '身旺': return ctx.strength==='强';
    case '身弱财多': {
      if(!tg) return false;
      return ctx.strength==='弱'&&(countTen()>=3||tg.some(t=>ctx.five[wxOf(t)]>=avg*1.15));
    }
    case '得其一为用': {
      if(!tg) return false;
      return tg.some(t=>ctx.xiYong.includes(wxOf(t)));
    }
    case '透出克官': {
      if(!tg) return false;
      const hasGuan=allTens.some(t=>t==='正官'||t==='七杀');
      return tg.some(t=>ctx.tens.includes(t))&&hasGuan; // 伤官透干且命局有官
    }
    case '为喜用': {
      if(c['位置']==='日支') return ctx.xiYong.includes(GAN_WX[ctx.dayZhiTG]);
      return false;
    }
    case '为忌神': {
      if(c['位置']==='日支') return ctx.jiYong.includes(GAN_WX[ctx.dayZhiTG]);
      return false;
    }
    case '身旺为用双美': {
      if(!tg) return false;
      return ctx.strength==='强'&&tg.some(t=>ctx.xiYong.includes(wxOf(t)));
    }
    case '身旺担财': return ctx.strength==='强';
    case '重重': {
      if(!tg) return false;
      return countTen()>=3;
    }
    case '一位得时': {
      if(!tg) return false;
      return countTen()===1&&tg.some(t=>{
        const w=wxOf(t);
        return CANG[ctx.pillars[1][1]].some(([tg2])=>GAN_WX[tg2]===w)||ctx.five[w]>=avg*0.9;
      });
    }
    case '成格': {
      const p=ctx.pattern||''; let ten=null;
      for(const k in PATTERN_NAME){ if(PATTERN_NAME[k]===p){ ten=k; break; } }
      if(!ten) return false;
      const w=wxOf(ten);
      return ctx.five[w]>=avg*0.8&&(ctx.tens.includes(ten)||cnt(allTens,ten)>=2);
    }
    case '伤官佩印': {
      const yin=WX_NAMES[(SHENG[ctx.dmWx]+4)%5];
      return ctx.pattern==='伤官格'&&ctx.five[yin]>=avg*0.5;
    }
    case '方局全不杂': {
      return !!ctx.special.zhuanwang&&ctx.five[ctx.dmWx]>=ctx.sumFive*0.45;
    }
    case '弱极从势': {
      return !!ctx.special.cong&&ctx.strength==='弱';
    }
    case '用神被冲克合': {
      if(ctx.xiYong.length>=5) return false; // 中和命局喜忌无定论，不存在明确用神
      return yongShenChong(ctx);
    }
    case '用神假': {
      if(ctx.xiYong.length>=5) return false; // 中和命局用神本就"皆有可假皆可"，不判为假
      const maxXi=Math.max(...ctx.xiYong.map(w=>ctx.five[w]||0));
      return maxXi<avg*0.6; // 喜用五行全弱，用神虚浮无力
    }
    default: return false; // 未知状态 / 应走五行分值分支的状态：不命中
  }
}
// 用神被冲克合：喜用所在干支被其他柱冲/合/克/刑
function yongShenChong(ctx){
  const gan=[], zhi=[];
  ctx.pillars.forEach((p,i)=>{
    if(ctx.xiYong.includes(GAN_WX[p[0]])) gan.push({g:p[0],i});
    const tg=CANG[p[1]][0][0];
    if(ctx.xiYong.includes(GAN_WX[tg])) zhi.push({z:p[1],i});
  });
  if(!gan.length&&!zhi.length) return false;
  for(const o of gan){
    for(let j=0;j<4;j++){
      if(j===o.i) continue;
      const g=ctx.pillars[j][0];
      if(WU_HE[g]===o.g||WU_HE[o.g]===g) return true;                    // 天干相合
      if(WX_SK[GAN_WX[g]]&&WX_SK[GAN_WX[g]].被克===GAN_WX[o.g]) return true; // 天干相克
    }
  }
  for(const o of zhi){
    for(let j=0;j<4;j++){
      if(j===o.i) continue;
      const z=ctx.pillars[j][1];
      if(CHONG[z]===o.z||CHONG[o.z]===z) return true;                          // 冲
      if(LIUHE.some(pr=>pr.includes(z)&&pr.includes(o.z))) return true;        // 合
      if(XING_PAIRS.some(pr=>(pr[0]===z&&pr[1]===o.z)||(pr[0]===o.z&&pr[1]===z))) return true; // 刑
    }
  }
  return false;
}

function matchRules(ctx){
  const cats={};
  RULES.forEach(r=>{ if(!cats[r.category]) cats[r.category]=[]; });
  RULES.forEach(r=>{
    const c=r.condition||{}; let hit=true;
    let wx=null,st=null,tenArr=null,pos=null;
    // 空 condition 规则为专用触发型（dayun_*/liuyue_*/liuri_*/qinq_27~30 等由专用函数按 id 触发），
    // 不参与主引擎匹配，避免无条件命中导致固定断语出现在每个命盘
    if(Object.keys(c).length===0){ hit=false; }
    for(const k in c){
      const v=c[k];
      if(k==='日主'){ if(v!==ctx.dayMasterFull) hit=false; }
      else if(k==='旺衰'){ if(v!==ctx.strength) hit=false; }
      else if(k==='十神'){ tenArr=Array.isArray(v)?v:[v]; }
      else if(k==='五行'){ wx=v; }
      else if(k==='状态'){ st=v; }
      else if(k==='性别'){ if(v!==ctx.gender) hit=false; }
      else if(k==='位置'){ pos=v; }
      else if(k==='组合'){ const arr=Array.isArray(v)?v:[v]; if(hit&&!arr.every(t=>ctx.tens.includes(t))) hit=false; }
      else if(k==='十神组合'){ const arr=Array.isArray(v)?v:[v]; if(hit&&!arr.every(t=>ctx.tens.includes(t))) hit=false; }
      else if(k==='否决'){ /* flag，后续在组合/十神匹配中反转逻辑 */ }
      else if(k==='干支'){ /* 位置标记键，仅指定柱位（年干/月干/时干），实际十神检查由十神+位置组合完成 */ }
      else if(k==='生克检测'){ /* 五行生克运行时检测，在循环后处理 */ }
      else if(k==='格局'){
        if(v==='专旺格'){ if(!ctx.special.zhuanwang) hit=false; }
        else if(v==='从格'){ if(!ctx.special.cong) hit=false; }
        else if(ctx.specialDetail && ctx.specialDetail.includes(v)){ /* 细分格局命中，如曲直格/从财格等 */ }
        else if(v!==ctx.pattern) hit=false;
      }
      else if(k==='神煞'){
        if(!ctx.shenSha || !ctx.shenSha.some(s=>s.name===v)) hit=false;
      }
      else if(k==='流年'||k==='流月'||k==='流日'){
        // 流年/流月/流日断语仅由对应分析面板（runLiuNian/runLiuYue/runLiuDay）的专用匹配函数触发；
        // 主排盘 matchRules 不输出这些时序类规则
        hit=false;
      }
      else if(k==='合婚'){
        hit=false;
      }
    }
    // 否决检查：组合键为"必须存在"，否决键为"必须不存在"。
    // 否决支持数组（明确列出禁用的十神）或 true（复用组合列表作为禁用集合，如"全无财星"）
    if(hit && c.否决){
      const veto=Array.isArray(c.否决)?c.否决:(Array.isArray(c.组合)?c.组合:[]);
      if(veto.length && ctx.tens.some(t=>veto.includes(t))) hit=false;
    }
    // 生克检测：五行通关/制化/反克
    if(hit && wx!==null && c['生克检测']){
      const skType=c['生克检测'];
      const sk=WX_SK[wx]; if(!sk){ hit=false; }
      else {
        const avg=ctx.avgFive;
        if(skType==='通关'){
          // 三行相生链条需要各链节都有"存在感"≥60%平均值
          const w2=sk.生, w3=WX_SK[w2]?WX_SK[w2].生:null;
          if(!w3 || ctx.five[wx]<avg*0.6 || ctx.five[w2]<avg*0.6 || ctx.five[w3]<avg*0.6) hit=false;
        } else if(skType==='制化'){
          // 克行需旺(≥avg)，被克行存在(≥0.4avg)，解救行存在(≥0.4avg)
          const ke=sk.被克, rescue=WX_SK[ke]?WX_SK[ke].被克:null;
          if(ctx.five[wx]<avg*0.4 || ctx.five[ke]<avg || !rescue || ctx.five[rescue]<avg*0.4) hit=false;
        } else if(skType==='反克'){
          const ke=sk.被克;
          if(!ke || ctx.five[wx]<=avg*1.3 || ctx.five[ke]>=avg*0.6) hit=false;
        } else { hit=false; }
      }
      wx=null; // 生克检测已处理，跳过后续 wx/st 通用匹配
    }
    // 过旺无制检测（杀: 某行过旺，且克制它的五行太弱）
    if(hit && wx!==null && c.杀===1){
      const sk=WX_SK[wx]; const ke=sk?sk.被克:null;
      const avg=ctx.avgFive;
      if(!ke || ctx.five[wx]<=avg*1.3 || ctx.five[ke]>=avg*0.5) hit=false;
      wx=null;
    }
    if(hit && tenArr){
      let pool=ctx.tens;
      if(pos==='日支'){ pool=[ctx.dayZhiTG_ten]; }
      else if(pos==='年干'){ pool=[ctx.tens[0]]; }
      else if(pos==='月干'){ pool=[ctx.tens[1]]; }
      else if(pos==='时干'){ pool=[ctx.tens[3]]; }
      else if(pos==='年月'){ pool=[ctx.tens[0],ctx.tens[1]]; if(!(ctx.caiGuanPos==='年月'||ctx.caiGuanPos==='双')) hit=false; }  // 财官需天干透出（藏而不透力度弱）
      else if(pos==='日时'){ pool=[ctx.tens[2],ctx.tens[3]]; if(!(ctx.caiGuanPos==='日时'||ctx.caiGuanPos==='双')) hit=false; }  // 财官需天干透出
      if(hit && !tenArr.some(t=>pool.includes(t))) hit=false;
    }
    if(hit && wx!==null){
      const sc=ctx.five[wx]; const avg=ctx.avgFive; let ok=false;
      if(st==='旺') ok=sc>=avg*1.15;
      else if(st==='弱') ok=sc<=avg*0.85;
      else if(st==='中和') ok=(sc>avg*0.85&&sc<avg*1.15);
      else if(st==='过旺或过弱') ok=(sc>=avg*1.3||sc<=avg*0.7);
      else ok=false;
      if(!ok) hit=false;
    }
    if(hit && st!==null && wx===null){
      // 无"五行"键的状态条件：由 evalState 按十神/喜忌/格局上下文运行时评估
      if(!evalState(st, c, ctx)) hit=false;
    }
    if(hit) cats[r.category].push(r);
  });
  return cats;
}
// [ENGINE:END]

let LAST=null; // 最近一次排盘 ctx
let LIU_OPEN=false, LIU_YUE_OPEN=false, LIU_DAY_OPEN=false, LIU_QIN_OPEN=false; // 展开/收起状态
// [ENGINE:BEGIN]
const SHI_CHEN_MAP={子:[0,0],丑:[2,0],寅:[4,0],卯:[6,0],辰:[8,0],巳:[10,0],午:[12,0],未:[14,0],申:[16,0],酉:[18,0],戌:[20,0],亥:[22,0]};
// 中国夏令时（1986-1991）窗口表：起止日 02:00 整（北京时间），期间钟表拨快 1 小时
const DST_WINDOWS=[
  {s:[1986,5,4], e:[1986,9,14]},
  {s:[1987,4,12],e:[1987,9,13]},
  {s:[1988,4,10],e:[1988,9,11]},
  {s:[1989,4,16],e:[1989,9,17]},
  {s:[1990,4,15],e:[1990,9,16]},
  {s:[1991,4,14],e:[1991,9,15]}
];
function dstOffset(y,m,d,hh){
  for(let i=0;i<DST_WINDOWS.length;i++){
    const w=DST_WINDOWS[i];
    if(y!==w.s[0]) continue;
    const t=Date.UTC(y,m-1,d,hh);
    if(t>=Date.UTC(w.s[0],w.s[1]-1,w.s[2],2) && t<Date.UTC(w.e[0],w.e[1]-1,w.e[2],2)) return 1;
  }
  return 0;
}
function applyDst(y,m,d,hh){
  if(!dstOffset(y,m,d,hh)) return {y,m,d,hh,dst:0};
  hh-=1;
  if(hh<0){
    hh+=24;
    const dt=new Date(y,m-1,d-1);
    y=dt.getFullYear(); m=dt.getMonth()+1; d=dt.getDate();
  }
  return {y,m,d,hh,dst:1};
}
// [ENGINE:END]

// [ENGINE:BEGIN]
// ===== 农历转换模块（1900-2099，零依赖） =====
const LUNAR_INFO=[
0x04bd8,0x04ae0,0x0a570,0x054d5,0x0d260,0x0d950,0x16554,0x056a0,0x09ad0,0x055d2,
0x04ae0,0x0a5b6,0x0a4d0,0x0d250,0x1d255,0x0b540,0x0d6a0,0x0ada2,0x095b0,0x14977,
0x04970,0x0a4b0,0x0b4b5,0x06a50,0x06d40,0x1ab54,0x02b60,0x09570,0x052f2,0x04970,
0x06566,0x0d4a0,0x0ea50,0x06e95,0x05ad0,0x02b60,0x186e3,0x092e0,0x1c8d7,0x0c950,
0x0d4a0,0x1d8a6,0x0b550,0x056a0,0x1a5b4,0x025d0,0x092d0,0x0d2b2,0x0a950,0x0b557,
0x06ca0,0x0b550,0x15355,0x04da0,0x0a5b0,0x14573,0x052b0,0x0a9a8,0x0e950,0x06aa0,
0x0aea6,0x0ab50,0x04b60,0x0aae4,0x0a570,0x05260,0x0f263,0x0d950,0x05b57,0x056a0,
0x096d0,0x04dd5,0x04ad0,0x0a4d0,0x0d4d4,0x0d250,0x0d558,0x0b540,0x0b6a0,0x195a6,
0x095b0,0x049b0,0x0a974,0x0a4b0,0x0b27a,0x06a50,0x06d40,0x0af46,0x0ab60,0x09570,
0x04af5,0x04970,0x064b0,0x074a3,0x0ea50,0x06b58,0x055c0,0x0ab60,0x096d5,0x092e0,
0x0c960,0x0d954,0x0d4a0,0x0da50,0x07552,0x056a0,0x0abb7,0x025d0,0x092d0,0x0cab5,
0x0a950,0x0b4a0,0x0baa4,0x0ad50,0x055d9,0x04ba0,0x0a5b0,0x15176,0x052b0,0x0a930,
0x07954,0x06aa0,0x0ad50,0x05b52,0x04b60,0x0a6e6,0x0a4e0,0x0d260,0x0ea65,0x0d530,
0x05aa0,0x076a3,0x096d0,0x04afb,0x04ad0,0x0a4d0,0x1d0b6,0x0d250,0x0d520,0x0dd45,
0x0b5a0,0x056d0,0x055b2,0x049b0,0x0a577,0x0a4b0,0x0aa50,0x1b255,0x06d20,0x0ada0,
0x14b63,0x09370,0x049f8,0x04970,0x064b0,0x168a6,0x0ea50,0x06b20,0x1a6c4,0x0aae0,
0x0a2e0,0x0d2e3,0x0c960,0x0d557,0x0d4a0,0x0da50,0x05d55,0x056a0,0x0a6d0,0x055d4,
0x052d0,0x0a9b8,0x0a950,0x0b4a0,0x0b6a6,0x0ad50,0x055a0,0x0aba4,0x0a5b0,0x052b0,
0x0b273,0x06930,0x07337,0x06aa0,0x0ad50,0x14b55,0x04b60,0x0a570,0x054e4,0x0d160,
0x0e968,0x0d520,0x0daa0,0x16aa6,0x056d0,0x04ae0,0x0a9d4,0x0a2d0,0x0d150,0x0f252];
const LUNAR_MONTH_NAMES=['正月','二月','三月','四月','五月','六月','七月','八月','九月','十月','冬月','腊月'];
function leapMonth(y){return LUNAR_INFO[y-1900]&0xf;}
function leapDays(y){return leapMonth(y)?((LUNAR_INFO[y-1900]&0x10000)?30:29):0;}
function monthDays(y,m){return(LUNAR_INFO[y-1900]&(0x10000>>m))?30:29;}
function lunarToSolar(lYear,lMonth,lDay,isLeap){
  let offset=0;
  for(let i=1900;i<lYear;i++){
    let yd=348;
    for(let j=1;j<=12;j++) yd+=(LUNAR_INFO[i-1900]&(0x10000>>j))?1:0;
    yd+=leapDays(i); offset+=yd;
  }
  const leap=leapMonth(lYear);
  for(let i=1;i<lMonth;i++){offset+=monthDays(lYear,i); if(i===leap) offset+=leapDays(lYear);}
  if(isLeap) offset+=monthDays(lYear,lMonth);
  offset+=lDay-1;
  const base=Date.UTC(1900,0,31);
  const dt=new Date(base+offset*86400000);
  return{y:dt.getUTCFullYear(),m:dt.getUTCMonth()+1,d:dt.getUTCDate()};
}
function lunarDayName(d){
  if(d===10)return'初十'; if(d===20)return'二十'; if(d===30)return'三十';
  const px=['初','十','廿','三'], dg=['','一','二','三','四','五','六','七','八','九','十'];
  return px[Math.floor((d-1)/10)]+dg[d%10||10];
}
// [ENGINE:END]

// ===== 原生 select 下拉初始化（年/月/日/时/分 + 合婚 A/B） =====
function selDaysIn(y,m){ return new Date(y,m,0).getDate(); }
function selFill(sel, opts, placeholder){
  if(!sel) return;
  const cur=sel.value;
  let html='<option value="">'+(placeholder||'请选择')+'</option>';
  for(let i=0;i<opts.length;i++){
    const v=String(opts[i].v);
    html+='<option value="'+v+'"'+(v===cur?' selected':'')+'>'+opts[i].l+'</option>';
  }
  sel.innerHTML=html;
}
function selYear(id){ const sel=document.getElementById(id); if(!sel) return; const a=[]; const curYear=new Date().getFullYear(); for(let i=curYear;i>=1895;i--) a.push({v:i,l:i+'年'}); selFill(sel, a, '年份'); if(!sel.value) sel.value=String(curYear); }
function selMonth(id){ const a=[]; for(let i=1;i<=12;i++) a.push({v:i,l:i+'月'}); selFill(document.getElementById(id), a, '月份'); }
function selDay(id, yId, mId){
  const sel=document.getElementById(id);
  const y=+(document.getElementById(yId).value)||2000;
  const m=+(document.getElementById(mId).value)||1;
  const max=selDaysIn(y,m);
  const a=[]; for(let i=1;i<=max;i++) a.push({v:i,l:i+'日'});
  const cur=sel.value;
  if(cur && +cur>max) sel.value='';
  selFill(sel, a, '日期');
  if(cur && +cur<=max) sel.value=cur;
}

// ===== 农历切换逻辑 =====
let calMode='solar'; // 'solar' | 'lunar'
let hCalModeA='solar', hCalModeB='solar';
function lunarDayName(d){
  if(d===10) return '初十'; if(d===20) return '二十'; if(d===30) return '三十';
  const px=['初','十','廿','三'], dg=['','一','二','三','四','五','六','七','八','九','十'];
  return px[Math.floor((d-1)/10)] + dg[d%10 || 10];
}
function switchCal(mode){
  if(mode===calMode) return;
  calMode=mode;
  document.querySelectorAll('#calToggle button').forEach(b=>{ b.classList.toggle('active', b.dataset.cal===mode); });
  document.getElementById('dateLabel').textContent = (mode==='lunar'?'农历':'阳历') + '生日';
  document.getElementById('year').value='';
  fillDateOptions();
}
function switchHeCal(side, mode){
  const oldMode = side==='A'?hCalModeA:hCalModeB;
  if(mode===oldMode) return;
  if(side==='A') hCalModeA=mode; else hCalModeB=mode;
  document.querySelectorAll('#hCalToggle'+side+' button').forEach(b=>{ b.classList.toggle('active', b.dataset.cal===mode); });
  document.getElementById('hDateLabel'+side).textContent = (mode==='lunar'?'农历':'阳历') + '生日';
  document.getElementById('hYear'+side).value='';
  fillHeDateOptions(side);
}
function fillDateOptions(){
  const ySel=document.getElementById('year'), mSel=document.getElementById('month'), dSel=document.getElementById('day');
  const yv=ySel.value;
  if(calMode==='solar'){
    selMonth('month');
    dSel.innerHTML='<option value="">日期</option>';
    if(yv && mSel.value) selDay('day','year','month');
  } else {
    // 农历月
    const y=+yv || new Date().getFullYear();
    const leap=leapMonth(y);
    let mh='<option value="">月份</option>';
    for(let i=1;i<=12;i++){
      mh += '<option value="'+i+'">'+LUNAR_MONTH_NAMES[i-1]+'</option>';
      if(i===leap) mh += '<option value="'+i+'l">'+LUNAR_MONTH_NAMES[i-1]+'（闰）</option>';
    }
    mSel.innerHTML=mh;
    dSel.innerHTML='<option value="">日期</option>';
  }
}
function fillLunarDays(y, mv, dId){
  const isLeap = mv.endsWith('l');
  const m = +mv.replace('l','');
  let n; if(isLeap) n=leapDays(y); else n=monthDays(y,m);
  let dh=''; for(let i=1;i<=n;i++) dh += '<option value="'+i+'">'+lunarDayName(i)+'</option>';
  document.getElementById(dId).innerHTML = '<option value="">日期</option>'+dh;
}
function fillHeDateOptions(side){
  const mode = side==='A'?hCalModeA:hCalModeB;
  const ySel=document.getElementById('hYear'+side), mSel=document.getElementById('hMonth'+side), dSel=document.getElementById('hDay'+side);
  const yv=ySel.value;
  if(mode==='solar'){
    selMonth('hMonth'+side);
    dSel.innerHTML='<option value="">日期</option>';
    if(yv && mSel.value) selDay('hDay'+side,'hYear'+side,'hMonth'+side);
  } else {
    const y=+yv || new Date().getFullYear();
    const leap=leapMonth(y);
    let mh='<option value="">月份</option>';
    for(let i=1;i<=12;i++){
      mh += '<option value="'+i+'">'+LUNAR_MONTH_NAMES[i-1]+'</option>';
      if(i===leap) mh += '<option value="'+i+'l">'+LUNAR_MONTH_NAMES[i-1]+'（闰）</option>';
    }
    mSel.innerHTML=mh;
    dSel.innerHTML='<option value="">日期</option>';
  }
}
function selHour(id){ const a=[]; for(let i=0;i<=23;i++) a.push({v:i,l:(i<10?'0':'')+i+'时'}); selFill(document.getElementById(id), a, '时'); }
function selMinute(id){ const a=[]; for(let i=0;i<=59;i++) a.push({v:i,l:(i<10?'0':'')+i+'分'}); selFill(document.getElementById(id), a, '分'); }
function selBindDay(yId, mId, dId){
  const yEl=document.getElementById(yId), mEl=document.getElementById(mId);
  if(yEl && yEl.addEventListener) yEl.addEventListener('change', function(){ selDay(dId, yId, mId); });
  if(mEl && mEl.addEventListener) mEl.addEventListener('change', function(){ selDay(dId, yId, mId); });
}
function initSelects(){
  // 主表单
  selYear('year'); selMonth('month'); selDay('day','year','month');
  selHour('hour'); selMinute('minute');
  selBindDay('year','month','day');
  // 农历日期联动（仅农历模式）
  const mEl=document.getElementById('month');
  if(mEl && mEl.addEventListener) mEl.addEventListener('change', function(){ if(calMode==='lunar'){ const y=+document.getElementById('year').value||2000; fillLunarDays(y, this.value, 'day'); } });
  // 合婚 A
  selYear('hYearA'); selMonth('hMonthA'); selDay('hDayA','hYearA','hMonthA');
  selHour('hHourA'); selMinute('hMinuteA');
  selBindDay('hYearA','hMonthA','hDayA');
  const hmA=document.getElementById('hMonthA');
  if(hmA && hmA.addEventListener) hmA.addEventListener('change', function(){ if(hCalModeA==='lunar'){ const y=+document.getElementById('hYearA').value||2000; fillLunarDays(y, this.value, 'hDayA'); } });
  // 合婚 B
  selYear('hYearB'); selMonth('hMonthB'); selDay('hDayB','hYearB','hMonthB');
  selHour('hHourB'); selMinute('hMinuteB');
  selBindDay('hYearB','hMonthB','hDayB');
  const hmB=document.getElementById('hMonthB');
  if(hmB && hmB.addEventListener) hmB.addEventListener('change', function(){ if(hCalModeB==='lunar'){ const y=+document.getElementById('hYearB').value||2000; fillLunarDays(y, this.value, 'hDayB'); } });
}
initSelects();
toggleTimeMode();
toggleHeTimeMode('A');
toggleHeTimeMode('B');

function toggleTimeMode(){
  const mode=document.getElementById('timeMode').value;
  const hourEl=document.getElementById('hour');
  const minuteEl=document.getElementById('minute');
  const sc=document.getElementById('shichen');
  const hint=document.getElementById('timeHint');
  if(mode==='exact'){
    hourEl.classList.remove('hidden');
    minuteEl.classList.remove('hidden');
    sc.classList.add('hidden');
    if(hint) hint.textContent='填写出生钟表时间，系统将自动判断夏令时与真太阳时校正。';
  } else {
    hourEl.classList.add('hidden');
    minuteEl.classList.add('hidden');
    sc.classList.remove('hidden');
    if(hint) hint.textContent='时辰本身即为真太阳时时段，系统将跳过夏令时与真太阳时校正。适用于按太阳/农活/作息估算的时间（如"早上9点多"→巳时）。';
  }
}

function generate(){
  const name=document.getElementById('name').value||'匿名';
  const gender=document.getElementById('gender').value;
  let y=+document.getElementById('year').value;
  let mVal=document.getElementById('month').value;
  let d=+document.getElementById('day').value;
  let m;
  let lunarInput=null;
  if(calMode==='lunar'){
    if(!y||!mVal||!d){alert('请填写完整农历生日');return;}
    const isLeap=mVal.endsWith('l');
    const lm=+mVal.replace('l','');
    lunarInput={y, m:lm, d, isLeap, mName:document.getElementById('month').selectedOptions[0].text, dName:lunarDayName(d)};
    const solar=lunarToSolar(y,lm,d,isLeap);
    y=solar.y; m=solar.m; d=solar.d;
  } else {
    m=+mVal;
    if(!y||!m||!d){alert('请填写完整阳历生日');return;}
  }
  const timeMode=document.getElementById('timeMode').value;
  const place=(document.getElementById('birthplace').value||'').trim();
  const truesun=document.getElementById('truesun').value;
  if(!gender){alert('请选择性别（用于排大运顺逆）');return;}
  let hh=0,mm=0;
  let shichenMode=false;
  if(timeMode==='exact'){
    const hhIn=+document.getElementById('hour').value;
    const mmIn=+document.getElementById('minute').value;
    if(Number.isNaN(hhIn)||Number.isNaN(mmIn)||hhIn<0||hhIn>23||mmIn<0||mmIn>59){alert('请填写有效的出生时间（时 0-23，分 0-59）');return;}
    hh=hhIn; mm=mmIn;
  } else {
    const sc=document.getElementById('shichen').value;
    if(!sc){alert('请选择出生时辰');return;}
    [hh,mm]=SHI_CHEN_MAP[sc];
    shichenMode=true;
  }
  let dstFlag=0;
  if(shichenMode){
    // 时辰本身即为真太阳时时段，跳过 DST 和经度校正
    const ctx=paipan(name,gender,y,m,d,hh,mm,place,'no');
    ctx.dst=0;
    ctx.shichenMode=true;
    ctx.lunarInput=lunarInput;
    LAST=ctx;
    renderResult(ctx);
  } else {
    const dst=applyDst(y,m,d,hh);
    y=dst.y; m=dst.m; d=dst.d; hh=dst.hh;
    dstFlag=dst.dst;
    const ctx=paipan(name,gender,y,m,d,hh,mm,place,truesun);
    ctx.dst=dstFlag;
    ctx.shichenMode=false;
    ctx.lunarInput=lunarInput;
    LAST=ctx;
    renderResult(ctx);
  }
}

function renderResult(ctx){
  document.getElementById('rName').textContent=ctx.name+' · '+(ctx.gender==='男'?'乾造':'坤造');
  let metaText=`阳历 ${ctx.y}年${ctx.m}月${ctx.d}日 ${String(ctx.hh).padStart(2,'0')}:${String(ctx.mm).padStart(2,'0')} | 出生地：${ctx.place||'未填'}`;
  if(ctx.lunarInput){
    metaText = `农历 ${ctx.lunarInput.y}年${ctx.lunarInput.mName}${ctx.lunarInput.dName} → ` + metaText;
  }
  document.getElementById('rMeta').textContent=metaText;
  document.getElementById('rDay').textContent=ctx.dayMaster+'（'+ctx.dmWx+'）';
  document.getElementById('rStrength').innerHTML='身<span class="tag">'+ctx.strength+'（藏干加权）</span>';
  // chips
  let chips=`<span class="chip">格局：<b>${ctx.pattern||'杂气/未成格'}</b></span>`;
  if(ctx.specialDetail) chips+=`<span class="chip" style="background:rgba(212,164,69,0.1);border-color:rgba(212,164,69,0.3);">特殊格局：<b style="color:#d4a445;">${ctx.specialDetail}</b></span>`;
  chips+=`<span class="chip">喜用：<b>${ctx.xiYong.join('、')||'—'}</b></span>`;
  if(ctx.special.tiaohou && ctx.special.tiaohouEls.length) chips+=`<span class="chip" style="background:rgba(77,168,124,0.1);border-color:rgba(77,168,124,0.3);">调候用神：<b style="color:#5dbe8a;">${ctx.special.tiaohouEls.join('、')}</b></span>`;
  if(ctx.special.bingyao) chips+=`<span class="chip" style="background:rgba(224,85,85,0.1);border-color:rgba(224,85,85,0.3);">病药：<b style="color:#e05555;">病在${ctx.special.bingyao.bing}</b>·<b style="color:#4da87c;">药取${ctx.special.bingyao.yao.filter((v,i,a)=>a.indexOf(v)===i).join('、')}</b></span>`;
  chips+=`<span class="chip">年柱纳音：<b>${ctx.naYinYear}</b></span>`;
  chips+=`<span class="chip">生肖：<b>${SHENGX[ZHI.indexOf(ctx.pillars[0][1])]}</b></span>`;
  document.getElementById('rChips').innerHTML=chips;
  // 真太阳时 / 时辰模式提示
  let solarHtml='';
  if(ctx.shichenMode){
    solarHtml='<b>以时辰直接排盘</b>：时辰本身即为真太阳时时段，已跳过夏令时与真太阳时校正。适用于按太阳位置或作息经验估算的出生时间。';
  } else {
  if(ctx.dst) solarHtml+='<b>已自动校正夏令时（−1 小时）</b>：出生日期落在 1986-1991 年中国夏令时窗口内，记录时间已先还原为标准时间再排盘。<br>';
  if(ctx.solarInfo){
    if(ctx.solarInfo.found){
      const t=ctx.solarInfo.time;
      const ts=`${t.getFullYear()}-${String(t.getMonth()+1).padStart(2,'0')}-${String(t.getDate()).padStart(2,'0')} ${String(t.getHours()).padStart(2,'0')}:${String(t.getMinutes()).padStart(2,'0')}`;
      solarHtml+=`已按真太阳时校正：出生地经度约 ${ctx.solarInfo.lon}°E，较北京时间${ctx.solarInfo.diffMin>=0?'早':'晚'} ${Math.abs(ctx.solarInfo.diffMin).toFixed(1)} 分钟。排盘采用校正后时间 ${ts}（北京时间 ${String(ctx.hh).padStart(2,'0')}:${String(ctx.mm).padStart(2,'0')}）。`;
      if(ctx.useH>=23) solarHtml+=' <b>注意：校正后已入晚子时，时柱按次日推算。</b>';
    } else {
      solarHtml+='未匹配到出生城市经度，已用北京时间排盘。县级市/海外地区请填写上一级主要城市（如：湖北省武汉市），或关闭真太阳时校正。';
    }
  } else {
    solarHtml+='未启用真太阳时校正，直接使用北京时间排盘（非 120°E 地区可能存在时辰偏差）。';
  }
  }
  document.getElementById('rSolar').innerHTML=solarHtml;
  // 四柱表（专业命盘：天干地支叠放、日柱高亮）
  const heads=['年柱','月柱','日柱','时柱'];
  let html='<tr><th class="phead">柱</th>'+heads.map(h=>`<th class="phead">${h}</th>`).join('')+'</tr>';
  html+=`<tr><th class="prow">干支</th>${ctx.pillars.map((p,i)=>`<td class="pgz${i===2?' cur':''}"><span class="ptg">${p[0]}</span><span class="pdz">${p[1]}</span></td>`).join('')}</tr>`;
  html+=`<tr><th>十神</th>${ctx.tens.map(t=>`<td><span class="ten">${t}</span></td>`).join('')}</tr>`;
  html+=`<tr><th>纳音</th>${ctx.pillars.map(p=>`<td><span class="ten">${NAYIN[p[0]+p[1]]}</span></td>`).join('')}</tr>`;
  html+=`<tr><th>十二长生</th>${ctx.pillars.map(p=>`<td><span class="ten">${calcChangSheng(ctx.dayMaster,p[1])}</span></td>`).join('')}</tr>`;
  document.getElementById('pillarTable').innerHTML=html;
  // 三式宫位（胎元·命宫·身宫）
  const ty=ctx.taiYuan, mg=ctx.mingGong, sg=ctx.shenGong;
  document.getElementById('threeHouse').innerHTML=`<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:10px"><div style="flex:1;min-width:140px;border:1px solid var(--line);border-radius:10px;padding:10px;text-align:center"><div style="font-size:12px;color:var(--muted)">胎元（先天根基）</div><div style="font-size:18px;font-weight:700;margin:4px 0">${ty}</div><div style="font-size:11px;color:var(--muted)">${NAYIN[ty]}</div></div><div style="flex:1;min-width:140px;border:1px solid var(--gold);border-radius:10px;padding:10px;text-align:center"><div style="font-size:12px;color:var(--muted)">命宫（人生大方向）</div><div style="font-size:18px;font-weight:700;color:var(--gold);margin:4px 0">${mg}</div><div style="font-size:11px;color:var(--muted)">${NAYIN[mg]}</div></div><div style="flex:1;min-width:140px;border:1px solid var(--line);border-radius:10px;padding:10px;text-align:center"><div style="font-size:12px;color:var(--muted)">身宫（后天安身）</div><div style="font-size:18px;font-weight:700;margin:4px 0">${sg}</div><div style="font-size:11px;color:var(--muted)">${NAYIN[sg]}</div></div></div>`;
  // 五行
  document.getElementById('fiveBox').innerHTML=WX_NAMES.map(k=>{
    const cls=k==='木'?'wood':k==='火'?'fire':k==='土'?'earth':k==='金'?'metal':'water';
    const pct=(ctx.five[k]/ctx.sumFive*100).toFixed(0);
    return `<div class="el"><div class="nm w-${cls}">${k}</div><div class="sc w-${cls}">${ctx.five[k].toFixed(1)}</div><div class="ten">${pct}%</div></div>`;
  }).join('');
  // 神煞
  renderShenSha(ctx);
  // 五行补救
  renderRemedy(ctx);
  // 调候用神 & 病药论
  renderTiaohou(ctx);
  // 断语
  const cats=matchRules(ctx);
  const catMap={char:'性格',career:'事业',wealth:'财运',marriage:'婚姻',health:'健康',pattern:'格局',yongshen:'用神喜忌',combo:'十神组合',qinqin:'六亲',edu:'学业',wuxing:'五行生克'};
  Object.keys(catMap).forEach(key=>{
    const rulesHit=cats[catMap[key]]||[];
    let txt;
    if(rulesHit.length){
      // 同文案去重兜底：结论文本相同的规则只渲染一次（防止近似规则同盘重复展示）
      const seen=new Set();
      const uniq=rulesHit.filter(r=>{ const k=r.conclusion.replace(/[\s，。；、：]/g,''); if(seen.has(k)) return false; seen.add(k); return true; });
      txt=uniq.map(r=>`<p>${r.conclusion}${r.suggestion?` <span style="color:var(--muted);font-size:12px">→ ${r.suggestion}</span>`:''}<span class="src">${r.source||''}</span></p>`).join('');
    } else {
      const fallbacks={
        char:`<p>${ctx.dayMaster}日主属${ctx.dmWx}，为人${ctx.dmWx==='木'?'仁厚有担当':ctx.dmWx==='火'?'热情有行动力':ctx.dmWx==='土'?'沉稳守信':ctx.dmWx==='金'?'果决有原则':'智慧善变'}。具体论断需结合全局十神与格局。<span class="src">《滴天髓》</span></p>`,
        yongshen:`<p>喜用神：<b>${ctx.xiYong.join('、')}</b>；忌神：<b>${ctx.jiYong.join('、')}</b>。身${ctx.strength}，需${ctx.strength==='强'?'克泄耗':'生扶'}。<span class="src">综合判定</span></p>`,
        combo:`<p>四柱十神：${ctx.tens.join('、')}。十神组合断语需特定十神同现方可触发。</p>`,
        qinqin:`<p>六亲断语需特定柱位十神组合方可触发，当前命局未匹配到典型六亲特征。</p>`,
        edu:`<p>学业断语需文昌/印星/食伤等特定条件方可触发，当前命局未匹配到典型学业特征。</p>`,
        wuxing:`<p>五行分布：${Object.entries(ctx.five).map(([w,v])=>`${w}${v.toFixed(1)}`).join(' ')}。五行生克断语需特定旺衰组合方可触发。</p>`,
      };
      txt=fallbacks[key]||`<p style="color:var(--muted)">暂无匹配断语，请结合全局分析。</p>`;
    }
    document.getElementById('rc-'+key).innerHTML=txt;
  });
  // 大运
  renderDaYun(ctx);
  // 流年大运下拉
  const sel=document.getElementById('liuDayun');
  sel.innerHTML=ctx.dy.steps.map((gz,k)=>`<option value="${k}">${gz}（${ctx.dy.shun?'顺':'逆'}·约${(ctx.dy.startAge+k*10).toFixed(0)}岁起）</option>`).join('');
  document.getElementById('liuYear').value=new Date().getFullYear();
  document.getElementById('liuMonthYear').value=new Date().getFullYear();
  document.getElementById('liuResult').innerHTML='';
  document.getElementById('liuMonthResult').innerHTML='';
  document.getElementById('liuDayYear').value=new Date().getFullYear();
  document.getElementById('liuDayResult').innerHTML='';
  document.getElementById('liuQinResult').innerHTML='';
  LIU_OPEN=LIU_YUE_OPEN=LIU_DAY_OPEN=LIU_QIN_OPEN=false;
  const btnLiu=document.getElementById('btnLiu'); if(btnLiu) btnLiu.textContent='分析该流年 →';
  const btnLiuYue=document.getElementById('btnLiuYue'); if(btnLiuYue) btnLiuYue.textContent='展开十二流月 →';
  const btnLiuDay=document.getElementById('btnLiuDay'); if(btnLiuDay) btnLiuDay.textContent='展开逐日运势 →';
  const btnLiuQin=document.getElementById('btnLiuQin'); if(btnLiuQin) btnLiuQin.textContent='展开六亲详解 →';
  // 绘制图表
  renderCharts(ctx);
  // 显示
  // 显示
  document.getElementById('formCard').style.display='none';
  document.getElementById('result').classList.remove('hidden');
  document.querySelectorAll('#tabs span').forEach(s=>{
    s.onclick=()=>{
      document.querySelectorAll('#tabs span').forEach(x=>x.classList.remove('on'));
      document.querySelectorAll('.rc').forEach(x=>x.classList.remove('on'));
      s.classList.add('on');
      document.getElementById('rc-'+s.dataset.t).classList.add('on');
    };
  });
}
// [ENGINE:BEGIN]
// 大运规则匹配（dayun_01~20 模板规则：按大运干支与原局关系命中）
function matchDayun(ctx, gz){
  const out=[];
  const tg=gz[0], tz=gz[1];
  const ten=tenGod(tg, ctx.dmWx, ctx.dmYin);
  const tgWx=GAN_WX[tg], tzWx=ZHI_WX[tz];
  const xi=ctx.xiYong||[], ji=ctx.jiYong||[];
  if(xi.includes(tgWx)) out.push(findRule('dayun_01'));
  if(ji.includes(tgWx)) out.push(findRule('dayun_02'));
  if(tz===ctx.pillars[1][1]) out.push(findRule('dayun_03'));
  if(WU_CHONG[tg]===ctx.pillars[2][0] && CHONG[tz]===ctx.pillars[2][1]) out.push(findRule('dayun_04'));
  if(WU_HE[tg]===ctx.pillars[3][0] && LIUHE.some(pr=>pr.includes(tz)&&pr.includes(ctx.pillars[3][1]))) out.push(findRule('dayun_05'));
  if(xi.includes(tgWx)&&xi.includes(tzWx)) out.push(findRule('dayun_06'));
  if(ji.includes(tgWx)&&ji.includes(tzWx)) out.push(findRule('dayun_07'));
  const tianyis=TIANYI[ctx.dayMaster]||[];
  if(tianyis.includes(tz)) out.push(findRule('dayun_08'));
  const ym=[YIMA[ctx.pillars[0][1]],YIMA[ctx.pillars[2][1]]];
  if(ym.includes(tz)) out.push(findRule('dayun_09'));
  const th=[TAOHUA[ctx.pillars[0][1]],TAOHUA[ctx.pillars[2][1]]];
  if(th.includes(tz)) out.push(findRule('dayun_10'));
  const tenRule={'食神':'dayun_12','伤官':'dayun_13','正印':'dayun_14','偏印':'dayun_15','正财':'dayun_16','偏财':'dayun_17','七杀':'dayun_18','正官':'dayun_19','比肩':'dayun_20','劫财':'dayun_20'}[ten];
  if(tenRule) out.push(findRule(tenRule));
  const seen={}; return out.filter(r=>r&&!seen[r.id]&&(seen[r.id]=true));
}
// [ENGINE:END]
function renderDaYun(ctx){
  const dy=ctx.dy;
  let html=`<p style="margin-bottom:12px">${ctx.gender==='男'?'男命':'女命'}年干${ctx.yg[0]}属${yang(ctx.yg[0])?'阳':'阴'}，大运${dy.shun?'顺排':'逆排'}，约 ${dy.startAge.toFixed(1)} 岁起运（起运岁数 = 出生距${dy.shun?'下一个':'上一个'}节的天数 ÷ 3）。</p><div class="dayun">`;
  dy.steps.forEach((gz,k)=>{
    const age=(dy.startAge+k*10);
    html+=`<div class="step"><div class="gz">${gz}</div><div class="age">${age.toFixed(0)}-${(age+10).toFixed(0)}岁</div></div>`;
  });
  html+='</div>';
  // 每步大运规则评语（dayun_01~20）
  html+='<div style="margin-top:14px">';
  let anyRule=false;
  dy.steps.forEach((gz,k)=>{
    const age=(dy.startAge+k*10);
    const ms=matchDayun(ctx, gz);
    if(ms.length){
      anyRule=true;
      html+=`<div style="margin-top:10px;padding:10px 12px;background:rgba(218,165,32,0.05);border-left:3px solid var(--gold3);border-radius:6px"><b style="color:var(--gold)">${gz}（${age.toFixed(0)}-${(age+10).toFixed(0)}岁）</b>${ms.map(r=>fmtRule(r)).join('')}</div>`;
    }
  });
  if(!anyRule) html+=`<p style="color:var(--muted);font-size:13px">各步大运干支与原局未见显著伏吟、天克地冲或贵人驿马主题，走势相对平顺。</p>`;
  html+='</div>';
  // 换运提醒（dayun_11，通用提示）
  const jh=findRule('dayun_11');
  if(jh) html+=`<p style="color:var(--muted);font-size:12px;margin-top:10px">⚠️ ${jh.conclusion}</p>`;
  document.getElementById('rc-dayun').innerHTML=html;
}
function renderShenSha(ctx){
  const ss=ctx.shenSha||[];
  const typeCls={吉:'ssh-j',凶:'ssh-x',中:'ssh-z'};
  const tpCls={吉:'tp-j',凶:'tp-x',中:'tp-z'};
  const label={吉:'吉神',凶:'凶神',中:'中性'};
  if(!ss.length){ document.getElementById('sshBox').innerHTML='<div style="font-size:13px;color:var(--muted)">此命局未现常见神煞。</div>'; return; }
  const byType={吉:[],凶:[],中:[]};
  ss.forEach(s=>byType[s.type].push(s));
  let html='';
  ['吉','凶','中'].forEach(tp=>{
    if(!byType[tp].length) return;
    html+=`<div class="ssh-group"><span class="gt ${tpCls[tp]}">${label[tp]} · ${byType[tp].length}</span><div class="ssh-row">`;
    byType[tp].forEach(s=>{
      html+=`<div class="ssh ${typeCls[tp]}"><div class="nm">${s.name}</div><div class="gt ${tpCls[tp]}">${s.meaning}</div><div class="pos">在 ${s.pos}</div></div>`;
    });
    html+='</div></div>';
  });
  document.getElementById('sshBox').innerHTML=html;
}
const REMEDY_SW={木:'#3da068',火:'#d94a4a',土:'#c89830',金:'#88949c',水:'#4488c0'};
function renderRemedy(ctx){
  const rm=ctx.remedy||{items:[],note:''};
  let html='';
  if(rm.items&&rm.items.length){
    html+='<div class="remedy-grid">';
    rm.items.forEach(it=>{
      html+=`<div class="remedy"><div class="wm"><span class="sw" style="background:${REMEDY_SW[it.wx]}"></span>喜用${it.wx}</div><dl>`;
      html+=`<dt>颜色</dt><dd>${it.color}</dd>`;
      html+=`<dt>方位</dt><dd>${it.dir}</dd>`;
      html+=`<dt>数字</dt><dd>${it.num}</dd>`;
      html+=`<dt>行业</dt><dd>${it.industry}</dd>`;
      html+=`<dt>饰品</dt><dd>${it.jewelry}</dd>`;
      html+=`<dt>饮食</dt><dd>${it.diet}</dd>`;
      html+=`<dt>依据</dt><dd style="color:var(--muted)">${it.basis}</dd>`;
      html+='</dl></div>';
    });
    html+='</div>';
    if(rm.note) html+=`<div class="solar-note">${rm.note}</div>`;
  } else {
    html=`<div style="font-size:13px;color:var(--muted)">${rm.note||'暂无补救建议。'}</div>`;
  }
  document.getElementById('remedyBox').innerHTML=html;
}
function renderTiaohou(ctx){
  const sp=ctx.special; let html='';
  // 调候用神
  if(sp.tiaohou && sp.tiaohouEls.length){
    const seasonNames={春:'春季',夏:'夏季',秋:'秋季',冬:'冬季'};
    const dmNames={甲:'甲木',乙:'乙木',丙:'丙火',丁:'丁火',戊:'戊土',己:'己土',庚:'庚金',辛:'辛金',壬:'壬水',癸:'癸水'};
    const dmFull=dmNames[ctx.dmWx]||ctx.dmWx;
    const seas=seasonNames[sp._season]||'';
    html+=`<div style="margin-bottom:12px"><b>调候用神（《穷通宝鉴》）</b><br><span style="font-size:13px;color:var(--muted)">${dmFull}生于${seas}${ctx.pillars[1][1]}月，需以 <b style="color:var(--gold)">${sp.tiaohouEls.map(w=>`「${w}」`).join('、')}</b> 调候，则命局寒暖燥湿平衡、生机不滞。</span></div>`;
  }
  // 病药理论
  if(sp.bingyao){
    const {bing,yao}=sp.bingyao;
    const uniqYao=[...new Set(yao)];
    html+=`<div><b>病药论（《滴天髓》）</b><br><span style="font-size:13px;color:var(--muted)">命局中<b style="color:var(--red)">${bing}</b>过旺为「病」，宜以 <b style="color:var(--green)">${uniqYao.map(w=>`「${w}」`).join('、')}</b> 为「药」——${uniqYao.map(w=>`${w}${WX_SK[bing]&&WX_SK[bing].被克===w?'制克':'泄秀'}${bing}`).join('、')}，以求中和。岁运逢${uniqYao.join('、')}得力之期，格局趋于平衡。</span></div>`;
  }
  if(!html) html='<div style="font-size:13px;color:var(--muted)">命局五行分布较为平衡，无需特别调候或药治。寒暖燥湿自适，流通有致。</div>';
  document.getElementById('tiaohouBox').innerHTML=html;
}
function backToForm(){
  document.getElementById('result').classList.add('hidden');
  document.getElementById('formCard').style.display='block';
  // 重置展开状态
  LIU_OPEN=LIU_YUE_OPEN=LIU_DAY_OPEN=LIU_QIN_OPEN=false;
  const btnLiu=document.getElementById('btnLiu'); if(btnLiu) btnLiu.textContent='分析该流年 →';
  const btnLiuYue=document.getElementById('btnLiuYue'); if(btnLiuYue) btnLiuYue.textContent='展开十二流月 →';
  const btnLiuDay=document.getElementById('btnLiuDay'); if(btnLiuDay) btnLiuDay.textContent='展开逐日运势 →';
  const btnLiuQin=document.getElementById('btnLiuQin'); if(btnLiuQin) btnLiuQin.textContent='展开六亲详解 →';
  document.getElementById('liuResult').innerHTML='';
  document.getElementById('liuMonthResult').innerHTML='';
  document.getElementById('liuDayResult').innerHTML='';
  document.getElementById('liuQinResult').innerHTML='';
}

// ===== 流年分析 =====
function runLiu(){
  if(!LAST){alert('请先排盘');return;}
  if(LIU_OPEN){document.getElementById('liuResult').innerHTML='';document.getElementById('btnLiu').textContent='分析该流年 →';LIU_OPEN=false;return;}
  const ctx=LAST;
  const ty=+document.getElementById('liuYear').value;
  const di=+document.getElementById('liuDayun').value;
  if(isNaN(ty)||!Number.isInteger(ty)||ty<1900||ty>2100){alert('请输入有效年份（1900-2100）');return;}
  if(isNaN(di)||di<0||di>7){alert('请选择对应大运（0-7）');return;}
  // 流年干支（取该年7月1日，确保过立春）
  const ly=yearGZ(ty,7,1,12,0);
  const lz=ly[1];
  const ltg=ly[0];
  const lTen=tenGod(ltg, ctx.dmWx, ctx.dmYin);
  const lzTen=tenGod(CANG[lz][0][0], ctx.dmWx, ctx.dmYin);
  const out=[];
  // 太岁值年（本命年）
  if(lz===ctx.pillars[0][1]){
    const r=findRule('liunian_太岁值年');
    out.push(`<div class="li">${fmtRule(r)}</div>`);
  }
  out.push(`<div class="li"><b>流年 ${ty} 年：${ly}（${NAYIN[ly]}）</b><br>流年天干 ${ltg} 对日主为 <b>${lTen}</b>，流年地支 ${lz} 本气为 <b>${lzTen}</b>。${liuTenDesc(lTen, ctx)}</div>`);
  // 与原局四柱地支冲合刑害
  const pillarNames=['年柱(祖/早年)','月柱(父/事业)','日柱(自身/婚)','时柱(子/晚运)'];
  let relTxt=[];
  ctx.pillars.forEach((p,i)=>{
    const z=p[1];
    if(CHONG[lz]===z) relTxt.push(`<b>冲${pillarNames[i]}</b>（${lz}冲${z}）`);
    if(LIUHE.some(pr=>pr.includes(lz)&&pr.includes(z))) relTxt.push(`<b>合${pillarNames[i]}</b>（${lz}与${z}六合）`);
    if(XING_PAIRS.some(pr=>(pr[0]===lz&&pr[1]===z)||(pr[0]===z&&pr[1]===lz))) relTxt.push(`<b>刑${pillarNames[i]}</b>（${lz}与${z}相刑）`);
    if(HAI_PAIRS.some(pr=>pr[0]===lz&&pr[1]===z)) relTxt.push(`<b>害${pillarNames[i]}</b>（${lz}害${z}）`);
    // 半合：流年支+该柱支成三合中的两字，且原局无第三字（三合全在下文独立检测）
    SANHE.forEach(g=>{
      if(g.includes(lz)&&g.includes(z)&&lz!==z){
        const third=g.find(x=>x!==lz&&x!==z);
        const allZhi=ctx.pillars.map(p=>p[1]);
        if(!allZhi.includes(third)) relTxt.push(`<b>半合${wxOfSanhe(g)}局</b>（${lz}与${z}半合，缺${third}，力量不及三合全）`);
      }
    });
  });
  // 三合：流年支 + 原局两柱地支成局
  SANHE.forEach(g=>{
    const others=g.filter(x=>x!==lz);
    if(others.every(o=>ctx.pillars.some(p=>p[1]===o)))
      relTxt.push(`<b>三合${wxOfSanhe(g)}局</b>（${g.join('')}全见）`);
  });
  // 天干五合
  ctx.pillars.forEach((p,i)=>{
    if(WU_HE[ltg]===p[0]) relTxt.push(`<b>天干五合</b>（${ltg}合${p[0]}，在${pillarNames[i]}）`);
  });
  if(relTxt.length) out.push(`<div class="li"><b>与原局关系：</b><br>${relTxt.join('；')}。<br>${liuRelDesc(relTxt)}</div>`);
  else out.push(`<div class="li"><b>与原局关系：</b>该流年地支与原局无显著冲合刑害，为相对平稳之年。</div>`);
  // 流年关系 → 断语库匹配
  const liuRules=[];
  ctx.pillars.forEach((p,i)=>{
    if(CHONG[lz]===p[1]){
      if(i===2) liuRules.push(findRule('liunian_太岁冲日'));
      else if(i===1) liuRules.push(findRule('liunian_太岁冲月'));
      else if(i===0) liuRules.push(findRule('liunian_太岁冲年'));
    }
  });
  // 天克地冲日柱
  if(liuRules.some(r=>r&&r.id==='liunian_太岁冲日') && WU_CHONG[ltg]===ctx.pillars[2][0]){
    liuRules.push(findRule('liunian_天克地冲日'));
  }
  // 天合地合
  const hasDiHe=LIUHE.some(pr=>pr.includes(lz)&&pr.includes(ctx.pillars[2][1]));
  if(WU_HE[ltg]===ctx.pillars[2][0] && hasDiHe) liuRules.push(findRule('liunian_流年天合地合'));
  // 半合/三合
  const hasBanHe=SANHE.some(g=>{ const others=g.filter(x=>x!==lz); return ctx.pillars.some(p=>g.includes(p[1])&&p[1]!==lz)&&!others.every(o=>ctx.pillars.some(p=>p[1]===o)); });
  const hasSanHe=SANHE.some(g=>{ const others=g.filter(x=>x!==lz); return others.every(o=>ctx.pillars.some(p=>p[1]===o)); });
  if(hasBanHe) liuRules.push(findRule('liunian_流年半合'));
  if(hasSanHe) liuRules.push(findRule('liunian_流年三合'));
  // 刑害
  if(XING_PAIRS.some(pr=>ctx.pillars.some(p=>(pr[0]===lz&&pr[1]===p[1])||(pr[0]===p[1]&&pr[1]===lz))) || HAI_PAIRS.some(pr=>ctx.pillars.some(p=>(pr[0]===lz&&pr[1]===p[1])||(pr[0]===p[1]&&pr[1]===lz))))
    liuRules.push(findRule('liunian_流年刑害'));
  // 流年十神旺度主题
  if(lTen==='正财'||lTen==='偏财') liuRules.push(findRule('liunian_流年财星旺'));
  if(lTen==='正官'||lTen==='七杀') liuRules.push(findRule('liunian_流年官星旺'));
  if(lTen==='正印'||lTen==='偏印') liuRules.push(findRule('liunian_流年印星旺'));
  if(lTen==='食神'||lTen==='伤官') liuRules.push(findRule('liunian_流年食伤旺'));
  // 流年模板规则（liu_21~30）
  const ssX=ctx.shenSha||[];
  const xiY=ctx.xiYong||[], jiY=ctx.jiYong||[];
  if(xiY.includes(GAN_WX[ltg])&&xiY.includes(ZHI_WX[lz])) liuRules.push(findRule('liu_21'));
  if(jiY.includes(GAN_WX[ltg])&&jiY.includes(ZHI_WX[lz])) liuRules.push(findRule('liu_22'));
  if((lTen==='正财'||lTen==='偏财')&&['辰','戌','丑','未'].includes(lz)) liuRules.push(findRule('liu_23'));
  if((lTen==='正官'||lTen==='七杀')&&(lzTen==='正印'||lzTen==='偏印')) liuRules.push(findRule('liu_24'));
  if(lTen==='劫财'||lzTen==='劫财') liuRules.push(findRule('liu_25'));
  if(ssX.some(s=>s.name==='天德'||s.name==='月德')) liuRules.push(findRule('liu_26'));
  if(XING_PAIRS.some(pr=>(pr[0]===lz&&pr[1]===ctx.pillars[2][1])||(pr[0]===ctx.pillars[2][1]&&pr[1]===lz))) liuRules.push(findRule('liu_27'));
  if(HAI_PAIRS.some(pr=>(pr[0]===lz&&pr[1]===ctx.pillars[2][1])||(pr[0]===ctx.pillars[2][1]&&pr[1]===lz))) liuRules.push(findRule('liu_28'));
  if([JIANGXING[ctx.pillars[0][1]],JIANGXING[ctx.pillars[2][1]]].includes(lz)) liuRules.push(findRule('liu_29'));
  if([HUAGAI[ctx.pillars[0][1]],HUAGAI[ctx.pillars[2][1]]].includes(lz)) liuRules.push(findRule('liu_30'));
  // 喜用神
  const liuIsXiYong=ctx.xiYong.includes(GAN_WX[ltg])||ctx.xiYong.includes(ZHI_WX[lz]);
  if(liuIsXiYong) liuRules.push(findRule('liunian_流年生用神'));
  else liuRules.push(findRule('liunian_流年克用神'));
  // 输出去重
  const seen={}; const unique=liuRules.filter(r=>r&&!seen[r.id]&&(seen[r.id]=true));
  if(unique.length){
    let rhtml='<div class="li"><b>流年古籍断语：</b>';
    unique.forEach(r=>{ rhtml+=fmtRule(r); });
    rhtml+='</div>';
    out.push(rhtml);
  }
  // 流年与大运
  const dyGz=ctx.dy.steps[di];
  const dyRel=[];
  if(CHONG[dyGz[1]]===lz) dyRel.push(`流年地支${lz}冲大运地支${dyGz[1]}`);
  if(LIUHE.some(pr=>pr.includes(lz)&&pr.includes(dyGz[1]))) dyRel.push(`流年${lz}与大运${dyGz[1]}六合`);
  if(WU_HE[ltg]===dyGz[0]) dyRel.push(`流年天干${ltg}合大运天干${dyGz[0]}`);
  // 大运天干十神
  const dyTen=tenGod(dyGz[0], ctx.dmWx, ctx.dmYin);
  out.push(`<div class="li"><b>与大运 ${dyGz} 的关系：</b>${dyRel.length?dyRel.join('；')+'。':'无显著冲合。'}大运天干 ${dyGz[0]} 对日主为 <b>${dyTen}</b>。${liuTenDesc(dyTen, ctx, '大运')}</div>`);
  // 大运→断语
  const dyRuleMap=[];
  // 岁运并临（干支完全相同）由下方 analyzeLiuDeep 统一输出，此处仅处理"天比地冲/天地皆冲"变体，避免重复
  if(ltg===dyGz[0]&&CHONG[lz]===dyGz[1]){ dyRuleMap.push(findRule('liunian_岁运并临_天比地冲')); }
  else if(WU_CHONG[ltg]===dyGz[0]&&CHONG[lz]===dyGz[1]){ dyRuleMap.push(findRule('liunian_岁运并临_天地皆冲')); }
  const dyU=dyRuleMap.filter(Boolean);
  if(dyU.length){ let h=''; dyU.forEach(r=>{ h+=fmtRule(r); }); out.push(`<div class="li">${h}</div>`); }
  // 流年深度规则：岁运并临 / 伏吟 / 反吟
  const deep=analyzeLiuDeep(ctx, ltg, lz, dyGz);
  if(deep.length){
    const cls={binglin:'tp-x',fuyin:'tp-z',fanyin:'tp-x'};
    let html='<div class="li"><b>流年深度规则：</b><br>';
    deep.forEach(r=>{ html+=`<div style="margin-top:6px"><span class="${cls[r.type]}">【${r.title}】</span> ${r.text}</div>`; });
    html+='</div>';
    out.push(html);
  }
  // 空亡判断
  if(ctx.kongWang && ctx.kongWang.includes(lz)){
    const kwNames=['年柱','月柱','日柱','时柱'];
    let kwHit=[];
    ctx.pillars.forEach((p,i)=>{ if(ctx.kongWang.includes(p[1])) kwHit.push(kwNames[i]); });
    let kwTxt=`流年地支 <b>${lz}</b> 为日柱空亡（日柱 ${ctx.dg} 旬空 ${ctx.kongWang.join('、')}）。${kwHit.length?'命局'+kwHit.join('、')+'亦逢空亡，该宫位事项尤需审慎。':''}`;
    if(ctx.xiYong.includes(GAN_WX[ltg])||ctx.xiYong.includes(ZHI_WX[lz])){
      kwTxt+='但此年干支为喜用，空亡之"虚"反有"清空负担、轻装上阵"之意，旧事翻篇即新机。';
    } else {
      kwTxt+='空亡逢非喜用，落空感偏重，重大投资、签约、婚恋等宜多方确认后再定，忌凭一时冲动。';
    }
    out.push(`<div class="li"><span class="tp-z">【空亡】</span> ${kwTxt}</div>`);
    const kwRule=findRule('liunian_流年空亡');
    if(kwRule) out.push(`<div class="li">${fmtRule(kwRule)}</div>`);
  }
  // 流年天喜照
  const ss=ctx.shenSha||[];
  if(ss.some(s=>s.name==='天喜')){ const tr=findRule('liunian_流年天喜照'); if(tr) out.push(`<div class="li">${fmtRule(tr)}</div>`); }
  // 十二长生：日干在流年地支
  const liuCS=calcChangSheng(ctx.dayMaster, lz);
  out.push(`<div class="li"><b>十二长生：</b>日主 ${ctx.dayMaster}(${ctx.dmWx}) 在流年 ${lz} 为 <b>${liuCS}</b>。${csLiuDesc(liuCS)}</div>`);
  out.push(`<div class="li" style="color:var(--muted);font-size:12px">注：流年分析为趋势参考。冲多为变动，合多为融合，具体吉凶须结合喜用神与全局。健康问题请遵医嘱。</div>`);
  document.getElementById('liuResult').innerHTML=out.join('');
  document.getElementById('btnLiu').textContent='收起流年分析 ↑';
  LIU_OPEN=true;
}
// ===== 流月分析 =====
function runLiuYue(){
  if(!LAST){alert('请先排盘');return;}
  if(LIU_YUE_OPEN){document.getElementById('liuMonthResult').innerHTML='';document.getElementById('btnLiuYue').textContent='展开十二流月 →';LIU_YUE_OPEN=false;return;}
  const ctx=LAST;
  const ty=+document.getElementById('liuMonthYear').value;
  if(isNaN(ty)||!Number.isInteger(ty)||ty<1900||ty>2100){alert('请输入有效年份（1900-2100）');return;}
  const monthNames=['正月(寅)','二月(卯)','三月(辰)','四月(巳)','五月(午)','六月(未)','七月(申)','八月(酉)','九月(戌)','十月(亥)','十一月(子)','十二月(丑)'];
  const midDays=[4,5,5,5,6,6,7,8,8,8,7,6];
  const refMs=[2,3,4,5,6,7,8,9,10,11,12,1]; // 每月取参考日的阳历月份
  let out=[`<h3 style="font-size:16px;color:var(--gold);margin-bottom:12px">${ty} 年十二流月分析</h3>`];
  out.push('<table class="month-table"><thead><tr><th>月令</th><th>月柱</th><th>纳音</th><th>十神</th><th>与命局合冲</th><th>月运简述</th></tr></thead><tbody>');
  for(let i=0;i<12;i++){
    const rm=refMs[i], rd=midDays[i];
    const yg=yearGZ(ty,rm,rd,12,0);
    if(!yg){out.push(`<tr><td><b>${monthNames[i]}</b></td><td colspan="5" style="color:var(--muted)">数据不足</td></tr>`);continue;}
    const mgz=monthGZ(ty,rm,rd,12,0,yg[0]);
    if(!mgz){out.push(`<tr><td><b>${monthNames[i]}</b></td><td colspan="5" style="color:var(--muted)">数据不足</td></tr>`);continue;}
    const mg=mgz[0], mz=mgz[1];
    const nayin=NAYIN[mgz]||'';
    const mTen=tenGod(mg,ctx.dmWx,ctx.dmYin);
    let rels=[];
    ctx.pillars.forEach((p,j)=>{
      if(CHONG[mz]===p[1]) rels.push(`冲${['年','月','日','时'][j]}`);
      if(LIUHE.some(pr=>pr.includes(mz)&&pr.includes(p[1]))) rels.push(`合${['年','月','日','时'][j]}`);
    });
    SANHE.forEach(g=>{
      if(g.includes(mz)){
        ctx.pillars.forEach((p,j)=>{
          if(p[1]!==mz&&g.includes(p[1])){
            const need=g.find(x=>x!==mz&&x!==p[1]);
            const allZhi=ctx.pillars.map(p2=>p2[1]);
            if(!allZhi.includes(need)){let nm=wxOfSanhe(g);if(!rels.find(r=>r.indexOf('半合')>=0))rels.push('半合'+nm);}
          }
        });
      }
    });
    const brief=getMonthBrief(mgz,mTen,ctx);
    const mr=matchLiuYue(ctx, mgz, mTen, rels);
    let briefHtml=brief;
    if(mr.length) briefHtml+=`<div style="margin-top:4px;font-size:12px;color:var(--muted)">${mr.map(r=>r.conclusion).join('<br>')}</div>`;
    out.push(`<tr><td><b>${monthNames[i]}</b></td><td><span class="mz">${mgz}</span></td><td style="color:var(--muted)">${nayin}</td><td>${mTen}</td><td>${rels.length?rels.join(' ') : '—'}</td><td>${briefHtml}</td></tr>`);
  }
  out.push('</tbody></table>');
  out.push('<div style="color:var(--muted);font-size:12px;margin-top:10px">注：流月分析基于月柱与命局关系，结合调候用神给出趋势参考。吉凶须结合大运流年综合判断。</div>');
  document.getElementById('liuMonthResult').innerHTML=out.join('');
  document.getElementById('btnLiuYue').textContent='收起十二流月 ↑';
  LIU_YUE_OPEN=true;
}
// ===== 流日分析（单月逐日 30 天）=====
function runLiuDay(){
  if(!LAST){alert('请先排盘');return;}
  if(LIU_DAY_OPEN){document.getElementById('liuDayResult').innerHTML='';document.getElementById('btnLiuDay').textContent='展开逐日运势 →';LIU_DAY_OPEN=false;return;}
  const ctx=LAST;
  const ty=+document.getElementById('liuDayYear').value;
  const tm=+document.getElementById('liuDayMonth').value;
  if(isNaN(ty)||!Number.isInteger(ty)||ty<1900||ty>2100){alert('请输入有效年份（1900-2100）');return;}
  if(isNaN(tm)||tm<1||tm>12){alert('请选择有效月份（1-12）');return;}
  const days=new Date(ty,tm,0).getDate(); // 该月实际天数（自动处理大小月/闰年）
  const monthNames=['正月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月'];
  const weekNames=['日','一','二','三','四','五','六'];
  const pn=['年','月','日','时'];
  const tenTxt={'正官':'利职名','七杀':'压力机遇','正财':'利正财','偏财':'利偏财','正印':'利贵人','偏印':'利钻研','食神':'利表达','伤官':'创新思','比肩':'合作助','劫财':'防耗财'};
  const xi=ctx.xiYong||[], ji=ctx.jiYong||[];
  let hotDays=[], relDays=[];
  let out=[`<h3 style="font-size:16px;color:var(--gold);margin-bottom:12px">${ty} 年${monthNames[tm-1]}（${ty}-${String(tm).padStart(2,'0')}）逐日分析 · ${days} 天</h3>`];
  out.push('<div class="ld-legend"><span class="ml-good">● 喜用</span><span class="ml-warn">● 忌神/空亡</span><span class="ld-hot">● 冲合日柱（关键日）</span><span class="ml-neu">● 中和</span></div>');
  out.push('<table class="month-table ld-table"><thead><tr><th>日期</th><th>日柱</th><th>纳音</th><th>十神</th><th>与命局关系</th><th>当日简评</th></tr></thead><tbody>');
  for(let d=1; d<=days; d++){
    const gz=dayGZ(ty,tm,d);
    const g=gz[0], z=gz[1];
    const ten=tenGod(g, ctx.dmWx, ctx.dmYin);
    const nayin=NAYIN[gz]||'';
    const week=weekNames[new Date(ty,tm-1,d).getDay()];
    // 与命局四柱地支冲合刑害
    const rels=[];
    ctx.pillars.forEach((p,j)=>{
      if(CHONG[z]===p[1]) rels.push(`<b class="ld-hot">冲${pn[j]}</b>`);
      if(LIUHE.some(pr=>pr.includes(z)&&pr.includes(p[1]))) rels.push(`<b class="ld-he">合${pn[j]}</b>`);
      if(XING_PAIRS.some(pr=>(pr[0]===z&&pr[1]===p[1])||(pr[0]===p[1]&&pr[1]===z))) rels.push(`刑${pn[j]}`);
      if(HAI_PAIRS.some(pr=>pr[0]===z&&pr[1]===p[1])) rels.push(`害${pn[j]}`);
    });
    // 半合（流日支 + 原局一支成半合）
    SANHE.forEach(sg=>{
      if(sg.includes(z)){
        ctx.pillars.forEach((p,j)=>{
          if(p[1]!==z&&sg.includes(p[1])){
            const need=sg.find(x=>x!==z&&x!==p[1]);
            if(!ctx.pillars.some(p2=>p2[1]===need)){
              const nm=wxOfSanhe(sg);
              if(!rels.find(r=>r.indexOf('半合')>=0)) rels.push(`半合${nm}`);
            }
          }
        });
      }
    });
    // 天干五合
    if(WU_HE[g]===ctx.pillars[2][0]) rels.push(`天干合日`);
    // 空亡
    const kong=(ctx.kongWang||[]).includes(z);
    // 喜忌
    const isXi=xi.includes(GAN_WX[g])||xi.includes(ZHI_WX[z]);
    const isJi=ji.includes(GAN_WX[g])||ji.includes(ZHI_WX[z]);
    // 十二长生
    const cs=calcChangSheng(ctx.dayMaster, z);
    // 简评
    let brief=[];
    if(isXi) brief.push('<span class="ml-good">喜用当值</span>');
    else if(isJi) brief.push('<span class="ml-warn">忌神当值</span>');
    else brief.push('<span class="ml-neu">中和</span>');
    if(tenTxt[ten]) brief.push(tenTxt[ten]);
    if(kong) brief.push('<span class="ml-warn">逢空亡</span>');
    if(cs) brief.push('<span class="ml-neu">'+cs+'</span>');
    // 断语匹配
    const mrs=matchLiuDay(ctx, g, z, ten, rels, kong, isXi, isJi);
    if(mrs.length) brief.push('<span class="ml-neu ld-rule">'+mrs.map(r=>r.conclusion.replace(/[，。].*$/,'')).join(' / ')+'</span>');
    // 关键日标记
    const hitRi=rels.some(r=>r.indexOf('冲日')>=0||r.indexOf('合日')>=0||r.indexOf('天干合日')>=0);
    if(hitRi){ hotDays.push(d); relDays.push(`${d}日${rels.filter(r=>r.indexOf('冲日')>=0||r.indexOf('合日')>=0||r.indexOf('天干合日')>=0).join('、')}`); }
    out.push(`<tr${hitRi?' class="ld-hot-row"':''}><td><b>${d}</b><br><span class="ml-neu" style="font-size:11px">周${week}</span></td><td><span class="mz">${gz}</span></td><td style="color:var(--muted);font-size:12px">${nayin}</td><td>${ten}</td><td style="font-size:12px">${rels.length?rels.slice(0,3).join(' '):'—'}</td><td style="text-align:left;font-size:12px">${brief.slice(0,3).join(' ')}</td></tr>`);
  }
  out.push('</tbody></table>');
  // 本月关键日小结
  if(hotDays.length){
    out.push(`<div class="li" style="margin-top:10px"><b>本月关键日：</b>${relDays.join('；')}。冲日柱之日宜静守，合日柱之日宜社交谈合作。</div>`);
  } else {
    out.push(`<div class="li" style="margin-top:10px"><b>本月关键日：</b>本月无冲合日柱的显著引动之日，整体节奏平稳，可关注上方喜用/忌神标记逐日安排。</div>`);
  }
  out.push('<div style="color:var(--muted);font-size:12px;margin-top:10px">注：流日分析为逐日趋势参考，冲合并见时以具体事项为准。重要签约、手术、考试等重大事项，建议优先选喜用当值、无冲克之日。吉凶须结合流年流月综合判断。</div>');
  document.getElementById('liuDayResult').innerHTML=out.join('');
  document.getElementById('btnLiuDay').textContent='收起逐日运势 ↑';
  LIU_DAY_OPEN=true;
}
// [ENGINE:BEGIN]
// 流日规则匹配 v2（liuri_01~05 基础 + 批次1 细分：十神/六冲/六合/三合/五合/十二长生/天克地冲/伏吟）
function matchLiuDay(ctx, g, z, ten, rels, kong, isXi, isJi){
  const out=[];
  const ri=ctx.pillars[2], zi=ri[1], riGan=ri[0];
  const GAN_ORDER=['甲','乙','丙','丁','戊','己','庚','辛','壬','癸'];
  // 1) 基础五条（通用骨架，保留）
  if(CHONG[z]===zi) out.push(findRule('liuri_01'));
  if(LIUHE.some(pr=>pr.includes(z)&&pr.includes(zi))) out.push(findRule('liuri_02'));
  if(kong) out.push(findRule('liuri_03'));
  if(isXi) out.push(findRule('liuri_04'));
  if(isJi) out.push(findRule('liuri_05'));
  // 2) 十神日（A组：流日天干对日主的十神）
  if(ten) out.push(findRule('liuri_ten_'+ten));
  // 3) 六冲细分（B组：具体冲对）
  if(CHONG[z]===zi){
    const key=[z,zi].sort((a,b)=>ZHI.indexOf(a)-ZHI.indexOf(b)).join('');
    out.push(findRule('liuri_chong_'+key));
  }
  // 4) 六合细分（C组：具体合对，按 LIUHE 规范顺序）
  const hePair=LIUHE.find(pr=>pr.includes(z)&&pr.includes(zi));
  if(hePair) out.push(findRule('liuri_he_'+hePair[0]+hePair[1]));
  // 5) 三合局（D组：流日支与原局两支成三合）
  const sg=SANHE.find(s=>s.includes(z)&&ctx.pillars.filter(p=>p[1]!==z&&s.includes(p[1])).length>=2);
  if(sg) out.push(findRule('liuri_sanhe_'+wxOfSanhe(sg)+'局'));
  // 6) 天干五合（E组：流日干与日干五合）
  if(WU_HE[g]===riGan){
    const key=[g,riGan].sort((a,b)=>GAN_ORDER.indexOf(a)-GAN_ORDER.indexOf(b)).join('');
    out.push(findRule('liuri_wuhe_'+key));
  }
  // 7) 十二长生（F组：流日支对日主的状态）
  const cs=calcChangSheng(ctx.dayMaster, z);
  if(cs) out.push(findRule('liuri_cs_'+cs));
  // 8) 天克地冲（G组：流日干支与日柱干支同冲同克）
  if(CHONG[z]===zi && GAN_WX[g]===WX_SK[GAN_WX[riGan]].克) out.push(findRule('liuri_tkdc'));
  // 9) 伏吟（H组：流日支与日支相同）
  if(z===zi) out.push(findRule('liuri_fuyin'));
  const seen={}; return out.filter(r=>r&&!seen[r.id]&&(seen[r.id]=true));
}
// [ENGINE:END]
// ===== 六亲详解（父母/配偶/子女/兄弟）=====
function runLiuQin(){
  if(!LAST){alert('请先排盘');return;}
  if(LIU_QIN_OPEN){document.getElementById('liuQinResult').innerHTML='';document.getElementById('btnLiuQin').textContent='展开六亲详解 →';LIU_QIN_OPEN=false;return;}
  const ctx=LAST;
  const pn=['年柱','月柱','日柱','时柱'];
  const p=ctx.pillars;
  const male=ctx.gender==='男';
  const xi=ctx.xiYong||[], ji=ctx.jiYong||[];
  const kong=ctx.kongWang||[];
  const st=ctx.strength||'中和';
  const zhiTg=p.map(pp=>CANG[pp[1]][0][0]);
  const tenG=ctx.tens, tenZ=zhiTg.map(g=>tenGod(g,ctx.dmWx,ctx.dmYin));
  const cnt={}; [...tenG,...tenZ].forEach(t=>cnt[t]=(cnt[t]||0)+1);
  const n=t=>cnt[t]||0, nG=t=>tenG.filter(x=>x===t).length;
  const posG=t=>{const i=tenG.indexOf(t);return i>=0?pn[i]:null;};
  const posZ=t=>{const i=tenZ.indexOf(t);return i>=0?pn[i]:null;};
  const starTxt=t=>{const a=posG(t)||posZ(t);return a?`<b style="color:var(--ink2)">${t}</b>现于${a}`:`${t}不显`;};
  const gzTxt=i=>`${p[i][0]}${p[i][1]}`;
  const tenTxtI=i=>`天干${tenG[i]} · 地支本气${tenZ[i]}`;
  const chongWith=z=>{const r=[];p.forEach((pp,i)=>{if(CHONG[z]===pp[1]||CHONG[pp[1]]===z) r.push(pn[i]);});return r;};
  const dz=p[2][1], mz=p[1][1], hz=p[3][1];
  // 十神→五行（用于判断是否属喜用）
  const wxOf=t=>{
    if(t==='比肩'||t==='劫财') return ctx.dmWx;
    if(t==='食神'||t==='伤官') return WX_SK[ctx.dmWx].生;
    if(t==='正财'||t==='偏财') return WX_SK[ctx.dmWx].克;
    if(t==='正官'||t==='七杀') return WX_SK[ctx.dmWx].被克;
    if(t==='正印'||t==='偏印') return WX_SK[ctx.dmWx].被生;
    return '';
  };
  const TEN_ALL=['比肩','劫财','食神','伤官','正财','偏财','正官','七杀','正印','偏印'];
  const useTens=new Set(TEN_ALL.filter(t=>xi.includes(wxOf(t))));
  const isUseT=t=>useTens.has(t);
  const ruleHtml=rs=>rs.filter(Boolean).map(r=>`<div class="li" style="margin-top:6px;font-size:12.5px"><b style="color:var(--gold)">【古籍断语】</b>${r.conclusion}（出处：${r.source}）${r.suggestion?`<div style="color:var(--muted);margin-top:2px">→ ${r.suggestion}</div>`:''}</div>`).join('');
  const seen={};
  const pushRules=(arr,ids)=>ids.forEach(id=>{const r=findRule(id);if(r&&!seen[r.id]){seen[r.id]=true;arr.push(r);}});
  const sec=(t,meta,stars,rules,extra)=>`<div class="qin-sec"><div class="qin-hd">${t}</div><div class="qin-meta">${meta}</div>${stars?`<div class="qin-star">${stars}</div>`:''}${rules?ruleHtml(rules):''}${extra||''}</div>`;

  let out=[];
  out.push('<h3 style="font-size:16px;color:var(--gold);margin-bottom:10px">六亲详解 · 宫位为体、十神为用</h3>');
  out.push(`<div style="color:var(--muted);font-size:12px;margin-bottom:12px">${male?'男命':'女命'} · 身${st}${xi.length?' · 喜用五行：'+xi.join('、'):''}${kong.length?' · 空亡：'+kong.join('、'):''}</div>`);

  // ① 父母（年柱祖上 + 月柱父母宫）
  const pRules=[];
  if(n('正印')+n('偏印')>=1 && st==='弱') pushRules(pRules,['kin_parent_yin']);
  if(n('正财')+n('偏财')>=2) pushRules(pRules,['kin_parent_cai']);
  if(n('偏财')>=2) pushRules(pRules,['kin_六亲_财旺父远']);
  if(nG('偏财')&&st==='弱') pushRules(pRules,['kin_父缘_偏财为用']);
  if(nG('正印')&&st==='弱') pushRules(pRules,['kin_母缘_正印为用']);
  if(n('正印')+n('偏印')>=3) pushRules(pRules,['kin_六亲_印旺母强']);
  if(tenG[0]==='比肩'||tenG[0]==='劫财') pushRules(pRules,['qinq_17']);
  if(tenG[0]==='食神'||tenG[0]==='伤官') pushRules(pRules,['qinq_18']);
  if(tenG[0]==='正财'||tenG[0]==='偏财') pushRules(pRules,['qinq_19']);
  if(tenG[1]==='正印'||tenG[1]==='偏印') pushRules(pRules,['qinq_20']);
  if(tenG[1]==='正财'||tenG[1]==='偏财') pushRules(pRules,['qinq_21']);
  if(tenG[1]==='正官'||tenG[1]==='七杀') pushRules(pRules,['qinq_22']);
  const pExtra=[];
  if(kong.includes(p[0][1])) pExtra.push('<div class="qin-note">年支逢空亡，祖上荫庇之力较弱，人生多自立。</div>');
  if(kong.includes(p[1][1])) pExtra.push('<div class="qin-note">月支逢空亡，父母或成长环境助力有限，独立性强。</div>');
  out.push(sec('① 父母 · 祖上与父母宫（年柱/月柱）',
    `年柱 ${gzTxt(0)} · ${tenTxtI(0)} ｜ 月柱 ${gzTxt(1)} · ${tenTxtI(1)}`,
    `${starTxt('偏财')}（父星） ｜ ${starTxt('正印')}（母星）`,
    pRules, pExtra.join('')));

  // ② 配偶（日支配偶宫）
  const sRules=[];
  const dzChong=chongWith(dz).filter(x=>x!=='日柱');
  if(xi.includes(ZHI_WX[dz]) && !dzChong.length) pushRules(sRules,['qinq_27']);
  const sExtra=[];
  if(dzChong.length) sExtra.push(`<div class="qin-note">配偶宫（日支）受${dzChong.join('、')}之冲，婚姻宫动，婚恋中宜多沟通、晚婚或聚少离多反而更稳。</div>`);
  if(kong.includes(dz)) sExtra.push('<div class="qin-note">日支逢空亡，配偶缘或婚姻宫力量偏虚，需用心经营方得圆满。</div>');
  if(dz==='子'||dz==='午'||dz==='卯'||dz==='酉') sExtra.push('<div class="qin-note">日支为四正桃花（子午卯酉），配偶容貌气质佳，亦主自身异性缘旺。</div>');
  const spouseStar=male?'正财':'正官';
  out.push(sec('② 配偶 · 婚姻宫（日支）',
    `日支 ${gzTxt(2)} · ${ctx.dayZhiTG_ten}${ctx.dayZhiTai?'（四正桃花）':''} ｜ 婚姻宫被冲：${dzChong.length?dzChong.join('、'):'无'}`,
    `${starTxt(spouseStar)}（${male?'妻星':'夫星'}） ｜ ${starTxt(male?'偏财':'七杀')}（${male?'偏财（次妻星）':'偏夫星'}）`,
    sRules, sExtra.join('')));

  // ③ 子女（时柱子女宫）
  const cRules=[];
  if(n('食神')+n('伤官')>=3) pushRules(cRules,['kin_child_shi']);
  if(n('正官')+n('七杀')>=3) pushRules(cRules,['kin_child_guan']);
  if(n('七杀')>=2) pushRules(cRules,['kin_六亲_官杀旺子女']);
  if(nG('食神')&&st==='弱') pushRules(cRules,['kin_子女_食神为用']);
  if(nG('伤官')&&st==='弱') pushRules(cRules,['kin_子女_伤官为用']);
  if(tenG[3]==='食神'||tenG[3]==='伤官') pushRules(cRules,['qinq_23']);
  if(tenG[3]==='正印'||tenG[3]==='偏印') pushRules(cRules,['qinq_24']);
  if(tenG[3]==='正财'||tenG[3]==='偏财') pushRules(cRules,['qinq_25']);
  if(tenG[3]==='正官'||tenG[3]==='七杀') pushRules(cRules,['qinq_26']);
  if(kong.includes(hz)) pushRules(cRules,['qinq_30']);
  const childStar=male?'正官七杀（子女星）':'食神伤官（子女星）';
  out.push(sec('③ 子女 · 子女宫（时柱）',
    `时柱 ${gzTxt(3)} · ${tenTxtI(3)} ｜ ${kong.includes(hz)?'时支逢空亡':'时支不空'}`,
    `${childStar}：天干${tenG.filter(t=>t==='正官'||t==='七杀'||t==='食神'||t==='伤官').join('、')||'不显'}`,
    cRules));

  // ④ 兄弟（比劫星 + 月令）
  const bRules=[];
  if(n('比肩')+n('劫财')>=3) pushRules(bRules,['kin_sibling_jie','kin_六亲_比劫多手足']);
  if(nG('比肩')&&st==='弱') pushRules(bRules,['kin_兄弟_比肩得力']);
  if(n('比肩')+n('劫财')>=1&&(nG('比肩')||nG('劫财'))) pushRules(bRules,['qinq_28']);
  const mzChong=chongWith(mz).filter(x=>x!=='月柱');
  if(mzChong.length) pushRules(bRules,['qinq_29']);
  out.push(sec('④ 兄弟 · 比劫星（月令为兄弟宫）',
    `比劫合计 ${n('比肩')+n('劫财')} 见（天干 ${nG('比肩')+nG('劫财')} · 地支本气 ${n('比肩')+n('劫财')-(nG('比肩')+nG('劫财'))}） ｜ 月支${mzChong.length?'受'+mzChong.join('、')+'之冲':'平稳'}`,
    `${starTxt('比肩')} ｜ ${starTxt('劫财')}`,
    bRules));

  // ⑤ 六亲缘神煞
  const gs=ctx.shenSha.filter(s=>s.name==='孤辰'||s.name==='寡宿');
  if(gs.length){
    const gRules=[]; pushRules(gRules,['kin_六亲_孤辰寡宿']);
    out.push(sec('⑤ 六亲缘 · 孤辰寡宿',
      `命中带 ${gs.map(s=>s.name).join('、')}${gs[0].pos?'（现于'+gs[0].pos+'）':''}`,
      '', gRules));
  }

  out.push('<div style="color:var(--muted);font-size:12px;margin-top:10px">注：六亲分析以宫位为体、十神为用，参合喜忌旺衰与神煞。六亲缘厚薄为命理参考，亲情经营重在当下用心。吉凶须结合大运流年综合判断。</div>');
  document.getElementById('liuQinResult').innerHTML=out.join('');
  document.getElementById('btnLiuQin').textContent='收起六亲详解 ↑';
  LIU_QIN_OPEN=true;
}
// 流月规则匹配（liuyue_01~20 模板规则：按流月干支十神与命局关系命中；v2 扩展：12长生/六冲细分/天干五合/特殊）
// [ENGINE:BEGIN]
function matchLiuYue(ctx, mgz, mTen, rels){
  const out=[];
  const mg=mgz[0], mz=mgz[1];
  const xi=ctx.xiYong||[], ji=ctx.jiYong||[];
  if(mTen==='正印'||mTen==='偏印') out.push(findRule('liuyue_01'));
  if(mTen==='正财'||mTen==='偏财') out.push(findRule('liuyue_02'));
  if(mTen==='正官') out.push(findRule('liuyue_03'));
  if(mTen==='食神') out.push(findRule('liuyue_04'));
  if(mTen==='伤官') out.push(findRule('liuyue_05'));
  if(mTen==='比肩'||mTen==='劫财') out.push(findRule('liuyue_06'));
  if(mTen==='七杀') out.push(findRule('liuyue_07'));
  if(mTen==='偏印') out.push(findRule('liuyue_08'));
  if(WU_HE[mg]===ctx.pillars[2][0] && LIUHE.some(pr=>pr.includes(mz)&&pr.includes(ctx.pillars[2][1]))) out.push(findRule('liuyue_09'));
  if(WU_CHONG[mg]===ctx.pillars[2][0] && CHONG[mz]===ctx.pillars[2][1]) out.push(findRule('liuyue_10'));
  if(CHONG[mz]===ctx.pillars[0][1]) out.push(findRule('liuyue_11'));
  if(LIUHE.some(pr=>pr.includes(mz)&&pr.includes(ctx.pillars[3][1]))) out.push(findRule('liuyue_12'));
  if(mz===ctx.pillars[1][1]) out.push(findRule('liuyue_13'));
  const sanHe=SANHE.some(g=>{ const others=g.filter(x=>x!==mz); return others.every(o=>ctx.pillars.some(p=>p[1]===o)); });
  if(sanHe) out.push(findRule('liuyue_14'));
  if(rels.some(r=>r.indexOf('冲')>=0)) out.push(findRule('liuyue_15'));
  if((ctx.kongWang||[]).includes(mz)) out.push(findRule('liuyue_16'));
  if(xi.includes(GAN_WX[mg])) out.push(findRule('liuyue_17'));
  if(ji.includes(GAN_WX[mg])) out.push(findRule('liuyue_18'));
  if([TAOHUA[ctx.pillars[0][1]],TAOHUA[ctx.pillars[2][1]]].includes(mz)) out.push(findRule('liuyue_19'));
  if([YIMA[ctx.pillars[0][1]],YIMA[ctx.pillars[2][1]]].includes(mz)) out.push(findRule('liuyue_20'));
  // v2-A) 十二长生（流月支对日主）
  const cs=calcChangSheng(ctx.dayMaster, mz);
  if(cs) out.push(findRule('liuyue_cs_'+cs));
  // v2-B) 六冲细分（流月支冲日支，按 ZHI 顺序键）
  if(CHONG[mz]===ctx.pillars[2][1]){
    const key=[mz,ctx.pillars[2][1]].sort((a,b)=>ZHI.indexOf(a)-ZHI.indexOf(b)).join('');
    out.push(findRule('liuyue_chong_'+key));
  }
  // v2-C) 天干五合（流月干合日干，按 GAN_ORDER 顺序键）
  const GAN_ORDER=['甲','乙','丙','丁','戊','己','庚','辛','壬','癸'];
  if(WU_HE[mg]===ctx.pillars[2][0]){
    const key=[mg,ctx.pillars[2][0]].sort((a,b)=>GAN_ORDER.indexOf(a)-GAN_ORDER.indexOf(b)).join('');
    out.push(findRule('liuyue_wuhe_'+key));
  }
  // v2-D1) 伏吟（流月支=日支）
  if(mz===ctx.pillars[2][1]) out.push(findRule('liuyue_fuyin_day'));
  // v2-D2) 旺相（流月支为日主旺相之地：同气为旺，当令所生为相）
  const SEASON={'寅':'木','卯':'木','巳':'火','午':'火','申':'金','酉':'金','亥':'水','子':'水','辰':'土','戌':'土','丑':'土','未':'土'};
  const dq=SEASON[mz];
  if(dq && (ctx.dmWx===dq || WX_SK[dq].生===ctx.dmWx)) out.push(findRule('liuyue_wangxiang'));
  const seen={}; return out.filter(r=>r&&!seen[r.id]&&(seen[r.id]=true));
}
function getMonthBrief(mgz,mTen,ctx){
  const mg=mgz[0],mz=mgz[1];
  const mWx=ZHI_WX[mz];
  const isXi=ctx.xiYong.some(wx=>wx===mWx||wx===GAN_WX[mg]);
  const isJi=ctx.jiYong&&ctx.jiYong.some(wx=>wx===mWx||wx===GAN_WX[mg]);
  let parts=[];
  if(isXi) parts.push('<span class="ml-good">喜用当令</span>');
  else if(isJi) parts.push('<span class="ml-warn">忌神当令</span>');
  else parts.push('<span class="ml-neu">中和</span>');
  const m2={'正官':'利职名','七杀':'压力机遇','正财':'利正财','偏财':'利偏财','正印':'利贵人','偏印':'利钻研','食神':'利表达','伤官':'创新思','比肩':'合作助','劫财':'防耗财'};
  if(m2[mTen]) parts.push(m2[mTen]);
  // 调候提示
  const dm=ctx.dayMaster;
  const wxy=ctx.xiYong||[];
  if(['亥','子','丑'].includes(mz)&&wxy.includes('火')) parts.push('寒需暖');
  if(['巳','午','未'].includes(mz)&&wxy.includes('水')) parts.push('炎需润');
  return parts.slice(0,3).join(' ');
}
function wxOfSanhe(g){
  const set=g.join('');
  if(set.indexOf('申子辰')>=0) return '水';
  if(set.indexOf('亥卯未')>=0) return '木';
  if(set.indexOf('寅午戌')>=0) return '火';
  if(set.indexOf('巳酉丑')>=0) return '金';
  return '';
}
function liuTenDesc(ten, ctx, label){
  const m={'正官':'利名望、职务，宜守正','七杀':'有压力亦有权威机遇，宜制化','正财':'利稳定收入、务实求财','偏财':'利投资交际之财，宜把握','正印':'利学习长辈贵人，宜进修','偏印':'利专精冷门，宜深研','食神':'利才艺表达，宜发挥','伤官':'利创意口才，忌傲犯官','比肩':'朋友同辈助，宜合作','劫财':'行动力强但防耗财'};
  let s=m[ten]||'';
  const isXi=ctx.xiYong.includes(GAN_WX_OfTen(ten,ctx));
  s+=(label?'（'+label+'）':'')+(isXi?'——此神为喜用，更利。':'——非喜用，宜守。');
  return s;
}
function GAN_WX_OfTen(ten, ctx){
  // 十神对应五行（相对日主）
  const dm=SHENG[ctx.dmWx];
  const map={'比肩':dm,'劫财':dm,'食神':(dm+1)%5,'伤官':(dm+1)%5,'正财':(dm+2)%5,'偏财':(dm+2)%5,'正官':(dm+3)%5,'七杀':(dm+3)%5,'正印':(dm+4)%5,'偏印':(dm+4)%5};
  return WX_NAMES[map[ten]];
}
function liuRelDesc(arr){
  const hasChong=arr.some(x=>x.indexOf('冲')>=0);
  const hasHe=arr.some(x=>x.indexOf('合')>=0);
  if(hasChong&&hasHe) return '冲合并见，动静交织：既有变动挑战，亦有融合机遇，宜稳中求进。';
  if(hasChong) return '流年冲命宫，主变动、迁移或人际关系波动，宜谨慎应对、避免冲动决策。';
  if(hasHe) return '流年合命宫，主融合、人缘提升或合作机会，宜顺势而为。';
  return '';
}
// 十二长生状态描述（用于流年分析）
function csLiuDesc(cs){
  const m={
    '长生':'生命力迸发，适合开创、学习、起步新项目，万事开头易。',
    '沐浴':'桃花人际活跃，但也易沉迷享乐，注意分寸与烂桃花。',
    '冠带':'稳步上升，形象与人际往来得体，宜社交与展示。',
    '临官':'事业运势强，宜积极进取、担责升职，为"禄"位。',
    '帝旺':'运势顶峰，精力充沛但易刚愎自用，物极必反需留余地。',
    '衰':'由盛转衰，宜保守、整理复盘而非开疆拓土。',
    '病':'状态低迷，健康与精力需关注，减少大动作。',
    '死':'停滞不前，耐心等待转机，顺势休息不为错。',
    '墓':'收藏入库之年，适合沉淀、储蓄、内省，不宜激进。',
    '绝':'新旧交替，旧局已破新局未立，宜清零重启、断舍离。',
    '胎':'孕育新机，暗中酝酿，宜低调筹划不宜张扬。',
    '养':'慢慢成长，需耐心培育，拔苗助长反受其害。'
  };
  return m[cs]||'';
}

// 流年深度规则：岁运并临 / 伏吟 / 反吟（纯函数，便于校验）
function analyzeLiuDeep(ctx, ltg, lz, dyGz){
  const rules=[];
  // 岁运并临：流年干支 == 大运干支
  if(ltg+lz===dyGz){
    const xi=ctx.xiYong.includes(GAN_WX[ltg])||ctx.xiYong.includes(ZHI_WX[lz]);
    rules.push({type:'binglin', title:'岁运并临', text:`流年 ${ltg}${lz} 与大运 ${dyGz} 干支完全相同，岁运力量叠加，该年变动剧烈、印象深刻。古籍云"岁运并临，不死也灾"，但须看喜忌：此干支${xi?'为命局喜用，机遇与好事成倍放大':'为命局忌神，压力剧增、宜谨慎守成'}。无论吉凶，此年重大决定宜三思、减少高风险动作。`});
  }
  // 伏吟 / 反吟：流年 vs 四柱
  const names=['年柱(祖/早年)','月柱(父/事业)','日柱(自身/婚)','时柱(子/晚运)'];
  const palace={0:'应长辈、祖业、早年环境之变化',1:'应父母、事业、同辈之反复',2:'应自身、婚姻、健康，最须重视',3:'应子女、晚运之变动'};
  ctx.pillars.forEach((p,i)=>{
    if(p[0]===ltg && p[1]===lz){
      rules.push({type:'fuyin', title:'伏吟·'+names[i], text:`流年与${names[i]}干支完全相同（${ltg}${lz}），主旧事重提、反复迟滞、故地重游。${palace[i]}。伏吟之年宜稳守复盘，不宜大动干戈。`});
    } else if(WU_CHONG[ltg]===p[0] && CHONG[lz]===p[1]){
      rules.push({type:'fanyin', title:'反吟·'+names[i], text:`流年与${names[i]}天克地冲（${ltg}${lz} 冲 ${p[0]}${p[1]}），主剧烈变动、冲突、分离。${palace[i]}。反吟之年宜柔性化解、避免正面冲撞，健康与关系尤需留意。`});
    }
  });
  return rules;
}
// [ENGINE:END]

// ===== 合婚 =====
function toggleHeTimeMode(s){
  const mode=document.getElementById('hTimeMode'+s).value;
  const hourEl=document.getElementById('hHour'+s);
  const minuteEl=document.getElementById('hMinute'+s);
  const sc=document.getElementById('hShichen'+s);
  if(mode==='exact'){ hourEl.classList.remove('hidden'); minuteEl.classList.remove('hidden'); sc.classList.add('hidden'); }
  else { hourEl.classList.add('hidden'); minuteEl.classList.add('hidden'); sc.classList.remove('hidden'); }
}

function runHe(){
  const a=readHe('A'), b=readHe('B');
  if(!a||!b) return;
  const ctxA=paipan(a.name,a.sex,a.y,a.m,a.d,a.hh,a.mm,a.place,a.truesun);
  ctxA.shichenMode=a.shichenMode;
  const ctxB=paipan(b.name,b.sex,b.y,b.m,b.d,b.hh,b.mm,b.place,b.truesun);
  ctxB.shichenMode=b.shichenMode;
  const rep=analyzeHe(ctxA,ctxB);
  let notes='';
  if(a.shichenMode||b.shichenMode) notes+='<div class="dstnote" style="font-size:12px;color:#5dbe8a;margin-bottom:10px;">一方或双方以时辰排盘，已跳过夏令时与真太阳时校正（时辰本身即为真太阳时时段）。</div>';
  if(a.dst||b.dst) notes+='<div class="dstnote" style="font-size:12px;color:#d4a445;margin-bottom:10px;">已自动校正夏令时（−1 小时）：一方或双方出生日期落在 1986-1991 年夏令时窗口内，记录时间已还原为标准时间。</div>';
  document.getElementById('heResult').innerHTML=notes+rep;
}
function readHe(s){
  const name=document.getElementById('hName'+s).value||('甲乙'[s==='A'?0:1]+'方');
  const sex=document.getElementById('hSex'+s).value;
  let y=+document.getElementById('hYear'+s).value;
  let mVal=document.getElementById('hMonth'+s).value;
  let d=+document.getElementById('hDay'+s).value;
  let m;
  const mode = s==='A'?hCalModeA:hCalModeB;
  if(mode==='lunar'){
    if(!y||!mVal||!d){alert('请填写'+s+'方完整农历生日');return null;}
    const isLeap=mVal.endsWith('l');
    const lm=+mVal.replace('l','');
    const solar=lunarToSolar(y,lm,d,isLeap);
    y=solar.y; m=solar.m; d=solar.d;
  } else {
    m=+mVal;
    if(!y||!m||!d){alert('请填写双方出生日期');return null;}
  }
  const timeMode=document.getElementById('hTimeMode'+s).value;
  const place=(document.getElementById('hPlace'+s).value||'').trim();
  if(!sex){alert('请选择'+(s==='A'?'甲方':'乙方')+'性别（用于排大运顺逆）');return null;}
  if(!y||!m||!d){alert('请填写双方出生日期');return null;}
  let hh=0,mm=0;
  let shichenMode=false;
  if(timeMode==='exact'){
    const hhIn=+document.getElementById('hHour'+s).value;
    const mmIn=+document.getElementById('hMinute'+s).value;
    if(Number.isNaN(hhIn)||Number.isNaN(mmIn)||hhIn<0||hhIn>23||mmIn<0||mmIn>59){alert('请填写双方有效的出生时间（时 0-23，分 0-59）');return null;}
    hh=hhIn; mm=mmIn;
  } else {
    const sc=document.getElementById('hShichen'+s).value;
    if(!sc){alert('请选择双方出生时辰');return null;}
    [hh,mm]=SHI_CHEN_MAP[sc];
    shichenMode=true;
  }
  if(shichenMode){
    return {name,sex,y,m,d,hh,mm,place,truesun:'no',dst:0,shichenMode:true};
  }
  const dst=applyDst(y,m,d,hh);
  return {name,sex,y:dst.y,m:dst.m,d:dst.d,hh:dst.hh,mm,place,truesun:'yes',dst:dst.dst,shichenMode:false};
}
function analyzeHe(A,B){
  const dims=[];
  // 1. 日柱关系（25）
  let sc=0,desc='';
  const dgzA=A.pillars[2], dgzB=B.pillars[2];
  const ghA=dgzA[0], gzA=dgzA[1], ghB=dgzB[0], gzB=dgzB[1];
  // 天干五合
  if(WU_HE[ghA]===ghB){ sc+=10; desc+='日干五合（'+ghA+ghB+'），性格相吸、强烈吸引；'; }
  else {
    const wa=SHENG[A.dmWx], wb=SHENG[B.dmWx];
    if(wa===wb){ sc+=7; desc+='日干比和，同气相求；'; }
    else if((wa+1)%5===wb){ sc+=8; desc+='日干相生（'+A.dmWx+'生'+B.dmWx+'），彼此滋养；'; }
    else if((wb+1)%5===wa){ sc+=8; desc+='日干相生（'+B.dmWx+'生'+A.dmWx+'），彼此滋养；'; }
    else { sc+=3; desc+='日干相克（'+A.dmWx+'克'+B.dmWx+'），需包容；'; }
  }
  // 日支关系
  if(gzA===gzB){ sc+=5; desc+='日支相同，夫妻宫契合；'; }
  else if(LIUHE.some(pr=>pr.includes(gzA)&&pr.includes(gzB))){ sc+=7; desc+='日支六合（'+gzA+gzB+'），生活习惯契合；'; }
  else if(CHONG[gzA]===gzB){ sc+=2; desc+='日支相冲（'+gzA+gzB+'），婚姻宫动，需高度包容；'; }
  else if(XING_PAIRS.some(pr=>(pr[0]===gzA&&pr[1]===gzB)||(pr[0]===gzB&&pr[1]===gzA))){ sc+=3; desc+='日支相刑（'+gzA+gzB+'），潜在摩擦；'; }
  else { sc+=5; desc+='日支无冲合，平稳；'; }
  sc=Math.min(sc,25);
  dims.push({name:'日柱关系',max:25,sc:sc,desc:desc});
  // 2. 五行互补（25）
  let sx=0,sxd='';
  WX_NAMES.forEach(w=>{
    const weakA=A.five[w]<A.avgFive*0.85, weakB=B.five[w]<B.avgFive*0.85;
    const strongA=A.five[w]>A.avgFive*1.15, strongB=B.five[w]>B.avgFive*1.15;
    if(weakA&&strongB){ sx+=5; sxd+=w+'（A弱B旺，B补A）；'; }
    else if(weakB&&strongA){ sx+=5; sxd+=w+'（B弱A旺，A补B）；'; }
    else if(strongA&&strongB){ sx+=1; sxd+=w+'（双旺，易竞争）；'; }
    else if(weakA&&weakB){ sx+=1; sxd+=w+'（双弱，需外补）；'; }
    else { sx+=3; }
  });
  sx=Math.min(sx,25);
  dims.push({name:'五行互补',max:25,sc:sx,desc:sxd||'双方五行分布较为均衡，互补性一般。'});
  // 3. 纳音婚配（10）
  const naA=NAYIN_WX[A.yg], naB=NAYIN_WX[B.yg];
  const nIdx={'木':0,'火':1,'土':2,'金':3,'水':4};
  let ns=0,nd='';
  if(naA===naB){ ns=6; nd='年柱纳音同属'+naA+'，志趣相投但互补性弱；'; }
  else if((nIdx[naA]+1)%5===nIdx[naB]){ ns=10; nd='年柱纳音相生（'+naA+'生'+naB+'），气场和谐；'; }
  else if((nIdx[naB]+1)%5===nIdx[naA]){ ns=10; nd='年柱纳音相生（'+naB+'生'+naA+'），气场和谐；'; }
  else { ns=4; nd='年柱纳音相克（'+naA+'克'+naB+'），气场需调和；'; }
  dims.push({name:'纳音婚配',max:10,sc:ns,desc:nd});
  // 4. 十神配合（15）：男财女官
  let ts=0,td='';
  const aCai=(A.gender==='男')?['正财','偏财']:['正官','七杀'];
  const bCai=(B.gender==='女')?['正官','七杀']:['正财','偏财'];
  const aHas=A.tens.some(t=>aCai.includes(t));
  const bHas=B.tens.some(t=>bCai.includes(t));
  if(aHas&&bHas){ ts=15; td='男命财星有力、女命官星有力，传统佳配；'; }
  else if(aHas||bHas){ ts=9; td='一方财官有力，另一方偏弱，需互补经营；'; }
  else { ts=5; td='双方财官均未显，婚姻更多靠情感经营；'; }
  dims.push({name:'十神配合',max:15,sc:ts,desc:td});
  // 5. 生肖婚配（10）
  const za=ZHI.indexOf(A.pillars[0][1]), zb=ZHI.indexOf(B.pillars[0][1]);
  const sxN=SHENGX[za], sxM=SHENGX[zb];
  let ss=0,sd='';
  if(CHONG[ZHI[za]]===ZHI[zb]){ ss=3; sd='生肖相冲（'+sxN+ZHI[za]+'冲'+sxM+ZHI[zb]+'），民间所谓需注意；'; }
  else if(HAI_PAIRS.some(pr=>(pr[0]===ZHI[za]&&pr[1]===ZHI[zb])||(pr[0]===ZHI[zb]&&pr[1]===ZHI[za]))){ ss=5; sd='生肖相害（'+sxN+'害'+sxM+'），需多沟通；'; }
  else if(LIUHE.some(pr=>pr.includes(ZHI[za])&&pr.includes(ZHI[zb]))){ ss=10; sd='生肖六合（'+sxN+ZHI[za]+'合'+sxM+ZHI[zb]+'），佳配；'; }
  else if(SANHE.some(g=>g.includes(ZHI[za])&&g.includes(ZHI[zb]))){ ss=10; sd='生肖三合（'+sxN+'与'+sxM+'），佳配；'; }
  else { ss=7; sd='生肖无冲合，平顺；'; }
  dims.push({name:'生肖婚配',max:10,sc:ss,desc:sd});
  // 6. 大运同步（10）：当前大运五行是否协调
  let us=5,ud='';
  // 取第一步大运
  const da=A.dy.steps[0], db=B.dy.steps[0];
  // 大运天干十神
  const ta=tenGod(da[0],A.dmWx,A.dmYin), tb=tenGod(db[0],B.dmWx,B.dmYin);
  if((ta==='正财'||ta==='偏财')&&(tb==='正财'||tb==='偏财')){ us=10; ud='双方同走财运，共同目标、齐头并进；'; }
  else if((['正财','偏财'].includes(ta)&&['正印','偏印'].includes(tb))||(['正印','偏印'].includes(ta)&&['正财','偏财'].includes(tb))){ us=9; ud='一方财运一方印运，一赚一持，互补；'; }
  else if((ta==='劫财'&&['正财','偏财'].includes(tb))||(['正财','偏财'].includes(ta)&&tb==='劫财')){ us=4; ud='一方劫财一方财，财务观念易冲突；'; }
  else { us=7; ud='大运特性各异，阶段感受不同属正常；'; }
  dims.push({name:'大运同步',max:10,sc:us,desc:ud});
  // 7. 用神互补（5）：A喜用为B旺
  let ys=0,yd='';
  let hit=0;
  A.xiYong.forEach(w=>{ if(B.five[w]>B.avgFive) hit++; });
  if(A.xiYong.length){ ys=Math.round(hit/A.xiYong.length*5); }
  yd='甲方喜用为['+A.xiYong.join('、')+']，其中'+hit+'项在乙方命局较旺'+(ys>=4?'，互补佳':ys>=2?'，部分互补':'，互补有限')+'。';
  dims.push({name:'用神互补',max:5,sc:ys,desc:yd});

  const total=dims.reduce((s,d)=>s+d.sc,0);
  let grade='';
  if(total>=85) grade='天生佳偶';
  else if(total>=70) grade='良好匹配，适当磨合';
  else if(total>=55) grade='可考虑，需共同努力';
  else if(total>=40) grade='较大挑战，需深度沟通';
  else grade='建议谨慎考虑';

  let html=`<div style="text-align:center;font-size:15px;margin-bottom:6px">${A.name}（${A.dayMasterFull}·${SHENGX[ZHI.indexOf(A.pillars[0][1])]}） × ${B.name}（${B.dayMasterFull}·${SHENGX[ZHI.indexOf(B.pillars[0][1])]}）</div>`;
  html+=`<div class="score-big">${total}<small> / 100</small></div>`;
  html+=`<div style="text-align:center;color:var(--gold);font-weight:700;margin-bottom:14px">综合评级：${grade}</div>`;
  dims.forEach(d=>{
    const pct=Math.round(d.sc/d.max*100);
    html+=`<div class="he-dim"><div class="top"><span>${d.name}</span><span>${d.sc} / ${d.max}</span></div><div class="bar"><i style="width:${pct}%"></i></div><div class="desc">${d.desc}</div></div>`;
  });
  html+=`<div class="note" style="text-align:left;margin-top:14px">💡 关键建议：合婚看互补与经营。日柱/五行互补佳者易和睦；生肖冲害、日支相冲者多靠包容与沟通化解。真正的婚姻质量取决于双方用心经营，八字仅为文化参考。</div>`;
  // 合婚断语匹配
  const heRules=[];
  // 日柱关系
  if(WU_HE[ghA]===ghB && LIUHE.some(pr=>pr.includes(gzA)&&pr.includes(gzB))){
    heRules.push(findRule('hehun_吉象_天地鸳鸯合'));
  } else if(WU_HE[ghA]===ghB||LIUHE.some(pr=>pr.includes(gzA)&&pr.includes(gzB))){
    heRules.push(findRule('hehun_优配_日柱相合'));
  } else if(CHONG[gzA]===gzB){
    heRules.push(findRule('hehun_中等_日支相冲'));
  }
  // 三合
  if(SANHE.some(g=>g.includes(gzA)&&g.includes(gzB)&&gzA!==gzB))
    heRules.push(findRule('hehun_吉象_三合'));
  // 五行互补
  if(sx>=18) heRules.push(findRule('hehun_良配_五行互补'));
  // 纳音
  if((nIdx[naA]+1)%5===nIdx[naB]||(nIdx[naB]+1)%5===nIdx[naA])
    heRules.push(findRule('hehun_良配_纳音相生'));
  // 用神互补
  if(ys>=3) heRules.push(findRule('hehun_良配_用神互助'));
  // 生肖
  if(CHONG[ZHI[za]]===ZHI[zb]) heRules.push(findRule('hehun_中等_生肖相冲'));
  // 总分
  if(total>=85) heRules.push(findRule('hehun_吉象_天地鸳鸯合'));
  else if(total<55) heRules.push(findRule('hehun_注意_忌神重叠'));
  else if(total>=55&&total<70) heRules.push(findRule('hehun_调整_婚配非上'));
  // 合婚细目（he_13~20：日柱纳音/四柱六合/天干合冲/用神互喜）
  const dNA=NAYIN_WX[dgzA], dNB=NAYIN_WX[dgzB];
  if(dNA&&dNB){
    const a=nIdx[dNA], b=nIdx[dNB];
    if(a!==b&&((a+1)%5===b||(b+1)%5===a)) heRules.push(findRule('he_13'));
    else if(a!==b) heRules.push(findRule('he_14'));
  }
  if(LIUHE.some(pr=>pr.includes(A.pillars[1][1])&&pr.includes(B.pillars[1][1]))) heRules.push(findRule('he_15'));
  if(LIUHE.some(pr=>pr.includes(A.pillars[0][1])&&pr.includes(B.pillars[0][1]))) heRules.push(findRule('he_16'));
  if(LIUHE.some(pr=>pr.includes(A.pillars[3][1])&&pr.includes(B.pillars[3][1]))) heRules.push(findRule('he_17'));
  if(WU_HE[ghA]===ghB) heRules.push(findRule('he_18'));
  if(WU_CHONG[ghA]===ghB) heRules.push(findRule('he_19'));
  let h1=0,h2=0;
  A.xiYong.forEach(w=>{ if(B.five[w]>B.avgFive) h1++; });
  B.xiYong.forEach(w=>{ if(A.five[w]>A.avgFive) h2++; });
  if(h1>0&&h2>0) heRules.push(findRule('he_20'));
  // 输出
  const heSeen={}; const heUniq=heRules.filter(r=>r&&!heSeen[r.id]&&(heSeen[r.id]=true));
  if(heUniq.length){
    html+=`<div style="text-align:left;margin-top:14px;padding:12px;background:rgba(218,165,32,0.06);border-radius:8px"><b style="color:var(--gold)">古籍合婚参考：</b>`;
    heUniq.forEach(r=>{ html+=fmtRule(r); });
    html+=`</div>`;
  }
  return html;
}

// ===== 图表可视化 =====
function switchChart(type){
  document.querySelectorAll('.chart-tabs span').forEach(s=>s.classList.remove('on'));
  document.querySelectorAll('.chart-panel').forEach(p=>p.classList.remove('on'));
  const tab=document.querySelector(`.chart-tabs span[onclick*="${type}"]`);
  if(tab) tab.classList.add('on');
  const panel=document.getElementById('chart-'+type);
  if(panel) panel.classList.add('on');
}
function renderCharts(ctx){
  if(!ctx||!ctx.five) return;
  document.getElementById('chart-wxbar').innerHTML=drawWxBar(ctx);
  document.getElementById('chart-balance').innerHTML=drawBalance(ctx);
  document.getElementById('chart-dayunTrend').innerHTML=drawDayunTrend(ctx);
}
function drawWxBar(ctx){
  const w=680,h=300,pad=20,barH=32,gap=10;
  const wx=['木','火','土','金','水'];
  const clr={木:varVal('--wood'),火:varVal('--fire'),土:varVal('--earth'),金:varVal('--metal'),水:varVal('--water')};
  const total=ctx.sumFive||1;
  let svg=`<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg" style="max-width:100%">`;
  svg+=`<text x="${w/2}" y="24" text-anchor="middle" font-size="14" fill="${varVal('--ink')}" font-weight="700">命局五行力量分布</text>`;
  // Scale bar
  const maxVal=Math.max(...wx.map(e=>ctx.five[e]||0),1);
  const barArea={x:90,y:40,w:w-120,h:barH};
  wx.forEach((e,i)=>{
    const v=ctx.five[e]||0;
    const bw=Math.max((v/maxVal)*(w-160),10);
    const y=55+i*(barH+gap);
    svg+=`<text x="82" y="${y+barH-10}" text-anchor="end" font-size="12" fill="${varVal('--muted')}">${e}</text>`;
    svg+=`<rect x="${barArea.x}" y="${y}" width="${bw}" height="${barH}" rx="6" fill="${clr[e]}" opacity="0.85"/>`;
    svg+=`<text x="${barArea.x+bw+6}" y="${y+barH-10}" font-size="12" fill="${varVal('--ink')}">${v.toFixed(1)}（${(v/total*100).toFixed(0)}%）</text>`;
    // 标记喜用/忌神
    const isXi=ctx.xiYong.includes(e), isJi=ctx.jiYong&&ctx.jiYong.includes(e);
    if(isXi) svg+=`<text x="${barArea.x+bw+70}" y="${y+barH-10}" font-size="10" fill="${varVal('--green')}">▲喜用</text>`;
    if(isJi) svg+=`<text x="${barArea.x+bw+70}" y="${y+barH-10}" font-size="10" fill="${varVal('--red')}">▼忌神</text>`;
  });
  // 帮扶/克泄耗 ratio
  const r=ctx.ratio||(ctx.support/(ctx.support+ctx.drain)||0);
  const botY=55+(barH+gap)*5+10;
  svg+=`<line x1="20" y1="${botY}" x2="${w-20}" y2="${botY}" stroke="${varVal('--line')}" stroke-width="1"/>`;
  svg+=`<text x="20" y="${botY+18}" font-size="12" fill="${varVal('--muted')}">帮扶（比劫+印）<tspan fill="${varVal('--green')}" font-weight="700">${ctx.support?ctx.support.toFixed(1):0}</tspan> | 克泄耗（食伤+财+官杀）<tspan fill="${varVal('--red')}" font-weight="700">${ctx.drain?ctx.drain.toFixed(1):0}</tspan>  |  比值 <tspan font-weight="700">${r.toFixed(2)}</tspan> → ${ctx.strength||'—'}</text>`;
  svg+=`</svg>`;
  return svg;
}
function drawBalance(ctx){
  const w=680,h=200;
  const r=ctx.ratio||0.5;
  const lstren=ctx.strength||'中和';
  let desc='';
  if(lstren==='强') desc='日主偏强，喜克泄耗（食伤/财/官杀）来平衡';
  else if(lstren==='弱') desc='日主偏弱，喜帮扶（比劫/印）来扶持';
  else desc='日主中和，五行流通较好，取最弱处微调';
  let clr='';
  if(lstren==='强') clr=varVal('--red');
  else if(lstren==='弱') clr=varVal('--water');
  else clr=varVal('--green');
  const cx=240,cy=120,rOuter=70,rInner=35;
  let svg=`<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg" style="max-width:100%">`;
  // Title
  svg+=`<text x="${w/2}" y="24" text-anchor="middle" font-size="14" fill="${varVal('--ink')}" font-weight="700">身强身弱平衡</text>`;
  // Gauge
  svg+=`<circle cx="${cx}" cy="${cy}" r="${rOuter}" fill="none" stroke="${varVal('--line')}" stroke-width="12"/>`;
  // Support arc (right side = 帮扶)
  const angle=r*Math.PI*2;
  const sx=cx+rOuter, sy=cy;
  const ex=cx+rOuter*Math.cos(angle), ey=cy-rOuter*Math.sin(angle);
  const large=angle>Math.PI?1:0;
  svg+=`<circle cx="${cx}" cy="${cy}" r="${rOuter}" fill="none" stroke="${varVal('--green')}" stroke-width="12" stroke-dasharray="${(r*2*Math.PI*rOuter).toFixed(0)} ${((1-r)*2*Math.PI*rOuter).toFixed(0)}" stroke-dashoffset="${(0.25*2*Math.PI*rOuter).toFixed(0)}" stroke-linecap="round"/>`;
  // Drain arc
  svg+=`<circle cx="${cx}" cy="${cy}" r="${rOuter}" fill="none" stroke="${varVal('--red')}" stroke-width="12" stroke-dasharray="${((1-r)*2*Math.PI*rOuter).toFixed(0)} ${(r*2*Math.PI*rOuter).toFixed(0)}" stroke-dashoffset="${((1-r)*2*Math.PI*rOuter*0).toFixed(0)}" stroke-linecap="round" transform="rotate(${(r*360).toFixed(0)} ${cx} ${cy})"/>`;
  // Inner text
  svg+=`<text x="${cx}" y="${cy-10}" text-anchor="middle" font-size="28" font-weight="800" fill="${clr}">${lstren}</text>`;
  svg+=`<text x="${cx}" y="${cy+14}" text-anchor="middle" font-size="11" fill="${varVal('--muted')}">帮扶比 ${(r*100).toFixed(0)}%</text>`;
  // Legend & desc
  svg+=`<text x="${cx}" y="${cy+rOuter+28}" text-anchor="middle" font-size="12" fill="${varVal('--muted')}">${desc}</text>`;
  // Right side info
  const ix=cx+rOuter+40;
  svg+=`<text x="${ix}" y="70" font-size="13" fill="${varVal('--ink')}"><tspan font-weight="700">喜用神：</tspan><tspan fill="${clr}">${(ctx.xiYong||[]).join('、')||'—'}</tspan></text>`;
  svg+=`<text x="${ix}" y="92" font-size="13" fill="${varVal('--ink')}"><tspan font-weight="700">忌神：</tspan>${(ctx.jiYong||[]).join('、')||'—'}</text>`;
  svg+=`<text x="${ix}" y="114" font-size="13" fill="${varVal('--ink')}"><tspan font-weight="700">格局：</tspan>${ctx.pattern||'—'}</text>`;
  svg+=`<text x="${ix}" y="136" font-size="13" fill="${varVal('--ink')}"><tspan font-weight="700">调候：</tspan>${((ctx.special&&ctx.special.tiaohouEls)||[]).join('、')||'—'}</text>`;
  svg+=`</svg>`;
  return svg;
}
function drawDayunTrend(ctx){
  const w=680,h=260,padL=45,padR=20,padT=30,padB=40;
  const wx=['木','火','土','金','水'];
  const clr={木:varVal('--wood'),火:varVal('--fire'),土:varVal('--earth'),金:varVal('--metal'),水:varVal('--water')};
  const steps=ctx.dy.steps;
  const n=steps.length;
  const chartW=w-padL-padR,chartH=h-padT-padB;
  const xStep=chartW/(n-1||1);
  // Calculate 大运 influence scores: each 大运 step adds stem+branch elements
  let series={木:[],火:[],土:[],金:[],水:[]};
  let maxV=0,minV=100;
  steps.forEach((gz,i)=>{
    const g=gz[0],z=gz[1];
    const base=ctx.five||{木:1,火:1,土:1,金:1,水:1};
    let add={木:0,火:0,土:0,金:0,水:0};
    // Stem contribution
    const gw=GAN_WX[g]; if(gw) add[gw]=(add[gw]||0)+3;
    // Branch hidden stems contribution
    (CANG[z]||[]).forEach(([cg,cw])=>{add[GAN_WX[cg]]=(add[GAN_WX[cg]]||0)+cw*2;});
    wx.forEach(ee=>{
      const v=(base[ee]||0)+add[ee];
      series[ee].push(v);
      maxV=Math.max(maxV,v);
    });
  });
  maxV=Math.ceil(maxV/2)*2;
  let svg=`<svg viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg" style="max-width:100%">`;
  svg+=`<text x="${w/2}" y="20" text-anchor="middle" font-size="14" fill="${varVal('--ink')}" font-weight="700">大运五行趋势</text>`;
  // Y axis labels
  for(let i=0;i<=4;i++){
    const y=padT+(chartH/4)*i, val=(maxV*(4-i)/4).toFixed(0);
    svg+=`<text x="${padL-6}" y="${y+4}" text-anchor="end" font-size="10" fill="${varVal('--muted')}">${val}</text>`;
    if(i>0) svg+=`<line x1="${padL}" y1="${y}" x2="${w-padR}" y2="${y}" stroke="${varVal('--line')}" stroke-width="0.5" stroke-dasharray="4,4"/>`;
  }
  // X axis labels
  steps.forEach((gz,i)=>{
    const x=padL+xStep*i;
    svg+=`<text x="${x}" y="${h-padB+16}" text-anchor="middle" font-size="10" fill="${varVal('--muted')}">${gz}<tspan x="${x}" dy="12">${(ctx.dy.startAge+i*10).toFixed(0)}y</tspan></text>`;
    // 标记喜用
    const g=gz[0],z=gz[1];
    const gw=GAN_WX[g];
    if(ctx.xiYong.includes(gw)) svg+=`<text x="${x}" y="${h-padB+42}" text-anchor="middle" font-size="9" fill="${varVal('--green')}">喜</text>`;
    else if(ctx.jiYong&&ctx.jiYong.includes(gw)) svg+=`<text x="${x}" y="${h-padB+42}" text-anchor="middle" font-size="9" fill="${varVal('--red')}">忌</text>`;
  });
  // Lines
  wx.forEach(ee=>{
    let d='';
    series[ee].forEach((v,i)=>{
      const x=padL+xStep*i, y=padT+chartH*(1-v/maxV);
      d+=(i===0?'M':'L')+`${x.toFixed(0)},${y.toFixed(0)} `;
    });
    svg+=`<path d="${d}" fill="none" stroke="${clr[ee]}" stroke-width="2" opacity="0.8"/>`;
    // Dots
    series[ee].forEach((v,i)=>{
      const x=padL+xStep*i, y=padT+chartH*(1-v/maxV);
      svg+=`<circle cx="${x.toFixed(0)}" cy="${y.toFixed(0)}" r="3" fill="${clr[ee]}"/>`;
    });
  });
  // Legend
  wx.forEach((ee,i)=>{
    svg+=`<rect x="${padL+i*55}" y="${12}" width="10" height="10" rx="2" fill="${clr[ee]}"/>`;
    svg+=`<text x="${padL+i*55+14}" y="${22}" font-size="10" fill="${varVal('--muted')}">${ee}</text>`;
  });
  svg+=`<text x="${w-padR}" y="22" text-anchor="end" font-size="10" fill="${varVal('--muted')}">曲线=各五行力量变化；下方"喜/忌"=大运干支属喜用/忌神</text>`;
  svg+=`</svg>`;
  return svg;
}
function varVal(k){
  return getComputedStyle(document.documentElement).getPropertyValue(k).trim();
}

</script>
</body>
</html>"""

html = TPL.replace("__JIEQI__", json.dumps(jieqi, ensure_ascii=False)).replace(
    "__RULES__", json.dumps(rules, ensure_ascii=False)
)
with open(ROOT + r"\ui\index.html", "w", encoding="utf-8") as f:
    f.write(html)
print(
    "index.html built, size=%dKB, jieqi years=%d, rules=%d"
    % (len(html) // 1024, len(jieqi["data"]), len(rules))
)

# ===== 抽取引擎层，生成独立可复用库 engine/engine.dist.js =====
# 引擎代码由 TPL 中的 [ENGINE:BEGIN]/[ENGINE:END] 标记对界定（纯计算、无 DOM 依赖），
# 与 ui/index.html 同源同步，供 C 端（bazi-app）及第三方直接复用。
import re

regions = re.findall(r"// \[ENGINE:BEGIN\]\n(.*?)\n?// \[ENGINE:END\]", html, re.S)
if len(regions) != 7:
    raise SystemExit("引擎标记区段数异常：期望 7，实际 %d" % len(regions))
engine_js = "\n\n".join(r.rstrip() for r in regions)

EXPORTS = """paipan, dayGZ, yearGZ, monthGZ, hourGZ, tenGod, computeFive, getDaYun, getPattern,
calcTaiYuan, calcMingGong, calcShenGong, calcKongWang, calcChangSheng, calcShenSha, getRemedy,
solarCorrection, matchRules, evalState, yongShenChong, findRule, matchDayun, matchLiuDay, matchLiuYue,
analyzeLiuDeep, applyDst, dstOffset, getMonthBrief, wxOfSanhe, liuTenDesc, GAN_WX_OfTen, liuRelDesc,
csLiuDesc, num, yang, parseItem, z, gv, ge, posOfToken,
JIEQI, RULES, GAN, ZHI, GAN_WX, ZHI_WX, WUHU, WUSHU, JIE_ZHI, JIE_ORDER, WX_NAMES, SHENG, CANG,
SHENGX, CHONG, LIUHE, SANHE, XING_PAIRS, HAI_PAIRS, WU_HE, WU_CHONG, NAYIN, NAYIN_WX, CS_NAME,
CS_BASE, CITY_LON, PATTERN_NAME, REMEDY, SHENSHA, WX_SK, SHI_CHEN_MAP, DST_WINDOWS, TIANYI, WENCHANG,
LUSHEN, XUETANG, JINYU, YIMA, TAOHUA, HUAGAI, HONGLUAN, JIANGXING, TIANDE, YUEDE, LONGDE, YANGBLADE,
JIESHA, WANGSHEN, ZAISHA, GUCHEN, GUASU, SUIPO, XUEREN, LIUXIA,
LUNAR_INFO, LUNAR_MONTH_NAMES, leapMonth, leapDays, monthDays, lunarToSolar, lunarDayName"""

DIST_TPL = """/* bazi-engine 独立引擎库 —— 由 tools/build_ui.py 自动生成，请勿手改
 * 纯计算层：四柱排盘 / 五行身强弱 / 大运 / 神煞 / 断语匹配 / 流年流月流日规则 / 合婚数据 / 夏令时与真太阳时校正。
 * 无 DOM 依赖。浏览器与 Node 双端可用：
 *   浏览器：<script src="engine.dist.js"></script> → window.BaziEngine
 *   Node：  const BaziEngine = require('./engine.dist.js');
 */
(function(root, factory){
  if (typeof module === 'object' && module.exports) { module.exports = factory(); }
  else { root.BaziEngine = factory(); }
})(typeof self !== 'undefined' ? self : this, function(){

__ENGINE__

return {
__EXPORTS__
};
});
"""
dist = DIST_TPL.replace("__ENGINE__", engine_js).replace("__EXPORTS__", EXPORTS)
os.makedirs(os.path.join(ROOT, "engine"), exist_ok=True)
with open(os.path.join(ROOT, "engine", "engine.dist.js"), "w", encoding="utf-8") as f:
    f.write(dist)
print(
    "engine/engine.dist.js built, size=%dKB, regions=%d"
    % (len(dist) // 1024, len(regions))
)
