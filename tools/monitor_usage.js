#!/usr/bin/env node
/**
 * bazi-engine 断语库使用监控脚本
 * --------------------------------------------
 * 用途：检测断语库文本是否被未经许可复用（抄袭/商用）。
 * 原理：读取本地私密指纹句清单 .fingerprints.json（勿提交到公开仓库），
 *       逐句调用 GitHub Code Search API 搜索精确匹配，命中即存在疑似复用。
 *
 * 用法：
 *   node tools/monitor_usage.js                     # 未认证：输出各指纹句的手动搜索链接
 *   GITHUB_TOKEN=xxx node tools/monitor_usage.js    # 认证：自动调用 GitHub Code Search
 *   node tools/monitor_usage.js --token=xxx         # 等价写法
 *
 * 说明：
 *   - GitHub Code Search API 必须认证（免费 token 即可，GitHub Settings → Developer settings → Tokens）。
 *   - Code Search 只覆盖公开仓库；闭源付费产品的复用需配合百度/必应/Google 手动搜索（脚本会输出链接）。
 *   - 建议每月跑一次；命中结果请人工核实后再取证（截图 + 时间戳）。
 */

const fs = require('fs');
const path = require('path');

const FP_FILE = path.join(__dirname, '..', '.fingerprints.json');
const CODE_SEARCH = 'https://api.github.com/search/code';
const USER_AGENT = 'bazi-engine-usage-monitor';

function loadFingerprints() {
  if (!fs.existsSync(FP_FILE)) {
    console.error('[!] 未找到指纹句清单：' + FP_FILE);
    console.error('    该文件为本地私密文件（.gitignore 已排除），请从备份恢复或重新生成。');
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(FP_FILE, 'utf-8'));
}

function searchLinks(text) {
  const quoted = '"' + text + '"';
  return {
    github: 'https://github.com/search?q=' + encodeURIComponent(quoted) + '&type=code',
    baidu: 'https://www.baidu.com/s?wd=' + encodeURIComponent(quoted),
    bing: 'https://www.bing.com/search?q=' + encodeURIComponent(quoted),
  };
}

function getToken() {
  const arg = process.argv.find((a) => a.startsWith('--token='));
  return process.env.GITHUB_TOKEN || (arg ? arg.slice('--token='.length) : '');
}

async function searchGitHub(token, phrase) {
  const headers = {
    'Accept': 'application/vnd.github+json',
    'User-Agent': USER_AGENT,
    'Authorization': 'token ' + token,
  };
  const url = CODE_SEARCH + '?q=' + encodeURIComponent('"' + phrase + '"');
  const res = await fetch(url, { headers });
  if (res.status === 401) throw new Error('GitHub Token 无效（401）。请检查 GITHUB_TOKEN。');
  if (res.status === 403) throw new Error('GitHub API 限流（403）。稍后再试，或检查 token 配额。');
  if (res.status === 422) throw new Error('搜索语法被拒（422）。');
  if (!res.ok) throw new Error('GitHub API 错误：HTTP ' + res.status);
  return res.json();
}

async function main() {
  const data = loadFingerprints();
  const fps = data.fingerprints;
  const token = getToken();

  console.log('========================================================');
  console.log(' bazi-engine 断语库使用监控');
  console.log(' 指纹句数量: ' + fps.length + '  | 创建: ' + data.created + ' | v' + data.engine_version);
  console.log(' 模式: ' + (token ? '自动搜索（GitHub Code Search API）' : '手动模式（输出搜索链接）'));
  console.log('========================================================');

  let totalHits = 0;
  const hits = [];

  for (let i = 0; i < fps.length; i++) {
    const fp = fps[i];
    const no = String(i + 1).padStart(2, '0');
    process.stdout.write('[' + no + '/' + fps.length + '] ' + fp.id + ' (' + fp.category + ') ... ');

    if (token) {
      try {
        const r = await searchGitHub(token, fp.text);
        if (r.total_count > 0) {
          totalHits += r.total_count;
          hits.push({ id: fp.id, count: r.total_count, items: r.items || [] });
          console.log('命中 ' + r.total_count + ' 处 ⚠');
          for (const it of (r.items || []).slice(0, 5)) {
            console.log('      - ' + it.repository.full_name + ' @ ' + it.path);
          }
        } else {
          console.log('0 命中 ✓');
        }
      } catch (e) {
        console.log('搜索失败: ' + e.message);
        if (/401|403/.test(e.message)) break;
      }
    } else {
      const links = searchLinks(fp.text);
      console.log('（手动模式）');
      console.log('      指纹句: ' + fp.text);
      console.log('      GitHub: ' + links.github);
      console.log('      百度:   ' + links.baidu);
      console.log('      必应:   ' + links.bing);
    }
  }

  console.log('========================================================');
  if (token) {
    if (totalHits === 0) {
      console.log(' 结果: 未发现公开仓库存在断语库指纹句，一切正常 ✓');
    } else {
      console.log(' 结果: 发现 ' + totalHits + ' 处疑似复用 ⚠ 请人工核实取证：');
      for (const h of hits) {
        for (const it of h.items) {
          console.log('   - ' + h.id + ' → ' + it.repository.html_url + ' (path: ' + it.path + ')');
        }
      }
      console.log(' 取证建议: 截图 + 时间戳 + 保留仓库链接；商用行为再按 LICENSE 维权。');
    }
  } else {
    console.log(' 提示: 未配置 GITHUB_TOKEN，以上为手动搜索链接。');
    console.log(' 设置方式: GITHUB_TOKEN=xxx node tools/monitor_usage.js');
    console.log(' 说明: GitHub Code Search 仅覆盖公开仓库；闭源商用需自行搜索百度/必应/Google。');
  }
  console.log('========================================================');
}

main().catch((e) => {
  console.error('[!] 运行失败:', e.message);
  process.exit(1);
});
