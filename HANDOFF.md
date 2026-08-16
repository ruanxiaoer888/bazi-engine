# bazi-engine 八字命理 Skill · 项目交接文档（HANDOFF）

> 更新时间：2026-08-16 11:40 · 当前版本 **v1.2.1**（标签未 bump，实际已含：农历/阳历双模式切换、合婚上下双区块布局、合婚时段模式 truesun 修复 + 测试脚本 toggle 适配）
> 项目性质：**Michael 个人独立研发项目**，与魅可科技（Meke）业务无任何关联，推广/发布按个人项目口径。
> **给 Codex / 新会话**：先读同目录 `AI_CONTEXT.md`（冷启动文档），再读本文件。

---

## 〇、双轨战略与引擎抽层（2026-08-15，重要架构决策）

**战略**：bazi-engine 走 B 端专业引擎底座（面向命理师，开源）；另建 **`E:\michael\workBuddy\bazi-app`** 走 C 端轻量娱乐变现（大白话 + 付费报告）。

**引擎抽层实现**（commit `807ab4c`）：
- `tools/build_ui.py` 的 TPL 内用 7 对 `// [ENGINE:BEGIN]` / `// [ENGINE:END]` 注释标记界定纯计算层（**不搬代码**，`ui/index.html` 行为不变，仅多无害注释）
- 构建时同时产出 **`engine/engine.dist.js`**（188KB，UMD：浏览器 `window.BaziEngine` / Node `require` 双端可用），导出 paipan/matchRules/calcShenSha/applyDst/matchLiuYue/lunarToSolar/leapMonth 等约 105 个函数与数据表
- 新增回归 `node tools/test_engine.js`（28 项，独立库直测）+ `node tools/test_lunar.js`（27 项，农历模块验证）；原有 8 套回归不受影响
- **C 端同步方法**：`python tools/build_ui.py` 后 `cp engine/engine.dist.js ../bazi-app/web/`
- **边界规则**：引擎层 = 纯计算（无 DOM/CSS）；`fmtRule`/`analyzeHe`/所有 render*/run*/draw* 留在 UI 层（返回 HTML 的展示函数不进引擎库）；新增引擎函数时放进标记区内即可自动进入 dist

---

## 一、当前任务（进行中 / 待办）

### ✅ 2026-08-16 审计修复（第一轮，已提交 `5a61801`）
- 接手后核实真实状态：文档记录 `main=330ff03` 已过时，实际 HEAD=`0dc1a45`（本地=远程，已同步）；HANDOFF/AI_CONTEXT 滞后 7 个 UI commit（08-16 00:56~02:15）
- 审计发现并修复 3 项，全套 **12 套回归复跑全绿（FAIL:0 WARN:0）**：
  1. **合婚时段模式 truesun 回归**（`cb4100f` 引入）：`readHe()` 时段模式（只知时辰）改为强制 `truesun:'no'`，与主表单 `generate()` 一致；精确模式仍读 `hTruesun` 下拉框（支持按人分别校正）
  2. **verify_ux_e2e 测试脚本 toggle 适配**（`80ec029` 加「展开/收起」开关后测试未同步，导致 F6/F8/G5/G7 判空）：`__setLast` 内联重置 4 个面板开关 + 新增 `__resetPanels`，F 组流日调用前重置
  3. **清理 lunarDayName 重复定义**：删除 UI 区重复定义（保留引擎区定义，engine.dist.js 不受影响）
- ✅ 已提交 commit `5a61801`（5 文件：`tools/build_ui.py` / `tools/verify_ux_e2e.js` / `ui/index.html` / `HANDOFF.md` / `AI_CONTEXT.md`；`engine/engine.dist.js` 无变化，无需同步 bazi-app）

### ✅ 2026-08-16 验收发现修复（第二轮，已完成，待提交）
- Michael 真人验收 1995-05-15 广州盘时发现「喜用」chip 五行全列（截图确认），根因 `build_ui.py:1143` 中和分支 `xiYong=WX_NAMES.slice()` 直接五行全列
- 修复 3 项：
  1. **`xiYong` 中和分支按 `ratio` 细分**（`build_ui.py:1139-1159`）：偏强 (ratio>0.5) → 走强逻辑（喜用=克泄耗 3 个），偏弱 (ratio<0.5) → 走弱逻辑（喜用=生扶 2 个），真中和 (ratio≈0.5) → 喜忌空（前端显示「—」）
  2. **`yongShenChong` 判定更严格**（`build_ui.py:1315-1344`）：需 ≥2 处冲克合证据才判「用神被冲克合」，避免单个合/克就命中（之前宽松，被 `xiYong.length>=5` workaround 掩盖，xiYong 修复后暴露为 test_eval_state 1 FAIL）
  3. **新增 `tools/test_xiyong.js`**：针对性回归，10 盘验证 xiYong/jiYong 结构合理性
