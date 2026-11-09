# 做爱源（Sileo / Cydia 源）

托管在 GitHub Pages 上的 Sileo/Cydia 源，GPG 签名，自动同步镜像 [jailrepo.initnil.com](https://jailrepo.initnil.com/)。

## 源地址

```
https://gan-jibamao.github.io/
```

在 Sileo → Sources → 右上角 `+` → 粘贴上面的地址。

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
| `theme.css` | **三页共用的主题变量**（亮色默认 + 跟随系统深色） |
| `depictions/` | 原生详情页 JSON + 头图（`manual.txt` 手工清单，列出的包不自动覆盖） |
| `mirror/initnil.Packages` | initnil 源的包清单快照 |
| `.github/workflows/sync.yml` | 自动同步工作流 |
| `sync_initnil.py` | 拉取 initnil 包（增量） |
| `fetch_depictions.py` | 抓取详情页 |
| `build_packages.py` / `build_repo.sh` | 生成索引 + Release + 签名 |
| `gen_packages_html.py` / `gen_status.py` | 生成网页 |

## 网页主题

三个页面共用 `theme.css`，**不要在页面里写死颜色**：

```css
:root{ /* 52 个亮色变量 */ }
@media (prefers-color-scheme: dark){ :root{ /* 51 个深色变量 */ } }
```

改配色只改 `theme.css` 一处，三页同步生效。

**改完必须把版本戳加一**（三个文件 + 生成器模板）：

```bash
sed -i 's/theme.css?v=2/theme.css?v=3/' index.html status.html gen_packages_html.py
python3 gen_packages_html.py
```

否则 GitHub Pages 的 CDN 缓存 600 秒，用户看到的还是旧样式。

### 页面结构

| 页面 | 是否手写 | 说明 |
|---|---|---|
| `index.html` | 手写 | 落地页。内联 `dedupe()` 按包 ID 归并，55+ stanza → 35 项 |
| `status.html` | 手写 | 同步历史 |
| `packages.html` | **生成** | 由 `gen_packages_html.py` 产出，每 6 小时被 sync.yml 重写，**改产物无效，必须改生成器** |

### 关键设计决策

**按包 ID 去重**：`Packages` 里同一包的多版本 × 多架构会平铺成多条（如
`com.jibamao.gaodeclean` 曾占 49 条）。网页两个列表都做了归并，只显示最新版，
架构合并显示，附「N 个版本」徽记。版本比较用 dpkg 语义（`ver_key()`），
已与 `dpkg --compare-versions` 交叉验证。

> 注意：去重只作用于网页展示。`Packages` 索引本身由下面的版本裁剪控制，
> 客户端（Sileo）里看到的是裁剪后的版本列表。

### 索引版本裁剪

`build_packages.py` 末尾有 `KEEP_VERSIONS = 3`，构建时每个包**只保留最新 3 个版本**：

- 同一版本的多个架构（`iphoneos-arm64` / `iphoneos-arm64e`）**全部保留**，架构不是版本
- 版本比较用 dpkg 语义（`_ver_key()`），已与 `dpkg --compare-versions` 交叉验证
- 被裁掉的版本 **deb 文件仍在 `debs/`**，可通过
  `https://gan-jibamao.github.io/debs/<文件名>` 直接下载回滚，只是不出现在源里
- `initnil` 镜像块是一整个多 stanza 字符串，裁剪前必须先 `split('\n\n')` 拆开，
  否则整块会被当成单个元素原样通过

实测：95 条 → 52 条（`com.jibamao.gaodeclean` 49 条 → 6 条），索引 76KB → 36KB。

想保留更多回滚余地就调大 `KEEP_VERSIONS`，改完推上去等 CI 重建即可。


