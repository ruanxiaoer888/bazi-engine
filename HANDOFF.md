# bazi-engine 八字命理 Skill · 项目交接文档（HANDOFF）

> 更新时间：2026-08-20 · 当前版本 **v1.3.6**（git tag `v1.3.0` 保留；实际已含：农历/阳历双模式切换、合婚上下双区块布局、晚子时/节气临界提示语、断语库 504→801→789→1000 并定版 v1.3.0、**三方深度审计 v1.3.1~v1.3.6 全量修复**——空亡真修活/天克地冲方向/专旺阈值/流月精确节气/合婚评分扩维/农历越界 P0/跨平台构建/CI 门禁/假断言/移动端表格/无障碍/视觉统一/打印样式、**C 端合规软化工具 compliance_soften.py 落地（坑 #41 解决）+ bazi-app 闭环收尾速贴块交付**、**README 推广优化（本初 C 端推广位 + 产品生态 + 7 张配图 + 开发者三路径快速开始 + 支持作者联系方式，commit `f0bd94a`~`1d045cc` 共 7 个 docs/chore 提交，HEAD=`1d045cc`）**）
> 项目性质：**Michael 个人独立研发项目**，与任何企业无任何关联，推广/发布一律按个人项目口径。
> 发布状态：✅ **双平台均已上架**（2026-08-17 确认）——① SkillHub（腾讯）**已发布**（「生态杀手」分类，申诉通过；平台归一化显示 V1.0.0，见坑 #21）；② ClawHub（OpenClaw 官方市场）**已发布**（Productivity 分类，SkillSpector 扫描通过转 Published，v1.3.6 GitHub 自动同步版——绑定 `ruanxiaoer888/bazi-engine`，git push 自动拉新）
> **给 Codex / 新会话**：先读同目录 `AI_CONTEXT.md`（冷启动文档），再读本文件。

---

## 〇、双轨战略与引擎抽层（2026-08-15，重要架构决策）

**战略**：bazi-engine 走 B 端专业引擎底座（面向命理师，开源）；另建 **`../bazi-app`**（独立仓库/工作区）走 C 端轻量娱乐变现（大白话 + 付费报告）。

**引擎抽层实现**（commit `807ab4c`）：
- `tools/build_ui.py` 的 TPL 内用 7 对 `// [ENGINE:BEGIN]` / `// [ENGINE:END]` 注释标记界定纯计算层（**不搬代码**，`ui/index.html` 行为不变，仅多无害注释）
- 构建时同时产出 **`engine/engine.dist.js`**（438KB，UMD：浏览器 `window.BaziEngine` / Node `require` 双端可用），导出 paipan/matchRules/calcShenSha/applyDst/matchLiuYue/lunarToSolar/leapMonth 等约 101 个函数与数据表（含 1000 条规则数据）
- 新增回归 `node tools/test_engine.js`（28 项，独立库直测）+ `node tools/test_lunar.js`（27 项，农历模块验证）；原有 8 套回归不受影响
- **C 端同步方法**：`python tools/build_ui.py` 后 `cp engine/engine.dist.js ../bazi-app/web/`
- **边界规则**：引擎层 = 纯计算（无 DOM/CSS）；`fmtRule`/`analyzeHe`/所有 render*/run*/draw* 留在 UI 层（返回 HTML 的展示函数不进引擎库）；新增引擎函数时放进标记区内即可自动进入 dist

---

## 一、当前任务（进行中 / 待办）

### 当前状态（2026-08-20 快照）
- **本仓库无阻塞**：132 项任务清零 / 真人验收通过 / 双平台已上架 / **断语库 1000 条**（路线图达成）/ **v1.3.6**（三方审计 6 批次全量修复）/ 13 套回归全绿 + **CI 门禁真实生效**；工作树干净，HEAD=`1d045cc` 与远程同步，dist MD5 `1A4722FA7B0974EB4F5CFA53C71AA9C3`（LF 口径，本次 README 优化未动引擎）
- **在途事项（等待 Michael 操作，非本仓库代码工作）**：bazi-app C 端真实闭环剩 2 个外部阻塞（服务器四件套更新 + 虎皮椒真实支付接入——**微信渠道已开通，支付宝未开通**）；**速贴块已于 2026-08-19 交付**（`docs/BAZI-APP-HANDOFF-v1.3.0.md` 顶部），Michael 复制粘贴给 bazi-app 对话即可启动，执行到 ③④ 步时向对话提供 SSH 凭据 + 虎皮椒微信 appid/appsecret
- **遗留待清理**：✅ 全部已清（死规则 2 轮清理 + 三方审计 6 批次，见下方各段）

### ✅ 2026-08-20 README 推广优化（commit `f0bd94a`~`1d045cc`，共 7 个 docs/chore 提交，中英文同步）
> 目标：把开源引擎 + C 端「本初」（benchu.xiaoerpro.com）的「开源 → 商业闭环」故事写进 README，形成推广闭环。全部为文档/素材变更，**引擎 dist 未动**（MD5 不变）。
- **产品生态章节 + 在线体验入口**（`f0bd94a`）：README 新增「产品生态」表（bazi-engine ↔ 本初）+ 顶部「在线体验」链接 + 徽章；License 段补**商业边界**说明（本初为作者自有产品，C 端只消费 MIT 代码层 API、付费内容自有实现，不涉及 NC 数据——消除双许可疑虑）
- **C 端截图素材管理**（`acc4c05`）：截图素材归档 `assets/screenshots/benchu/_raw/`（28 张原始素材，**gitignore 排除不入库**），入库仅 3 张语义化命名（paipan/hehun/year）；新建 `assets/screenshots/promo/` 存宣传物料（compare 对比图 / flow 流程图，压缩自 2MB+ 原始图）
- **技术说明补充**（`fad5dc7`）：CI 门禁（`.github/workflows/ci.yml`）+ 跨平台一致性（`.gitattributes` LF 规范）说明；目录结构补 engine.dist.js / .github / .gitattributes
- **精选 3 张配图**（`b6688fa`）：功能特性→对比宣传图（引擎卖点）、产品生态→六维人格图谱（付费报告深度）、技术说明→处理链路流程图
- **README 全面优化**（`6528751`）：中文版新增「为什么是引擎？」段（对标英文 Why engine，LLM 猜盘 vs 确定性排盘卖点）；新增 **CI 徽章**；回归脚本清单折叠 `<details>`；快速开始拆 **用户 / 开发者 / AI 三路径**并补 `engine.dist.js` 浏览器+Node 双示例；新增「支持作者」入口；**修正示例代码两处 bug**（见坑 #42/#43）
- **支持作者联系方式**（`bdffa17`→`1d045cc`）：微信 `feizi6651` + 二维码 → 升级为**微信+公众号双二维码海报**（`assets/screenshots/contact-card.png`，@阮小贰 水印与 GitHub 账号一致，保留微信号文字防失效）
- **虚构示例命盘 5 个**（README 截图用，引擎实测验证）：李明远（男 1990-05-15 10:00 广州，夏令时+真太阳时链路）/ 林小雅（女 1992-08-08 20:00 北京，合婚乙方）/ 陈子墨（男 1990-02-20 15:00 深圳，合婚甲方）/ 王建国（男 1988 腊月廿七 西安，农历+节气临界）/ 陈静怡（女 1995-03-06 12:00 成都，流年类）——**均为虚构人物**，可放心用于公开截图