- 引擎层影响：`yongShenChong` 在引擎标记区内（1196-1448），`engine.dist.js` 188KB → 189KB，**已同步到 bazi-app**（md5 一致）
- 验收样本 1995-05-15 修复后：xiYong=`水、金、土`（3 个），jiYong=`火、木`（2 个）

### 发布前（就差这两步）
1. **真人验收**（需 Michael 亲手操作，约 10 分钟）
   - 打开 `ui/index.html` 排 2~3 个真实盘
   - 重点看：四柱命盘表（日柱金边高亮）、手机窄屏（640px 响应式）、流日面板、六亲详解面板
2. **提交发布**
   - 生成图标：按 `发布物料.md` 中的图标提示词（可用 ImageGen）
   - 按 `发布物料.md` 准备 SkillHub 提交材料（简介/示例对话/合规声明）

> ✅ 发布前收尾（2026-08-13 已完成）：check_conflicts.js 已同步打包目录 + SKILL.md 登记；`断语库.json.bak` 旧备份已清理；新增对外 `README.md`；SKILL.md frontmatter 补 `tags`/`license`（MIT）。

### 发布后增强（已记录，可后置）
- 晚子时 / 节气临界时刻的引擎提示语（已知缺口，非阻塞）

---

## 二、已完成内容（截至 v1.2.1）

### 功能全景（132 项任务中 132 completed）
| 模块 | 状态 |
|------|------|
| 排盘引擎（四柱/大运/流年/流月/流日） | ✅ 完整 |
| **UI 美学升级**：墨底 + 古铜金高端商务界面，壹~玖中文序号徽章，四柱专业表，零外部依赖 | ✅ v1.1 |
| **流日分析**：单月逐日 30 天（每日干支/十神/与命局冲合刑害/空亡/喜忌/十二长生 + 关键日小结） | ✅ v1.1 |
| **六亲详解**：宫位为体（年祖上/月父母/日配偶/时子女）+ 十神为用 + 喜忌空亡，五段式输出 | ✅ v1.2 |
| 流月分析（十二流月逐月 + 断语） | ✅ |
| 流年深度规则（岁运并临/伏吟/反吟/空亡/十二长生） | ✅ |
| 合婚七大维度评分 | ✅ |
| 五行补救 / 神煞 / 调候用神（穷通宝鉴） | ✅ |
| 三式宫位（胎元/命宫/身宫）、特殊格局（专旺5+从格4） | ✅ |
| **农历转换模块**：引擎层新增 `lunarToSolar`/`leapMonth`/`leapDays`/`monthDays`/`lunarDayName` + `LUNAR_INFO` 数据表（1900-2099），与 bazi-app C 端实现完全一致 | ✅ 2026-08-16 |
| **农历/阳历双模式切换**：主表单 + 合婚 A/B 各自独立切换（`switchCal`/`switchHeCal`），农历输入自动 `lunarToSolar` 转公历后排盘 | ✅ 2026-08-16 |
| **合婚上下双区块布局**：移除 `.two-col` 左右双栏，改为甲乙上下独立区块 + 金色虚线分隔；每人独立「是否校正真太阳时」下拉框（`hTruesunA/B`），`readHe` 支持按人分别校正 | ✅ 2026-08-16 |

### 关键资产
- **断语库**：`knowledge-base/04-断语库/断语库.json` — **504 条**（六亲30 / 流年30 / 流月20 / 流日5 / 合婚20 等），每条含 `suggestion` 建议字段，全量接入渲染
- **UI**：`ui/index.html` — 单文件离线（**零外部依赖**，无 Google Fonts 外链），内置 206 年节气 + 504 条断语
- **引擎**：`tools/build_ui.py` — Python 构建脚本，内联断语库 + 节气 + 全部 JS 逻辑
- **知识库**：三命通会/渊海子平/滴天髓/子平真诠/穷通宝鉴全文梳理均已入库
- **打包目录**：`~/.workbuddy/skills/bazi-engine/` — 已同步，MD5 全 MATCH，可独立运行
- **版本**：SKILL.md frontmatter 已加 `version: 1.2.1` + `tags` + `license: MIT`
- **对外文档**：`README.md`（项目门面：功能/快速开始/示例对话/免责声明）+ `发布物料.md`（内部发布材料：卖点/图标提示词/渠道建议）

