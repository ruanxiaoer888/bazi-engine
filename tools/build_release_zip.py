"""bazi-engine 发布包构建（SkillHub 专用，平台无关版）

用法：
    python tools/build_release_zip.py            # 打包当前工作区 → bazi-engine-v1.3.0.zip
    python tools/build_release_zip.py v1.4.0     # 指定版本号

要点（对齐 HANDOFF 踩坑 #17/#18/#22）：
- ZIP 内文件直接在根，无外层嵌套目录
- 排除 SkillHub 禁止的 LICENSE / LICENSE-DATA / README.en.md
- ZIP 根放 SKILL.md（从 skill/SKILL.md 复制），与项目源 skill/SKILL.md 保持同步
- 只打包可对外内容（ui/engine/kb/skill/tools + README.md），内部文档（HANDOFF/AI_CONTEXT/发布物料等）与 docs/assets 不进 ZIP
"""
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
                      'HANDOFF.md', 'AI_CONTEXT.md', 'SkillHub-Submission-Kit.md',
                      'SkillHub发布最终指引.md', '冷启动提示词_COLD_START.md',
                      '验收与截图清单_3案例.md', '.gitignore'}
# 目录内排除的子路径/文件模式
EXCLUDE_SUB = {
    'kb/04-rules-db/drafts',        # 内部取材源
    'tools/__pycache__', 'tools/_dbg', 'tools/archive',  # 归档脚本不进发布包（2026-08-19 审计修复）
    'kb/05-reference',  # 内部参考
}
EXCLUDE_NAMES = {'__pycache__', '.DS_Store', 'Thumbs.db'}


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
    nested = [n for n in names if n.count('/') == 0 and n not in ('README.md', 'SKILL.md')]
    print(f'ZIP 输出: {OUT}')
    print(f'ZIP 大小: {OUT.stat().st_size / 1024:.1f} KB')
    print(f'包含文件: {len(names)} 个')
    print('根文件:', ', '.join(sorted(n for n in names if '/' not in n)))
    print('校验-排除名单残留:', bad_root if bad_root else '无')
    print('校验-根无嵌套:', 'OK' if not nested else f'异常: {nested}')
    # 关键产物 MD5（发布验证，替代旧打包目录同步）
    import hashlib
    key_files = ['ui/index.html', 'engine/engine.dist.js', 'skill/SKILL.md', 'kb/04-rules-db/rules.json', 'SKILL.md']
    for kf in key_files:
        src = ROOT / kf
        if src.exists():
            h = hashlib.md5(src.read_bytes()).hexdigest()
            print(f'MD5 {kf}: {h}')


if __name__ == '__main__':
    main()
