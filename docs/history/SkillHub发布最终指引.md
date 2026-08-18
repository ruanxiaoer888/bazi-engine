# SkillHub 发布最终指引 · bazi-engine v1.2.1

> ⚠️ **历史存档文档**：本次发布已完成（2026-08-17 已上架）。下方路径仅记录当时（WorkBuddy 时代）环境，仅供追溯；后续发版请以 HANDOFF.md 第六节「发布验证（平台无关）」为准。
>
> 三盘验收已全部通过（排盘/流日/合婚），3 张截图已就位，final.zip 上传已通过
> 日期：2026-08-16 · 状态：已提交审核（最终 2026-08-17 申诉通过并上架）

---

## 一、上传文件清单

| 用途 | 文件路径 |
|---|---|
| **技能包 ZIP（已验证上传成功）** | `E:\michael\workBuddy\bazi-project\bazi-engine-v1.2.1-final.zip`（64 文件 / 0.5MB / 无嵌套 / 无中文路径） |
| **图标** | `E:\michael\workBuddy\bazi-project\assets\icon_taiji_v1.png` |
| **截图 1（封面）** | `E:\michael\workBuddy\bazi-project\assets\screenshots\final\01_paipan.png` |
| **截图 2（流日）** | `E:\michael\workBuddy\bazi-project\assets\screenshots\final\02_liuri.png` |
| **截图 3（合婚）** | `E:\michael\workBuddy\bazi-project\assets\screenshots\final\03_hehun.png` |

### ZIP 结构（已上传验证通过）

```
bazi-engine-v1.2.1-final.zip
├── SKILL.md                    ← 根目录（无外层嵌套目录）
├── LICENSE / LICENSE-DATA      ← 双许可
├── README.md / README.en.md
├── SkillHub-Submission-Kit.md
├── kb/                         ← 31 个知识库文件（01-basics / 02-rules / 03-classics / 04-rules-db / 05-reference）
├── tools/  ui/  skill/  engine/
```

---

## 二、变更说明（直接复制粘贴）

```
v1.2.1 全面升级批次：
- 农历/阳历双模式切换（主表单 + 合婚 A/B）
- 合婚 UI 改上下双区块布局，支持按人独立真太阳时校正
- 合婚时段模式（只知时辰）强制跳过真太阳时校正修复
- 喜用神中和分支按 ratio 细分（偏强/偏弱/真中和）
- "用神被冲克合"判定更严格
- 流日面板冲日柱红/合日柱绿/冲+合金 区分
- 流年/流月/流日 控件切换自动刷新
- 移动端 ~645px 响应式适配
- UI logo 统一为太极图（与上传图标一致）
- 五行补救文案按身强/身弱区分
- 13 套回归测试全绿（含新增 test_xiyong.js 10 盘验证）
- 504 条断语库，suggestion/source 100% 覆盖
```

---

## 三、SkillHub 填表逐字段指引

| 字段 | 填什么 | 备注 |
|---|---|---|
| **Skill 文件** | 拖拽 `bazi-engine-v1.2.1-final.zip` | ✅ 已验证上传无报错（64 文件全部识别） |
| **Slug** | `bazi-engine` | **提交后不可改**，谨慎核对 |
| **显示名称** | `bazi-engine（四柱八字命理引擎）` | |
| **图标** | 上传 `icon_taiji_v1.png` | ZIP 内不含此文件，需单独上传 |
| **描述** | 粘贴 `SkillHub-Submission-Kit.md`「二、详细描述」整段 | 或留空让平台从 SKILL.md 自动发现 |
| **版本号** | `1.2.1` | **不要带 v** |
| **变更说明** | 粘贴上面的变更说明 | |
| **分类** | 传统文化 / 命理占卜 / 自我探索 | 按页面选项选 |
| **标签** | 八字、命理、四柱、排盘、运势、合婚、流日、传统文化 | 逗号分隔 |
| **截图** | 上传上面 3 张 final 截图 | 第 1 张为封面 |
| **计费模式** | 免费 | MIT 开源，免商户入驻 |
| **宝藏级技巧征集大赛** | 勾选 | 增加曝光，不影响发布 |

---

## 四、提交后

- 三线并行安全审核（内容合规 + 漏洞扫描 + 模型安全评估）+ TRACE 评测
- 首次发布可能需 1~3 天
- 通过后出现在「我的 Skills」页，可申请提升到全局市场

---

## 五、验收复核记录（本次已通过）

| 案例 | 输入 | 结果 |
|---|---|---|
| 1 排盘 | 男 / 1990-05-15 / 10:00 / 广州 / 真太阳时=是 | ✅ 四柱庚辰金边 + 双校正提示 + 喜用火木水 + 命局偏强文案 |
| 2 流日 | 女 / 1996-02-22 / 16:41 → 2026-06 | ✅ 3 红 5 绿高亮 + 关键日红绿分组 + 切月刷新 |
| 3 合婚 | 男 1996-08-13 00:39 + 女 1973-03-02 07:08 | ✅ 85/100 天生佳偶 + 七维度 + 9 条古籍 |

> 本清单随 SkillHub-Submission-Kit.md 配合使用；任何字段卡住，截图发我。
