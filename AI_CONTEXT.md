# AI 冷启动文档（给 Codex / 新会话）

> 读我。本文件是 `HANDOFF.md` 的会话级补充，专门解决"换个 AI 怎么继续"的问题。
> 任何新 AI 介入前，先读：1. 本文件 2. HANDOFF.md 3. `发布物料.md`（发布材料）

---

## 1. 这是什么项目

- **产品名**：bazi-engine（对外名称，原名 bazi-master 因 SkillHub 同名竞品已弃用）
- **仓库**：`ruanxiaoer888/bazi-engine`（GitHub，Public 意向，当前按开源准备）
- **定位**：B 端专业四柱八字排盘引擎底座，面向**命理师**，开源（MIT），可嵌入/二次开发
- **一句话**：输入出生信息 → 四柱八字 + 大运流年 + 流日/流月/流年深度 + 六亲详解 + 合婚评分，全程标注古籍出处
- **项目性质**：Michael 个人独立研发项目，**与魅可科技（Meke）业务无任何关联**，推广/发布一律按个人项目口径
- **双轨关系**：bazi-engine（B 端引擎底座）↔ 另仓 `bazi-app`（C 端「算了么」变现），引擎层共用，UI 各自独立

## 2. 当前阶段（2026-08-16）

- **版本**：v1.2.1（全面扫描修复批次：原生 select 初始化 / 合婚 HTML 结构 / iOS 防缩放 / 文档断语数同步）
- **功能**：132 项任务**全部完成**（排盘/大运/流年/流月/流日/六亲/合婚/五行补救/神煞/调候用神/三式宫位/特殊格局）
- **农历模块**：引擎层新增 `lunarToSolar`/`leapMonth`/`leapDays`/`monthDays`/`lunarDayName` + `LUNAR_INFO` 数据表（1900-2099），与 bazi-app C 端实现完全一致
- **断语库**：`knowledge-base/04-断语库/断语库.json` — **504 条**（六亲30/流年30/流月20/流日5/合婚20 等），每条含 `suggestion` 建议字段
- **UI**：`ui/index.html` 单文件离线，**零外部依赖**（无 Google Fonts），墨底 + 古铜金高端商务风，壹~玖中文序号徽章，内置 206 年节气
- **引擎**：`engine/engine.dist.js`（188KB，UMD 双端）
- **阻塞项**：**无技术阻塞**。唯一卡点是**真人验收需要 Michael 亲手做**（模拟回归无法替代真实观感）
- **GitHub**：已推送，远程 main=`330ff03`，与本地 HEAD 一致（已同步）

## 3. 技术架构

| 层 | 文件/目录 | 说明 |
|---|---|---|
| 构建 | `tools/build_ui.py` | Python 构建脚本，内联断语库 + 节气 + 全部 JS → 产出 `ui/index.html` + `engine/engine.dist.js` |
| UI | `ui/index.html` | 单文件成品（唯一真源），打开即用，离线可用 |
| 引擎 | `engine/engine.dist.js` | 构建副产物，**不要手改**。UMD：浏览器 `window.BaziEngine` / Node `require` |
| 知识库 | `knowledge-base/` | 01-基础表 / 02-规则手册 / 03-古籍原文 / 04-断语库 / 05-参考资料 |
| 打包 | `~/.workbuddy/skills/bazi-engine/` | SkillHub 发布用打包目录，与源码 MD5 同步校验 |
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
| 断语库 | 504 条（v1.2.1），路线图 434→504→800→1000；每条必须含 `suggestion` 建议字段；规则命中须可追溯古籍出处 |
| 古籍规范 | 输出必须标注出处（穷通宝鉴/三命通会/滴天髓/渊海子平/子平真诠），保证可追溯、可检验 |
| 验收规范 | **发布前必须真人验收 2~3 个样本盘**（模拟回归不能替代），通过后才批准提交 SkillHub |
| 命名 | 对外统一 "bazi-engine"（不挂钩魅可）；C 端叫「算了么」 |
| 引擎同步 | `python tools/build_ui.py` 后 `cp engine/engine.dist.js ../bazi-app/web/engine.dist.js` |

## 5. 下一步优先级（不要打乱顺序）

1. **[Michael 亲手] 真人验收**（约 10 分钟）：打开 `ui/index.html` 排 2~3 个真实盘，重点看四柱命盘表（日柱金边高亮）/ 手机窄屏 640px 响应式 / 流日面板 / 六亲详解面板；顺手验证 1990 年 5 月夏令时盘是否提示回拨
2. **[Michael] 选最终图标**：`发布物料.md` 有 v1 平面古印风（推荐）/ v2 立体金属感，定稿后放入发布包
3. **[Michael] 提交发布**：按 `SkillHub-Submission-Kit.md` 提交包（简介/示例对话/合规声明）
4. **[后置] 晚子时/节气临界引擎提示语**（已知缺口，非阻塞）
5. **[后置] v1.3 断语库扩容**：流年 30→55 / 用神喜忌 31→55 / 六亲 30→50，目标 800~1000 条（复用 `drafts/` 取材方法论）

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

### 构建/依赖
- **Google Fonts `@import` 外链违反"单文件零外部依赖"承诺**，已删除，勿加回
- **SKILL.md 实际位于 `skill/SKILL.md`（非项目根）**：同步打包时第一版 `cp` 失败，用正确相对路径
- **断语库 JSON 每改必验**：`python json.load` 校验合法性 + 统计规则数，再重建 UI

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

# 同步到打包目录（发布前必做，md5 校验）
#   ~/.workbuddy/skills/bazi-engine/  ← 复制 README/README.en/SKILL.md/tools/build_ui.py/ui/index.html/各测试脚本

# C 端引擎同步
cp engine/engine.dist.js ../bazi-app/web/engine.dist.js
```

## 9. 相关仓库

- **bazi-app**（C 端「算了么」）：`github.com/ruanxiaoer888/bazi-app`（Private）
  - 本地路径：`E:\michael\workBuddy\bazi-app`
  - 状态：支付链路（虎皮椒 mock）+ 兑换码解锁已完成；阻塞在虎皮椒新通道未开通、未部署
  - 冷启动文档：该仓 `AI_CONTEXT.md`（注意其第 9 节对 bazi-project 的状态描述以本文件为准）

---

**每次接手时先做三件事**：
1. `git status` 看工作树是否干净 + `git log --oneline -5` 看最新提交
2. 读 `HANDOFF.md` 最新版（项目真相源）
3. 对照本文件第 5 节确认下一步任务
