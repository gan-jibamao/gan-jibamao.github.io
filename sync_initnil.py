#!/usr/bin/env python3
"""从 jailrepo.initnil.com 拉取 Packages 与全部 deb 到本地。
增量同步：新增/更新下载；initnil 已移除的包同步删除（仅限镜像包，不影响本地包）。
"""
import re, os, hashlib, urllib.request

BASE = 'https://jailrepo.initnil.com/'
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
DEBS_DIR = os.path.join(REPO_DIR, 'debs')
MIRROR_DIR = os.path.join(REPO_DIR, 'mirror')
MIRROR_PKG = os.path.join(MIRROR_DIR, 'initnil.Packages')
UA = {'User-Agent': 'Sileo/3.1 CFNetwork/1568 Darwin/24.0'}

os.makedirs(DEBS_DIR, exist_ok=True)
os.makedirs(MIRROR_DIR, exist_ok=True)

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()

def filenames(text):
    return set(re.findall(r'^Filename:\s*(\S+)', text, re.M))

# 1) 旧镜像清单（用于对比）
old_fn = filenames(open(MIRROR_PKG).read()) if os.path.exists(MIRROR_PKG) else set()

# 2) 新 Packages
packages = get(BASE + 'Packages').decode('utf-8')
new_fn = filenames(packages)

# 3) 删除 initnil 已移除的包（只删镜像包，不碰本地包）
removed = old_fn - new_fn
for fn in removed:
    deb = os.path.join(DEBS_DIR, os.path.basename(fn))
    if os.path.exists(deb):
        os.remove(deb)
        print('移除:', os.path.basename(fn))

# 4) 写入新 Packages
open(MIRROR_PKG, 'w', encoding='utf-8').write(packages)

# 5) 下载新增/缺失的 deb
paras = [p for p in packages.split('\n\n') if p.strip()]
ok = skip = fail = 0
for p in paras:
    m_fn = re.search(r'^Filename:\s*(\S+)', p, re.M)
    m_sha = re.search(r'^SHA256:\s*(\S+)', p, re.M)
    if not m_fn:
        continue
    fn = m_fn.group(1)
    dst = os.path.join(DEBS_DIR, os.path.basename(fn))
    want = m_sha.group(1) if m_sha else None
    if os.path.exists(dst) and want and hashlib.sha256(open(dst, 'rb').read()).hexdigest() == want:
        skip += 1
        continue
    try:
        open(dst, 'wb').write(get(BASE + fn))
        got = hashlib.sha256(open(dst, 'rb').read()).hexdigest()
        if want and got == want:
            ok += 1
        else:
            print('哈希不匹配:', fn)
            fail += 1
    except Exception as e:
        print('下载失败:', fn, e)
        fail += 1

print(f'sync done: {ok} 新增, {skip} 已存在, {len(removed)} 移除, {fail} 失败')
