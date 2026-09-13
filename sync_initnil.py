#!/usr/bin/env python3
"""从 jailrepo.initnil.com 拉取 Packages 与全部 deb 到本地（增量，跳过已存在且哈希一致的）。
只增不删：initnil 移除的包仍保留在本地源中，不会删除。
"""
import re, os, hashlib, urllib.request

BASE = 'https://jailrepo.initnil.com/'
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
DEBS_DIR = os.path.join(REPO_DIR, 'debs')
MIRROR_DIR = os.path.join(REPO_DIR, 'mirror')
UA = {'User-Agent': 'Sileo/3.1 CFNetwork/1568 Darwin/24.0'}

os.makedirs(DEBS_DIR, exist_ok=True)
os.makedirs(MIRROR_DIR, exist_ok=True)

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()

packages = get(BASE + 'Packages').decode('utf-8')
open(os.path.join(MIRROR_DIR, 'initnil.Packages'), 'w', encoding='utf-8').write(packages)

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

print(f'sync done: {ok} 新增, {skip} 已存在, {fail} 失败')
