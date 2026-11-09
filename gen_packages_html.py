#!/usr/bin/env python3
"""从 Packages 索引生成网页版包列表 packages.html。"""
import re, html

BASE = 'https://gan-jibamao.github.io'

def parse(path):
    paras = [p for p in open(path, encoding='utf-8').read().split('\n\n') if p.strip()]
    out = []
    for p in paras:
        def f(k):
            m = re.search(rf'^{k}:\s*(.*)$', p, re.M)
            return m.group(1).strip() if m else ''
        out.append({
            'package': f('Package'), 'name': f('Name') or f('Package'),
            'version': f('Version'), 'author': f('Author') or f('Maintainer'),
            'desc': f('Description'), 'filename': f('Filename'), 'section': f('Section'),
            'arch': f('Architecture'),
        })
    return out

def ver_key(v):
    """dpkg 版本比较键：数字段按数值、字母段按字典序，逐段比较。"""
    parts = [s for s in re.split(r'[.\-~:]', str(v or '0').replace('+', '.')) if s]
    return [(0, int(s), '') if s.isdigit() else (1, 0, s) for s in parts]


def dedupe(rows):
    """同一包的多版本 / 多架构只保留最新一条，架构合并。
    versions 记不同版本号，不是 stanza 数（一版两架构只算 1 版）。"""
    best, archs, versions = {}, {}, {}
    for r in rows:
        pid = r['package']
        if not pid:
            continue
        arch = r['arch'].replace('iphoneos-', '')
        if pid not in best:
            best[pid] = r
            archs[pid] = [arch] if arch else []
            versions[pid] = {r['version']}
            continue
        versions[pid].add(r['version'])
        if arch and arch not in archs[pid]:
            archs[pid].append(arch)
        if ver_key(r['version']) > ver_key(best[pid]['version']):
            best[pid] = r
    for pid, r in best.items():
        r['archs'] = archs[pid]
        r['versions'] = versions[pid]
    return list(best.values())


pkgs = dedupe(parse('Packages'))
pkgs.sort(key=lambda x: x['name'].lower())

items = []
for p in pkgs:
    name = html.escape(p['name']); ver = html.escape(p['version'])
    author = html.escape(p['author']); desc = html.escape(p['desc'])
    fn = html.escape(p['filename']); pkg = html.escape(p['package'])
    key = html.escape((p['name'] + ' ' + p['package'] + ' ' + p['desc']).lower())
    meta = ' · '.join(p['archs']) if p.get('archs') else ''
    if len(p.get('versions', [])) > 1:
        meta += f" · {len(p['versions'])} 个版本"
    items.append(f'''
    <div class="item" data-search="{key}">
      <div class="head"><span class="pname">{name}</span><span class="pver">v{ver}</span></div>
      <div class="pauthor">{author}</div>
      <div class="pdesc">{desc}</div>
      <div class="pmeta">{meta}</div>
      <div class="btns">
        <a class="btn dl" href="{BASE}/{fn}">下载 deb</a>
        <a class="btn sileo" href="sileo://package/{pkg}">在 Sileo 打开</a>
      </div>
    </div>''')

page = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#f3f4f9">
<title>插件列表 · 做爱源</title>
<link rel="stylesheet" href="theme.css?v=2">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }}
  body {{
    font-family:-apple-system,"SF Pro Text","PingFang SC","Helvetica Neue",sans-serif;
    background:var(--bg); color:var(--txt);
    min-height:100vh; padding:24px 16px 60px;
  }}
  .wrap {{ max-width:560px; margin:0 auto; }}
  header {{ text-align:center; padding:20px 0 8px; }}
  header h1 {{ font-size:24px; font-weight:800; letter-spacing:.01em; }}
  header p {{ color:var(--dim-2); font-size:13px; margin-top:6px; }}
  .search {{
    width:100%; padding:14px 18px; margin:16px 0 20px;
    border-radius:14px; border:1px solid var(--line);
    background:var(--panel); color:var(--txt); font-size:16px; outline:none;
    -webkit-appearance:none; appearance:none;
    transition:border-color .18s, box-shadow .18s;
  }}
  .search:focus {{ border-color:rgba(99,102,241,.45); box-shadow:var(--focus-shadow); }}
  .search::-webkit-search-decoration,
  .search::-webkit-search-cancel-button {{ -webkit-appearance:none; display:none; }}
  .search::placeholder {{ color:var(--dim-2); }}
  .item {{
    background:var(--panel); border:1px solid var(--line);
    border-radius:18px; padding:18px; margin-bottom:12px;
    box-shadow:var(--pkg-shadow);
  }}
  .head {{ display:flex; justify-content:space-between; align-items:center; gap:10px; }}
  .pname {{ font-size:17px; font-weight:700; }}
  .pver {{
    font-size:12px; color:var(--ver-fg); background:var(--ver-bg);
    border:1px solid var(--ver-bd); padding:3px 10px; border-radius:20px;
    white-space:nowrap; flex:none;
  }}
  .pauthor {{ color:var(--dim-2); font-size:12px; margin:4px 0 8px; }}
  .pdesc {{ color:var(--dim); font-size:14px; line-height:1.5; }}
  .pmeta {{ color:var(--dim-2); font-size:11px; margin-top:8px;
           font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }}
  .btns {{ display:flex; gap:10px; margin-top:14px; }}
  .btn {{
    flex:1; text-align:center; padding:10px 0; border-radius:12px;
    font-size:14px; font-weight:600; text-decoration:none;
  }}
  .btn.dl {{ background:var(--btn2-bg); border:1px solid var(--btn2-bd); color:var(--btn2-fg); }}
  .btn.sileo {{
    background:linear-gradient(135deg,#4f46e5,#7c3aed 55%,#9333ea);
    color:#fff; box-shadow:0 6px 16px rgba(99,102,241,.28);
  }}
  .back {{
    display:inline-block; margin-top:20px; color:var(--dim);
    font-size:14px; text-decoration:none;
  }}
  .count {{ color:var(--dim-2); font-size:12px; text-align:center; margin-bottom:12px; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>插件列表</h1>
    <p>共 {len(pkgs)} 个插件 · 点击下载或直接在 Sileo 打开</p>
  </header>
  <input class="search" id="q" placeholder="搜索插件名 / 描述..." oninput="filter()">
  <div class="count" id="count"></div>
  <div id="list">{''.join(items)}</div>
  <a class="back" href="./">← 返回首页</a>
</div>
<script>
  function filter() {{
    var q = document.getElementById('q').value.toLowerCase();
    var items = document.querySelectorAll('.item');
    var n = 0;
    items.forEach(function(it) {{
      var hit = it.dataset.search.indexOf(q) > -1;
      it.style.display = hit ? '' : 'none';
      if (hit) n++;
    }});
    document.getElementById('count').textContent = n === {len(pkgs)} ? '' : '显示 ' + n + ' / {len(pkgs)} 个';
  }}
</script>
</body>
</html>'''

open('packages.html', 'w', encoding='utf-8').write(page)
print(f'packages.html 生成完成：{len(pkgs)} 个包')
