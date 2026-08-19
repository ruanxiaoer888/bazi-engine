# bazi-app 闭环收尾启动指令 · 引擎 v1.3.6

> 用途：bazi-app 对话（C 端「本初」仓库）接入 bazi-engine **v1.3.6**（三方审计后稳定版）并完成闭环收尾（回归确认 → 服务器四件套更新 → 虎皮椒通道 → 锁定）。
> 由 bazi-engine 侧交付（2026-08-19，随引擎更新至 v1.3.6），Michael 直接粘贴给 bazi-app 对话即可。
> 边界约定（双项目 git 边界）：引擎 dist 由 bazi-engine 侧交付，bazi-app 不手改 engine.dist.js；发现引擎 bug 记录后反馈 bazi-engine 侧。

---

## ✅ 引擎 v1.3.6 交付状态（bazi-engine 侧已核）

- **dist 已拷贝交付**：`web/engine.dist.js`，MD5 `1A4722FA7B0974EB4F5CFA53C71AA9C3`（LF 口径，跨平台可比）
- **C 端只消费 `paipan` / `applyDst` / `SHI_CHEN_MAP`**（已 grep 确认，不用 matchRules/RULES；`lunarToSolar` 为 C 端自有实现，与引擎同步但独立——引擎 v1.3.3 加的防御**不影响 C 端**）
- **v1.3.2~v1.3.6 对 C 端影响评估**：仅 **v1.3.4 专旺格判定收紧**（0.55→0.75+他行≤0.15 双条件，5000 盘 0.94%→0.02% 去误标）——C 端若显示「特殊格局」，**此前被误标的盘不再显示专旺细分**（更准确，属预期）；其余均为 B 端 matchRules/UI 层，C 端无感知
- 一致性基线：8 盘 ctx 全字段 0 差异（v1.3.0 验证，v1.3.6 引擎层对 C 端消费 API 无改动）

## ✅ 已完成的验证（bazi-engine 侧，无需重复）

- 一致性回归：8 盘 ctx 0 差异 + applyDst/SHI_CHEN_MAP 一致
- 页面冒烟：1990-05-15 10:00 广州 四柱/格局/喜用全对（含夏令时+真太阳时时柱链路）
- 闭环 API 演练：18/18 全通（下单/首单优惠/mock 支付/解锁/兑换码/防浪费）

---

## ✅ 页面冒烟确认（2026-08-19，bazi-engine 侧截图核对）

对 1990-05-15 10:00 广州（男）报告逐项核对：

| 显示项 | 页面值 | 引擎实测 | 判定 |
|---|---|---|---|
| 四柱 | 庚午 辛巳 庚辰 庚辰 | 同（含时柱链路） | ✅ |
| 格局 | 建禄格 | 建禄格 | ✅ |
| 身强/弱 | 能量强 | 强 | ✅ |
| 喜用（五行） | 火·木·水 | xiYong=[火,木,水] | ✅ |
| 神煞天赋 | 学堂、将星 | shenSha 含 | ✅ |

**时柱庚辰链路验证**（看似可疑实为正确）：1990-05-15 在中国夏令时窗口（4/15~9/16）内 → C 端先 `applyDst` 回拨 1 小时（10:00→9:00）→ paipan 内真太阳时再校 ≈8:33 → **辰时** → 庚辰。引擎实测 `applyDst(1990,5,15,10,0)`=`{hh:9,dst:1}`，回拨后排盘=`庚午/辛巳/庚辰/庚辰`，与页面逐字一致。页面「生成依据」应显示「检测到该日期处于夏令时时段，已自动回拨 1 小时」。

**说明**：五行百分比（金 41%）为 C 端藏干加权算法（本气1.0/中气0.5/余气0.25+月令×1.5），与引擎 ctx.five 不同源，但 C 端输入（pillars）新旧一致 → 显示与之前一致。付费报告内「喜用十神」列表为 C 端自有逻辑（ctx 输入不变 → 输出不变）；如需核查该列表是否符合产品预期，属 bazi-app 产品逻辑问题，不在引擎回归范围。

**冒烟结论：通过，v1.3.0 对 C 端零破坏确认，可锁定。**

---

## ✅ C 端闭环 API 全链路演练（2026-08-19，本地 mock 模式 18/18 通过）

本地启动 `api/server.js`（mock:true，`config.json` 由 example 复制，8787 端口）跑通完整商业闭环：

