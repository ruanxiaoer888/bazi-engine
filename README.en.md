# bazi-engine · Four Pillars (BaZi) Astrology Engine

A deterministic, zero-dependency BaZi (Chinese Four Pillars) charting and analysis engine. Feed it a birth date, and it computes the Four Pillars, Luck Cycles (Da Yun), and annual/monthly/daily fortunes with **every reading traced back to a classical text source**.

[![GitHub Stars](https://img.shields.io/github/stars/ruanxiaoer888/bazi-engine?style=flat-square&label=Stars&color=blue)](https://github.com/ruanxiaoer888/bazi-engine)
[![CI](https://img.shields.io/github/actions/workflow/status/ruanxiaoer888/bazi-engine/ci.yml?style=flat-square&label=CI)](https://github.com/ruanxiaoer888/bazi-engine/actions)
[![License](https://img.shields.io/badge/License-MIT%2FCC--BY--NC--SA%204.0-blue?style=flat-square)](LICENSE)
[![SkillHub](https://img.shields.io/badge/SkillHub-Published-purple?style=flat-square)](https://skillhub.com/)

> Single-file offline runtime — open in a browser and it works. No API keys, no external services, no build step.  
> **GitHub**: https://github.com/ruanxiaoer888/bazi-engine  
> 🚀 **Try it live**: **[Benchu · benchu.xiaoerpro.com](https://benchu.xiaoerpro.com/)** — a consumer web product powered by this engine

## Why "engine"?

Most "AI fortune-telling" products let a large language model *guess* the chart — and LLMs are notoriously bad at calendar math. **bazi-engine never guesses.** Chart computation is implemented as deterministic, testable code:

- Year pillar split at the exact **Li Chun (立春) instant**, month pillar at **solar term instants** — computed from 206 years (1895–2100) of pre-verified solar-term data
- Day pillar via a fixed sexagenary-cycle recursion from a canonical reference date
- Late Zi hour (23:00+) day-rollover, true solar time correction, and Da Yun onset to the exact birth hour

Same birth data in, same chart out — every single time.

## Features

- **Chart engine**: Four Pillars, Ten Gods (十神), Hidden Stems, Na Yin, Da Yun (8 steps), Liu Nian (year), Liu Yue (month), Liu Ri (day)
- **Day-level precision**: expand any month into a day-by-day reading (30 days) — daily stem-branch, Ten Gods, clashes/combos/punishments against the natal chart, void (空亡), favorable/unfavorable elements, Twelve Life Stages, auto-flagged key days
- **Family analysis**: parents / spouse / children / siblings, palace-as-body × ten-god-as-function
- **Marriage compatibility (合婚)**: 7-dimension composite score
- **Element remediation (五行补救)**: favorable gods, seasonal conditioning gods (穷通宝鉴), missing-element suggestions
- **24 auspicious/inauspicious stars (神煞)** with hit-based display
- **Three palaces (三式宫位)**: Tai Yuan, Ming Gong, Shen Gong
- **Traceable readings**: 1000 rules, each citing its classical source (三命通会 / 渊海子平 / 滴天髓 / 子平真诠 / 穷通宝鉴) plus a practical suggestion

<p align="center">
  <img src="assets/screenshots/final/02_liuri.png" alt="bazi-engine · day-level analysis" width="520"/>
  <br/>
  <em>Engine depth example: month expanded into 30 day-by-day readings (daily stem-branch / Ten Gods / clashes & combos / void / favorable-unfavorable / Twelve Life Stages)</em>
</p>

### Why bazi-engine?

<p align="center">
  <img src="assets/screenshots/promo/compare.png" alt="bazi-engine vs traditional tools" width="420"/>
  <br/>
  <em>Open source · exact solar-term split · local zero-dependency · 1000 traceable rules with classical citations</em>
</p>

## Ecosystem

| | Project | Description |
|---|---|---|
| 🧩 | **bazi-engine** (this repo) | Open-source engine foundation: Skill + single-file UI + standalone JS library (MIT), for developers & practitioners |
| 🚀 | **[Benchu](https://benchu.xiaoerpro.com/)** | The author's own consumer web product: AI BaZi reports (chart / compatibility / yearly), paid unlock, WeChat Pay |

**Open source → commercial loop**: the engine is open-sourced on GitHub for community use and redevelopment; **Benchu** is the author's own commercial landing built on the same deterministic charting core — the consumer product consumes only **MIT code-layer** APIs (`paipan` / `applyDst`), and its paid readings are its own implementation, not NC-licensed data. Open source gains community polish, the product validates commercial value — each feeds the other.

<p align="center">
  <img src="assets/screenshots/benchu/paipan.png" alt="Benchu · chart result page" width="700"/>
  <br/>
  <em>Chart result: Four Pillars + element energy + personality reading (sample chart)</em>
</p>
<p align="center">
  <img src="assets/screenshots/benchu/hehun.png" alt="Benchu · compatibility" width="460"/>
  <img src="assets/screenshots/benchu/year.png" alt="Benchu · yearly energy trends" width="460"/>
  <br/>
  <em>Compatibility scoring · Yearly energy trends (month-by-month reminders)</em>
</p>
<p align="center">
  <img src="assets/screenshots/benchu/insight.png" alt="Benchu · six-dimension personality radar" width="700"/>
  <br/>
  <em>Deep report example: six-dimension personality radar (decision-making / resilience, etc.)</em>
</p>

## Quick Start

### 👤 End users — try it now

- **Online**: visit [Benchu · benchu.xiaoerpro.com](https://benchu.xiaoerpro.com/) (paid reports, WeChat Pay)
- **Offline**: open `ui/index.html` in a browser (single file, zero deps, works from `file://`)

### 🧑‍💻 Developers — use the engine

`engine/engine.dist.js` is a standalone UMD library (zero deps, 101 exported APIs), usable in browser or Node:

```html
<!-- Browser -->
<script src="engine/engine.dist.js"></script>
<script>
  // Note: gender must be '男' or '女' (Chinese); applyDst rolls back DST (e.g. 1990 China)
  const d = window.BaziEngine.applyDst(1990, 5, 15, 10);           // {hh: 9, dst: 1}
  const c = window.BaziEngine.paipan('李明远', '男', 1990, 5, 15, d.hh, 0, '广州市', 'yes');
  console.log(c.yg, c.mg, c.dg, c.hg); // 庚午 辛巳 庚辰 庚辰
</script>
```

```js
// Node.js
const BaziEngine = require('./engine/engine.dist.js');
const d = BaziEngine.applyDst(1990, 5, 15, 10);
const c = BaziEngine.paipan('李明远', '男', 1990, 5, 15, d.hh, 0, '广州市', 'yes');
console.log(c.yg, c.mg, c.dg, c.hg); // 庚午 辛巳 庚辰 庚辰
```

Key APIs: `paipan` (charting) / `matchRules` (rule matching) / `applyDst` (DST correction) / `lunarToSolar` (lunar→solar) / `calcShenSha` (stars) / `getDaYun` (Luck Cycles).

### 🤖 AI assistants — use the Skill

Import the skill into a Skill-capable assistant (WorkBuddy / DeepSeek Harness / Codex, etc.) and ask in natural language:

1. Provide: name, birth date (solar or lunar), birth time, gender, birthplace
2. Get back: Four Pillars → element analysis → Da Yun & current year → integrated reading
3. Follow up with: annual / monthly / daily fortunes, compatibility, family analysis

### Example dialogue

**Q:** Chart for me — May 15, 1990, 10:00 AM, male, born in Guangzhou.

**A:** Four Pillars (庚午 辛巳 庚辰 庚辰, incl. DST rollback + true solar time note), element distribution, favorable gods, 8-step Da Yun, current-year reading — every statement with its classical citation.

**Q:** Are we compatible? Me: 1990-05-15 10:00 M Guangzhou. Her: 1992-08-08 20:00 F Beijing.

**A:** 7-dimension compatibility score (day-master complementarity / element generation / family cross-check / year synchronicity), flagging harmonious and clashing points.

**Q:** Which day in March 2026 is good for a business meeting?

**A:** Day-by-day expansion: clash/combine days against the natal chart, favorable vs unfavorable days, key-day summary — "clash days favor stillness, combine days favor socializing."

## Technical Notes

- **Runtime**: `ui/index.html` — single file, zero external dependencies, 206 years of solar-term data + 1000-rule database inlined
- **Build**: `tools/build_ui.py` (Python) inlines solar terms + rules into the UI
- **Verification**: 13 regression suites covering the engine library, lunar calendar, DST, input tolerance, boundary cases, report quality, and end-to-end user flows — run automatically by CI

  <details>
  <summary>13 regression suites (click to expand)</summary>

  ```
  tools/test_engine.js       toolchain audit (28 checks, standalone lib)
  tools/test_lunar.js        lunar calendar (27 checks)
  tools/test_ui.js           UI regression
  tools/test_eval_state.js   strength state machine
  tools/test_p1_fixes.js     P1 fix regressions
  tools/verify_sleep_rules.js Twelve Life Stages rules
  tools/verify_ux_e2e.js     end-to-end user flows
  tools/test_dst.js          daylight-saving time
  tools/test_liuri_v2.js     day-level analysis
  tools/test_liuyue_v2.js    month-level analysis
  tools/verify_edu_rules.js  education rules
  tools/test_xiyong.js       favorable-god rules
  tools/check_conflicts.js   contradiction detection
  ```
  </details>
- **CI gate**: `.github/workflows/ci.yml` (GitHub Actions) builds the UI + engine dist, validates the rule-database JSON, and runs all 13 regressions + a hit-distribution audit on every push / PR — nothing merges until green
- **Cross-platform consistency**: `.gitattributes` enforces LF line endings on build artifacts & data files (Windows CRLF once made dist bytes differ, breaking MD5 alignment across platforms), keeping local / CI / consumer builds byte-identical
- **Quality tooling**: `audit_hit_distribution.js` (hit-distribution audit), `check_dup_hits.js` (duplicate-hit detection), `check_conflicts.js` (contradictory-rule detection)

<p align="center">
  <img src="assets/screenshots/promo/flow.png" alt="bazi-engine · processing pipeline" width="420"/>
  <br/>
  <em>Pipeline: input → time correction (DST / true solar time) → computation → structured output → optional AI reading</em>
</p>

## Directory Layout

```
skill/SKILL.md           Skill definition (guided interaction + analysis workflow)
ui/index.html            Single-file offline UI
engine/engine.dist.js    Standalone engine library (UMD: browser / Node)
tools/                   Build / test / quality-audit tooling
kb/                      Classical texts + rule handbooks + 1000-rule database
.github/workflows/       CI gate (GitHub Actions: build + regressions + audit)
.gitattributes           LF line-ending policy (cross-platform consistency)
```

## Disclaimer

This tool performs charting and divination based on traditional Chinese metaphysics (Zi Ping method). Output is provided for cultural study and entertainment only, and does not constitute medical, investment, legal, or any other professional advice. Treat it with an open but rational mind.

## Data Provenance Fingerprints

The rule database (`kb/04-rules-db/rules.json`) contains embedded **provenance fingerprint phrases** (watermarks; exact locations undisclosed). Any unauthorized reuse of the database (e.g., republishing it into a commercial product) will carry these phrases verbatim, enabling identification and evidence collection. Compliant use under [LICENSE](LICENSE) / [LICENSE-DATA](LICENSE-DATA) is unaffected.

## License

This repository uses a **dual-license** structure:

- **Code** (charting engine / UI / build & test scripts / Skill definition): [MIT](LICENSE) — free to use
- **Data** (`kb/` verdict library & classical-text compilations): [CC BY-NC-SA 4.0](LICENSE-DATA) — Attribution · NonCommercial · ShareAlike (classical texts are public domain and freely quotable)

> **Commercial boundary**: **Benchu** is the author's own commercial product (the author retains full rights to their own code and data); third-party use of this repository still follows the dual license above (MIT for code / CC BY-NC-SA 4.0 for data). For commercial licensing, contact the author.
>
> See [LICENSE-DATA](LICENSE-DATA) for the exact boundaries, source attribution, and commercial licensing.

## Support the Author

If this project helps you, consider [Starring ⭐](https://github.com/ruanxiaoer888/bazi-engine) or trying the paid reports on [Benchu](https://benchu.xiaoerpro.com/); for commercial licensing, custom work, or feedback, contact the author.
