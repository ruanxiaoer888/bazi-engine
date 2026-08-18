# AI 冷启动文档（通用版 · 任意 AI 平台 / 新会话）

> 读我。本文件是 `HANDOFF.md` 的会话级补充，专门解决"换个 AI 怎么继续"的问题。
> 任何新 AI 介入前，先读：1. 本文件 2. HANDOFF.md 3. `发布物料.md`（发布材料）
>
> **跨平台说明**：本项目会在多个 AI 平台间切换开发（WorkBuddy / DeepSeek Harness / Codex / 百度搭子等）。本文档**不含任何平台专属路径或目录**——工作区路径以你当前环境为准（如 `E:\michael\DSHProjects\bazi-engine` 或 `E:\michael\workBuddy\bazi-project`）；bazi-app 一律用相对路径 `../bazi-app` 表示，任何布局下都成立。

---

## 1. 这是什么项目

- **产品名**：bazi-engine（对外名称，原名 bazi-master 因 SkillHub 同名竞品已弃用）
- **仓库**：`ruanxiaoer888/bazi-engine`（GitHub，Public 意向，当前按开源准备）
- **定位**：B 端专业四柱八字排盘引擎底座，面向**命理师**，开源（MIT），可嵌入/二次开发
- **一句话**：输入出生信息 → 四柱八字 + 大运流年 + 流日/流月/流年深度 + 六亲详解 + 合婚评分，全程标注古籍出处
- **项目性质**：Michael 个人独立研发项目，**与魅可科技（Meke）业务无任何关联**，推广/发布一律按个人项目口径
- **双轨关系**：bazi-engine（B 端引擎底座）↔ 另仓 `bazi-app`（C 端「本初」变现），引擎层共用，UI 各自独立

## 2. 当前阶段（2026-08-17 19:48）

- **版本**：v1.2.1（标签未 bump，累计：全面扫描修复批次 + 农历模块同步 + 农历/阳历双模式切换 + 合婚上下布局 + 合婚时段模式修复 + xiYong ratio 细分 + 五行补救文案强/弱区分 + 太极 logo + 输入侧晚子时/节气临界提示语 + 断语库 504→801）
- **功能**：132 项任务**全部完成**（排盘/大运/流年/流月/流日/六亲/合婚/五行补救/神煞/调候用神/三式宫位/特殊格局）
- **农历模块**：引擎层新增 `lunarToSolar`/`leapMonth`/`leapDays`/`monthDays`/`lunarDayName` + `LUNAR_INFO` 数据表（1900-2099），与 bazi-app C 端实现完全一致
- **农历/阳历双模式切换**：主表单 + 合婚 A/B 各自独立（`switchCal`/`switchHeCal`），农历输入自动 `lunarToSolar` 转公历
- **合婚布局**：甲乙上下双区块（移除左右双栏），每人独立「是否校正真太阳时」下拉框（`hTruesunA/B`）；`readHe` 时段模式强制 `truesun:'no'`
- **输入侧提示语**（2026-08-17）：主表单 + 合婚 A/B 填时间即时提示——晚子时（23 点，时柱按次日）+ 节气临界（距十二节交节 ≤6h 提示年/月柱切换敏感点，立春特判；农历模式跳过）
- **断语库**：`kb/04-rules-db/rules.json` — **801 条**（事业96/性格77/财运57/用神喜忌57/六亲48/流日50/十神组合48/婚姻47/神煞46/流月45/格局41/健康41/学业42/五行生克36/流年30/大运20/合婚20），每条含 `suggestion` 建议字段
- **UI**：`ui/index.html` 单文件离线，**零外部依赖**（无 Google Fonts），墨底 + 古铜金高端商务风，壹~玖中文序号徽章，内置 206 年节气
- **引擎**：`engine/engine.dist.js`（247KB，UMD 双端，含 getRemedy/yongShenChong/农历模块 + 801 条规则数据）
- **发布状态**：✅ **双平台均已上架（2026-08-17）**——① **SkillHub**：申诉通过已发布（「生态杀手」分类，平台归一化显示 V1.0.0，实际 v1.2.1）；② **ClawHub**：已发布（SkillSpector 转 Published，Productivity 分类，v1.2.1 GitHub 自动同步版——绑定 `ruanxiaoer888/bazi-engine`，git push 自动拉新）；③ GitHub 开源仓库
- **真人验收**：✅ 已完成（3 案例全部通过，截图 `assets/screenshots/final/`）
- **阻塞项**：**无**。功能/验收/发布/扩库全部完成，无外部等待
- **GitHub**：已推送，HEAD=`a69af86`（2026-08-17），远程 `ed973d9`（`a69af86` 为文档 commit 未推）