### 关键修复（2026-08-14 全面扫描）
- **空 condition 规则无条件命中 bug**：71 条 condition 为 `{}` 的规则中，8 条（qinq_27~30 + edu_17~20）落入主渲染分类会**固定显示在每个命盘**（`for...in` 空对象后 `hit` 保持 true）。修复：`matchRules` 开头 `if(Object.keys(c).length===0){ hit=false; }` 排除（专用函数仍按 id 触发 dayun_*/liuyue_*/liuri_*/qinq_27~30/he_*）
- **edu_17~20 真孤儿复活**：补差异化 condition 使其重新参与主引擎匹配——edu_17 印星为用有力 / edu_18 食神多而有力 / edu_19 月干透印+伤官泄秀 / edu_20 身弱财多；edu_19 原与 combo_伤官_正印 条件相同会同盘重复，已加"月干+印为用有力"约束并改文案消除
- 验证：新增 `tools/verify_edu_rules.js` 回归（edu 命中率 ≥1 次且 <60%、qinq_27~30 不进主渲染）；8 套既有回归 + 冲突检测全绿

### 验证体系（12 套回归，全部 PASS：FAIL:0 WARN:0，2026-08-16 复跑确认）
| 脚本 | 覆盖 |
|------|------|
| `test_ui.js` | UI 结构与渲染 |
| `test_eval_state.js` | 引擎状态 |
| `test_p1_fixes.js` | P1 修复回归 |
| `verify_sleep_rules.js` | 沉睡规则接入 |
| `verify_ux_e2e.js` | 端到端用户视角（A~G 组：输入容错/边界/报告质量/稳定性/完整性/**流日 F 组 12 项**/**六亲 G 组 8 项**） |
| `check_conflicts.js` | 反义断语同盘矛盾检测（40 对规则，1000 盘 0 冲突） |
| `test_dst.js` | 夏令时窗口/边界校正（29 项） |
| `test_liuri_v2.js` | 流日规则 v2（10 项） |
| `test_liuyue_v2.js` | 流月规则 v2（10 项） |
| `verify_edu_rules.js` | 空 condition 排除 + 学业规则复活回归（edu_17~20 命中率须 ≥1 次且 <60%，qinq_27~30 不进入主渲染） |
| `test_engine.js` | 独立引擎库直测（28 项） |
| `test_lunar.js` | 农历转换模块（导出完整性/闰月判断/非闰月转换/闰月转换/日名映射/边界年份/排盘联动，27 项） |

> 另含 `audit_hit_distribution.js`（命中分布审查）、`check_dup_hits.js`（重复命中检测）——发布后仍可继续用于断语库维护。

### 交付文档
- `发布物料.md` — 6 大卖点 / 图标提示词 / 3 个示例对话 / 合规声明 / 渠道建议（SkillHub 优先）

---

## 三、卡住的问题（当前阻塞：无）

- ✅ 全部 132 项任务已清零（刚理清 #74 滞留状态）
- ⚠️ 唯一"卡点"是**真人验收**需要 Michael 本人操作（模拟回归无法替代真实观感）
- 🔜 无技术性阻塞；晚子时提示语为已知非阻塞缺口

---

## 四、下一步计划（按优先级）

0. **[Michael] 确认并提交本轮修复** → 3 文件（`tools/build_ui.py`/`tools/verify_ux_e2e.js`/`ui/index.html`），可选 bump 版本号至 v1.2.2（须全局清查 README/README.en/SKILL/发布物料中的版本号，避免散落不一致）
1. **[Michael] 真人验收** → 排 2~3 个真实盘，反馈 UI/流日/六亲体验（打开 `ui/index.html`）
2. **[Michael] 选最终图标** → v1 平面古印风（推荐）/ v2 立体金属感，选后定稿 logo
3. **[Michael] 提交发布** → SkillHub（用 `SkillHub-Submission-Kit.md` 提交包）
4. **[后置] 晚子时/节气临界引擎提示语** → 发布后迭代
5. **[后置] 第 3 批次断语扩充**（流年 30→55 / 用神喜忌 31→55 / 六亲 30→50，目标 800~1000 条，复用 `drafts/` 取材方法论）→ 发布后迭代

---

## 五、踩过的坑（经验教训，避免重蹈）

