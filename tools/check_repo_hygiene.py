# -*- coding: utf-8 -*-
"""公开仓库卫生门禁：阻止内部/商业文档与私密文件再次进入公开仓库。

为什么存在（2026-10 事故）：
  本仓库曾把内部文档（HANDOFF.md / 工作区说明.md / docs/history/ 下的竞对分析、发布物料、
  SkillHub-Submission-Kit 等）提交进公开仓库；即使后来 `git rm`，旧提交对象在 GitHub 上仍可按 SHA
  取回，最终只能**删库重建 + 全量重写历史**才清干净（并留下一个第三方 fork 无法回收）。
  教训：靠"记得别提交"不可靠，必须有机器门禁 —— 这就是本脚本。

两种模式：
  · 默认（CI/手动）：检查**已跟踪文件**（`git ls-files`）
  · `--staged`：检查**暂存区待提交文件**（`git diff --cached`），用于 git pre-commit 钩子 —— 在**泄漏发生前**拦截

安装钩子：`python tools/check_repo_hygiene.py --install-hook`
"""
import io
import os
import re
import subprocess
import sys

# 禁止进入公开仓库的路径模式（保持通用，不写出具体业务文档名以免自曝）
FORBIDDEN = [
    (r"(^|/)HANDOFF\.md$", "内部交接文档（含定价/渠道/卡点等商业信息）"),
    (r"(^|/)工作区说明\.md$", "内部工作区说明"),
    (r"(^|/)AI_CONTEXT\.md$", "内部上下文文档"),
    (r"^docs/history/", "历史归档（发布物料/竞对分析/验收清单）"),
    (r"^docs/course-", "课程物料（商业内容）"),
    (r"^docs/专栏/", "专栏物料（商业内容）"),
    (r"\.zip$", "发布包（构建产物，不入库）"),
    (r"qrcode", "个人二维码素材"),
    (r"^_local/", "本地临时工作目录"),
    (r"^marketing-assets/", "营销素材缓存"),
    (r"^\.dsh-uploads/", "DSH 上传临时目录"),
    (r"^\.workbuddy/", "WorkBuddy 本地缓存"),
    (r"(^|/)\.fingerprints\.json$", "溯源指纹（公开即失效）"),
]

# 高置信度的低级泄密特征（只在暂存内容上做很窄的匹配，避免误报）
SECRET_PATTERNS = [
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "私钥内容"),
]

HOOK = """#!/bin/sh
# 由 tools/check_repo_hygiene.py --install-hook 安装：提交前拦截内部文档/私密文件
exec python "$(git rev-parse --show-toplevel)/tools/check_repo_hygiene.py" --staged
"""


def sh(args):
    p = subprocess.run(args, capture_output=True)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace")


def repo_root():
    rc, out = sh(["git", "rev-parse", "--show-toplevel"])
    return out.strip() if rc == 0 else os.getcwd()


def targets(staged):
    if staged:
        rc, out = sh(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"])
    else:
        rc, out = sh(["git", "ls-files"])
    if rc != 0:
        print("⚠️ 无法读取 git 文件列表（退出码 %d），跳过检查" % rc)
        return None
    return [l for l in out.splitlines() if l.strip()]


def main():
    argv = sys.argv[1:]
    if "--install-hook" in argv:
        root = repo_root()
        hooks = os.path.join(root, ".git", "hooks")
        os.makedirs(hooks, exist_ok=True)
        hp = os.path.join(hooks, "pre-commit")
        with io.open(hp, "w", encoding="utf-8", newline="\n") as f:
            f.write(HOOK)
        print("✅ 已安装 pre-commit 钩子：%s" % hp)
        print("   （本机生效，不入库；CI 侧另有同名检查步骤）")
        return 0

    staged = "--staged" in argv
    files = targets(staged)
    if files is None:
        return 0

    scope = "暂存区" if staged else "已跟踪文件"
    hits = []
    for f in files:
        for pat, why in FORBIDDEN:
            if re.search(pat, f):
                hits.append((f, why))
                break

    secret_hits = []
    if staged:
        root = repo_root()
        for f in files:
            full = os.path.join(root, f)
            if not os.path.isfile(full):
                continue
            try:
                with io.open(full, "r", encoding="utf-8", errors="ignore") as fh:
                    head = fh.read(200000)
            except Exception:
                continue
            for pat, why in SECRET_PATTERNS:
                if re.search(pat, head):
                    secret_hits.append((f, why))

    if hits or secret_hits:
        print("❌ 公开仓库卫生门禁未通过（%s，共 %d 项）：" % (scope, len(hits) + len(secret_hits)))
        for f, why in hits:
            print("   🔴 %s   ← %s" % (f, why))
        for f, why in secret_hits:
            print("   🔴 %s   ← 疑似%s" % (f, why))
        print()
        print("   这些内容属于内部/商业资料，不得进入公开仓库（2026-10 曾因此删库重建）。")
        print("   正确做法：放进本地归档 E:\\michael\\DSHProjects\\Courses\\bazi-engine-internal\\，")
        print("   并用 .gitignore 忽略。确认确实需要提交时：git commit --no-verify（请三思）。")
        return 1

    print("✅ 公开仓库卫生门禁通过（%s %d 个文件，无内部/商业文档）" % (scope, len(files)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