## 3. 技术架构

| 层 | 文件/目录 | 说明 |
|---|---|---|
| 构建 | `tools/build_ui.py` | Python 构建脚本，内联断语库 + 节气 + 全部 JS → 产出 `ui/index.html` + `engine/engine.dist.js` |
| UI | `ui/index.html` | 单文件成品（唯一真源），打开即用，离线可用 |
| 引擎 | `engine/engine.dist.js` | 构建副产物，**不要手改**。UMD：浏览器 `window.BaziEngine` / Node `require` |
| 知识库 | `kb/` | 01-basics / 02-rules / 03-classics / 04-rules-db / 05-reference |
| 发布 | `tools/build_release_zip.py` | 发布验证流程：打 ZIP（自动排除 LICENSE/LICENSE-DATA/README.en.md）+ 关键产物 MD5 校验，不依赖任何平台目录 |
| 引擎变更记录 | `docs/ENGINE-CHANGES.md` | 权威记录（版本 + 变更 + dist MD5），bazi-app 对话据此对齐；引擎变更必须 bump 版本并追加记录 |
| 发布材料 | `发布物料.md` + `SkillHub-Submission-Kit.md` | 卖点/图标提示词/示例对话/合规声明 + 提交包模板 |

### 引擎抽层机制（重要，commit `807ab4c`）

- `tools/build_ui.py` 的 TPL 内用 7 对 `// [ENGINE:BEGIN]` / `// [ENGINE:END]` 注释标记界定**纯计算层**（不搬代码，UI 行为不变）
- 构建时把标记区段抽取拼装为 `engine/engine.dist.js`
- **边界规则（铁律）**：引擎层 = 纯计算（无 DOM/CSS）；`fmtRule`/`analyzeHe`/所有 `render*`/`run*`/`draw*` 留在 UI 层（返回 HTML 的展示函数不进引擎库）
- **新增引擎函数**：写进标记区内即可自动进入 dist；新增 UI 函数则写标记区外

### 引擎 API（B 端常用）

```js
const ctx = BaziEngine.paipan(name, gender, y, m, d, hh, mm, place, truesun)
// ctx: dayMaster, dmWx, pillars[4], five, strength, xiYong, pattern, shenSha[], solarInfo, dayun...
const rules = BaziEngine.matchRules(ctx, category)   // 断语匹配
const adj = BaziEngine.applyDst(y, m, d, hh, mm)     // {dst:0|1, y,m,d,hh,mm}
const map = BaziEngine.SHI_CHEN_MAP['巳']            // [9,0] 时辰→时分

// 农历转公历（1900-2099，与 bazi-app C 端实现一致）
const solar = BaziEngine.lunarToSolar(2024, 1, 1, false)  // {y:2024,m:2,d:10}
const leap = BaziEngine.leapMonth(2017)                    // 6（闰六月）
const dayName = BaziEngine.lunarDayName(15)                // '十五'
```

**排盘前预处理（B/C 端通用）**：
- 时段模式（只知时辰）→ 强制 `truesun='no'`，不调 `applyDst`（时段本身即太阳时）
- 具体时间模式 → 先 `applyDst` 回拨，再 `paipan`

## 4. 关键决策（不要回头讨论）

| 决策 | 结论 |
|---|---|
| 双轨战略 | bazi-engine 走 B 端专业引擎底座（开源，面向命理师）；`bazi-app` 走 C 端轻量娱乐变现，引擎抽层共享 |
| 视觉 | 墨底 + 古铜金高端商务风；卡片标题用壹~玖深中文序号圆形徽章；系统字体栈（Songti SC/STSong/SimSun + system-ui）；**零外部依赖**（已移除 Google Fonts） |
| 断语库 | 801 条（v1.2.1，2026-08-17 扩充 504→801），路线图 434→504→801→1000；每条必须含 `suggestion` 建议字段；规则命中须可追溯古籍出处 |
| 古籍规范 | 输出必须标注出处（穷通宝鉴/三命通会/滴天髓/渊海子平/子平真诠），保证可追溯、可检验。**注意：SkillHub 发布版 SKILL.md 不写具体典籍名**（平台误判"涉政"，改为「古代命理典籍」）；内部文档/KB 保留 |
| 验收规范 | ✅ 已通过真人验收（3 案例：排盘 1990-05-15 / 流日 1996-02-22 / 合婚 1996-08-13+1973-03-02） |
| 命名 | 对外统一 "bazi-engine"（不挂钩魅可）；C 端 bazi-app 叫「本初」（原「算了么」因品牌冲突改名，域名 benchu.xiaoerpro.com） |
| 引擎同步 | `python tools/build_ui.py` 后 `cp engine/engine.dist.js ../bazi-app/web/engine.dist.js` 并 commit |

