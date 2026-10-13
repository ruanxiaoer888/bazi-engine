"""bazi-engine 引擎 dist 合规软化工具（C 端微信生态合规用）

用途：bazi-engine 的 engine.dist.js 含专业术语（姻缘/桃花/大运/运势/八字…），
bazi-app（C 端）因微信生态合规要求需软化为大众话术。

【2026-10-13 重写 · 结构感知软化】原实现是"整文件全局文本替换"，会连**机器读的标识**一起改，
已造成 4 类越界（由 tools/check_compliance_equivalence.js 门禁实测）：
  ① 引擎代码里的比较字面量 `k==='流年'` → `k==='年度'`
     → matchRules 中"流年/流月/流日条件不参与主匹配"的守卫失效 → **每张命盘凭空多出 8 条流年断语**；
  ② 规则 id `liunian_流年XXX` → `liunian_年度XXX` → 面板按 id `findRule()` 全部查不到（12 个 id）；
  ③ `category` 被改名 38 处（流年→年度、大运→十年节奏）→ 消费方 `cats['流年']` / `cats['大运']` 直接取空；
  ④ `source`（古籍出处）被改写 1 处 —— 与授权书"不得删除/篡改 source"的义务相冲突。

现在改为两条通道，互不越界：
  · **数据区**（`const RULES = [...]` 那一行）：解析 JSON，只软化 `conclusion` 与 `suggestion` 两个文案字段；
    `id` / `category` / `condition` / `source` / `confidence` 原样保留。
  · **代码区**：软化前先把"标识字面量"（出现在 ===/!==/case/includes() 等位置的字符串）占位保护，
    软化后再还原 → 代码里的注释与用户可见文案会被软化，判断逻辑一个字都不动。

用法：
    python tools/compliance_soften.py                    # 读 engine/engine.dist.js → 写 engine/engine.compliance.js（不动 dist）
    python tools/compliance_soften.py path/to/dist.js    # 就地软化指定文件（C 端替换自己那份 dist 时用）
    python tools/compliance_soften.py --check            # 校验产物是否已软化（判据=再软化一次不会产生任何变化）
    python tools/compliance_soften.py <file> --check     # 校验指定文件

（2026-10-13 同时修掉一个地雷：原实现**无参数运行时也是就地改写**，与文档说明的"输出 compliance.js"不符——
  照着 docstring 跑一条 `python tools/compliance_soften.py` 就会把仓库里的 engine.dist.js 就地软化掉。
  现无参数运行只写 compliance.js，绝不修改 dist。）
"""
import hashlib
import json
import os
import re
import sys

# 精确串优先（长→短），词级兜底
REPLACEMENTS = [
    ('流年冲命宫', '年度冲命宫'),
    ('流年合命宫', '年度合命宫'),
    ('桃花正缘', '人际正缘'),
    ('烂桃花', '不良人际'),
    ('八字命盘', '出生信息命盘'),  # 防御：避免「八字→出生信息」把标题变成「出生信息命盘」后再处理
    ('运势', '能量'),
    ('大运', '十年节奏'),
    ('姻缘', '情感'),
    ('命格', '特质'),
    ('八字', '出生信息'),
]

# 注意：'桃花' 不列入 SENSITIVE——它是引擎神煞内部 key（{name:'桃花'}/case '桃花:'/s.name==='桃花'），
# 全局替换会破坏匹配逻辑；真正敏感的组合表述「烂桃花」「桃花正缘」已在上方替换（→不良人际/人际正缘）。
SENSITIVE = ['八字', '大运', '姻缘', '运势', '命格']

# 机器读的标识：出现在比较 / 分支 / 成员判断位置的字符串字面量，一律占位保护，不得软化
IDENT_RE = re.compile(
    r"""(['"])(?P<a>[^'"\\]*)\1\s*(?:===|!==|==|!=)                # '流年' ===
      | (?:===|!==|==|!=)\s*(['"])(?P<b>[^'"\\]*)\3              # === '流年'
      | \bcase\s+(['"])(?P<c>[^'"\\]*)\5                         # case '桃花'
      | \.(?:includes|indexOf|startsWith|endsWith)\(\s*(['"])(?P<d>[^'"\\]*)\6
    """,
    re.X,
)

RULES_RE = re.compile(r'^const RULES = (\[.*\]);[ \t]*$', re.M)

PROSE_FIELDS = ('conclusion', 'suggestion')