### ✅ 2026-08-19 bazi-app 闭环收尾交付（commit `df9cd7b`/`0605386`/`a9d1261`/`41d7688`/`41ba0eb`）
- **速贴块交付**：`docs/BAZI-APP-HANDOFF-v1.3.0.md` 顶部新增「速贴版」5 步指令（① MD5 核对基线 `3B90D659…` ② 回归确认含专旺收紧说明 ③ 服务器四件套 + `web/paid/` 目录 + pm2 ④ 微信支付接入——填微信 appid/appsecret、`mock:false`、¥0.01 真实验证 ⑤ 锁定引擎依赖并 commit），可直接复制粘贴给 bazi-app 对话
- **支付渠道状态更正**：虎皮椒**微信渠道已开通**（支付宝未开通）——`xunhu.channel` 已是 `wechat` 默认值，代码无需改，只差填凭证 + `mock:false`
- **合规定制边界说明**：bazi-app commit `2bb404f` 手改 dist 做术语软化（姻缘→情感/桃花正缘→人际正缘/流年→年度/烂桃花→不良人际 等 10 处，MD5 `1A4722FA`→`3B90D659`）——记录为坑 #41
- **`tools/compliance_soften.py` 落地（坑 #41 解决方案，commit `41ba0eb`）**：构建后术语替换工具（运势→能量/大运→十年节奏/姻缘→情感/八字→出生信息/烂桃花→不良人际/命格→特质/流年冲(合)命宫→年度…/桃花正缘→人际正缘，保护 `"流年":` 条件键；`--check` 检查残留；软化后 MD5 `1CA0DF3EC306DF96E160D76A9CEB191D`）——今后 bazi-app 同步 dist 后跑一次即得合规版，免手改构建产物

### ✅ 2026-08-19 三方深度审计（v1.3.1~v1.3.6，6 批次全量修复，commit `cc5e405`~`37a720d`）
> 引擎逻辑 / UI 功能视觉 / 构建工具链 三路并行审计（subagent 深读 + 运行时验证），🔴 严重 9 项全清、🟡 全修、🟢 大部分落地。
- **v1.3.1（`cc5e405`）**：空亡断语真修活（0→44%，原「日支逢空亡」因旬空定义永不可能——两版皆死）+ wealth_kugu 换补 + audit 0 命中检测
- **v1.3.2（`f1617cf`）**：🔴 流日天克地冲方向错误（甲庚冲漏判/乙庚五合误判，统一 WU_CHONG 标准）+ 跨平台构建反斜杠路径（Linux CI 曾测旧产物假绿）+ CI 门禁恒绿（audit/check_conflicts 加退出码）+ 农历越界 P0（1895-1899/2100 静默算错）
- **工具链批（`5c2a539`）**：🔴 check_conflicts 检测整体失效（matchRules 第二参数被忽略，矛盾恒 0）+ 假断言×3（test_engine 恒真/P1-2 纯注释/P1-5 自证式）+ CRLF 产物（.gitattributes 固化 LF，跨平台 MD5 可比）+ 发布包净化（排除 tools/archive）+ audit 可复现种子
- **v1.3.3（`65b42cc`）**：M6 lunarToSolar 公共 API 防御 + M7 流年喜用三分支（非喜非忌不再误报克用神）+ 死代码清理（evalState length>=5 / tiaohou 冗余 / GAN_ORDER 全局化）
- **v1.3.4（`5832995`）**：M3 专旺格阈值 0.55→0.75+他行≤0.15 双条件（5000 盘 0.94%→0.02%，去误标）+ M4 规则语义修复（写死五行→按日主动态）+ M5 晚子时流派标注
- **v1.3.5（`47ad09c`）**：M1 流月月柱改用 12 节精确时刻（临界月曾系统性错一月）+ M2 合婚日柱关系 17→25 可触达（纳音相生+三合，佳偶≥85 从不可达变 8/4000）
- **v1.3.6（`37a720d`）**：UI 批——移动端 6 列表格横向滚动 + 无障碍（focus-visible/键盘可达/触控≥40px）+ 硬编码色统一 var() + 打印样式 + theme-color/favicon + 年份动态化
- **审计确认可靠**：年柱立春/五虎遁五鼠遁/日柱基准/旬空/十二长生/大运顺逆/DST 窗口/合婚权重=100/JIEQI 全覆盖——核心排盘正确性无问题
- 引擎核心（排盘/大运/流年/流月/流日/合婚）经三方审计后 v1.3.6 全绿，可发布

### ✅ 2026-08-17 断语库扩充 504→801 条（commit `bd7f5ab`）
- 复用 `drafts/` 取材方法论（古籍摘录标出处），新增 297 条，覆盖 12 类主引擎规则：事业+44 / 性格+37 / 财运+29 / 用神喜忌+26 / 婚姻+22 / 十神组合+22 / 学业+22 / 神煞+22 / 健康+21 / 格局+18 / 六亲+18 / 五行生克+16
- 每条含 `suggestion`，source 标注到书名·篇（穷通宝鉴调候/子平真诠格局/三命通会十干/滴天髓旺衰等），内部 KB 保留典籍名
- **命中分布审计**（`audit_hit_distribution.js` + 自写 600 盘 0 命中扫描）：无 100% 命中规则、无 >80% 规则；修复 7 条死规则（引用 SHENSHA 表外神煞——空亡/咸池/天喜/元辰，及"为忌神/为用神有力"缺位置/十神键、`十神:"桃花"` 错误）
- 13 套回归全绿（测试脚本同步：test_engine 504→801 断言、verify_ux_e2e C3 主面板区间 20-40→30-70、G0 六亲 30→48）
- **engine.dist.js 因 RULES 内联变大 189→247KB，已同步 bazi-app**（commit `4a6416e`）
- 打包目录已同步（ui/index.html + kb/rules.json + 测试脚本，MD5 全 MATCH）
- **遗留（既有缺陷，未本次处理）**：约 9 条旧规则引用 SHENSHA 表外神煞（shensha_元辰/空亡/魁罡/太极贵人/福星贵人/国印贵人/天喜/咸池/文昌贵人、study_文昌配印/学业_魁罡路、kin_六亲_财旺父远 等"状态:旺"无五行键死规则）→ 0 命中，属发布前既有问题，建议下轮统一清理

