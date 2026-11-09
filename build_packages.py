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

# 5) 版本裁剪：每个包只保留最新 KEEP_VERSIONS 个版本
#    同一版本的多个架构全部保留（架构不是版本，不该被截断）
KEEP_VERSIONS = 3

def _field(para, key):
    m = re.search(rf'^{key}:\s*(.*)$', para, re.M)
    return m.group(1).strip() if m else ''

def _ver_key(v):
    parts = [x for x in re.split(r'[.\-~:]', str(v or '0').replace('+', '.')) if x]
    return [(0, int(x), '') if x.isdigit() else (1, 0, x) for x in parts]

def prune(paras, keep=KEEP_VERSIONS):
    groups = {}
    order = []
    for para in paras:
        pid = _field(para, 'Package')
        ver = _field(para, 'Version')
        if pid not in groups:
            groups[pid] = {}
            order.append(pid)
        groups[pid].setdefault(ver, []).append(para)
    out = []
    for pid in order:
        vers = groups[pid]
        kept = sorted(vers.keys(), key=_ver_key, reverse=True)[:keep]
        for ver in vers:              # 按原始顺序输出，避免索引顺序抖动
            if ver in kept:
                out.extend(vers[ver])
    return out

# 6) 合并写入
#    注意：initnil 是一个「含 N 条 stanza 的大字符串」，必须先拆成单条再裁剪，
#    否则整块会被当成一个元素，只认到第一个 Package 就原样通过。
parts = []
for chunk in ([initnil] + local_final):
    if chunk:
        parts.extend(p for p in chunk.split('\n\n') if p.strip())

before = len(parts)
parts = prune(parts)

open('Packages', 'w', encoding='utf-8').write('\n\n'.join(parts) + '\n')

print(f'Packages 生成完成：镜像 {len(initnil_names)} + 本地 {len(local_final)} = {before} 个包')
print(f'版本裁剪（每包保留最新 {KEEP_VERSIONS} 版）：{before} -> {len(parts)} 条')