def _apply_words(s: str):
    """对一段纯文案做软化，返回 (新文案, 词频明细)"""
    out = s
    detail = {}
    for frm, to in REPLACEMENTS:
        n = out.count(frm)
        if n:
            out = out.replace(frm, to)
            detail[frm] = detail.get(frm, 0) + n
    n = out.count('流年')
    if n:
        out = out.replace('流年', '年度')
        detail['流年'] = detail.get('流年', 0) + n
    return out, detail


def _protect_identifiers(code: str):
    """把标识字面量替换为占位符，返回 (受保护文本, {占位符: 原文})"""
    spans = sorted({sp for m in IDENT_RE.finditer(code)
                    for g in ('a', 'b', 'c', 'd')
                    if m.group(g) is not None
                    for sp in [m.span(g)]})
    keep = {}
    parts, prev = [], 0
    for i, (s, e) in enumerate(spans):
        ph = '\x00ID%d\x00' % i
        keep[ph] = code[s:e]
        parts.append(code[prev:s])
        parts.append(ph)
        prev = e
    parts.append(code[prev:])
    return ''.join(parts), keep


def soften(text: str):
    """返回 (软化后文本, 替换总数, {位置: 词频明细})；软化是幂等的"""
    detail = {}
    m = RULES_RE.search(text)
    if not m:
        raise SystemExit('❌ 未找到 `const RULES = [...]` 数据行 —— 这不是一份 bazi-engine dist？')
    head, json_literal, tail = text[:m.start(1)], m.group(1), text[m.end(1):]

    # ── 1. 数据区：解析 JSON，只软化 conclusion / suggestion ──
    rules = json.loads(json_literal)
    n_data = 0
    for r in rules:
        for f in PROSE_FIELDS:
            v = r.get(f)
            if isinstance(v, str):
                nv, d = _apply_words(v)
                if nv != v:
                    r[f] = nv
                    n_data += sum(d.values())
    new_json = json.dumps(rules, ensure_ascii=False)
    detail['规则文案(conclusion/suggestion)'] = n_data

    # ── 2. 代码区（数据行**前后**两段）：先保护标识字面量，软化后再还原 ──
    #   注意必须是"数据行之外"，否则第 2 步的全局替换会把 id/category/condition/source 再软化一遍。
    n_code = 0
    pieces = []
    for seg in (head, tail):
        protected, keep = _protect_identifiers(seg)
        softened_seg, d = _apply_words(protected)
        for ph, original in keep.items():
            softened_seg = softened_seg.replace(ph, original)
        n_code += sum(d.values())
        pieces.append(softened_seg)
    detail['代码区文案/注释'] = n_code

    total = sum(detail.values())
    return pieces[0] + new_json + pieces[1], total, detail


def _read(p):
    with open(p, 'r', encoding='utf-8') as f:
        return f.read()


def _write_atomic(p, s):
    tmp = p + '.tmp-soften'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(s)
    os.replace(tmp, p)


def main():
    argv = sys.argv[1:]
    check = '--check' in argv
    paths = [a for a in argv if not a.startswith('--')]
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    dist = os.path.join(root, 'engine', 'engine.dist.js')
    comp = os.path.join(root, 'engine', 'engine.compliance.js')

    if check:
        src = os.path.abspath(paths[0]) if paths else (comp if os.path.exists(comp) else dist)
        content = _read(src)
        softened, n, detail = soften(content)
        print('检查对象:', src)
        if softened != content:
            print('敏感词残留:', {k: v for k, v in detail.items() if v} if n else '有')
            print('❌ 仍有可软化文案（未软化或软化不完整）')
            sys.exit(1)
        print('敏感词残留: 无 ✓（已软化）')
        sys.exit(0)

    if paths:
        src = os.path.abspath(paths[0])
        dst = src  # C 端用法：就地替换自己那份 dist
    else:
        src, dst = dist, comp  # 默认：dist → compliance.js，绝不修改 dist

    content = _read(src)
    softened, n, detail = soften(content)
    if softened == content:
        print('无需替换（已软化或无可替换项）:', dst)
        return
    _write_atomic(dst, softened)
    md5 = hashlib.md5(softened.encode('utf-8')).hexdigest().upper()
    print(f'已软化: {src} → {dst}' if src != dst else f'已软化: {src}')
    print(f'替换 {n} 处 | ' + ' + '.join(f'{k} {v}' for k, v in detail.items()))
    print(f'MD5 {md5}')
    print('提示：改动后请跑 `node tools/check_compliance_equivalence.js` 验证与 dist 行为等价')


if __name__ == '__main__':
    main()