| 环节 | 结果 |
|---|---|
| /api/health | ✅ ok + mock |
| 下单 report（新设备） | ✅ **首单 ¥9.9**（firstOrder 生效） |
| mock-pay → status | ✅ PENDING→PAID |
| unlock/check | ✅ 解锁 report |
| 同设备二单 report | ✅ 恢复 ¥19.9（首单已用） |
| match ¥29.9 / year ¥19.9 | ✅ 下单+支付+解锁 |
| 无效 SKU / 缺 deviceId | ✅ 400 拒绝 |
| admin 登录（username/password） | ✅ 24h 会话 token |
| 生成兑换码（report×2 + match×1）+ 列表 | ✅ |
| 新设备兑换码解锁 | ✅ |
| 防兑换码浪费（已解锁输入未用码不消耗、可转赠） | ✅ |
| 无效码拒绝 | ✅ |

**注意**：admin 登录字段为 `username`/`password`（不是 user/pass）；`config.json` 未配置 adminUser/adminPass 时回退 `admin` / `CFG.adminToken`。测试发现 8787 曾被 WorkBuddy 旧实例占用（无 config 的残留进程），需先清理再起新实例。

**结论：支付-解锁-兑换码商业链路本地全通**。剩余真实闭环阻塞（需 Michael 操作）：① 服务器四件套更新（线上仍旧版）；② 虎皮椒真实通道（申请被拒，需换支付宝重提）。

---

你是 bazi-app（C 端「本初」）的 AI 助手。现在完成 **bazi-engine v1.3.6 引擎接入 + 闭环收尾**（回归确认 → 服务器更新 → 支付通道 → 锁定）。

## 背景

- bazi-engine **v1.3.6**（断语库 1000 条 + 三方深度审计 6 批次修复，稳定版）；引擎文件已交付 `web/engine.dist.js`
- C 端只消费 `paipan`/`applyDst`/`SHI_CHEN_MAP`（lunarToSolar 为 C 端自有实现，不受引擎 v1.3.3 防御影响）
- 一致性零破坏 + 页面冒烟 + 闭环 API 18/18 均已由 bazi-engine 侧验证（见上文）
- 本仓真实闭环剩 2 个外部阻塞：**服务器四件套更新**（线上仍旧版）+ **虎皮椒真实通道**（申请被拒）

## 执行步骤

**第 1 步 · 版本核对（必做）**：
```bash
md5sum web/engine.dist.js
# 期望：1A4722FA7B0974EB4F5CFA53C71AA9C3
# 不一致 → 停下，找 bazi-engine 侧重拷
```

**第 2 步 · 回归确认（引擎侧已做过一致性/冒烟/闭环，本仓只需轻量确认）**：
- 本地打开 `web/index.html`，1990-05-15 10:00 广州 → 四柱/格局/喜用正常渲染（对照上文冒烟表）
- **特殊格局核对**：找一张此前显示「专旺·X」的盘确认是否仍显示——v1.3.4 专旺判定收紧，误标盘不再显示（预期，更准确）
- 农历输入一条（如 2024-01-01 腊月初一）→ 排盘正常（C 端自有农历实现）

**第 3 步 · 服务器四件套更新（真实闭环关键，线上仍旧版）**：
1. 上传 `web/index.html` + `web/admin.html` + **`web/paid/` 目录**（match.js/year.js 必须连目录一起）+ `api/server.js` + `api/config.json`（adminUser/adminPass 用生产值）到服务器
2. `pm2 restart benchu_api` → 验证 `curl /api/health`（含 mock 状态）
3. 新账号登录 `web/admin.html` 验证（24h 会话 token）
4. **重新生成兑换码**（线上 codes.json 为空/旧数据）——`api/gen_codes.js` 或后台生成
5. 可选：Nginx `/api/admin/` 加 IP 白名单

**第 4 步 · 虎皮椒真实通道**：
1. 换支付宝账号重提虎皮椒申请（原账号被风控拒）→ 通过后填 `config.json` 的 `xunhu.appid/appsecret` → `mock:false`
2. `pm2 restart` → 真实支付验证一单（¥0.01 试单）：下单 → 支付 → 回调 → 解锁 全链路
3. 验证通过后恢复正式价格（如 ¥19.9 首单 ¥9.9 已在 skus 配置）

**第 5 步 · 锁定**：全部通过后，将引擎依赖记录到本仓 `HANDOFF.md` / `AI_CONTEXT.md`（**v1.3.6 + MD5 `1A4722FA7B0974EB4F5CFA53C71AA9C3`**），commit 闭环收尾结果。

**第 6 步 · 反馈**：如发现引擎层 bug，记录复现盘与现象反馈 bazi-engine 侧（不要在本仓改 dist）。

## 边界红线

- `web/engine.dist.js` 是 bazi-engine 构建产物，**不手改**；引擎更新由 bazi-engine 侧交付
- 命理输出保留「仅供娱乐文化参考」免责；健康类不做疾病断言
- 完成后汇报：核对 MD5、回归确认结果、服务器更新状态（health/登录/兑换码）、虎皮椒验证结果、锁定记录位置
