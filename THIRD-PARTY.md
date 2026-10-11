# 第三方来源与权利声明（THIRD-PARTY NOTICES）

> 本文件列出 `bazi-engine` 仓库中**非作者原创**内容的来源、许可与使用边界。
> 目的：① 履行上游 MIT 许可的"保留版权声明"义务；② 明确**哪些内容不得转授商业许可**。
> 维护约定：新增/移除任何第三方来源内容时，必须同步更新本文件。

最后更新：2026-10-11

---

## 1. 开源社区项目

### 1.1 jinchenma94/bazi-skill

| 项 | 内容 |
|---|---|
| 仓库 | https://github.com/jinchenma94/bazi-skill |
| 许可 | **MIT License**（GitHub API `license.spdx_id = MIT`） |
| 版权 | `Copyright (c) 2025 jinchenma94` |
| 本项目使用方式 | 排盘静态查表数据与部分规则整理的**参考来源**（见 `kb/README.md` 数据来源说明） |
| 义务 | 保留上述版权声明与 MIT 许可全文；MIT 允许商用与再许可 |
| 影响范围 | `kb/01-basics/`（干支/纳音/时辰/神煞等查表类数据）及部分规则条目 |

> MIT 许可全文见 <https://opensource.org/licenses/MIT>。

### 1.2 dshxliuyu-lang/bazimbtifenxi.skill ⚠️ 权利链不完整

| 项 | 内容 |
|---|---|
| 仓库 | https://github.com/dshxliuyu-lang/bazimbtifenxi.skill |
| 许可 | **无许可证声明**（GitHub API `license = null`）→ 依默认规则"保留一切权利" |
| 本项目使用方式 | `kb/README.md` 曾将其列为数据来源之一（`kb/02-rules/bazi-mbti.md` 与本项目的早期整理存在主题重叠） |
| 结论 | **作者无权就该项目的表达性内容对外转授许可**，也不得将其纳入商业授权交付包 |
| 处置 | ① `kb/02-rules/bazi-mbti.md` **已从发布包与商业交付包中排除**（见 `tools/build_release_zip.py` 的 `EXCLUDE_SUB`）；② 该文件不属于 `kb/04-rules-db/rules.json`（断语库 1000 条中无该来源条目）；③ 后续如需继续使用，应重写为原创表达或取得原作者书面许可 |

---

## 2. 古籍原文（公有领域）

《三命通会》《渊海子平》《滴天髓》《子平真诠》《穷通宝鉴》《黄帝内经》等经典原文**属公有领域**，
任何人可自由引用。本项目的贡献在于**汇编、摘录、结构化与条件化编译**，而非原文本身。

- 目录：`kb/03-classics/`（含由 docx 提取整理的全文梳理件）
- 说明：`rules.json` 每条规则的 `source` 字段标注古籍出处，属引用与溯源，不主张对原文的权利。

---

## 3. 地理坐标数据（`engine/engine.dist.js` 内 `CITY_LON`）

| 数据 | 来源 | 说明 |
|---|---|---|
| 行政区划名单 | modood 行政区划项目 | 仅用于确定城市名称集合 |
| 经纬度坐标 | GeoNames | CC BY 4.0（署名要求）；本项目以数值形式内联使用 |
| 县改市旧址经度 | 公开资料整理 | 少数县级市 |
| 少量常识补录 | 公开地理常识 | 已逐项人工复核 |

> 该表仅提供"真太阳时经度校正"的近似值（精度目标 <0.3°，约 1.2 分钟），不用于任何测绘用途。
> 若未来将 `CITY_LON` 单独作为数据产品对外授权，需单独核实并标注 GeoNames 的 CC BY 署名。

---

## 4. 明确排除在商业授权交付包之外的内容

以下内容**不随商业授权交付**，理由见上：

1. `kb/02-rules/bazi-mbti.md`（来源为微信公众号/百家号文章，无作者、无 URL、无授权）
2. `kb/03-classics/` 中的 docx 提取件（古籍原文属公有领域，转售无标的价值，且来源为第三方整理）。
   **具体为 6 个文件**：`bazi-wuxing-table.md`、`ditian-sui.md`、`qiongtong-baojian.md`、
   `sanming-tonghui.md`、`workflow-full.md`、`yuanhai-ziping.md`。
3. `HANDOFF.md`、`工作区说明.md`、`docs/`（内部文档，非交付物）
4. `assets/screenshots/`（含作者个人联系方式素材）

> **本条已由构建脚本强制执行（不是纸面声明）**：`tools/build_release_zip.py` 会读取每个 `.md` 文件头部的
> `来源：…docx` 标注，**自动排除**这类第三方整理件，并在打包后做硬校验——一旦交付包内仍存在此类文件则
> **构建失败（exit 1）**。因此 `bazi-engine-*.zip`（GitHub Release 附件与 SkillHub 上传包）与本节声明一致；
> 2026-10 风险面扫描曾发现此声明**未被执行**（旧包内含上述 6 个文件），现已修复并加门禁。


---

## 5. 作者原创部分（可对外授权）

以下为作者原创编译成果，是本项目**唯一可对外授权**的标的：

- `kb/04-rules-db/rules.json`：1000 条结构化断语（触发条件 / 结论 / 古籍出处 / 置信度 / 行动建议）
- 质检流水线（`tools/audit_hit_distribution.js`、`check_conflicts.js`、`check_dup_hits.js` 等）
- 规则条件化编译方法、`suggestion` 行动建议文案、置信度标注

---

*本文件不替代 [LICENSE](LICENSE) 与 [LICENSE-DATA](LICENSE-DATA)；如有冲突，以两者为准。*
