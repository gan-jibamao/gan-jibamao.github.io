#!/usr/bin/env python3
"""生成源状态 status.json：包数、最后同步时间、initnil 变化历史。"""
import re, os, json, hashlib, datetime

repo = os.path.dirname(os.path.abspath(__file__))
os.chdir(repo)

# 1) 当前包数
pkgs = open('Packages', encoding='utf-8').read()
count = len(re.findall(r'^Package:\s*\S+', pkgs, re.M))

# 2) initnil 内容指纹（判断 initnil 是否变化）
mirror_path = os.path.join('mirror', 'initnil.Packages')
mirror = open(mirror_path, encoding='utf-8').read() if os.path.exists(mirror_path) else ''
fp = hashlib.sha256(mirror.encode()).hexdigest()[:16]

# 3) 读旧 status
status_path = 'status.json'
status = json.load(open(status_path, encoding='utf-8')) if os.path.exists(status_path) else {'history': []}

now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

# 4) 仅当 initnil 内容变化时记录历史（保留最近 50 条）
if status.get('last_fingerprint') != fp:
    status.setdefault('history', []).append({'time': now, 'packages': count, 'fingerprint': fp})
    status['history'] = status['history'][-50:]

# 5) 更新元数据
status['last_sync'] = now
status['package_count'] = count
status['last_fingerprint'] = fp

open(status_path, 'w', encoding='utf-8').write(json.dumps(status, ensure_ascii=False, indent=2))
print(f'status updated: {count} 包, {len(status.get("history", []))} 条历史')
