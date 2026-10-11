"""bazi-engine 发布包构建（通用市场分发版，平台无关）

用法：
    python tools/build_release_zip.py            # 打包当前工作区 → bazi-engine-v1.3.0.zip
    python tools/build_release_zip.py v1.4.0     # 指定版本号

要点（对齐 HANDOFF 踩坑 #17/#18/#22）：
- ZIP 内文件直接在根，无外层嵌套目录
- 排除平台禁止的 LICENSE / LICENSE-DATA / README.en.md（数据许可改以 DATA-LICENSE.txt 随包分发）
- ZIP 根放 SKILL.md（从 skill/SKILL.md 复制），与项目源 skill/SKILL.md 保持同步
- 只打包可对外内容（ui/engine/kb/skill/tools + README.md），内部文档（HANDOFF/AI_CONTEXT/发布物料等）与 docs/assets 不进 ZIP
"""
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION = sys.argv[1] if len(sys.argv) > 1 else 'v1.3.0'
OUT = ROOT / f'bazi-engine-{VERSION}.zip'

# 顶层目录白名单（只打包这些目录）
INCLUDE_DIRS = {'ui', 'engine', 'kb', 'skill', 'tools'}
# 顶层文件白名单（根文件只放 README.md；SKILL.md 单独复制到根）
INCLUDE_ROOT_FILES = {'README.md'}
# SkillHub 禁止 / 内部不对外
EXCLUDE_ROOT_FILES = {'LICENSE', 'LICENSE-DATA', 'README.en.md',
                      'HANDOFF.md', 'SkillHub-Submission-Kit.md',
                      'SkillHub发布最终指引.md',
                      '验收与截图清单_3案例.md', '.gitignore'}
# 目录内排除的子路径/文件模式
EXCLUDE_SUB = {
    'kb/04-rules-db/drafts',        # 内部取材源
    'kb/02-rules/bazi-mbti.md',     # 2026-10：早期版本来源不明（无作者无 URL），现版已重写但按约定仍不纳入对外/商用交付
    'tools/__pycache__', 'tools/_dbg', 'tools/archive',  # 归档脚本不进发布包（2026-08-19 审计修复）
    'kb/05-reference',  # 内部参考
    # 2026-10-11：作者运维工具不进市场包（compliance_soften 涉及自有 C 端产品口径，publish_clawhub 为发布操作脚本），
    # 与交付标的无关且会暴露内部业务流程
    'tools/compliance_soften.py', 'tools/publish_clawhub.ps1',
}
EXCLUDE_NAMES = {'__pycache__', '.DS_Store', 'Thumbs.db'}

# 2026-10 风险面扫描修复：THIRD-PARTY.md 声明"kb/03-classics/ 中的 docx 提取件不进商业交付包"，
# 但当时 EXCLUDE_SUB 并未包含它们 → 声明与实际不符（发布包/Release 附件里实有 6 个 docx 提取件：
# bazi-wuxing-table / ditian-sui / qiongtong-baojian / sanming-tonghui / workflow-full / yuanhai-ziping）。
# 现改为**按文件头部的来源标记自动排除**，并在打包后做硬校验（见 main 的 docx_left 检查），
# 保证"声明即事实"：以后任何新增的 docx 提取件也会自动被挡在交付包之外。
DOCX_PROVENANCE_RE = re.compile(r'来源[：:].{0,60}\.docx', re.IGNORECASE)

# 本次构建中被"docx 来源"规则自动排除的文件（打印出来，避免静默）
DOCX_EXCLUDED = []


def has_docx_provenance(path: Path) -> bool:
    """文件头部 1500 字符内声明了 .docx 来源 → 第三方整理件，不进交付包"""
    if path.suffix.lower() not in ('.md', '.txt'):
        return False
    try:
        head = path.read_text(encoding='utf-8', errors='ignore')[:1500]
    except Exception:
        return False
    return bool(DOCX_PROVENANCE_RE.search(head))