## 5. 下一步优先级（不要打乱顺序）

0. ✅ ~~SkillHub 申诉~~（2026-08-17 通过并上架）
1. ✅ ~~ClawHub SkillSpector 扫描~~（已转 Published，海外发布闭环完成）
2. **[协作] bazi-app C 端**：引擎已同步（v1.2.1，含 801 条规则），C 端部署/虎皮椒开通在另一个对话推进（读 `docs/ENGINE-CHANGES.md` 对齐）
3. ✅ ~~断语库扩充 504→800+~~（已完成 `bd7f5ab`，801 条，2026-08-17）
4. ✅ ~~晚子时/节气临界**输入侧**提示语~~（已完成 `53a3bd2`，2026-08-17）
5. **[后置] 断语库 801→1000+**（先清 HANDOFF 记录的表外神煞旧死规则）
6. **[后置] MCP/API 化**（P2 路线图）
7. **[后置] 商标注册**（41/42 必选 + 9/45 防御，注册前代理检索规避「本初子午」近似）

## 6. 与 Michael 协作的偏好

- 语言：中文
- 表达：结论先行，先给建议再展开；复杂问题分点 + 对比表格
- 多方案：直接给出推荐判断，不要平铺选项
- 开发：严格按顺序推进 A→B→C；重大模块完成**主动暂停做代码审计**再打包
- **HANDOFF.md 是项目真相源**：写之前必须核实真实状态（任务台账 + 文件版本 + git log），不能凭记忆
- 常说"你自己想办法解决" = 期望 AI 独立完成，不需要逐步指导
- 喜欢：状态检查点 + MD5 校验 + 详尽表格摘要 + 下一步清单
- 完成后主动问"接下来我需要做什么"获取优先级清单

## 7. 容易踩的坑（来自 HANDOFF，精简版）

### 测试/调试
- **`LAST` 是 eval 内块级变量（`let LAST`）**：测试脚本必须用 `__setLast()` 设置，直接 `globalThis.LAST=...` 会触发"请先排盘"拦截
- **`new Date(2026,2,0)` 取 2 月末（28 天）**：月份参数从 0 开始，算月末天数月份要 +1
- **node `-e` 跑长脚本有 TS 剥离干扰**：改临时文件 `_dbg_*.js` 调试，用完即删
- **vm 沙箱 stub 必须经 `document.getElementById` 触发创建**：直接访问 `_els['id']` 会 undefined
- **`initSelects()` 只填选项不显隐**：改原生 select 后须显式调用 `toggleTimeMode()` / `toggleHeTimeMode('A'/'B')`
- **合婚 A/B 两侧 HTML 结构必须对称**：漏 `</div>` 浏览器容错不报错，扫描时 diff A/B 对比
- **iOS Safari select 字号 <16px 聚焦自动放大**：移动端 media query 内 `select{font-size:16px}`
- **文档数字随功能同步**：断语数/版本号散落在 README/README.en/SKILL/HANDOFF/发布物料，扩库后用 `grep -rn "旧数字"` 全局清查
- **合婚「只知时辰」须强制 `truesun:'no'`**：`readHe` 时段模式不能读 `hTruesun` 下拉框默认值（默认 `'yes'`），否则会错误做真太阳时校正，与主表单 `generate` 行为不一致
- **流日/六亲面板是 toggle 开关（非幂等渲染）**：`runLiuDay`/`runLiuQin` 每次调用切换展开/收起，测试脚本连续调用第二次会触发「收起」判空；`LIU_DAY_OPEN` 等是 eval 内 `let` 变量，外部须经 `__resetPanels` 辅助函数访问（`globalThis.xxx` 访问不到）
- **身中和喜用不能五行全列**：原 `xiYong=WX_NAMES.slice()` 让所有身中和盘喜用五行全列（UI 显示 5 个元素），但此时喜忌无定论。修复：按 `ratio` 细分——偏强(ratio>0.5)走强逻辑，偏弱(ratio<0.5)走弱逻辑，真中和(ratio≈0.5)喜忌空
- **「用神被冲克合」状态判定要 ≥2 处证据**：原 `yongShenChong` 任一合/克就 return true（宽松，被 `xiYong.length>=5` workaround 掩盖）。xiYong 修复后 workaround 失效，所有有明确 xiYong 的盘都命中 → 改为累计冲克合次数，<2 时不判破损