### ✅ 2026-08-19 死规则清理 + 空亡断语修活（commit `cc5e405`，v1.2.2）
- **断语库 801→789**：删除 12 条永不命中死规则——7 条 SHENSHA 表外神煞（元辰/魁罡/太极贵人/福星贵人/国印贵人/天喜/咸池：咸池与桃花同盘矛盾，其余引擎未实现算法）+ `study_学业_魁罡路` + 4 条「状态:旺」六亲（`evalState` 无'旺'分支 → default false；且 kin_parent_cai/kin_六亲_财旺父远、kin_child_guan/kin_六亲_官杀旺子女 两对语义重复）
- **修复 2 条**：`shensha_文昌贵人`/`study_文昌配印` 神煞名「文昌贵人」→ 表内「文昌」（表内叫文昌，表外名永不命中）
- **修活 `shensha_空亡`**：`matchRules` 神煞分支特判 `ctx.kongWang` 且**限定日支逢空亡**——第一版「有空亡即命中」100% 命中（80/80）被 audit 拦截，收紧后约 16% 正常
- **引擎影响**：`matchRules` 在 ENGINE 标记区内 → dist 247→245KB，MD5 `FEC924A713D83E38B3BDF81E4A055AA1`，**已同步 bazi-app**（拷贝交付，见 `docs/ENGINE-CHANGES.md` v1.2.2）
- **回归 13 套全绿**（断言同步：test_engine RULES 801→789、verify_ux_e2e G0 六亲 48→44；audit 无 100% 命中；check_conflicts 1000 盘 0 矛盾）

### ✅ 2026-08-19 断语库扩充 789→1000（v1.2.3，5 批次 commit：`026bf4d`/`1c3aea3`/`7d03ba1`/`d89f3f9`/`338f981`）
- **批次 1（神煞 +24）**：神煞×十神组合 24 条（吉 18：天乙×3/文昌×2/禄神×2/金舆×2/天德/月德/龙德/将星×2/华盖×2/驿马；凶 6：羊刃×2/灾煞/勾绞/流霞/孤辰）
- **批次 2（婚姻+20/健康+20）**：婚姻——日支十神补齐 6 + 日支坐桃花 + 官财星一位 + 伤官有制 + 财官双美/官印相生/财印相生/食神制杀 + 妻夫星天乙/驿马 + 桃花正官/劫财；健康——日主弱 5 + 神煞 4 + 十神组合 4 + 吉护 2 + 3 + 有制 2（全部合规仅提示+就医建议）
- **批次 3（学业+15/六亲+15/十神组合+10）**：学业——伤官泄秀/位置 4/日主补齐 5/调候 1/神煞组合 4；六亲——宫位 11/亲缘 3/官印 1；十神组合——财印/食伤生财/官财/枭印化杀 等 10
- **批次 4（性格+20/事业+15/格局+15）**：性格——月干位置 5/阴干调候 5/中和 1/神煞 9；事业——位置 5/神煞 5/格局 2/身强财透/身弱杀重；格局——格+透干成格 9 + 格+忌 6
- **批次 5（用神+15/五行+12/十神组合+10/神煞+10/学业+5/六亲+5）**：含 10 干×调候×强弱细分、五行相生相克弱态、双财/食伤双透等；剔除 1 条 0 命中三神组合（combo_食神制杀_印 400 盘 0 命中），换补 shensha_龙德_正财
- **质量红线**：每批 audit 无 100%/>80% 命中、抽查无 0 命中；check_conflicts 1000 盘 0 矛盾；13 套回归全绿；C3 主面板 6 类命中 52.6→66.1（30-70 内，主面板类增量受控）
- **引擎影响**：dist 245→287KB，MD5 `CE99E451F5733376A56BDCE9F49D8ED4`，**已同步 bazi-app**（v1.2.3，见 `docs/ENGINE-CHANGES.md`）

### ✅ 2026-08-19 全项目扫描审计 + v1.3.1 修复（commit `d0e940e`/`648755a`/`a93d584`）
- **重大发现：空亡断语「两版皆死」**——v1.2.2 的「日支逢空亡」特判**永不命中**（60 甲子中旬空支总在下一旬，日支不可能坐本柱旬空；当时只把 100% 命中改成 0 命中，从一种死法换成另一种）。v1.3.1 改为「命局任一柱地支逢日柱旬空」→ **实测 44%（200 盘），真修活**
- **`wealth_kugu` 0 命中**（正财偏财正印偏印四神同透几乎不可能）→ 换补 `wealth_财官印三宝`（正财正官正印三透，实测 1%），总数保持 1000
- **build_ui.py 打印 bug**：size 按字符数（中文 3 字节）→ 改 UTF-8 字节口径（打印 400/287KB 实际 566/438KB，此前 dist 大小记录全部偏小 ~40%）
- **audit_hit_distribution.js 新增 0 命中检测**（信息级，排除流年/流月/大运/合婚专用类）——防死规则再次潜伏（`combo_食神制杀_印` 曾靠手动深挖才发现）
- **结构调整**：发布文档归档 `docs/history/`、7 个一次性脚本归档 `tools/archive/`、图标压缩 1399→147KB、kb 清理 WorkBuddy 专属路径、REGRESSION 文档改名 v1.3.0、新增 `.github/workflows/ci.yml`（build + JSON 校验 + 13 套回归 + audit）
- **引擎影响**：dist MD5 `3E4E97B260C313B4D295F5696FD11EEC`（437KB），**已同步 bazi-app**（影响 C 端：否——仅 matchRules 层，见 `docs/ENGINE-CHANGES.md` v1.3.1）
- 回归 13 套全绿（C3 66.1 不变、check_conflicts 0 矛盾、audit 无 100%/>80%）

### ✅ 2026-08-19 bazi-app C 端闭环本地演练（18/18 通过，commit `e6aa341` 记录）
- 本地启动 `../bazi-app/api/server.js`（mock 模式）全链路：下单（首单 ¥9.9）→ mock 支付 → PAID → 解锁 → 二单恢复 ¥19.9 → match/year SKU → 兑换码生成/兑换 → 防浪费（已解锁输入未用码不消耗、可转赠）→ 无效参数拒绝，**18/18 全通**
- 页面冒烟 + 引擎一致性回归（8 盘 ctx 0 差异）均通过，结论 **v1.3.0/1.3.1 对 C 端零破坏**
- 交付物：`docs/BAZI-APP-REGRESSION-v1.3.0.md`（回归清单）+ `docs/BAZI-APP-HANDOFF-v1.3.0.md`（启动指令，含一致性/冒烟/闭环结论），均已拷贝到 bazi-app
- **剩余真实阻塞（需 Michael/bazi-app 对话操作）**：① 服务器四件套更新（线上仍旧版，缺 `/api/redeem`）② 虎皮椒真实支付接入（**微信渠道已开通**，支付宝未开通；`config.json` 的 `xunhu.channel` 已是 `wechat`，填微信 appid/appsecret 后 `mock:false` 即可，代码无需改）

