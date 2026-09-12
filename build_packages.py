#!/usr/bin/env python3
"""生成合并后的 Packages 索引：
- 镜像包（mirror/initnil.Packages）原样保留全部字段（含 Sileodepiction 等）
- 本地包（debs/ 中不在镜像里的）由 dpkg-scanpackages 生成，并注入 Icon 字段
"""
import re, subprocess, os, sys

repo = os.path.dirname(os.path.abspath(__file__))
os.chdir(repo)

ICON_BASE = 'https://gan-jibamao.github.io/repo/icons'

# 1) 镜像包条目（原样保留）
mirror_path = os.path.join('mirror', 'initnil.Packages')
if os.path.exists(mirror_path):
    initnil = open(mirror_path, encoding='utf-8').read().strip()
    initnil_names = set(re.findall(r'^Package:\s*(\S+)', initnil, re.M))
else:
    initnil = ''
    initnil_names = set()

# 2) 用 scanpackages 生成全部条目（含正确 Filename/Size/哈希）
out = subprocess.run(['dpkg-scanpackages', '-m', 'debs'],
                     capture_output=True, text=True)
all_entries = [p for p in out.stdout.split('\n\n') if p.strip()]

# 3) 本地条目 = 不在镜像清单里的
local_entries = []
for para in all_entries:
    m = re.search(r'^Package:\s*(\S+)', para, re.M)
    if m and m.group(1) not in initnil_names:
        local_entries.append(para)

# 4) 给本地条目注入 Icon
local_final = []
for para in local_entries:
    m = re.search(r'^Package:\s*(\S+)', para, re.M)
    name = m.group(1)
    icon = f'Icon: {ICON_BASE}/{name}.png'
    lines = para.split('\n')
    new = []
    for line in lines:
        new.append(line)
        if line.startswith('Package:'):
            new.append(icon)
    local_final.append('\n'.join(new))

# 5) 合并写入
parts = [p for p in ([initnil] + local_final) if p]
open('Packages', 'w', encoding='utf-8').write('\n\n'.join(parts) + '\n')

print(f'Packages 生成完成：镜像 {len(initnil_names)} + 本地 {len(local_final)} = {len(initnil_names) + len(local_final)} 个包')