def collect() -> list:
    """返回 [(arc_name, abs_path)]，arc 为 ZIP 内路径（根无嵌套）"""
    items = []
    # 根文件
    for f in sorted(ROOT.iterdir()):
        if not f.is_file():
            continue
        if f.name in INCLUDE_ROOT_FILES:
            items.append((f.name, f))
    # 根 SKILL.md ← skill/SKILL.md（坑 #22：ZIP 根必须有且与源同步）
    skill_src = ROOT / 'skill' / 'SKILL.md'
    if skill_src.exists():
        items.append(('SKILL.md', skill_src))
    # 2026-10：数据许可随包分发。平台禁止 LICENSE/LICENSE-DATA 文件名，故改名为 DATA-LICENSE.txt，
    # 避免"包内含 1000 条 NC 数据却无任何数据许可声明"（第三方据此主张 MIT/MIT-0 授权）。
    lic_data = ROOT / 'LICENSE-DATA'
    if lic_data.exists():
        items.append(('DATA-LICENSE.txt', lic_data))
    # 2026-10：第三方权利与排除清单必须随包分发（否则包内数据无权利说明）
    tp = ROOT / 'THIRD-PARTY.md'
    if tp.exists():
        items.append(('THIRD-PARTY.md', tp))
    # 白名单目录
    for d in sorted(ROOT.iterdir()):
        if not d.is_dir() or d.name not in INCLUDE_DIRS:
            continue
        for p in sorted(d.rglob('*')):
            if not p.is_file():
                continue
            if p.name in EXCLUDE_NAMES:
                continue
            arc = p.relative_to(ROOT).as_posix()
            if any(arc.startswith(s) for s in EXCLUDE_SUB):
                continue
            if has_docx_provenance(p):
                DOCX_EXCLUDED.append(arc)
                continue
            if arc.endswith(('.tmp', '.bak')):
                continue
            items.append((arc, p))
    return items


def main():
    if OUT.exists():
        OUT.unlink()
    items = collect()
    with zipfile.ZipFile(str(OUT), 'w', zipfile.ZIP_DEFLATED) as zf:
        for arc, path in items:
            zf.write(str(path), arc)
    # 校验
    z = zipfile.ZipFile(str(OUT))
    names = z.namelist()
    bad_root = [n for n in names if n.split('/')[0] in EXCLUDE_ROOT_FILES]
    nested = [n for n in names if n.count('/') == 0 and n not in ('README.md', 'SKILL.md', 'DATA-LICENSE.txt', 'THIRD-PARTY.md')]
    print(f'ZIP 输出: {OUT}')
    print(f'ZIP 大小: {OUT.stat().st_size / 1024:.1f} KB')
    print(f'包含文件: {len(names)} 个')
    print('根文件:', ', '.join(sorted(n for n in names if '/' not in n)))
    print('校验-排除名单残留:', bad_root if bad_root else '无')
    print('校验-根无嵌套:', 'OK' if not nested else f'异常: {nested}')
    # 硬校验：交付包内不得含 docx 提取件（THIRD-PARTY.md 声明的"不进商业交付包"必须为真）
    docx_left = []
    for n in names:
        if not n.lower().endswith(('.md', '.txt')):
            continue
        try:
            head = z.read(n)[:1500].decode('utf-8', 'ignore')
        except Exception:
            continue
        if DOCX_PROVENANCE_RE.search(head):
            docx_left.append(n)
    print('自动排除(来源标注为 .docx 的第三方整理件):', ', '.join(sorted(DOCX_EXCLUDED)) or '无')
    print('校验-包内无 docx 提取件:', 'OK' if not docx_left else f'❌ 异常: {docx_left}')
    # 关键产物 MD5（发布验证，替代旧打包目录同步）
    import hashlib
    key_files = ['ui/index.html', 'engine/engine.dist.js', 'skill/SKILL.md', 'kb/04-rules-db/rules.json', 'SKILL.md']
    for kf in key_files:
        src = ROOT / kf
        if src.exists():
            h = hashlib.md5(src.read_bytes()).hexdigest()
            print(f'MD5 {kf}: {h}')
    if docx_left:
        print('\n❌ 交付包仍含 docx 提取件（第三方整理，权利链不完整）：' + ', '.join(docx_left))
        sys.exit(1)


if __name__ == '__main__':
    main()