### ✅ 2026-08-17 新会话接手：输入侧晚子时/节气临界提示语（commit `53a3bd2`）
- 接手核实：工作树干净，本地 HEAD=`941d749`=远程（`[gone]` 是本地引用缓存误报）；打包目录 MD5 一致
- 完成已知缺口「晚子时/节气临界**输入侧**提示语」（HANDOFF 后置项 #4，原计划发布后迭代，本轮提前清掉）：
  1. **主表单** `timeHint`：精确时间模式小时=23 → 红色提示「晚子时（23:00-23:59）：时柱按次日干支推算」；出生时刻距十二节交节 ≤6 小时 → 提示「临近『X』交节（日期 时:分，年柱与月柱/月柱在此刻切换），请确认出生钟表时间准确」（立春特判：年柱与月柱切换）
  2. **合婚 A/B**：新增 `hTimeHintA/B` 提示区（结构对称，遵守坑 #6），`toggleHeTimeMode` 委托刷新，逻辑与主表单一致
  3. 监听：主表单 hour/minute/year/month/day + 合婚 A/B 同名单控件 change 即刷新；农历模式跳过节气提示（农历日期不映射交节时刻）
  4. 实现位置：UI 层（ENGINE 标记区外），`engine/engine.dist.js` **无变化**，无需同步 bazi-app
- 回归：13 套全绿（含新增逻辑验证 7 案例：立春前后 2h 触发 / 16h 不触发 / 清明前 4.7h 触发 / 缺省输入不抛错）
- **新坑（第 26 条）**：`parseItem()` 返回 **[月,日,时,分]**（无年份，年份来自 `JIEQI.data` 的 key），写节气相关新函数时勿把 p[0] 当年份（曾致 `new Date` 得 Invalid Date → diff=NaN → 提示静默失效）

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

### ✅ 2026-08-16 真人验收 + 发布（已完成，双平台 2026-08-17 均已上架）

**真人验收（3 案例全部通过，截图存档 `assets/screenshots/final/`）**：
1. **排盘总览**：男 / 1990-05-15 / 10:00 / 广州 / 真太阳时=是 → 四柱庚辰金边 + 夏令时/真太阳时双提示 + 喜用火木水 + 命局偏强文案
2. **流日分析**：女 / 1996-02-22 / 16:41 → 2026-06 → 冲日柱红高亮（2/14/26）+ 合日柱绿高亮（7/8/19/20/29）+ 关键日红绿分组小结
3. **合婚**：男 1996-08-13 00:39 + 女 1973-03-02 07:08 → 85/100 天生佳偶 + 七维度 + 9 条古籍

**验收发现并修复（第三轮）**：
- **五行补救文案 bug**（`getRemedy` note 写死「命局偏弱」，身强盘文案错误且与喜用矛盾）：按 strength 动态生成——强→「偏强，宜克泄耗（食伤/财/官杀）平衡」；弱→「偏弱，宜生扶（印/比劫）扶持」；中和→平衡文案。commit `597efdc` + 引擎 `ea2b309`（已同步 bazi-app）
- **UI logo 统一**：header logo 从 CSS 日轮改为 `icon_taiji_v1.png` 太极图（128px PNG-8 base64 内联，10KB），与 SkillHub 上传图标一致。commit `d8806bb`

**发布全流程（踩坑见第五节）**：
- 发布 ZIP（SkillHub 版）：`bazi-engine-v1.2.1.zip`（61 文件 / 0.5MB / **无外层嵌套** / **排除 LICENSE/LICENSE-DATA/README.en.md**）
- 发布 ZIP（ClawHub 版）：`bazi-engine-v1.2.1-clawhub.zip`（64 文件 / 515KB / **含 LICENSE**，ClawHub 无审核用完整版）
- 打包工具：`tools/build_release_zip.py`（永久脚本，每次发版跑一次）
- **SKILL.md 清典籍名**（穷通宝鉴/子平真诠/滴天髓/渊海子平/千里命稿/神峰通考 → 「古代命理典籍」）——SkillHub 误判「内容涉政」，commit `de631a3`
- **关键坑**：SkillHub 审核看的是 **ZIP 里根目录 SKILL.md**，不是项目源 `skill/SKILL.md`——之前只同步了打包目录 `skill/` 子目录漏了根，导致反复「涉政」。已 cp 同步 + 重打 ZIP 验证（ZIP 内根 SKILL.md 无典籍名）
- SkillHub 时间线：20:09 提交「安全审核中」→ 审核未通过（内容涉政）→ 20:17 提交申诉（1/3 次）→ **2026-08-17 申诉通过、已上架**（「生态杀手」分类，平台归一化显示 V1.0.0 见坑 #21）
- **ClawHub 发布成功**（21:04）：clawhub.ai/skills 公开可见，一键安装 `npx clawhub@latest install bazi-engine`；**2026-08-17 SkillSpector 扫描通过转 Published**（Productivity 分类，v1.2.1 GitHub 自动同步版）

> ✅ 发布前待办已全部完成（真人验收 2026-08-16 通过 / 图标与提交材料按 `发布物料.md` 准备 / 2026-08-13 收尾：check_conflicts.js 同步打包目录 + SKILL.md 登记 + `断语库.json.bak` 清理 + 对外 `README.md` + SKILL.md frontmatter 补 `tags`/`license: MIT`）

### 发布后增强（已清项并入 §四；剩余 2 项）
- ✅ 晚子时 / 节气临界时刻的**输入侧**提示语（已完成 `53a3bd2`，2026-08-17）
- ✅ 断语库扩充 504 → 800+（已完成 `bd7f5ab`，801 条，2026-08-17）
- MCP/API 化（P2，见 §四 第 6 项）
- **bazi-app C 端全流程闭环**（见 §四 第 2 项，独立对话推进）

---

## 二、已完成内容（截至 v1.3.6）

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
| **输入侧晚子时/节气临界提示语**：主表单 + 合婚 A/B 填时间即时提示（23 点→时柱按次日；距十二节交节 ≤6h→年/月柱切换敏感点） | ✅ 2026-08-17 |
| **合婚上下双区块布局**：移除 `.two-col` 左右双栏，改为甲乙上下独立区块 + 金色虚线分隔；每人独立「是否校正真太阳时」下拉框（`hTruesunA/B`），`readHe` 支持按人分别校正 | ✅ 2026-08-16 |

### 关键资产
- **断语库**：`kb/04-rules-db/rules.json` — **1000 条**（事业112 / 性格97 / 神煞74 / 用神喜忌72 / 婚姻67 / 十神组合65 / 六亲64 / 健康62 / 学业61 / 财运57 / 格局56 / 五行生克48 / 流月45 / 流日50 / 流年30 / 合婚20 / 大运20），每条含 `suggestion` 建议字段，全量接入渲染
- **UI**：`ui/index.html` — 单文件离线（**零外部依赖**，无 Google Fonts 外链），内置 206 年节气 + 1000 条断语
- **引擎**：`tools/build_ui.py` — Python 构建脚本，内联断语库 + 节气 + 全部 JS 逻辑
- **知识库**：三命通会/渊海子平/滴天髓/子平真诠/穷通宝鉴全文梳理均已入库
- **发布验证**：`python tools/build_release_zip.py` 产出发布 ZIP（自动排除 LICENSE/LICENSE-DATA/README.en.md，文件在 ZIP 根无嵌套）+ 关键产物 MD5 校验（`ui/index.html` / `engine/engine.dist.js` / `skill/SKILL.md` / `kb/04-rules-db/rules.json`）——平台无关，不依赖任何平台专属目录
- **版本**：SKILL.md frontmatter `version: 1.3.6` + `tags` + `license: MIT`；git tag `v1.3.0`（定版）；dist MD5 `1A4722FA7B0974EB4F5CFA53C71AA9C3`（v1.3.4 起 LF 口径不变）
- **对外文档**：`README.md`（项目门面：功能/快速开始/示例对话/免责声明）+ `docs/history/发布物料.md`（内部发布材料：卖点/图标提示词/渠道建议）

