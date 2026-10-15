#!/bin/bash
# 生成 /repo 旧地址兼容镜像 —— 把站点根产物复制到 repo/ 子目录
# 用途：https://gan-jibamao.github.io/repo/（旧地址）与根地址并行可用
# 说明：镜像内容与根目录逐字节一致；git 中同内容复用同一 blob（存储零增量）；
#       repo/index.html 由根 index.html 改写源地址生成（两地址均可加源）。
set -e
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
MIRROR_DIR="$REPO_ROOT/repo"

case "$REPO_ROOT" in
  ""|"/") echo "❌ 路径异常，终止"; exit 1 ;;
esac

# 1) 全量重建镜像目录（避免陈旧文件残留）
rm -rf "$MIRROR_DIR"
mkdir -p "$MIRROR_DIR"

# 2) 索引 + 签名 + 图标 + 状态
for f in Packages Packages.gz Packages.bz2 Release Release.gpg CydiaIcon.png status.json; do
  cp -f "$REPO_ROOT/$f" "$MIRROR_DIR/$f"
done

# 3) 页面（内容与根一致；下载链接为绝对地址，照常可用）
for f in packages.html status.html; do
  cp -f "$REPO_ROOT/$f" "$MIRROR_DIR/$f"
done

# 4) 目录：depictions（详情页+头图）、debs（Packages 中 Filename 为相对路径，需在本地址下可下载）
cp -R "$REPO_ROOT/depictions" "$MIRROR_DIR/depictions"
cp -R "$REPO_ROOT/debs" "$MIRROR_DIR/debs"

# 5) 落地页：由根 index.html 生成，源地址替换为 /repo 版本
sed -e 's#https://gan-jibamao.github.io/#https://gan-jibamao.github.io/repo/#g' \
    -e 's#gan-jibamao.github.io%2F%2F#gan-jibamao.github.io%2Frepo%2F#g' \
    "$REPO_ROOT/index.html" > "$MIRROR_DIR/index.html"

echo "✅ /repo 镜像完成"
echo "   Packages: $(wc -c < "$MIRROR_DIR/Packages") B | debs: $(ls "$MIRROR_DIR/debs" | wc -l) 个 | depictions: $(ls "$MIRROR_DIR/depictions" | wc -l) 项"
echo "   落地页抽查: $(grep -o 'sileo://source/https://[^"]*' "$MIRROR_DIR/index.html" | head -1)"
