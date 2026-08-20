"""bazi-engine 引擎 dist 合规软化工具（C 端微信生态合规用）

用途：bazi-engine 的 engine.dist.js 为专业术语（姻缘/桃花/大运/运势/八字…），
bazi-app（C 端）因微信生态合规要求需软化为大众话术。本工具在构建后对 dist 做术语替换，
产出合规版，避免手改构建产物（坑 #41）。

用法：
    python tools/compliance_soften.py                     # 读 engine/engine.dist.js → 输出 engine/engine.compliance.js
    python tools/compliance_soften.py path/to/dist.js     # 指定输入文件（就地替换）
    python tools/compliance_soften.py --check             # 检查当前 dist 是否已软化（含敏感词检测）

替换规则（2026-08-19 提取自 bazi-app commit 2bb404f，与 bazi-app 现有定制一致）：
- 词级全局：运势→能量 / 大运→十年节奏 / 姻缘→情感 / 烂桃花→不良人际 / 命格→特质 / 八字→出生信息
- 上下文精确：桃花正缘→人际正缘 / 流年冲命宫→年度冲命宫 / 流年合命宫→年度合命宫
顺序：先长串（精确）后短串（词级），避免部分重叠误替换。

注意：B 端（bazi-engine 自身 UI）保持专业术语，本工具仅供 C 端产物使用。
"""
import sys
import os
import re

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

SENSITIVE = ['八字', '大运', '姻缘', '桃花', '运势', '命格']


def soften(text: str) -> tuple:
    """返回 (软化后文本, 替换次数)"""
    out = text
    count = 0
    # 流年：`"流年":` 是 matchRules 条件键名（匹配依赖，绝不能改），仅替换用户可见文案中的「流年」
    KEY_PLACEHOLDER = '\x00LIUNIAN_KEY\x00'
    nk = out.count('"流年":')
    out = out.replace('"流年":', KEY_PLACEHOLDER)
    for frm, to in REPLACEMENTS:
        n = out.count(frm)
        if n:
            out = out.replace(frm, to)
            count += n
    # 流年文案 → 年度（键名已保护）
    n = out.count('流年')
    if n:
        out = out.replace('流年', '年度')
        count += n
    out = out.replace(KEY_PLACEHOLDER, '"流年":')
    count += nk  # 键名恢复次数不计为文案替换，仅统计
    return out, count - nk


def main():
    args = sys.argv[1:]
    check = '--check' in args
    paths = [a for a in args if not a.startswith('--')]
    src = paths[0] if paths else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine', 'engine.dist.js')
    src = os.path.abspath(src)

    with open(src, 'r', encoding='utf-8') as f:
        content = f.read()

    if check:
        hits = {w: content.count(w) for w in SENSITIVE if w in content}
        print('敏感词残留:', hits if hits else '无 ✓（已软化）')
        sys.exit(1 if hits else 0)

    softened, n = soften(content)
    if softened == content:
        print('无需替换（已软化或无可替换项）')
        return
    with open(src, 'w', encoding='utf-8', newline='\n') as f:
        f.write(softened)
    import hashlib
    md5 = hashlib.md5(softened.encode('utf-8')).hexdigest().upper()
    print(f'已软化: {src}')
    print(f'替换 {n} 处 | MD5 {md5}')


if __name__ == '__main__':
    main()
