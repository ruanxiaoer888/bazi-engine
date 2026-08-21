# bazi-engine · 四柱八字命理引擎

一个开箱即用的八字排盘与命理分析 Skill：输入出生信息，自动排出四柱八字、大运流年，并参照经典命理典籍给出带出处的专业解读。

[![GitHub Stars](https://img.shields.io/github/stars/ruanxiaoer888/bazi-engine?style=flat-square&label=Stars&color=blue)](https://github.com/ruanxiaoer888/bazi-engine)
[![License](https://img.shields.io/badge/License-MIT%2FCC--BY--NC--SA%204.0-blue?style=flat-square)](LICENSE)
[![在线体验](https://img.shields.io/badge/%E5%9C%A8%E7%BA%BF%E4%BD%93%E9%AA%8C-%E6%9C%AC%E5%88%9D%20benchu.xiaoerpro.com-brightgreen?style=flat-square)](https://benchu.xiaoerpro.com/)
[![SkillHub](https://img.shields.io/badge/SkillHub-%E5%B7%B2%E4%B8%8A%E6%9E%B6-purple?style=flat-square)](https://skillhub.com/)

> **English**: [README.en.md](README.en.md)  
> **GitHub**: https://github.com/ruanxiaoer888/bazi-engine  
> 🔗 **在线体验**：**[本初 · benchu.xiaoerpro.com](https://benchu.xiaoerpro.com/)** — 基于本引擎的 C 端在线产品

> 单文件离线运行，无任何外部依赖；排盘精确至节气时刻。

## 功能特性

- **排盘引擎**：四柱八字、十神、藏干、纳音、大运（精确至出生时刻起运）、流年、流月、流日
- **流日分析**：任意月份逐日 30 天，每日干支 / 十神 / 与命局冲合刑害 / 空亡 / 喜忌 / 十二长生，自动标记关键日
- **六亲详解**：父母 / 配偶 / 子女 / 兄弟分项分析，宫位为体、十神为用
- **合婚评分**：七大维度综合评分
- **五行补救**：喜用神、调候用神（古籍）、五行缺失与补救建议
- **神煞速查**：24 项吉凶星曜按命中展示
- **三式宫位**：胎元、命宫、身宫
- **断语可追溯**：1000 条断语，每条标注古籍出处（古代命理典籍）与行动建议

<p align="center">
  <img src="assets/screenshots/final/02_liuri.png" alt="bazi-engine · 流日分析" width="520"/>
  <br/>
  <em>引擎深度能力示例：单月逐日 30 天分析（每日干支 / 十神 / 冲合刑害 / 空亡 / 喜忌 / 十二长生）</em>
</p>

## 产品生态

| | 项目 | 说明 |
|---|---|---|
| 🧩 | **bazi-engine**（本仓库） | 开源排盘引擎底座：Skill + 单文件 UI + 独立 JS 库（MIT），面向开发者与命理师 |
| 🚀 | **[本初](https://benchu.xiaoerpro.com/)** | 作者自有的 C 端在线产品：AI 八字报告（排盘 / 合婚 / 流年），付费解锁，微信支付 |

**开源 → 商业闭环**：引擎开源于 GitHub 供社区使用与二次开发；C 端产品「本初」是作者自有的商业落地，与引擎共用同一确定性排盘内核——C 端仅消费 `paipan` / `applyDst` 等 **MIT 代码层** API，付费解读内容为 C 端自有实现，不涉及 NC 数据。开源获得社区打磨，产品验证商业价值，互相成就。

<p align="center">
  <img src="assets/screenshots/benchu/paipan.png" alt="本初 · 排盘结果页" width="700"/>
  <br/>
  <em>排盘结果：四柱命盘 + 五行能量 + 人格解读（以示例命盘展示）</em>
</p>
<p align="center">
  <img src="assets/screenshots/benchu/hehun.png" alt="本初 · 双人匹配" width="460"/>
  <img src="assets/screenshots/benchu/year.png" alt="本初 · 年度能量趋势" width="460"/>
  <br/>
  <em>双人匹配（合婚评分）· 年度能量趋势（逐月提醒）</em>
</p>

## 快速开始

直接打开 `ui/index.html`（单文件，浏览器即可运行，无需安装任何东西），或通过支持 Skill 的 AI 助手（WorkBuddy / DeepSeek Harness / Codex 等）调用本 Skill：

1. 告诉我你的出生信息：姓名、生日（阳历或农历均可）、出生时间、性别、出生地
2. 自动排盘并输出：四柱命盘 → 五行分析 → 大运流年 → 综合解读
3. 可继续追问流年 / 流月 / 流日 / 合婚 / 六亲等深入分析

### 示例对话

**Q：** 帮我算一下八字，1990年5月15日上午10点，男，广州出生。

**A：** 排出四柱（庚午 辛巳 庚辰 庚辰，含夏令时回拨 + 真太阳时校正说明）、五行分布、喜用神，并给出大运 8 步与当前流年解读（每条断语附古籍出处）。

**Q：** 看看我和她合不合，我1990年5月15日10点男广州，她1992年8月8日20点女北京。

**A：** 七大维度合婚评分（日主互补 / 五行相生 / 六亲对照 / 流年同步等），并标注相合与相冲之处。

**Q：** 2026年3月哪天适合谈合作？

**A：** 展开流日分析：逐日标注冲合日柱、喜用忌神日，汇总本月关键日，给出"冲日宜静守、合日宜社交"的建议。

## 技术说明

- **UI**：`ui/index.html` — 单文件离线（零外部依赖），内置 206 年节气数据 + 1000 条断语
- **构建**：`tools/build_ui.py`（Python）内联节气与断语库生成 UI
- **验证**：13 套回归脚本（`test_engine` / `test_lunar` / `test_ui` / `test_eval_state` / `test_p1_fixes` / `verify_sleep_rules` / `verify_ux_e2e` / `test_dst` / `test_liuri_v2` / `test_liuyue_v2` / `verify_edu_rules` / `test_xiyong` / `check_conflicts`），覆盖引擎库、农历、夏令时、输入容错、边界场景、报告质量与端到端用户视角，CI 自动执行
- **质检工具**：`audit_hit_distribution.js`（命中分布审查）、`check_dup_hits.js`（重复命中检测）、`check_conflicts.js`（反义矛盾检测）

## 目录结构

```
skill/SKILL.md           Skill 定义（引导式交互 + 分析流程）
ui/index.html            单文件离线界面
tools/                   构建 / 测试 / 质检工具
kb/          古籍原文 + 规则手册 + 断语库
```

## 免责声明

本工具基于传统命理典籍（子平法）进行排盘与推演，结果仅供文化研究与娱乐参考，不构成医疗、投资、法律等任何专业建议。命理之说，信则有，不信则无，请理性看待。

## 数据溯源指纹

断语库（`kb/04-rules-db/rules.json`）内含**溯源指纹句**（水印，具体位置不公开）。未经许可复用本断语库（如直接搬运数据做商业产品），指纹句会原样出现在对方内容中，可据此识别与取证。遵守 [LICENSE](LICENSE) / [LICENSE-DATA](LICENSE-DATA) 的正常使用不受任何影响。

## License

本仓库采用**双许可**结构：

- **代码**（排盘引擎 / UI / 构建测试脚本 / Skill 定义）：[MIT](LICENSE) — 自由使用
- **数据**（`kb/` 断语库与古籍汇编等）：[CC BY-NC-SA 4.0](LICENSE-DATA) — 署名 · 非商业 · 相同方式共享（古籍原文属公有领域，可自由引用）

> **商业边界**：「本初」为作者自有商业产品（作者对自有代码与数据享有完整权利）；第三方使用本仓库仍按上方双许可执行（代码 MIT / 数据 CC BY-NC-SA 4.0），商业授权请联系作者。
>
> 双许可边界、来源归属与商业授权说明详见 [LICENSE-DATA](LICENSE-DATA)。