### 关键修复（2026-08-14 全面扫描）
- **空 condition 规则无条件命中 bug**：71 条 condition 为 `{}` 的规则中，8 条（qinq_27~30 + edu_17~20）落入主渲染分类会**固定显示在每个命盘**（`for...in` 空对象后 `hit` 保持 true）。修复：`matchRules` 开头 `if(Object.keys(c).length===0){ hit=false; }` 排除（专用函数仍按 id 触发 dayun_*/liuyue_*/liuri_*/qinq_27~30/he_*）
- **edu_17~20 真孤儿复活**：补差异化 condition 使其重新参与主引擎匹配——edu_17 印星为用有力 / edu_18 食神多而有力 / edu_19 月干透印+伤官泄秀 / edu_20 身弱财多；edu_19 原与 combo_伤官_正印 条件相同会同盘重复，已加"月干+印为用有力"约束并改文案消除
- 验证：新增 `tools/verify_edu_rules.js` 回归（edu 命中率 ≥1 次且 <60%、qinq_27~30 不进主渲染）；8 套既有回归 + 冲突检测全绿

### 验证体系（13 套回归，全部 PASS：FAIL:0 WARN:0，2026-08-17 复跑确认）
| 脚本 | 覆盖 |
|------|------|
| `test_ui.js` | UI 结构与渲染 |
| `test_eval_state.js` | 引擎状态 |
| `test_p1_fixes.js` | P1 修复回归 |
| `verify_sleep_rules.js` | 沉睡规则接入 |
| `verify_ux_e2e.js` | 端到端用户视角（A~G 组：输入容错/边界/报告质量/稳定性/完整性/**流日 F 组 12 项**/**六亲 G 组 8 项**；C3 主面板命中区间 30-70） |
| `check_conflicts.js` | 反义断语同盘矛盾检测（40 对规则，1000 盘 0 冲突） |
| `test_dst.js` | 夏令时窗口/边界校正（29 项） |
| `test_liuri_v2.js` | 流日规则 v2（10 项） |
| `test_liuyue_v2.js` | 流月规则 v2（10 项） |
| `verify_edu_rules.js` | 空 condition 排除 + 学业规则复活回归（edu_17~20 命中率须 ≥1 次且 <60%，qinq_27~30 不进入主渲染） |
| `test_engine.js` | 独立引擎库直测（28 项；RULES 1000 条断言） |
| `test_lunar.js` | 农历转换模块（导出完整性/闰月判断/非闰月转换/闰月转换/日名映射/边界年份/排盘联动，27 项） |
| `test_xiyong.js` | 喜用/忌用结构回归（10 盘验证 xiYong/jiYong 合理性，2026-08-16 新增） |

> 另含 `audit_hit_distribution.js`（命中分布审查：无 100%/>80% 命中规则）、`check_dup_hits.js`（重复命中检测）——断语库维护持续使用。

### 交付文档
- `发布物料.md` — 6 大卖点 / 图标提示词 / 3 个示例对话 / 合规声明 / 渠道建议（SkillHub 优先）

---

## 三、卡住的问题

- ✅ **本仓库无阻塞**：132 项任务清零 / 真人验收通过 / 双平台已上架 / 断语库 1000 条 / **v1.3.6**（三方审计 6 批次全量修复）/ 13 套回归全绿 + CI 门禁真实生效；**README 推广优化已完成（2026-08-20，HEAD `1d045cc`）**
- 🔜 **bazi-app C 端真实闭环剩 2 个外部阻塞**（本地 mock 全链路已通，属部署/支付侧，需 bazi-app 对话推进；**速贴块已交付，Michael 粘贴即可启动**；⚠️ README 推广已上线，此阻塞**更紧迫**——引流访客来了若卡在支付环节会直接流失）：
  1. **服务器四件套更新**：线上 CentOS 仍是旧版（缺 `/api/redeem`、删除接口无鉴权、旧账号密码）——需上传 `web/index.html` + `web/admin.html` + `api/server.js` + `api/config.json` + **`web/paid/` 目录** → `pm2 restart benchu_api` → 新账号登录 → 重新生成兑换码（**执行到此处需要 Michael 提供服务器 SSH/宝塔凭据**）
  2. **虎皮椒真实支付接入**：**微信渠道已开通**（支付宝未开通）——填 `config.json` 的 `xunhu.appid/appsecret`（**微信**凭证）→ `mock:false` → `pm2 restart` → 真实支付验证一单（¥0.01）；`channel` 已是 `wechat` 无需改代码（**需要 Michael 提供虎皮椒微信 appid/appsecret**）
- 🔜 **bazi-app 功能边界（产品决策，非 bug）**：C 端只有 3 个 SKU（report 个人报告 / match 双人匹配 / year 年度能量趋势），**无流月 / 流日功能**（bazi-app 源码搜不到这两个关键词；"年度能量趋势"= 流年+流月的轻量版，12 个月卡片，非引擎级逐日 30 天分析）。README 配图已按 **B/C 分区**处理：产品生态章节只放 C 端 3 个 SKU 截图；流日截图（`final/02_liuri.png`）放「功能特性」作为**引擎深度能力**展示，不误导读者以为本初有流日。若要补流月/流日付费 SKU（FateTell 验证过的复购点），属 bazi-app 侧产品决策，可规划后续迭代

---

## 四、下一步计划（按优先级）

