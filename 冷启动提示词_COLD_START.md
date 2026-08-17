# bazi-engine 项目冷启动提示词

> 用途：切换到新 WorkBuddy 账号时，把下面【提示词】整段复制粘贴给新账号即可冷启动。
> 新账号 AI 会自动读项目真相源（HANDOFF.md）核实状态，无需用户再补充背景。

---

## 【提示词】（从这里开始复制）

我是 Michael，独立开发者（个人身份，不挂任何公司品牌）。现在接手我的 B 端八字排盘引擎项目 **bazi-engine**，工作目录 `E:\michael\workBuddy\bazi-project`。

**接手第一步（必须做）**：
1. 先读 `E:\michael\workBuddy\bazi-project\HANDOFF.md`——它是项目真相源，包含完整状态（当前任务、已完成内容、卡住问题、下一步计划、踩坑 18+ 条）。所有决策以它为准。
2. 再读 `E:\michael\workBuddy\bazi-project\AI_CONTEXT.md`——冷启动补充（技术架构/引擎 API/关键决策/协作偏好）。
3. 核实 git 真实状态：`cd E:\michael\workBuddy\bazi-project && git status --short && git log --oneline -5`（远程显示 `[gone]` 是本地引用缓存误报，遇到推送问题先 `git fetch origin`）。

**项目背景（一句话）**：
- bazi-engine = 确定性四柱八字排盘引擎（开源 MIT），输入出生信息 → 四柱/大运/流年/流日/六亲/合婚/五行补救，全程标注古籍出处
- 双轨战略：B 端引擎（本仓库，开源引流）+ C 端产品 `E:\michael\workBuddy\bazi-app`（「本初」，付费变现，另设对话推进）
- 技术栈：`ui/index.html` 单文件离线 UI（零依赖）+ `engine/engine.dist.js` UMD 引擎库 + `tools/build_ui.py` Python 构建 + `kb/` 知识库（31 文件，504 条断语）
- 打包目录：`C:\Users\34743\.workbuddy\skills\bazi-engine\`（发布源，与源码 MD5 同步校验）

**当前状态（2026-08-17）**：
- ✅ 功能全部完成（132 项任务清零），13 套回归全绿（test_engine/test_lunar/test_dst/test_ui/test_eval_state/test_p1_fixes/verify_sleep_rules/test_liuri_v2/test_liuyue_v2/verify_edu_rules/check_conflicts/verify_ux_e2e/test_xiyong）
- ✅ 真人验收通过（3 案例：排盘 1990-05-15 / 流日 1996-02-22 / 合婚 1996-08-13+1973-03-02）
- ✅ **ClawHub 已发布双版本**（v1.0.0 ZIP 手动版 + v1.2.1 GitHub 自动同步版——绑定 ruanxiaoer888/bazi-engine，git push 后自动同步）
- 🔄 **SkillHub 申诉中**（被误判"涉政"→ 已清 SKILL.md/README.md 典籍名 + 修 ZIP 根 SKILL.md 不同步，申诉 1/3 次等回复；不通过换 Coze 扣子/Dify）
- ⏳ 等 SkillHub 申诉回复（1~3 工作日）；ClawHub Needs review 转正

**接手后任务（按优先级）**：
1. 若 SkillHub 申诉有结果 → 通过则申请提升全局市场；被拒则按拒绝理由针对性改（若回复"kb 文件触发"→ 说明 SkillHub 不适合命理类，直接走 ClawHub/Coze）
2. 断语库扩充 504→800+（复用 `kb/04-rules-db/drafts/` 取材方法论）
3. 晚子时/节气临界**输入侧**提示语（已知非阻塞缺口）
4. MCP/API 化（P2 路线图）
5. 商标注册（41/42 必选 + 9/45 防御，注册前代理检索规避「本初子午」近似——注意这是 bazi-app 的品牌，若做 C 端商标需核实）

**红线约束（不可违反）**：
- **引擎**：`engine/engine.dist.js` 是构建产物，**勿手改**；新增引擎函数写进 `tools/build_ui.py` 的 `// [ENGINE:BEGIN/END]` 标记区内
- **SKILL.md 典籍名**：SkillHub 发布版不写具体典籍名（穷通宝鉴/子平真诠等触发"涉政"误判），用「古代命理典籍」；内部文档/KB 保留
- **发布打包**：用 `python tools/build_release_zip.py`（自动排除 LICENSE/LICENSE-DATA/README.en.md，文件在 ZIP 根无嵌套）
- **合规**：命理输出保留"仅供娱乐文化参考"免责，不做健康/疾病断言、不做改运消灾收费
- **HANDOFF.md 是真相源**：写之前必须核实真实状态（git log + 文件版本），不能凭记忆

**技术约定**：
- 构建：`python tools/build_ui.py`（输出 `ui/index.html` + `engine/engine.dist.js`）
- 回归：`node tools/test_engine.js` 等 13 套（命令见 HANDOFF 第六节）
- 打包目录同步：文件 cp 到 `~/.workbuddy/skills/bazi-engine/` 后 md5sum 校验（README.md/README.en.md/SKILL.md/build_ui.py/ui/index.html/各测试脚本）
- **引擎同步到 C 端**：`cp engine/engine.dist.js ../bazi-app/web/` 并 commit（bazi-app 有独立对话，改引擎后通知）
- 每完成一个任务 commit，commit message 用中文描述清楚

---

## 使用说明

1. 复制上面【提示词】到新账号第一句话
2. 新账号应自动读 HANDOFF.md + AI_CONTEXT.md 并核实 git 状态
3. 之后正常对话推进（SkillHub 申诉跟进 / 断语库扩充 / 迭代都行）

**提醒**：HANDOFF.md 会随项目推进更新，切换账号时如果隔了很久，先看一眼 HANDOFF 更新时间戳，过时的话让新账号先更新它再干活。
