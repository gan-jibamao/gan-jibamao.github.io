#!/usr/bin/env python3
"""自托管原生详情页（Sileo depiction）：
1. 从 initnil 拉取每个包的详情 JSON，下载头图（去重），改写为自托管路径，存到 depictions/
2. 为本地包（debs/ 中不在镜像里的）生成简单详情 JSON
"""
import re, os, json, subprocess, urllib.request

BASE = 'https://jailrepo.initnil.com/'
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
DEP_DIR = os.path.join(REPO_DIR, 'depictions')
IMG_DIR = os.path.join(DEP_DIR, 'images')
MIRROR_PKG = os.path.join(REPO_DIR, 'mirror', 'initnil.Packages')
DEBS_DIR = os.path.join(REPO_DIR, 'debs')
SELF_BASE = 'https://gan-jibamao.github.io/repo/depictions'
UA = {'User-Agent': 'Sileo/3.1 CFNetwork/1568 Darwin/24.0'}

os.makedirs(IMG_DIR, exist_ok=True)

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()

def deb_field(deb, field):
    try:
        out = subprocess.run(['dpkg-deb', '-f', deb, field], capture_output=True, text=True)
        return out.stdout.strip()
    except Exception:
        return ''

# ---- 1) 镜像包：拉取 initnil 详情 + 头图 ----
mirror = open(MIRROR_PKG).read()
mirror_names = set(re.findall(r'^Package:\s*(\S+)', mirror, re.M))
seen_img = {}

for p in mirror.split('\n\n'):
    m_name = re.search(r'^Package:\s*(\S+)', p, re.M)
    m_dep = re.search(r'^Sileodepiction:\s*(\S+)', p, re.M)
    if not (m_name and m_dep):
        continue
    name = m_name.group(1)
    try:
        data = json.loads(get(m_dep.group(1)))
    except Exception as e:
        print('skip', name, e)
        continue
    hdr = data.get('headerImage')
    if hdr:
        if hdr not in seen_img:
            ext = '.jpg' if 'jpg' in hdr.lower() else '.png'
            local = 'header' + ext
            dst = os.path.join(IMG_DIR, local)
            if not os.path.exists(dst):
                open(dst, 'wb').write(get(hdr))
                print('头图已下载:', local)
            else:
                print('头图已缓存，跳过下载')
            seen_img[hdr] = local
        data['headerImage'] = f'{SELF_BASE}/images/{seen_img[hdr]}'
    open(os.path.join(DEP_DIR, f'{name}.json'), 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False))

# ---- 2) 本地包：生成简单详情 ----
for deb in sorted(os.listdir(DEBS_DIR)):
    if not deb.endswith('.deb'):
        continue
    pkg = deb_field(os.path.join(DEBS_DIR, deb), 'Package')
    if not pkg or pkg in mirror_names:
        continue
    name = deb_field(os.path.join(DEBS_DIR, deb), 'Name') or pkg
    version = deb_field(os.path.join(DEBS_DIR, deb), 'Version')
    author = deb_field(os.path.join(DEBS_DIR, deb), 'Author') or deb_field(os.path.join(DEBS_DIR, deb), 'Maintainer')
    desc = deb_field(os.path.join(DEBS_DIR, deb), 'Description')
    arch = deb_field(os.path.join(DEBS_DIR, deb), 'Architecture')
    dep = {
        'minVersion': '0.1',
        'tintColor': '#1F91DC',
        'class': 'DepictionTabView',
        'tabs': [{
            'tabname': 'Details',
            'class': 'DepictionStackView',
            'views': [
                {'class': 'DepictionMarkdownView', 'useRawFormat': True,
                 'markdown': desc.replace('\n', '<br>')},
                {'class': 'DepictionTableTextView', 'title': '作者', 'text': author},
                {'class': 'DepictionTableTextView', 'title': '版本', 'text': version},
                {'class': 'DepictionTableTextView', 'title': '架构', 'text': arch},
            ]
        }]
    }
    open(os.path.join(DEP_DIR, f'{pkg}.json'), 'w', encoding='utf-8').write(json.dumps(dep, ensure_ascii=False))
    print('本地详情:', pkg)

print('done')