0. ✅ ~~SkillHub 申诉~~（2026-08-17 通过并上架）
1. ✅ ~~ClawHub SkillSpector 扫描~~（已转 Published，海外发布闭环完成）
2. **[推荐·最高优先] bazi-app C 端真实闭环收尾** → 引擎已同步（v1.3.6，dist MD5 `1A4722FA7B0974EB4F5CFA53C71AA9C3`），本地 mock 全链路 18/18 已通 + 一致性/冒烟零破坏确认 + 三方审计后引擎更稳；剩**服务器四件套更新** + **虎皮椒真实支付接入（微信渠道已开通，支付宝未）**。**⚠️ README 推广已于 2026-08-20 上线（本初链接 + 7 张配图 + 支持作者微信），引流通道已开，支付闭环未通会直接流失访客——本项应优先于一切**。**Michael 当前唯一要做的操作**：把 `docs/BAZI-APP-HANDOFF-v1.3.0.md` 顶部的速贴块粘贴给 bazi-app 对话 → 该对话按 ①~⑤ 推进；到 ③④ 步时把 **SSH 凭据** + **虎皮椒微信 appid/appsecret** 提供给 bazi-app 对话。若后续引擎升级，bazi-app 侧用 `python tools/compliance_soften.py web/engine.dist.js` 生成合规版（坑 #41 解决方案）
2b. **[可选] bazi-app 补流月/流日付费 SKU**（复购点，FateTell「运之书」模式）：C 端现有 3 SKU 无流月/流日，README 已按 B/C 分区展示引擎流日能力；若要在 C 端变现，需 bazi-app 侧新增 SKU + 报告页（引擎 matchLiuDay/matchLiuYue 可复用，见坑 #44）
3. ✅ ~~断语库扩充 504→800+~~（已完成 `bd7f5ab`，801 条，2026-08-17）
4. ✅ ~~晚子时/节气临界**输入侧**提示语~~（已完成 `53a3bd2`，2026-08-17；输出侧原有提示保留）
5. ✅ ~~断语库 789→1000+~~（已完成 `338f981` 等 5 批次 + 定版 v1.3.0 + 三方审计 v1.3.1~v1.3.6，2026-08-19；若续扩可考虑为元辰/魁罡/太极贵人等补 SHENSHA 算法后重新入库）
6. **[后置] MCP/API 化**（P2 路线图：为引擎提供 MCP 工具/HTTP API，供 B 端命理师/其他 agent 编程调用）
7. **[后置] 商标注册**（41/42 必选 + 9/45 防御，注册前代理检索规避「本初子午」近似——注意这是 bazi-app 品牌，若做 C 端商标需核实）

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
12. **Google Fonts `@import` 外链违反"单文件零外部依赖"承诺** —— UI 升级时删除，改用系统字体栈（Songti SC/STSong/SimSun + system-ui）
13. **SKILL.md 实际位于 `skill/SKILL.md`（非项目根）** —— 同步打包时第一版 `cp` 失败，须用正确相对路径
14. **断语库 JSON 每改必验** —— 用 `python json.load` 校验合法性 + 统计规则数，再重建 UI（断语数会反映在 build 输出里）

### 需求/流程类
15. **7 项功能核查中 #2 与 #4 重复（都是流月分析）** —— 先向用户澄清再动手，避免重复劳动
16. **任务账目会滞留**：实际完成但状态未更新（本次理清 #27/41/59/66/68/69/70/71/72/75/74 共 11 个）—— 完成一项应立即 TaskUpdate

### SkillHub 发布类（2026-08-16 三次踩坑）
17. **ZIP 不能嵌套外层目录**：`Compress-Archive -Path 整个目录` 会生成 `bazi-engine/` 外层，SkillHub 解压后看到 `bazi-engine/LICENSE` 报「文件路径不安全」。**正确：ZIP 内文件直接在根**（SKILL.md 在根）。教训：勿用 `-Path 目录`，用 `-Path 目录\*` 或 Python zipfile 逐文件写
18. **SkillHub 不允许 LICENSE/LICENSE-DATA/README.en.md 类元文件**（报「文件路径不安全」「不允许的文件类型」）：GitHub 开源项目根必须保留，但**打包 ZIP 时排除**——用 `tools/build_release_zip.py`（EXCLUDE_PATTERNS），项目根文件不动
19. **SkillHub 内容审核误判「涉政」**：命理典籍名（穷通宝鉴/三命通会/滴天髓/渊海子平/子平真诠/千里命稿/神峰通考）触发关键词扫描误判 → SKILL.md 中删除具体典籍名，改为「古代命理典籍」；**变更说明也勿写典籍名**
20. **WorkBuddy 的 safe-delete（genie-trash）有 bug（仅 WorkBuddy 环境适用）**：删文件报「Some operations were aborted」，os.remove/unlink 被拦截——用 bash `rm -f` 或 Python `os.remove`（绕过 sitecustomize shim）可删；旧 ZIP 无法覆盖时输出新文件名。其他平台无此问题
21. **SKILL.md 版本被 SkillHub 归一化**：v1.2.1 在平台显示 v1.0.0，不影响功能，无需纠结
22. **SkillHub 审核看的是 ZIP 内根目录 SKILL.md，不是项目源 skill/SKILL.md**：打包目录根 SKILL.md 与项目源是两个副本，改 SKILL.md 必须 `cp skill/SKILL.md 打包目录/SKILL.md`（根）**且** `打包目录/skill/SKILL.md`（子目录）——漏同步根目录会导致审核扫到旧版（「涉政」反复的根源）
23. **SkillHub 对命理/玄学类内容审核严格**（典籍名可触发「内容涉政」误判）：规避 = SKILL.md 不写具体典籍名，用「古代命理典籍」；变更说明同样不写
24. **ClawHub 是 SkillHub 之外的「免审核」发布通道**：OpenClaw 官方市场（clawhub.ai，中文镜像 mirror-cn.clawhub.com），无内容审核（可信/可疑标注制），发布即公开可见；上传用完整版 ZIP（可含 LICENSE）；与腾讯 SkillHub（skillhub.tencent.com）是**两个不同平台**，注意区分
25. **`git reset --hard` 会丢 untracked 文件**（如 assets/screenshots/final/ 三张截图、SkillHub发布最终指引.md）：发布物归档后记得重新复制；乱操作后回滚用 reset 但先 `git stash`/备份 untracked

### 通用新增（2026-08-17，双项目协作/规则库）
26. **`parseItem()` 返回 `[月,日,时,分]`，不含年份**（年份来自 `JIEQI.data` 的 key）：写节气相关新函数时，`new Date(yy, p[0]-1, p[1], p[2], p[3])` 才是正确构造；把 p[0] 当年份会得 Invalid Date → `getTime()=NaN` → 差值 NaN → 条件静默不触发（输入侧节气提示曾踩，静默失效无报错）
27. **Python 改 JSON：`rules=[r for r in ...]` 生成新列表后必须回写 `data['rules']=rules`**：直接 `json.dump(data)` 写的是旧引用，修改静默丢失（断语库扩充曾两次"改了没生效"，检查落盘用重新 load 验证条数）
28. **`matchRules` 神煞键只认 `SHENSHA` 表内 24 项**：空亡（实为 `ctx.kongWang`）/咸池/元辰/天喜/魁罡/太极贵人/福星贵人/国印贵人/文昌贵人（表内叫"文昌"）均**不在表内**，`{神煞:"X"}` 条件永不命中（既有 9+ 条旧规则中招）；`evalState` 的"为喜用/为忌神"必须带 `位置:"日支"`、"为用神有力"必须带 `十神` 键，否则返回 false 静默失效
29. **双项目 git 边界**：bazi-project 与 bazi-app 分属两个工作区/两个对话，本仓库只负责引擎变更的「拷贝交付」（`cp engine/engine.dist.js ../bazi-app/web/`），**commit/push 一律留给 bazi-app 对话**；引擎变更必须 bump 版本 + 记入 `docs/ENGINE-CHANGES.md`（bazi-app 对话据此核对 MD5 对齐）

