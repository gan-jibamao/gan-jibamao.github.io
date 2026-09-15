#!/usr/bin/env python3
"""生成源状态 status.json：包数、最后同步、initnil 版本变化日志（增/删/升级明细）。"""
import re, os, json, hashlib, datetime

repo = os.path.dirname(os.path.abspath(__file__))
os.chdir(repo)

def parse_mirror(path):
    """解析 initnil Packages -> {package: {version, name}}"""
    out = {}
    if not os.path.exists(path):
        return out
    for para in open(path, encoding='utf-8').read().split('\n\n'):
        if not para.strip():
            continue
        def f(k):
            m = re.search(rf'^{k}:\s*(.*)$', para, re.M)
            return m.group(1).strip() if m else ''
        pkg = f('Package')
        if pkg:
            out[pkg] = {'version': f('Version'), 'name': f('Name') or pkg}
    return out

# 1) 全源包数
pkgs = open('Packages', encoding='utf-8').read()
count = len(re.findall(r'^Package:\s*\S+', pkgs, re.M))

# 2) initnil 当前清单 + 指纹
current = parse_mirror(os.path.join('mirror', 'initnil.Packages'))
fp = hashlib.sha256(json.dumps(current, sort_keys=True).encode()).hexdigest()[:16]

# 3) 读旧 status
status_path = 'status.json'
status = json.load(open(status_path, encoding='utf-8')) if os.path.exists(status_path) else {'history': []}
previous = status.get('last_packages') or {}

now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

# 4) 变化检测（仅 initnil 内容变化时记录）
if status.get('last_fingerprint') != fp:
    if not previous:
        # 首次建立快照
        changes = {'added': [], 'updated': [], 'removed': []}
        entry = {'time': now, 'packages': count, 'fingerprint': fp, 'changes': changes, 'initial': True}
    else:
        added = [{'package': p, **current[p]} for p in current if p not in previous]
        removed = [{'package': p, **previous[p]} for p in previous if p not in current]
        updated = [{'package': p, 'name': current[p]['name'],
                    'from': previous[p].get('version'), 'to': current[p]['version']}
                   for p in current
                   if p in previous and previous[p].get('version') != current[p]['version']]
        changes = {'added': sorted(added, key=lambda x: x['name']),
                   'updated': sorted(updated, key=lambda x: x['name']),
                   'removed': sorted(removed, key=lambda x: x['name'])}
        entry = {'time': now, 'packages': count, 'fingerprint': fp, 'changes': changes}
    status.setdefault('history', []).append(entry)
    status['history'] = status['history'][-50:]

# 5) 更新元数据
status['last_sync'] = now
status['package_count'] = count
status['last_fingerprint'] = fp
status['last_packages'] = current

open(status_path, 'w', encoding='utf-8').write(json.dumps(status, ensure_ascii=False, indent=2))
n = status['history'][-1]['changes']
print(f'status updated: {count} 包, 本次变化 +{len(n["added"])} ~{len(n["updated"])} -{len(n["removed"])}')
