#!/usr/bin/env python3
"""从 Packages 索引生成网页版包列表 packages.html。"""
import re, html

BASE = 'https://gan-jibamao.github.io/repo'

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
        })
    return out

pkgs = parse('Packages')
pkgs.sort(key=lambda x: x['name'].lower())

items = []
for p in pkgs:
    name = html.escape(p['name']); ver = html.escape(p['version'])
    author = html.escape(p['author']); desc = html.escape(p['desc'])
    fn = html.escape(p['filename']); pkg = html.escape(p['package'])
    key = html.escape((p['name'] + ' ' + p['package'] + ' ' + p['desc']).lower())
    items.append(f'''
    <div class="item" data-search="{key}">
      <div class="head"><span class="pname">{name}</span><span class="pver">v{ver}</span></div>
      <div class="pauthor">{author}</div>
      <div class="pdesc">{desc}</div>
      <div class="btns">
        <a class="btn dl" href="{BASE}/{fn}">下载 deb</a>
        <a class="btn sileo" href="sileo://package/{pkg}">在 Sileo 打开</a>
      </div>
    </div>''')

page = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>插件列表 · 做爱源</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family:-apple-system,"PingFang SC","Helvetica Neue",sans-serif;
    background:linear-gradient(135deg,#0f172a,#1e1b4b); color:#e2e8f0;
    min-height:100vh; padding:24px 16px 60px;
  }}
  .wrap {{ max-width:560px; margin:0 auto; }}
  header {{ text-align:center; padding:20px 0 8px; }}
  header h1 {{ font-size:24px; }}
  header p {{ color:#94a3b8; font-size:13px; margin-top:6px; }}
  .search {{
    width:100%; padding:14px 18px; margin:16px 0 20px;
    border-radius:14px; border:1px solid rgba(255,255,255,0.12);
    background:rgba(255,255,255,0.06); color:#e2e8f0; font-size:16px; outline:none;
  }}
  .search::placeholder {{ color:#64748b; }}
  .item {{
    background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.1);
    border-radius:18px; padding:18px; margin-bottom:12px;
  }}
  .head {{ display:flex; justify-content:space-between; align-items:center; }}
  .pname {{ font-size:17px; font-weight:700; }}
  .pver {{
    font-size:12px; color:#a5b4fc; background:rgba(99,102,241,0.15);
    padding:3px 10px; border-radius:20px;
  }}
  .pauthor {{ color:#94a3b8; font-size:12px; margin:4px 0 8px; }}
  .pdesc {{ color:#cbd5e1; font-size:14px; line-height:1.5; }}
  .btns {{ display:flex; gap:10px; margin-top:14px; }}
  .btn {{
    flex:1; text-align:center; padding:10px 0; border-radius:12px;
    font-size:14px; font-weight:600; text-decoration:none; color:#fff;
  }}
  .btn.dl {{ background:#334155; }}
  .btn.sileo {{ background:linear-gradient(90deg,#3b82f6,#8b5cf6); }}
  .back {{
    display:inline-block; margin-top:20px; color:#94a3b8; font-size:14px; text-decoration:none;
  }}
  .count {{ color:#64748b; font-size:12px; text-align:center; margin-bottom:12px; }}
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
