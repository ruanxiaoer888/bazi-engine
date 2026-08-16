# 太卜 · 图文并茂输出规范

> 本规范定义命理分析过程中各阶段应生成的SVG可视化图表类型、触发时机、设计标准与实现方式。
> 
> 核心原则：**一图胜千言**——在关键分析节点用图表替代纯文字描述，提升可读性与专业感。

---

## 一、图表生成工具

使用 WorkBuddy 内置 Visualizer 工具生成内联 SVG 图表：

1. **加载模块**：先调用 `read_me` 加载 `diagram` 模块（获取CSS变量、颜色、布局规则）
2. **渲染图表**：调用 `show_widget` 传入 SVG 代码片段
3. **每个图表独立渲染**：多个图表不要合并为一个，分别渲染便于用户理解

### SVG 设计通用规范

- **viewBox**：统一使用 `0 0 680 400` 或根据内容调整
- **配色方案**：
  - 木（甲乙寅卯）：`#4CAF50`（绿色）
  - 火（丙丁巳午）：`#F44336`（红色）
  - 土（戊己辰戌丑未）：`#FF9800`（橙色）
  - 金（庚辛申酉）：`#FFC107`（金色/黄色）
  - 水（壬癸亥子）：`#2196F3`（蓝色）
  - 背景：`#FAFAFA`，文字：`#333333`，辅助线：`#E0E0E0`
- **字体**：使用系统默认 sans-serif 字体
- **样式**：简洁大方，避免过度装饰，确保文字清晰可读

---

## 二、八字模块图表

### 2.1 八字四柱排盘表（必生成）

**触发时机**：完成八字四柱排盘后，进入分析前。

**图表内容**：
- 四列：年柱 | 月柱 | 日柱 | 时柱
- 每列两行：天干（上方）+ 地支（下方）
- 日柱天干高亮标注"日主"
- 每柱标注对应的十神
- 地支下方标注藏干

**设计要点**：
- 表格居中，列宽均等
- 天干地支用不同字号区分（天干大、地支略小）
- 日柱用边框或背景色高亮
- 十神用较小字号标注在柱旁

### 2.2 五行力量分布图（必生成）

**触发时机**：完成旺衰判断、确定日主强弱后。

**图表内容**：
- 柱状图：木、火、土、金、水五行的力量对比
- 每根柱子标注具体分数（0-100）
- 日主对应的五行用特殊颜色高亮
- 用虚线标注"平衡线"

**设计要点**：
- X轴：五行名称
- Y轴：力量值（0-100）
- 柱子宽度一致，间距均匀
- 柱顶标注具体数值

### 2.3 十神关系图（必生成）

**触发时机**：完成十神排列后。

**图表内容**：
- 中心为"日主（我）"
- 周围环绕十神：比肩、劫财、食神、伤官、偏财、正财、七杀、正官、偏印、正印
- 用箭头标注生克关系（生我、我生、克我、我克）
- 十神用不同颜色分组：
  - 比劫（绿色）、食伤（红色）、财星（金色）、官杀（蓝色）、印星（橙色）

**设计要点**：
- 中心圆较大，外围十神均匀分布
- 关系线用虚线或实线区分
- 标注生克方向箭头

---

## 三、紫微斗数模块图表

### 3.1 紫微十二宫格图（必生成）

**触发时机**：完成紫微命盘排布后，进入十二宫详批前。

**图表内容**：
- 3x4 或 4x3 的宫格布局（按实际命盘排列）
- 每个宫格标注：
  - **宫位名称**（如"命宫""财帛宫"）
  - **地支**（如"午宫""未宫"）
  - **主星**（如"贪狼""太阳"）
  - **庙旺利陷**（庙/旺/利/陷，用不同颜色区分）
  - **四化**（禄权科忌，用彩色小圆点或文字标注）
  - **重要辅星/煞星**（如"火星""陀罗""天魁"等）
  - **一句核心断语**（宫格底部）
- **命宫**：用深色边框（红色/深绿色）高亮，加粗标注
- **身宫**：用虚线边框或浅色高亮标注
- **三方四正**：命宫与财帛、官禄、迁移三宫用同色背景或连线标注
- **四化汇总条**：图表底部或侧边汇总四化飞星信息

**宫格排列**（标准布局示例，按实际排盘调整）：
```
巳(6/疾厄)  午(7/命宫)  未(8/财帛)  申(9/兄弟)
辰(5/迁移)              酉(10/夫妻)
卯(4/仆役)   身宫位置   戌(11/子女)
寅(3/官禄)   丑(2/田宅)  子(1/福德)  亥(12/父母)
```