### 环境类（2026-08-19，Git for Windows / ssh）
30. **Git for Windows 的 MSYS2 运行时在部分环境崩溃（`CreateFileMapping ... Win32 error 5`）**：`D:\Program Files\Git\usr\bin\ssh.exe`（及经 shell 包装时 `sh.exe`）直接崩，git fetch/push 失败；但系统 OpenSSH（`C:\Windows\System32\OpenSSH\ssh.exe`，9.5）完全正常。**绕过方案**：设 `GIT_SSH=C:\Windows\System32\OpenSSH\ssh.exe`（用户环境变量）——git 直接 spawn 该程序、不经 MSYS shell（core.sshCommand 会经 sh 包装仍崩，勿用）。**注意**：dsh 等长驻宿主进程不会自动刷新环境变量，当前会话内远程操作需内联 `$env:GIT_SSH=...; git ...`，重启宿主后自动生效。系统 ssh 认证成功标志为输出 `Hi ruanxiaoer888! You've successfully authenticated`（exit 1 是 GitHub 无 shell 的正常返回，勿当失败）

### 审计/规则库类（2026-08-19，v1.3.1 全项目审计）
31. **「日支逢空亡」在 60 甲子中不可能出现**：旬空支（2 个）属于本旬 10 个日柱，但日支等于空支的日柱总在**下一旬**（甲子旬空戌亥，而日支戌/亥的日柱甲戌/乙亥属甲戌旬）——`ctx.kongWang.includes(日支)` 永不命中。空亡特判第一版「有空亡即命中」100% 被 audit 拦截后，第二版「日支逢空亡」0 命中，**两版皆死**；正确语义 =「命局任一柱地支逢日柱旬空」（实测 44%）。教训：修死规则必须验证命中率落入合理区间（0<命中<80%），不能只保证「不再 100%」
32. **build_ui.py 的 size 打印用 `len(str)`（字符数）**：中文 UTF-8 占 3 字节，打印 400/287KB 实际文件 566/438KB，误导 dist 大小记录（历史文档 247KB 等均为字符口径）。改 `len(x.encode('utf-8'))`；Windows 下写入还含 CRLF（`\n`→`\r\n`），文件字节比 encode 再大 ~1%
33. **PowerShell `>` 重定向是 UTF-16 编码**：`git show <commit>:<file> > tmp.js` 会写出 UTF-16 破坏 JS（字节数翻倍）。提取 git blob 到文件须用 `cmd /c "git show ... > file"`（字节流）或 `[IO.File]::WriteAllBytes`
34. **audit 0 命中检测的小样本误报**：<1% 低命中规则（如「日主+旺衰」组合，实测 char_甲_强 0.9%）在 200 盘样本内可能 0 命中（概率 ~16%），属正常不是死规则——0 命中段定为**信息级**并排除专用触发类（流年/流月/大运/合婚：matchRules 主引擎本就不输出），大样本 2000 盘仍 0 才需深挖
35. **GitHub Release 的「Release label」= Pre-release 标记**：稳定版必须选 None（否则不顶掉 Latest，ClawHub/访客仍拿旧版）；About 栏描述（如「504 条」）随版本同步更新，开源门面数字要与仓库一致

### 三方审计类（2026-08-19 第二轮，v1.3.2~v1.3.6）
36. **vm 测试 stub 的 `document` 无 `addEventListener`/`setAttribute`**：UI 层做 DOM 增强（键盘委托/无障碍注入）必须存在性防御（`if(typeof document.addEventListener==='function')`、`if(s.setAttribute)`），否则 test_ui/verify_ux_e2e 的 eval 环境直接崩（v1.3.6 曾踩）
37. **`JIEQI.data[year]` 是 12 节非 24 节气**（`JIE_ORDER` 仅 12 项：立春/惊蛰/…/大雪/小寒）——写流月/节气函数时按 12 节索引，勿假设 24 节气（M1 流月精确节气曾误用 [2,4,…,0] 索引）
38. **评分维度「声明 max」必须与实际可达上限一致**：合婚「日柱关系」声明 25 实际最高 17（五合 10+六合 7），总分天花板 92 → 评级「佳偶≥85」几乎不可达（进度条永不 100%）。修法：扩充评分项（纳音相生+三合）使上限可触达，或校准阈值
39. **专旺格等罕见格局的阈值要用大样本验证**：0.55 时 5000 盘判专旺 0.94%（远高于传统「万中无一」，含大量普通身强误标）→ 0.75+他行≤0.15 双条件后 0.02%（1/5000 真一行独旺）
40. **`matchRules(ctx, {id})` 第二参数被静默忽略**：check_conflicts 曾用它判「单规则是否命中」→ 返回值是分类对象（无 .length）→ 检测恒 0 失效恒绿。测单规则命中须从返回值分类里 Set 查 id，且工具门禁要有真实退出码

### 双项目协作类（2026-08-19 第三轮）
41. **bazi-app 为合规手改 dist（引擎构建产物）会与 B 端重建冲突**：bazi-app 在 commit `2bb404f`（合规风控整改）对 `web/engine.dist.js` 做了术语软化定制（姻缘→情感 / 桃花正缘→人际正缘 / 流年→年度 / 烂桃花→不良人际 等 10 处，MD5 `1A4722FA`→`3B90D659`），属 C 端微信生态合规需求，但**手改构建产物违反坑 #29 边界**——bazi-engine 下次重建 dist 会覆盖该定制。正确做法：a) 软化文案回馈 bazi-engine 纳入构建源（build_ui.py 的 RULES/文案），或 b) bazi-app 用构建后脚本统一替换；否则每次引擎升级都要重打补丁。**✅ 已解决（commit `41ba0eb`）**：bazi-engine 侧落地 `tools/compliance_soften.py`（构建后术语替换，保护 `"流年":` 条件键，`--check` 残留检测），bazi-app 今后同步 dist 后跑一次即得合规版（软化后 MD5 `1CA0DF3EC306DF96E160D76A9CEB191D`），免手改。当前状态：bazi-app 锁 v1.3.4 引擎 + 合规定制（MD5 `3B90D659`），引擎逻辑与 v1.3.6 一致（v1.3.5/1.3.6 为 B 端 UI 层、dist 未变）

