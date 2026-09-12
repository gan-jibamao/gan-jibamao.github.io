#!/bin/bash
# Sileo/Cydia 源自动构建脚本 —— 放在仓库根目录运行（./build_repo.sh）
# 前置：apk add dpkg-dev（或本机装有 dpkg-scanpackages）
set -e
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

# 1) 生成 Packages 索引（合并镜像包 + 本地包，见 build_packages.py）
python3 "$REPO_ROOT/build_packages.py"

# 2) 压缩索引（Sileo 优先读 .bz2 / .gz）
gzip  -9 -c "$REPO_ROOT/Packages" > "$REPO_ROOT/Packages.gz"
bzip2 -9 -c "$REPO_ROOT/Packages" > "$REPO_ROOT/Packages.bz2"

# 3) 生成 Release（哈希校验清单，Sileo 用 SHA256 核对）
{
  echo "Origin: 做爱"
  echo "Label: 做爱"
  echo "Suite: stable"
  echo "Version: 1.0"
  echo "Codename: ios"
  echo "Architectures: iphoneos-arm iphoneos-arm64 iphoneos-arm64e"
  echo "Components: main"
  echo "Description: My Sileo repository"
  echo
  for algo in MD5Sum SHA1 SHA256; do
    case "$algo" in
      MD5Sum)    cmd=md5sum    ;;
      SHA1)      cmd=sha1sum   ;;
      SHA256)    cmd=sha256sum ;;
    esac
    echo "$algo:"
    for f in Packages Packages.gz Packages.bz2; do
      h=$("$cmd" "$REPO_ROOT/$f" | awk '{print $1}')
      s=$(wc -c < "$REPO_ROOT/$f")
      printf ' %s %s %s\n' "$h" "$s" "$f"
    done
  done
} > "$REPO_ROOT/Release"

# 4) 签名 Release（需要本机已生成 GPG 密钥；没有则跳过并提示）
if gpg --list-secret-keys 2>/dev/null | grep -q .; then
  gpg --batch --yes --armor --detach-sign -o "$REPO_ROOT/Release.gpg" "$REPO_ROOT/Release"
  echo "✅ 已签名 Release -> Release.gpg"
else
  echo "⚠️  未找到 GPG 密钥，已跳过签名（源将显示为 unsigned）"
fi

echo "✅ 完成：Packages / Packages.gz / Packages.bz2 / Release 已生成。"
ls -l "$REPO_ROOT"/Packages* "$REPO_ROOT/Release" "$REPO_ROOT"/Release.gpg 2>/dev/null
