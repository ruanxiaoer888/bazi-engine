# bazi-engine · Four Pillars (BaZi) Astrology Engine

A deterministic, zero-dependency BaZi (Chinese Four Pillars) charting and analysis engine. Feed it a birth date, and it computes the Four Pillars, Luck Cycles (Da Yun), and annual/monthly/daily fortunes with **every reading traced back to a classical text source**.

> Single-file offline runtime — open in a browser and it works. No API keys, no external services, no build step.  
> **GitHub**: https://github.com/ruanxiaoer888/bazi-engine

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
- **Traceable readings**: 504 rules, each citing its classical source (三命通会 / 渊海子平 / 滴天髓 / 子平真诠 / 穷通宝鉴) plus a practical suggestion

## Quick Start

**Option A — Browser (no install):** open `ui/index.html`. Everything is inline — solar-term data, rule database, engine, UI. Works offline, works from `file://`.

**Option B — WorkBuddy Skill:** import the skill and ask in natural language:

1. Provide: name, birth date (solar or lunar), birth time, gender, birthplace
2. Get back: Four Pillars → element analysis → Da Yun & current year → integrated reading
3. Follow up with: annual / monthly / daily fortunes, compatibility, family analysis

### Example dialogue

**Q:** Chart for me — May 15, 1990, 10:00 AM, male, born in Guangzhou.
**A:** Four Pillars (庚午 辛巳 庚辰 癸巳), element distribution, favorable gods, 8-step Da Yun, current-year reading — every statement with its classical citation.

**Q:** Are we compatible? Me: 1990-05-15 10:00 M Guangzhou. Her: 1992-08-08 20:00 F Beijing.
**A:** 7-dimension compatibility score (day-master complementarity / element generation / family cross-check / year synchronicity), flagging harmonious and clashing points.

**Q:** Which day in March 2026 is good for a business meeting?
**A:** Day-by-day expansion: clash/combine days against the natal chart, favorable vs unfavorable days, key-day summary — "clash days favor stillness, combine days favor socializing."

## Technical Notes

- **Runtime**: `ui/index.html` — single file, zero external dependencies, 206 years of solar-term data + 504-rule database inlined
- **Build**: `tools/build_ui.py` (Python) inlines solar terms + rules into the UI
- **Verification**: 5 regression suites (`tools/test_ui.js` / `test_eval_state.js` / `test_p1_fixes.js` / `verify_sleep_rules.js` / `verify_ux_e2e.js`) covering input tolerance, boundary cases (incl. the 1895 data-start-year edge), report quality, output stability, and end-to-end user flows
- **Quality tooling**: `audit_hit_distribution.js` (hit-distribution audit), `check_dup_hits.js` (duplicate-hit detection), `check_conflicts.js` (contradictory-rule detection)

## Directory Layout

```
skill/SKILL.md           Skill definition (guided interaction + analysis workflow)
ui/index.html            Single-file offline UI
tools/                   Build / test / quality-audit tooling
knowledge-base/          Classical texts + rule handbooks + 504-rule database
```

## Disclaimer

This tool performs charting and divination based on traditional Chinese metaphysics (Zi Ping method). Output is provided for cultural study and entertainment only, and does not constitute medical, investment, legal, or any other professional advice. Treat it with an open but rational mind.

## License

This repository uses a **dual-license** structure:

- **Code** (charting engine / UI / build & test scripts / Skill definition): [MIT](LICENSE) — free to use
- **Data** (`knowledge-base/` verdict library & classical-text compilations): [CC BY-NC-SA 4.0](LICENSE-DATA) — Attribution · NonCommercial · ShareAlike (classical texts are public domain and freely quotable)

> See [LICENSE-DATA](LICENSE-DATA) for the exact boundaries, source attribution, and commercial licensing.