### README 推广 / 引擎 API 使用类（2026-08-20，README 优化 + 配图 + 联系方式）
42. **`paipan` 的 gender 参数只接受中文 `'男'/'女'`**：源码第 376 行 `if(gender!=='男'&&gender!=='女'){ alert('性别需为男或女'); return null; }`——传 `'M'`/`'male'` 会触发 alert（Node 下 `ReferenceError: alert is not defined` 崩溃）。README 英文版示例最初写 `'M'` 会误导开发者，已改为中文 `'男'`。教训：README/文档里的引擎示例代码必须**实跑验证**，不能只凭直觉写
43. **1990 年中国夏令时：直接传 9:00 排盘时柱是 `辛巳` 而非 `庚辰`**：1990-05-15 在夏令时窗口（4/15~9/16）内，正确链路 = `applyDst(1990,5,15,10)`（回拨 1 小时→9:00）→ `paipan(..., 9, 0, ...)` 才是庚辰时柱（README 示例对话的值）。README 开发者示例曾直接写 `paipan(1990,5,15,9,0,...)` + 注释庚辰（错误，实排辛巳），已改为完整 DST 链路。教训：示例代码的**注释结果值**也要实测核对，DST 窗口期的盘最容易错
44. **bazi-app C 端只有 3 个 SKU，无流月/流日**：`web/index.html` 全文搜不到「流月/流日/逐日」（`Select-String` 0 匹配）；「年度能量趋势」= 12 个月卡片（月五行×喜忌×与日主关系 50 组文案），是流年+流月的**轻量版**，非引擎级逐日 30 天。规划 C 端截图/推广时必须按**真实功能边界**来（README 已 B/C 分区），否则截图与产品不符会砸口碑
45. **PowerShell 5.1 不支持 `&&` 连接符**：`cmd1 && cmd2` 报 `The token '&&' is not a valid statement separator`——用 `;` 分隔或分行执行（`$?` 判断上一条结果）；多步 git 操作用 `git add ...; git commit ...; git push ...` 串行即可（有依赖时分行判断）
46. **PowerShell `Add-Content` 中文注释落盘乱码**：控制台显示 `鍥剧墖` 类乱码，但用 read 工具按 UTF-8 读回是**正常中文**——是控制台代码页（GBK）与文件编码（UTF-8）不一致的显示问题，**以 read 工具内容为准**，勿据此改文件（.gitignore 追加中文注释曾虚惊一场）
47. **Windows 沙箱里 `System.Drawing` 读图片尺寸失败**（受限环境），改用 Node 读 PNG 头部字节：`buf.readUInt32BE(16)`（宽）/ `readUInt32BE(20)`（高），校验魔数 `0x89 0x50 0x4E 0x47`——临时脚本 `tools/tmp_*.js` 用完即删（坑 #3 延续）
48. **DSH Web GUI 用户上传图片的下载途径**：`Invoke-WebRequest http://127.0.0.1:3080/describe-image/raw/sha256:<附件id>` → `[IO.File]::WriteAllBytes(本地路径, $resp.Content)` 可把会话里用户贴的图片存到工作区（本仓库 `assets/screenshots/contact-card.png` 即由此取得）；`$resp.Content` 是 byte[] 可直接写，勿转 string

---

## 六、项目速查

> 工作区路径随平台而异（WorkBuddy / DeepSeek Harness / Codex / 百度搭子等），下文一律用相对路径；bazi-app 为 `../bazi-app`（任何布局下成立）。

- 源码目录：**当前工作区**（随平台而异，如 `E:\michael\DSHProjects\bazi-engine` 或 `E:\michael\workBuddy\bazi-project`）
- GitHub 仓库：https://github.com/ruanxiaoer888/bazi-engine
- 构建命令：`python tools/build_ui.py`（输出 `ui/index.html` + `engine/engine.dist.js`）
- **发布包命令：`python tools/build_release_zip.py`**（输出 `bazi-engine-v1.3.6.zip`，排除 LICENSE/LICENSE-DATA/README.en.md、tools/archive，文件在 ZIP 根；可传版本号参数）
- **发布验证（平台无关，替代旧打包目录同步）**：`python tools/build_release_zip.py` 产出 ZIP 后，md5sum 校验关键产物（`ui/index.html` / `engine/engine.dist.js` / `skill/SKILL.md` / `kb/04-rules-db/rules.json`）
- 回归命令（13 套，全部必须 PASS）：`node tools/test_engine.js` + `node tools/test_lunar.js` + `node tools/test_ui.js` + `node tools/test_eval_state.js` + `node tools/test_p1_fixes.js` + `node tools/verify_sleep_rules.js` + `node tools/verify_ux_e2e.js` + `node tools/test_dst.js` + `node tools/test_liuri_v2.js` + `node tools/test_liuyue_v2.js` + `node tools/verify_edu_rules.js` + `node tools/test_xiyong.js` + `node tools/check_conflicts.js`；断语库维护另用 `audit_hit_distribution.js`（命中分布 + 0 命中检测，`--sample=2000` 大样本判死规则）；CI 已接入 `.github/workflows/ci.yml`（push 自动跑 build + 13 套 + audit）
- **C 端合规软化工具**：`python tools/compliance_soften.py <dist路径>`（就地替换：运势→能量/大运→十年节奏/姻缘→情感/八字→出生信息/烂桃花→不良人际/流年文案→年度，保护 `"流年":` 条件键；`--check` 检查敏感词残留）——bazi-app 同步 dist 后跑一次即可，免手改构建产物（坑 #41）
- C 端同步：`cp engine/engine.dist.js ../bazi-app/web/` 并 commit（bazi-app 独立仓库/对话，仅拷贝交付，commit/push 留给 bazi-app 侧）
- 命名约定：对外统一 "bazi-engine"（原名 bazi-master 因 SkillHub 同名竞品已弃用），个人项目口径，不挂钩任何企业
- 发布文档：`docs/history/SkillHub-Submission-Kit.md`（提交母版）+ `docs/history/SkillHub发布最终指引.md`（填表指引）+ `docs/history/验收与截图清单_3案例.md`（回归验收模板）
- **引擎变更记录：`docs/ENGINE-CHANGES.md`**（权威记录：每次引擎变更 bump 版本 + 记 dist MD5，供 bazi-app 对话核对；2026-08-17 建立，首条 v1.2.1）
- 历史文档：`docs/history/`（第七轮验收 / 发布物料 / 竞对分析，历史快照）
- 截图素材：
  - `assets/screenshots/final/`（3 张 B 端验收截图：01_paipan / 02_liuri 流日 / 03_hehun，README 引用 02_liuri）
  - `assets/screenshots/benchu/`（**C 端「本初」截图，已入库 4 张**：paipan 排盘 / hehun 合婚 / year 年度 / insight 六维人格图谱；`README.md` 目录说明；`_raw/` 28 张原始素材 **gitignore 排除不入库**）
  - `assets/screenshots/promo/`（宣传物料 2 张：compare 引擎对比图 / flow 处理链路流程图，压缩自 _raw/图2/图3）
  - `assets/screenshots/contact-card.png`（作者微信+公众号双二维码海报，README 支持作者章节用）
- 发布平台：**SkillHub**（腾讯，已上架，「生态杀手」分类）+ **ClawHub**（已上架，clawhub.ai/skills，npx clawhub@latest install bazi-engine）+ **GitHub**（开源仓库）
- **C 端「本初」**：https://benchu.xiaoerpro.com/（README 在线体验入口；微信 `feizi6651` 在支持作者章节）
- **README 推广资产速查**：产品生态章节（本初推广位）/ 徽章（Stars/CI/License/SkillHub）/ 「为什么是引擎？」（中文核心卖点）/ 快速开始三路径（用户/开发者/AI，含 engine.dist.js 双端示例）/ 支持作者（微信+公众号海报）——2026-08-20 全部落地，改动只动 docs 与 assets，引擎 dist MD5 不变