**设计要点**：
- 宫格大小一致，间距均匀（建议每格宽150-170px，高70-80px）
- 命宫用**1.5px深色边框+浅色背景高亮**（如红色边框+浅红背景）
- 身宫用**0.5px虚线边框**标注
- 主星名称用较大字号（12-14px），辅星/煞星用较小字号（9-10px）
- 四化标注方式：
  - 禄：橙色圆点或"化禄"文字
  - 权：蓝色圆点或"化权"文字
  - 科：紫色圆点或"化科"文字
  - 忌：红色圆点或"化忌"文字
- 庙旺利陷标注：庙=绿色，旺=蓝色，利=灰色，陷=红色（或字体颜色区分）
- 三方四正用同色背景块或虚线连线连接
- 底部增加"四化飞星汇总"和"关键格局特征"说明区
- 每个宫格底部可标注一句核心断语（9-10px灰色字）

**必含信息清单**：
- [ ] 命宫位置及主星（高亮）
- [ ] 身宫位置（虚线框）
- [ ] 十四主星在各宫的分布
- [ ] 四化星（禄权科忌）的落宫
- [ ] 重要煞星（火铃羊陀空劫）的落宫
- [ ] 三方四正的连线/背景标注
- [ ] 底部四化汇总 + 关键格局总结

### 3.2 大运流年时间线（必生成）

**触发时机**：完成大运排布后，分析人生阶段运势时。

**图表内容**：
- 水平时间轴，从左到右为年龄增长方向
- 每个大运区间标注：起止年龄 + 大运干支 + 大运命宫主星
- 当前年龄位置用竖线标注
- 吉凶用颜色区分（吉：绿色/蓝色，凶：红色/橙色，平：灰色）

**设计要点**：
- 时间轴贯穿全图
- 大运区间用色块填充
- 标注关键转折点（换大运年份）
- 流年可叠加在小刻度上

---

## 四、面相模块图表

### 4.1 面相十二宫位置示意图（必生成）

**触发时机**：进入面相分析阶段，描述面相十二宫位置时。

**图表内容**：
- 简化的人脸轮廓（正面）
- 标注十二宫位置：命宫（印堂）、兄弟宫（眉毛）、夫妻宫（奸门）、子女宫（卧蚕）、财帛宫（鼻子）、疾厄宫（山根）、迁移宫（额角）、奴仆宫（下巴两侧）、官禄宫（额头）、田宅宫（上眼皮）、福德宫（眉尾上方）、父母宫（日月角）
- 每个宫位用引线+文字标注

**设计要点**：
- 人脸轮廓简洁，不追求写实
- 标注线不交叉，清晰指向对应部位
- 宫位名称用中文标注
- 当前分析的宫位可用高亮色

---

## 五、手相模块图表

### 5.1 手相主线示意图（必生成）

**触发时机**：进入手相分析阶段，描述掌纹时。

**图表内容**：
- 手掌轮廓（左手或右手，根据分析需要）
- 标注三大主线：生命线、智慧线、感情线
- 标注辅助线：事业线、太阳线、婚姻线、财运线
- 每条线用不同颜色区分

**设计要点**：
- 手掌轮廓简洁
- 主线用粗线，辅助线用细线
- 线旁标注名称
- 可用小图标标注特殊标记（如岛纹、十字纹等）

---

## 六、综合断事模块图表

### 6.1 三法合一验证对照表（可选生成）

**触发时机**：三法合一综合断事阶段，需要交叉验证时。

**图表内容**：
- 三列：八字推断 | 紫微推断 | 面相验证
- 多行：性格、婚姻、事业、财运、健康等分项
- 一致项用绿色勾选，矛盾项用黄色感叹号，待验证项用灰色问号

**设计要点**：
- 表格清晰，行列对齐
- 用图标代替文字状态标注
- 底部可附综合结论

---

## 七、图表渲染示例代码

### 示例：八字四柱排盘表 SVG

