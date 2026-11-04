#!/usr/bin/env python3
"""生成合并后的 Packages 索引：
- 镜像包（mirror/initnil.Packages）：Sileodepiction 重写为自托管地址
- 本地包（debs/ 中不在镜像里的）：由 scanpackages 生成，注入自托管 Sileodepiction
"""
import re, subprocess, os

repo = os.path.dirname(os.path.abspath(__file__))
os.chdir(repo)

DEP_BASE = 'https://gan-jibamao.github.io/depictions'

# 1) 镜像包条目：Sileodepiction 重写为自托管地址
mirror_path = os.path.join('mirror', 'initnil.Packages')
if os.path.exists(mirror_path):
    raw = open(mirror_path, encoding='utf-8').read().strip()
    initnil_names = set(re.findall(r'^Package:\s*(\S+)', raw, re.M))
    paras = []
    for para in raw.split('\n\n'):
        m = re.search(r'^Package:\s*(\S+)', para, re.M)
        if m:
            name = m.group(1)
            dep = f'Sileodepiction: {DEP_BASE}/{name}.json'
            if re.search(r'^Sileodepiction:', para, re.M):
                para = re.sub(r'^Sileodepiction:.*$', dep, para, flags=re.M)
            else:
                para += '\n' + dep
        paras.append(para)
    initnil = '\n\n'.join(paras)
else:
    initnil = ''
    initnil_names = set()

# 2) scanpackages 生成全部条目
# 0.9.111 修：CI 上 sync_initnil.py 会从镜像拉新包，其中个别 deb 的 control
# 是 GBK/GB18030 编码（老国区包常见）。原来 text=True 强制按 utf-8 解码，
# 遇到这种包直接 UnicodeDecodeError 崩在 subprocess 里。
# 改成 capture 字节流后逐级降级解码：utf-8 → utf-8(替换) → GB18030(替换)。
# 用替换模式而不是报错 —— 索引里出现几个「」远好过整个源构建失败。
out = subprocess.run(['dpkg-scanpackages', '-m', 'debs'],
                     capture_output=True)
text = None
for enc in ('utf-8', 'gb18030'):
    try:
        text = out.stdout.decode(enc)
        break
    except UnicodeDecodeError:
        continue
if text is None:
    text = out.stdout.decode('utf-8', errors='replace')
all_entries = [p for p in text.split('\n\n') if p.strip()]

# 3) 本地条目 = 不在镜像清单里的
local_entries = []
for para in all_entries:
    m = re.search(r'^Package:\s*(\S+)', para, re.M)
    if m and m.group(1) not in initnil_names:
        local_entries.append(para)

# 4) 给本地条目注入自托管 Sileodepiction
local_final = []
for para in local_entries:
    m = re.search(r'^Package:\s*(\S+)', para, re.M)
    name = m.group(1)
    dep = f'Sileodepiction: {DEP_BASE}/{name}.json'
    lines = para.split('\n')
    new = []
    for line in lines:
        new.append(line)
        if line.startswith('Package:'):
            new.append(dep)
    local_final.append('\n'.join(new))

# 5) 合并写入
parts = [p for p in ([initnil] + local_final) if p]
open('Packages', 'w', encoding='utf-8').write('\n\n'.join(parts) + '\n')

print(f'Packages 生成完成：镜像 {len(initnil_names)} + 本地 {len(local_final)} = {len(initnil_names) + len(local_final)} 个包')
