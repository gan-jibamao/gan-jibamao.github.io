# 我的 Sileo 源

一个托管在 GitHub Pages 上的 Sileo / Cydia 源。

## 源地址

```
https://你的用户名.github.io/你的仓库名/
```

## 添加 / 更新包的流程

1. 把 `.deb` 文件放进 `debs/` 目录；
2. 在仓库根目录运行：

```bash
sh build_repo.sh
```

3. 提交并推送：

```bash
git add -A && git commit -m "update packages" && git push
```

脚本会自动生成 `Packages`、`Packages.gz`、`Packages.bz2` 和 `Release`（含 MD5/SHA1/SHA256 校验）。

## 目录说明

| 文件 / 目录 | 作用 |
|---|---|
| `debs/` | 存放所有 .deb 包 |
| `Packages*` | 包索引（脚本生成，勿手改） |
| `Release` | 源元数据 + 哈希校验（脚本生成） |
| `CydiaIcon.png` | 源图标 |
| `sileo-featured.json` | Sileo「精选」横幅（可选） |
| `build_repo.sh` | 自动构建脚本 |
