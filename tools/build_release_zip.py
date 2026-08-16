"""bazi-engine 发布包构建（SkillHub 专用）

与 tools/build_ui.py 不同，本脚本只负责把打包目录打包成 ZIP，
**排除 SkillHub 禁止的文件类型**：
- LICENSE / LICENSE-DATA（GitHub 协议标识用，但 SkillHub 禁）
- README.en.md（标准元文件，SkillHub 可能禁）

项目根的这些文件**保留**，不进 git 删除；只是不进 ZIP。
GitHub 开源项目仍然能通过项目根 LICENSE 文件正确识别协议。
"""
import zipfile
from pathlib import Path

PKG = Path(r'C:\Users\34743\.workbuddy\skills\bazi-engine')
OUT = Path(r'E:\michael\workBuddy\bazi-project\bazi-engine-v1.2.1.zip')

# SkillHub 禁止的文件类型（在 ZIP 中排除，项目根保留）
EXCLUDE_PATTERNS = {'LICENSE', 'LICENSE-DATA', 'README.en.md'}


def is_excluded(name: str) -> bool:
    """检查文件名是否在排除名单（顶层文件）"""
    base = name.split('/')[0]
    return base in EXCLUDE_PATTERNS


def main():
    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(str(OUT), 'w', zipfile.ZIP_DEFLATED) as zf:
        included = []
        excluded = []
        for p in sorted(PKG.rglob('*')):
            if not p.is_file():
                continue
            if p.suffix in {'.tmp', '.bak'}:
                continue
            arc = p.relative_to(PKG).as_posix()
            if is_excluded(arc):
                excluded.append(arc)
            else:
                zf.write(str(p), arc)
                included.append(arc)
    print(f'ZIP 输出: {OUT}')
    print(f'ZIP 大小: {OUT.stat().st_size / 1024:.1f} KB')
    print(f'包含文件: {len(included)} 个')
    print(f'排除文件: {len(excluded)} 个')
    for e in excluded:
        print(f'  - {e}')
    # 校验
    z = zipfile.ZipFile(str(OUT))
    names = z.namelist()
    bad = [n for n in names if any(n.split('/')[0] == x for x in EXCLUDE_PATTERNS)]
    print()
    print('校验：剩余排除名单文件 →', bad if bad else '无 ✓')


if __name__ == '__main__':
    main()
