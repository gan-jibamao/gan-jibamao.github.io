# 做爱源（Sileo / Cydia 源）

托管在 GitHub Pages 上的 Sileo/Cydia 源，GPG 签名，自动同步镜像 [jailrepo.initnil.com](https://jailrepo.initnil.com/)。

## 源地址

```
https://gan-jibamao.github.io/
```

在 Sileo → Sources → 右上角 `+` → 粘贴上面的地址。

旧地址 `https://gan-jibamao.github.io/repo/` 由 CI 生成兼容镜像，同样可用（两份内容逐字节一致）。

## 相关页面

| 页面 | 地址 |
|---|---|
| 落地页（添加源入口） | [index.html](https://gan-jibamao.github.io/) |
| 插件列表（可搜索） | [packages.html](https://gan-jibamao.github.io/packages.html) |
| 源状态（同步历史） | [status.html](https://gan-jibamao.github.io/status.html) |

## 自动化

GitHub Actions 每 6 小时自动：

1. 从 `jailrepo.initnil.com` 拉取最新 Packages + 全部 deb（只增不删）
2. 抓取/更新原生详情页（depictions，`manual.txt` 清单中的包跳过）
3. 用 GPG 私钥（GitHub Secret）签名 Release
4. 重建插件列表页 + 状态页
5. 提交推送

## 目录结构

| 路径 | 说明 |
|---|---|
| `debs/` | 所有 .deb 包（镜像 + 本地） |
| `Packages*` / `Release*` | 源索引与签名（自动生成） |
| `depictions/` | 原生详情页 JSON + 头图（`manual.txt` 手工清单，列出的包不自动覆盖） |
| `mirror/initnil.Packages` | initnil 源的包清单快照 |
| `.github/workflows/sync.yml` | 自动同步工作流 |
| `sync_initnil.py` | 拉取 initnil 包（增量） |
| `fetch_depictions.py` | 抓取详情页 |
| `build_packages.py` / `build_repo.sh` | 生成索引 + Release + 签名 |
| `gen_packages_html.py` / `gen_status.py` | 生成网页 |
| `build_legacy_mirror.sh` | 生成 `/repo` 旧地址兼容镜像（复制站点产物到 `repo/`） |