### 测试/调试类
1. **`LAST` 是 eval 内块级变量（`let LAST`）**，测试脚本必须用项目既有的 `__setLast()` 设置，直接 `globalThis.LAST=...` 会触发"请先排盘"拦截 —— verify_ux_e2e.js F 区曾因此报错
2. **`new Date(2026,2,0)` 取的是 2 月末（28 天）**，`new Date(2026,3,0)` 才是 3 月末（31 天）—— 月份参数从 0 开始，算月末天数时月份要 +1
3. **node `-e` 方式跑长脚本有 TS 剥离干扰**，异常堆栈不可读 —— 改用临时文件（`_dbg_*.js`）调试，用完即删
4. **vm 沙箱 stub 中元素必须经 `document.getElementById` 触发创建**，直接访问 `_els['id']` 会 undefined —— 调试脚本要先调用 getElementById 再取 innerHTML
5. **`initSelects()` 只填选项不显隐**：改原生 select 后，时/分 select 带 `class="hidden"`，必须在 `initSelects()` 后显式调用 `toggleTimeMode()` / `toggleHeTimeMode('A'/'B')`，否则时间选择器对用户不可见
6. **合婚 A/B 两侧 HTML 结构必须对称**：B 侧性别 div 漏 `</div>` 会致 `.row` 嵌套错乱（浏览器容错不报错），扫描时用 diff 对比 A/B 或数标签平衡
7. **iOS Safari select 字号 <16px 聚焦自动放大页面**：移动端 media query 内 `select{font-size:16px}` 防误触
8. **文档数字随功能同步**：断语数/版本号等硬数字散落在 README/README.en/SKILL/HANDOFF/发布物料，扩库后易漏改——用 `grep -rn "旧数字"` 全局清查
9. **打包目录防多版本混入**：`tools/index.html`（旧 UI 误拷贝 337KB）曾与 `ui/index.html` 并存，打开错文件会看到旧界面——UI 唯一真源是 `ui/index.html`，定期比对打包目录与源码清单
10. **合婚「只知时辰」必须强制 `truesun:'no'`**：合婚改造加 `hTruesun` 下拉框后，`readHe` 时段模式若读下拉框默认 `'yes'` 会错误做真太阳时校正——时段模式须强制 `'no'`（主表单 `generate` 已有此处理），否则两处行为不一致
11. **流日/六亲面板是 toggle 开关（非幂等渲染）**：`runLiuDay`/`runLiuQin` 每次调用切换展开/收起，测试脚本连续调用第二次会触发「收起」判空——测试前须重置 `LIU_DAY_OPEN`/`LIU_QIN_OPEN`（它们是 eval 内 `let` 变量，外部必须经 `__resetPanels` 辅助函数访问，`globalThis.xxx` 访问不到）

### 构建/依赖类
5. **Google Fonts `@import` 外链违反"单文件零外部依赖"承诺** —— UI 升级时删除，改用系统字体栈（Songti SC/STSong/SimSun + system-ui）
6. **SKILL.md 实际位于 `skill/SKILL.md`（非项目根）** —— 同步打包时第一版 `cp` 失败，须用正确相对路径
7. **断语库 JSON 每改必验** —— 用 `python json.load` 校验合法性 + 统计规则数，再重建 UI（断语数会反映在 build 输出里）

### 需求/流程类
8. **7 项功能核查中 #2 与 #4 重复（都是流月分析）** —— 先向用户澄清再动手，避免重复劳动
9. **任务账目会滞留**：实际完成但状态未更新（本次理清 #27/41/59/66/68/69/70/71/72/75/74 共 11 个）—— 完成一项应立即 TaskUpdate

---

## 六、项目速查

- 源码目录：`E:\michael\workBuddy\bazi-project`
- GitHub 仓库：https://github.com/ruanxiaoer888/bazi-engine
- 打包目录：`C:\Users\34743\.workbuddy\skills\bazi-engine`
- 构建命令：`python tools/build_ui.py`（输出 `ui/index.html` + `engine/engine.dist.js`）
- 回归命令：`node tools/test_engine.js`（独立引擎库）+ `node tools/verify_ux_e2e.js`（其余 8 套同理：test_ui / test_dst / test_liuri_v2 / test_liuyue_v2 / test_eval_state / test_p1_fixes / verify_sleep_rules / verify_edu_rules）
- 同步命令：文件 cp 到打包目录后 md5sum 校验（README.md / README.en.md / SKILL.md / tools/build_ui.py / ui/index.html / tools/各测试脚本）
- 命名约定：对外统一 "bazi-engine"（原名 bazi-master 因 SkillHub 同名竞品已弃用），个人项目口径，不挂钩魅可