### 构建/依赖
- **Google Fonts `@import` 外链违反"单文件零外部依赖"承诺**，已删除，勿加回
- **SKILL.md 实际位于 `skill/SKILL.md`（非项目根）**：同步打包时第一版 `cp` 失败，用正确相对路径
- **断语库 JSON 每改必验**：`python json.load` 校验合法性 + 统计规则数，再重建 UI
- **`parseItem()` 返回 `[月,日,时,分]`（无年份，年份来自 `JIEQI.data` 的 key）**：写节气新函数用 `new Date(yy, p[0]-1, p[1], p[2], p[3])`；把 p[0] 当年份 → Invalid Date → diff=NaN → 条件静默失效（2026-08-17 输入侧节气提示曾踩，静默无报错）
- **matchRules 神煞键只认 SHENSHA 表内 24 项**：空亡(kongWang)/咸池/元辰/天喜/魁罡/太极贵人/福星贵人/国印贵人/文昌贵人(表内名"文昌")不在表内 → `{神煞:"X"}` 永不命中；evalState "为喜用/为忌神"须带位置日支、"为用神有力"须带十神键（2026-08-17 扩充修复 7 条死规则，另有 ~9 条旧规则待清理）
- **Python 改 JSON 后必须回写 `data['rules']=rules`**：`rules=[r for r in ...]` 生成新列表后直接 dump 旧引用 = 修改丢失（2026-08-17 曾两次"改了没生效"）

### 流程
- **任务账目会滞留**：完成一项立即更新任务状态，发布前对照 132 项清单核对
- **打包目录防多版本混入**：`tools/index.html`（旧 UI 337KB）曾与 `ui/index.html` 并存，UI 唯一真源是 `ui/index.html`

## 8. 常用命令

```bash
# 构建（产出 ui/index.html + engine/engine.dist.js）
python tools/build_ui.py

# 回归（核心 3 套 + 其余 8 套）
node tools/test_engine.js        # 独立引擎库 28 项
node tools/test_lunar.js         # 农历转换模块 27 项
node tools/verify_ux_e2e.js      # 端到端用户视角（A~G 组，含流日 F 组 12 项/六亲 G 组 8 项）
node tools/test_dst.js           # 夏令时窗口/边界 29 项
# 其余：test_ui / test_eval_state / test_p1_fixes / verify_sleep_rules /
#       verify_liuri_v2(test_liuri_v2) / verify_liuyue_v2(test_liuyue_v2) / verify_edu_rules / check_conflicts

# 发布验证（替代旧打包目录同步，平台无关）：python tools/build_release_zip.py 产出 ZIP 后 md5sum 校验关键产物
#   （ui/index.html / engine/engine.dist.js / skill/SKILL.md / kb/04-rules-db/rules.json）

# C 端引擎同步
cp engine/engine.dist.js ../bazi-app/web/engine.dist.js
```

## 9. 相关仓库

- **bazi-app**（C 端「本初」，原「算了么」因品牌冲突已改名）：`github.com/ruanxiaoer888/bazi-app`（Private）
  - 本地路径：`../bazi-app`（相对于本仓库工作区，平台不同则位置不同）
  - 状态：报告功能（25+ 板块）+ 海报分享 + 支付链路（虎皮椒 mock）+ 兑换码解锁均已完成；**待部署上线**（等 SSH+DNS），阻塞在虎皮椒新通道未开通
  - 冷启动文档：该仓 `AI_CONTEXT.md` + `HANDOFF.md`（注意其第 9 节对 bazi-project 的状态描述以本文件为准）

---

**每次接手时先做三件事**：
1. `git status` 看工作树是否干净 + `git log --oneline -5` 看最新提交
2. 读 `HANDOFF.md` 最新版（项目真相源）
3. 对照本文件第 5 节确认下一步任务