```svg
<svg viewBox="0 0 680 300" xmlns="http://www.w3.org/2000/svg">
  <!-- 背景 -->
  <rect width="680" height="300" fill="#FAFAFA"/>
  
  <!-- 标题 -->
  <text x="340" y="30" text-anchor="middle" font-size="18" font-weight="bold" fill="#333">八字四柱排盘</text>
  
  <!-- 表头 -->
  <rect x="80" y="50" width="120" height="40" fill="#E3F2FD" stroke="#2196F3" stroke-width="1"/>
  <rect x="210" y="50" width="120" height="40" fill="#E3F2FD" stroke="#2196F3" stroke-width="1"/>
  <rect x="340" y="50" width="120" height="40" fill="#FFF3E0" stroke="#FF9800" stroke-width="2"/>
  <rect x="470" y="50" width="120" height="40" fill="#E3F2FD" stroke="#2196F3" stroke-width="1"/>
  
  <text x="140" y="78" text-anchor="middle" font-size="16" fill="#333">年柱</text>
  <text x="270" y="78" text-anchor="middle" font-size="16" fill="#333">月柱</text>
  <text x="400" y="78" text-anchor="middle" font-size="16" font-weight="bold" fill="#E65100">日柱（日主）</text>
  <text x="530" y="78" text-anchor="middle" font-size="16" fill="#333">时柱</text>
  
  <!-- 天干行 -->
  <rect x="80" y="100" width="120" height="60" fill="white" stroke="#ccc" stroke-width="1"/>
  <rect x="210" y="100" width="120" height="60" fill="white" stroke="#ccc" stroke-width="1"/>
  <rect x="340" y="100" width="120" height="60" fill="#FFF8E1" stroke="#FF9800" stroke-width="2"/>
  <rect x="470" y="100" width="120" height="60" fill="white" stroke="#ccc" stroke-width="1"/>
  
  <text x="140" y="140" text-anchor="middle" font-size="28" fill="#333">甲</text>
  <text x="270" y="140" text-anchor="middle" font-size="28" fill="#333">丙</text>
  <text x="400" y="140" text-anchor="middle" font-size="28" font-weight="bold" fill="#E65100">戊</text>
  <text x="530" y="140" text-anchor="middle" font-size="28" fill="#333">庚</text>
  
  <!-- 十神标注 -->
  <text x="140" y="158" text-anchor="middle" font-size="11" fill="#666">七杀</text>
  <text x="270" y="158" text-anchor="middle" font-size="11" fill="#666">偏印</text>
  <text x="400" y="158" text-anchor="middle" font-size="11" fill="#E65100">日主</text>
  <text x="530" y="158" text-anchor="middle" font-size="11" fill="#666">食神</text>
  
  <!-- 地支行 -->
  <rect x="80" y="170" width="120" height="60" fill="white" stroke="#ccc" stroke-width="1"/>
  <rect x="210" y="170" width="120" height="60" fill="white" stroke="#ccc" stroke-width="1"/>
  <rect x="340" y="170" width="120" height="60" fill="#FFF8E1" stroke="#FF9800" stroke-width="2"/>
  <rect x="470" y="170" width="120" height="60" fill="white" stroke="#ccc" stroke-width="1"/>
  
  <text x="140" y="210" text-anchor="middle" font-size="28" fill="#333">子</text>
  <text x="270" y="210" text-anchor="middle" font-size="28" fill="#333">寅</text>
  <text x="400" y="210" text-anchor="middle" font-size="28" font-weight="bold" fill="#E65100">辰</text>
  <text x="530" y="210" text-anchor="middle" font-size="28" fill="#333">午</text>
  
  <!-- 藏干标注 -->
  <text x="140" y="232" text-anchor="middle" font-size="10" fill="#999">癸</text>
  <text x="270" y="232" text-anchor="middle" font-size="10" fill="#999">甲丙戊</text>
  <text x="400" y="232" text-anchor="middle" font-size="10" fill="#999">戊乙癸</text>
  <text x="530" y="232" text-anchor="middle" font-size="10" fill="#999">丁己</text>
  
  <!-- 地支十神 -->
  <text x="140" y="246" text-anchor="middle" font-size="10" fill="#666">正财</text>
  <text x="270" y="246" text-anchor="middle" font-size="10" fill="#666">杀枭比</text>
  <text x="400" y="246" text-anchor="middle" font-size="10" fill="#666">比官财</text>
  <text x="530" y="246" text-anchor="middle" font-size="10" fill="#666">印劫</text>
  
  <!-- 纳音 -->
  <text x="140" y="270" text-anchor="middle" font-size="10" fill="#888">海中金</text>
  <text x="270" y="270" text-anchor="middle" font-size="10" fill="#888">炉中火</text>
  <text x="400" y="270" text-anchor="middle" font-size="10" fill="#888">大林木</text>
  <text x="530" y="270" text-anchor="middle" font-size="10" fill="#888">路旁土</text>
  
  <!-- 底部说明 -->
  <text x="340" y="295" text-anchor="middle" font-size="10" fill="#999">日主：戊土 | 格局：正官格 | 纳音五行仅供参考</text>
</svg>
```

### 示例：五行力量分布图 SVG

```svg
<svg viewBox="0 0 680 320" xmlns="http://www.w3.org/2000/svg">
  <rect width="680" height="320" fill="#FAFAFA"/>
  <text x="340" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">五行力量分布</text>
  
  <!-- Y轴 -->
  <line x1="80" y1="50" x2="80" y2="260" stroke="#ccc" stroke-width="1"/>
  <!-- X轴 -->
  <line x1="80" y1="260" x2="620" y2="260" stroke="#ccc" stroke-width="1"/>
  
  <!-- Y轴刻度 -->
  <text x="70" y="55" text-anchor="end" font-size="10" fill="#999">100</text>
  <text x="70" y="105" text-anchor="end" font-size="10" fill="#999">75</text>
  <text x="70" y="155" text-anchor="end" font-size="10" fill="#999">50</text>
  <text x="70" y="205" text-anchor="end" font-size="10" fill="#999">25</text>
  <text x="70" y="265" text-anchor="end" font-size="10" fill="#999">0</text>
  
  <!-- 平衡线 -->
  <line x1="80" y1="155" x2="620" y2="155" stroke="#FF5722" stroke-width="1" stroke-dasharray="5,5"/>
  <text x="625" y="158" font-size="9" fill="#FF5722">平衡线</text>
  
  <!-- 柱子：木 45 -->
  <rect x="110" y="158" width="70" height="102" fill="#4CAF50" opacity="0.8"/>
  <text x="145" y="150" text-anchor="middle" font-size="12" font-weight="bold" fill="#4CAF50">45</text>
  <text x="145" y="280" text-anchor="middle" font-size="14" fill="#333">木</text>
  
  <!-- 柱子：火 20 -->
  <rect x="210" y="208" width="70" height="52" fill="#F44336" opacity="0.8"/>
  <text x="245" y="200" text-anchor="middle" font-size="12" font-weight="bold" fill="#F44336">20</text>
  <text x="245" y="280" text-anchor="middle" font-size="14" fill="#333">火</text>
  
  <!-- 柱子：土 85 -->
  <rect x="310" y="78" width="70" height="182" fill="#FF9800" opacity="0.8"/>
  <text x="345" y="70" text-anchor="middle" font-size="12" font-weight="bold" fill="#FF9800">85</text>
  <text x="345" y="280" text-anchor="middle" font-size="14" fill="#333">土</text>
  
  <!-- 柱子：金 30 -->
  <rect x="410" y="188" width="70" height="72" fill="#FFC107" opacity="0.8"/>
  <text x="445" y="180" text-anchor="middle" font-size="12" font-weight="bold" fill="#FFC107">30</text>
  <text x="445" y="280" text-anchor="middle" font-size="14" fill="#333">金</text>
  
  <!-- 柱子：水 60 -->
  <rect x="510" y="118" width="70" height="142" fill="#2196F3" opacity="0.8"/>
  <text x="545" y="110" text-anchor="middle" font-size="12" font-weight="bold" fill="#2196F3">60</text>
  <text x="545" y="280" text-anchor="middle" font-size="14" fill="#333">水</text>
  
  <!-- 结论 -->
  <text x="340" y="310" text-anchor="middle" font-size="11" fill="#666">结论：土旺（得令得地），火弱（失令），日主偏旺</text>
</svg>
```

---

## 八、输出规范

1. **图表与文字交替穿插**：由于 `show_widget` 生成的 SVG 在对话界面中以独立消息卡片呈现，无法物理嵌入文字段落内部。因此必须在对话流程中**交替输出**：先输出对应段落的文字 → 调用 `show_widget` 生成图表 → 再输出图表解读和下一段文字。禁止先集中输出全部文字再集中生成图表，反之亦然。
2. **每个图表必须有标题**：说明图表内容
3. **图表后必须跟解读文字**：不要只给图不给解释，图表卡片后必须立即输出 2-3 句解读
4. **图表与文字互补**：图表展示结构，文字阐述含义
5. **避免过度渲染**：图表服务于分析，不要为了好看而生成无关图表
6. **响应式考虑**：SVG 在不同设备上均可缩放显示
7. **配色一致**：同一命盘分析中的图表使用统一的五行配色

---

## 九、图表生成优先级

| 优先级 | 图表类型 | 触发阶段 | 必做/选做 |
| :--- | :--- | :--- | :--- |
| P0 | 八字四柱排盘表 | 八字排盘完成 | 必做 |
| P0 | 五行力量分布图 | 旺衰判断后 | 必做 |
| P1 | 十神关系图 | 十神排列后 | 必做 |
| P1 | 紫微十二宫格图 | 紫微排盘完成 | 必做 |
| P1 | 大运流年时间线 | 大运排布后 | 必做 |
| P2 | 面相十二宫示意图 | 面相分析阶段 | 必做 |
| P2 | 手相主线示意图 | 手相分析阶段 | 必做 |
| P3 | 三法合一验证对照表 | 综合断事阶段 | 选做 |

---

## 十、注意事项

1. **图表不是替代文字**：图表用于直观展示结构关系，详细的命理推断仍需文字阐述
2. **保持简洁**：SVG 代码不宜过长，每个图表控制在合理大小
3. **中文显示**：确保 SVG 中的中文文字正确编码
4. **数据准确**：图表中的数据必须与文字分析完全一致
5. **逐步展示**：复杂分析分多个图表逐步展示，不要一次性堆叠过多信息
