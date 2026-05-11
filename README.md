<p align="center">
  <a href="#简体中文">简体中文</a> &nbsp;|&nbsp;
  <a href="#繁體中文">繁體中文</a> &nbsp;|&nbsp;
  <a href="#english">English</a>
</p>

---

<h1 id="简体中文" align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="version" />
  &nbsp;
  <img src="https://img.shields.io/badge/license-MIT-green" alt="license" />
  &nbsp;
  <img src="https://img.shields.io/badge/python-3.9+-yellow" alt="python" />
  &nbsp;
  <img src="https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20Windows-lightgrey" alt="platform" />
</h1>

<p align="center">
  <strong>EnvForge</strong> — 轻量级开发环境智能配置与同步引擎<br/>
  <em>零依赖 · 跨平台 · 一键配置 · 环境可复现</em>
</p>

<p align="center">
  <a href="https://github.com/gitstq/EnvForge">GitHub 仓库</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/gitstq/EnvForge/issues">问题反馈</a>
</p>

---

## 目录

- [项目介绍](#项目介绍)
- [核心特性](#核心特性)
- [快速开始](#快速开始)
- [详细使用指南](#详细使用指南)
  - [环境检测](#环境检测)
  - [配置生成](#配置生成)
  - [环境快照](#环境快照)
  - [健康检查](#健康检查)
  - [差异对比](#差异对比)
  - [系统信息](#系统信息)
- [设计思路与迭代规划](#设计思路与迭代规划)
- [打包与部署](#打包与部署)
- [贡献指南](#贡献指南)
- [开源协议](#开源协议)

---

## 项目介绍

**EnvForge** 是一款面向开发者的轻量级环境管理工具。它能自动扫描项目目录、识别技术栈，并据此生成标准化的环境配置文件。无论是团队协作中的环境一致性维护，还是个人多设备间的开发环境迁移，EnvForge 都能帮你轻松搞定。

**为什么选择 EnvForge？**

- **零核心依赖** — 纯 Python 标准库实现，不引入任何第三方包，安装即用
- **智能检测** — 支持 13+ 种主流编程语言的技术栈自动识别
- **一键配置** — 从检测到生成配置文件，一条命令搞定
- **环境可复现** — 快照机制让开发环境可以随时导出、还原
- **跨平台** — Linux、macOS、Windows 全平台支持

---

## 核心特性

### 🔍 环境检测引擎

自动扫描项目目录，精准识别项目所使用的技术栈。目前已支持 **13+ 种编程语言**：

Python、JavaScript、TypeScript、Go、Rust、Java、Ruby、PHP、Swift、Kotlin、Dart、Shell 等。

```
$ envforge detect
[EnvForge] 正在扫描项目目录...
[检测] Python 3.11.5 (pyproject.toml, requirements.txt)
[检测] Node.js 20.x (package.json)
[检测] Docker (Dockerfile)
[结果] 检测到 3 个技术栈组件
```

### 🛠️ 配置生成器

根据检测结果，自动生成标准化的项目配置文件：

| 文件 | 说明 |
|------|------|
| `.env.example` | 环境变量模板 |
| `Dockerfile` | 容器化构建文件 |
| `docker-compose.yml` | 多服务编排文件 |
| `.tool-versions` | 工具版本管理（asdf 兼容） |
| `Makefile` | 常用命令快捷方式 |
| `.gitignore` | Git 忽略规则 |
| `devcontainer.json` | VS Code 开发容器配置 |

### 📸 环境快照

将当前开发环境的完整配置导出为可复现的快照文件，支持历史版本管理。快照包含系统信息、已安装工具链、项目依赖等全部关键数据。

### 🔄 环境同步

将环境配置同步到其他机器，在新设备上一键还原完整的开发环境，告别"在我机器上能跑"的尴尬。

### 🏥 健康检查

全面检测环境配置状态：

- 配置文件一致性检查
- 依赖版本偏差检测
- 安全漏洞扫描（硬编码密钥、敏感信息泄露等）
- 综合健康评分（0-100 分）

### 📊 差异对比

对比两台机器的环境差异，自动生成详细的迁移指南，让环境迁移有据可依。

---

## 快速开始

### 环境要求

- Python 3.9 或更高版本
- pip 包管理器

### 安装

**方式一：从 GitHub 直接安装**

```bash
pip install git+https://github.com/gitstq/EnvForge.git
```

**方式二：克隆后本地安装**

```bash
git clone https://github.com/gitstq/EnvForge.git
cd EnvForge
pip install -e .
```

### 三分钟上手

```bash
# 1. 检测当前项目的技术栈
envforge detect

# 2. 自动生成配置文件
envforge generate

# 3. 查看环境健康状态
envforge health

# 4. 创建环境快照
envforge snapshot create

# 5. 查看快照列表
envforge snapshot list
```

---

## 详细使用指南

### 环境检测

扫描指定目录，自动识别项目使用的技术栈。

```bash
# 检测当前目录
envforge detect

# 检测指定目录
envforge detect -p /path/to/project

# 输出 JSON 格式（便于脚本集成）
envforge detect --json

# 静默模式（仅输出关键信息）
envforge detect --quiet
```

**参数说明：**

| 参数 | 缩写 | 说明 |
|------|------|------|
| `--path` | `-p` | 指定项目目录路径 |
| `--json` | | 以 JSON 格式输出结果 |
| `--quiet` | | 静默模式，减少输出信息 |

### 配置生成

根据检测结果生成各类配置文件。

```bash
# 生成所有配置文件
envforge generate

# 生成指定类型的配置文件
envforge generate --dockerfile
envforge generate --makefile
envforge generate --gitignore
envforge generate --env-example

# 预览模式（不实际写入文件）
envforge generate --dry-run

# 强制覆盖已有文件
envforge generate --force
```

**参数说明：**

| 参数 | 缩写 | 说明 |
|------|------|------|
| `--path` | `-p` | 指定项目目录路径 |
| `--dockerfile` | | 仅生成 Dockerfile |
| `--makefile` | | 仅生成 Makefile |
| `--gitignore` | | 仅生成 .gitignore |
| `--env-example` | | 仅生成 .env.example |
| `--dry-run` | | 预览模式，不写入文件 |
| `--force` | | 强制覆盖已有文件 |

### 环境快照

管理开发环境快照，支持创建、查看、导入等操作。

```bash
# 创建新快照
envforge snapshot create

# 列出所有快照
envforge snapshot list

# 查看快照详情
envforge snapshot show <snapshot_name>

# 从快照文件导入
envforge snapshot import <snapshot_file>
```

### 健康检查

对项目环境进行全面健康评估。

```bash
# 执行健康检查
envforge health

# 检查指定目录
envforge health -p /path/to/project

# JSON 格式输出
envforge health --json

# 按严重级别过滤（critical / warning / info）
envforge health -s critical
```

**参数说明：**

| 参数 | 缩写 | 说明 |
|------|------|------|
| `--path` | `-p` | 指定项目目录路径 |
| `--json` | | 以 JSON 格式输出结果 |
| `--severity` | `-s` | 按严重级别过滤问题 |

### 差异对比

对比当前环境与快照之间的差异。

```bash
# 基础对比
envforge diff snapshot.envforge

# 对比指定目录
envforge diff snapshot.envforge -p /path/to/project

# 生成迁移指南
envforge diff snapshot.envforge --migration

# JSON 格式输出
envforge diff snapshot.envforge --json
```

**参数说明：**

| 参数 | 缩写 | 说明 |
|------|------|------|
| `SNAPSHOT_FILE` | | 快照文件路径（必填） |
| `--path` | `-p` | 指定项目目录路径 |
| `--migration` | | 生成迁移指南 |
| `--json` | | 以 JSON 格式输出结果 |

### 系统信息

查看当前系统与工具链信息。

```bash
# 查看系统信息
envforge info

# JSON 格式输出
envforge info --json
```

---

## 设计思路与迭代规划

### 设计理念

EnvForge 的核心设计理念围绕三个关键词展开：

1. **轻量** — 零核心依赖，纯标准库实现，安装包体积小，启动速度快
2. **智能** — 基于文件特征的技术栈检测，而非依赖运行时环境，即使未安装对应语言也能识别
3. **可复现** — 快照机制确保开发环境可以被完整记录和还原

### 架构设计

```
envforge/
├── cli/            # 命令行接口层
├── detector/       # 环境检测引擎
├── generator/      # 配置文件生成器
├── snapshot/       # 快照管理模块
├── health/         # 健康检查模块
├── sync/           # 环境同步模块
└── utils/          # 通用工具函数
```

### 迭代规划

- **v1.0** — 核心功能实现：环境检测、配置生成、快照管理、健康检查、差异对比
- **v1.1** — 增强检测能力：支持更多语言框架、深度依赖分析
- **v1.2** — 云端同步：支持快照的远程存储与团队共享
- **v2.0** — 插件系统：支持社区扩展自定义检测规则和生成模板

---

## 打包与部署

### 使用 pip 打包分发

```bash
# 安装构建工具
pip install build

# 构建 sdist 和 wheel
python -m build

# 生成的包在 dist/ 目录下
ls dist/
# envforge-1.0.0.tar.gz
# envforge-1.0.0-py3-none-any.whl
```

### 使用 pipx 安装（推荐隔离安装方式）

```bash
pipx install git+https://github.com/gitstq/EnvForge.git
```

### Docker 中使用

```bash
# 在 Docker 容器中运行
docker run --rm -v $(pwd):/app python:3.11-slim bash -c \
  "pip install git+https://github.com/gitstq/EnvForge.git && envforge detect -p /app"
```

### CI/CD 集成

```yaml
# GitHub Actions 示例
- name: Setup EnvForge
  run: pip install git+https://github.com/gitstq/EnvForge.git

- name: Detect Environment
  run: envforge detect --json > env-report.json

- name: Health Check
  run: envforge health -s critical
```

---

## 贡献指南

我们欢迎任何形式的贡献！无论是提交 Bug 报告、改进文档，还是提交代码 PR。

### 参与流程

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交改动：`git commit -m "feat: add your feature"`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 **Pull Request**

### 代码规范

- 遵循 PEP 8 编码规范
- 使用类型注解（Type Hints）
- 编写单元测试覆盖新增功能
- 保持零核心依赖原则

### 提交规范

提交信息请遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
feat: 新增功能
fix: 修复缺陷
docs: 文档更新
refactor: 代码重构
test: 测试相关
chore: 构建/工具链相关
```

---

## 开源协议

本项目基于 [MIT License](https://opensource.org/licenses/MIT) 开源。

```
MIT License

Copyright (c) 2024 gitstq

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  <strong>EnvForge</strong> 由 <a href="https://github.com/gitstq">gitstq</a> 倾力打造
</p>

---
---
---

<h1 id="繁體中文" align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="version" />
  &nbsp;
  <img src="https://img.shields.io/badge/license-MIT-green" alt="license" />
  &nbsp;
  <img src="https://img.shields.io/badge/python-3.9+-yellow" alt="python" />
  &nbsp;
  <img src="https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20Windows-lightgrey" alt="platform" />
</h1>

<p align="center">
  <strong>EnvForge</strong> — 輕量級開發環境智慧配置與同步引擎<br/>
  <em>零依賴 · 跨平台 · 一鍵配置 · 環境可重現</em>
</p>

<p align="center">
  <a href="https://github.com/gitstq/EnvForge">GitHub 儲存庫</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/gitstq/EnvForge/issues">問題回報</a>
</p>

---

## 目錄

- [專案介紹](#專案介紹)
- [核心特性](#核心特性)
- [快速開始](#快速開始)
- [詳細使用指南](#詳細使用指南)
  - [環境偵測](#環境偵測)
  - [配置生成](#配置生成)
  - [環境快照](#環境快照)
  - [健康檢查](#健康檢查)
  - [差異對比](#差異對比)
  - [系統資訊](#系統資訊)
- [設計思路與迭代規劃](#設計思路與迭代規劃)
- [打包與部署](#打包與部署)
- [貢獻指南](#貢獻指南)
- [開源授權](#開源授權)

---

## 專案介紹

**EnvForge** 是一款面向開發者的輕量級環境管理工具。它能自動掃描專案目錄、識別技術棧，並據此生成標準化的環境配置檔案。無論是團隊協作中的環境一致性維護，還是個人多裝置間的開發環境遷移，EnvForge 都能幫你輕鬆搞定。

**為什麼選擇 EnvForge？**

- **零核心依賴** — 純 Python 標準函式庫實作，不引入任何第三方套件，安裝即用
- **智慧偵測** — 支援 13+ 種主流程式語言的技術棧自動識別
- **一鍵配置** — 從偵測到生成配置檔案，一條指令搞定
- **環境可重現** — 快照機制讓開發環境可以隨時匯出、還原
- **跨平台** — Linux、macOS、Windows 全平台支援

---

## 核心特性

### 🔍 環境偵測引擎

自動掃描專案目錄，精準識別專案所使用的技術棧。目前已支援 **13+ 種程式語言**：

Python、JavaScript、TypeScript、Go、Rust、Java、Ruby、PHP、Swift、Kotlin、Dart、Shell 等。

```
$ envforge detect
[EnvForge] 正在掃描專案目錄...
[偵測] Python 3.11.5 (pyproject.toml, requirements.txt)
[偵測] Node.js 20.x (package.json)
[偵測] Docker (Dockerfile)
[結果] 偵測到 3 個技術棧元件
```

### 🛠️ 配置生成器

根據偵測結果，自動生成標準化的專案配置檔案：

| 檔案 | 說明 |
|------|------|
| `.env.example` | 環境變數範本 |
| `Dockerfile` | 容器化建構檔案 |
| `docker-compose.yml` | 多服務編排檔案 |
| `.tool-versions` | 工具版本管理（asdf 相容） |
| `Makefile` | 常用指令快捷方式 |
| `.gitignore` | Git 忽略規則 |
| `devcontainer.json` | VS Code 開發容器配置 |

### 📸 環境快照

將當前開發環境的完整配置匯出為可重現的快照檔案，支援歷史版本管理。快照包含系統資訊、已安裝工具鏈、專案依賴等全部關鍵資料。

### 🔄 環境同步

將環境配置同步到其他機器，在新裝置上一鍵還原完整的開發環境，告別「在我機器上能跑」的尷尬。

### 🏥 健康檢查

全面偵測環境配置狀態：

- 配置檔案一致性檢查
- 依賴版本偏差偵測
- 安全漏洞掃描（硬編碼金鑰、敏感資訊洩漏等）
- 綜合健康評分（0-100 分）

### 📊 差異對比

對比兩台機器的環境差異，自動生成詳細的遷移指南，讓環境遷移有據可依。

---

## 快速開始

### 環境需求

- Python 3.9 或更高版本
- pip 套件管理器

### 安裝

**方式一：從 GitHub 直接安裝**

```bash
pip install git+https://github.com/gitstq/EnvForge.git
```

**方式二：複製後本地安裝**

```bash
git clone https://github.com/gitstq/EnvForge.git
cd EnvForge
pip install -e .
```

### 三分鐘上手

```bash
# 1. 偵測當前專案的技術棧
envforge detect

# 2. 自動生成配置檔案
envforge generate

# 3. 查看環境健康狀態
envforge health

# 4. 建立環境快照
envforge snapshot create

# 5. 查看快照列表
envforge snapshot list
```

---

## 詳細使用指南

### 環境偵測

掃描指定目錄，自動識別專案使用的技術棧。

```bash
# 偵測當前目錄
envforge detect

# 偵測指定目錄
envforge detect -p /path/to/project

# 輸出 JSON 格式（便於腳本整合）
envforge detect --json

# 靜默模式（僅輸出關鍵資訊）
envforge detect --quiet
```

**參數說明：**

| 參數 | 縮寫 | 說明 |
|------|------|------|
| `--path` | `-p` | 指定專案目錄路徑 |
| `--json` | | 以 JSON 格式輸出結果 |
| `--quiet` | | 靜默模式，減少輸出資訊 |

### 配置生成

根據偵測結果生成各類配置檔案。

```bash
# 生成所有配置檔案
envforge generate

# 生成指定類型的配置檔案
envforge generate --dockerfile
envforge generate --makefile
envforge generate --gitignore
envforge generate --env-example

# 預覽模式（不實際寫入檔案）
envforge generate --dry-run

# 強制覆蓋已有檔案
envforge generate --force
```

**參數說明：**

| 參數 | 縮寫 | 說明 |
|------|------|------|
| `--path` | `-p` | 指定專案目錄路徑 |
| `--dockerfile` | | 僅生成 Dockerfile |
| `--makefile` | | 僅生成 Makefile |
| `--gitignore` | | 僅生成 .gitignore |
| `--env-example` | | 僅生成 .env.example |
| `--dry-run` | | 預覽模式，不寫入檔案 |
| `--force` | | 強制覆蓋已有檔案 |

### 環境快照

管理開發環境快照，支援建立、查看、匯入等操作。

```bash
# 建立新快照
envforge snapshot create

# 列出所有快照
envforge snapshot list

# 查看快照詳情
envforge snapshot show <snapshot_name>

# 從快照檔案匯入
envforge snapshot import <snapshot_file>
```

### 健康檢查

對專案環境進行全面健康評估。

```bash
# 執行健康檢查
envforge health

# 檢查指定目錄
envforge health -p /path/to/project

# JSON 格式輸出
envforge health --json

# 按嚴重級別過濾（critical / warning / info）
envforge health -s critical
```

**參數說明：**

| 參數 | 縮寫 | 說明 |
|------|------|------|
| `--path` | `-p` | 指定專案目錄路徑 |
| `--json` | | 以 JSON 格式輸出結果 |
| `--severity` | `-s` | 按嚴重級別過濾問題 |

### 差異對比

對比當前環境與快照之間的差異。

```bash
# 基礎對比
envforge diff snapshot.envforge

# 對比指定目錄
envforge diff snapshot.envforge -p /path/to/project

# 生成遷移指南
envforge diff snapshot.envforge --migration

# JSON 格式輸出
envforge diff snapshot.envforge --json
```

**參數說明：**

| 參數 | 縮寫 | 說明 |
|------|------|------|
| `SNAPSHOT_FILE` | | 快照檔案路徑（必填） |
| `--path` | `-p` | 指定專案目錄路徑 |
| `--migration` | | 生成遷移指南 |
| `--json` | | 以 JSON 格式輸出結果 |

### 系統資訊

查看當前系統與工具鏈資訊。

```bash
# 查看系統資訊
envforge info

# JSON 格式輸出
envforge info --json
```

---

## 設計思路與迭代規劃

### 設計理念

EnvForge 的核心設計理念圍繞三個關鍵詞展開：

1. **輕量** — 零核心依賴，純標準函式庫實作，安裝包體積小，啟動速度快
2. **智慧** — 基於檔案特徵的技術棧偵測，而非依賴執行期環境，即使未安裝對應語言也能識別
3. **可重現** — 快照機制確保開發環境可以被完整記錄和還原

### 架構設計

```
envforge/
├── cli/            # 命令列介面層
├── detector/       # 環境偵測引擎
├── generator/      # 配置檔案生成器
├── snapshot/       # 快照管理模組
├── health/         # 健康檢查模組
├── sync/           # 環境同步模組
└── utils/          # 通用工具函式
```

### 迭代規劃

- **v1.0** — 核心功能實作：環境偵測、配置生成、快照管理、健康檢查、差異對比
- **v1.1** — 增強偵測能力：支援更多語言框架、深度依賴分析
- **v1.2** — 雲端同步：支援快照的遠端儲存與團隊共享
- **v2.0** — 外掛系統：支援社群擴充自訂偵測規則和生成範本

---

## 打包與部署

### 使用 pip 打包分發

```bash
# 安裝建構工具
pip install build

# 建構 sdist 和 wheel
python -m build

# 生成的套件在 dist/ 目錄下
ls dist/
# envforge-1.0.0.tar.gz
# envforge-1.0.0-py3-none-any.whl
```

### 使用 pipx 安裝（推薦隔離安裝方式）

```bash
pipx install git+https://github.com/gitstq/EnvForge.git
```

### Docker 中使用

```bash
# 在 Docker 容器中執行
docker run --rm -v $(pwd):/app python:3.11-slim bash -c \
  "pip install git+https://github.com/gitstq/EnvForge.git && envforge detect -p /app"
```

### CI/CD 整合

```yaml
# GitHub Actions 範例
- name: Setup EnvForge
  run: pip install git+https://github.com/gitstq/EnvForge.git

- name: Detect Environment
  run: envforge detect --json > env-report.json

- name: Health Check
  run: envforge health -s critical
```

---

## 貢獻指南

我們歡迎任何形式的貢獻！無論是提交 Bug 回報、改進文件，還是提交程式碼 PR。

### 參與流程

1. **Fork** 本儲存庫
2. 建立特性分支：`git checkout -b feature/your-feature`
3. 提交變更：`git commit -m "feat: add your feature"`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 **Pull Request**

### 程式碼規範

- 遵循 PEP 8 編碼規範
- 使用型別註解（Type Hints）
- 撰寫單元測試覆蓋新增功能
- 保持零核心依賴原則

### 提交規範

提交資訊請遵循 [Conventional Commits](https://www.conventionalcommits.org/) 規範：

```
feat: 新增功能
fix: 修復缺陷
docs: 文件更新
refactor: 程式碼重構
test: 測試相關
chore: 建構/工具鏈相關
```

---

## 開源授權

本專案基於 [MIT License](https://opensource.org/licenses/MIT) 開源。

```
MIT License

Copyright (c) 2024 gitstq

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  <strong>EnvForge</strong> 由 <a href="https://github.com/gitstq">gitstq</a> 傾力打造
</p>

---
---
---

<h1 id="english" align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="version" />
  &nbsp;
  <img src="https://img.shields.io/badge/license-MIT-green" alt="license" />
  &nbsp;
  <img src="https://img.shields.io/badge/python-3.9+-yellow" alt="python" />
  &nbsp;
  <img src="https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20Windows-lightgrey" alt="platform" />
</h1>

<p align="center">
  <strong>EnvForge</strong> &mdash; Lightweight Development Environment Intelligent Configuration &amp; Sync Engine<br/>
  <em>Zero Dependencies &middot; Cross-Platform &middot; One-Command Setup &middot; Reproducible Environments</em>
</p>

<p align="center">
  <a href="https://github.com/gitstq/EnvForge">GitHub Repository</a>
  &nbsp;&middot;&nbsp;
  <a href="https://github.com/gitstq/EnvForge/issues">Issue Tracker</a>
</p>

---

## Table of Contents

- [Introduction](#introduction)
- [Core Features](#core-features)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
  - [Environment Detection](#environment-detection)
  - [Configuration Generation](#configuration-generation)
  - [Environment Snapshots](#environment-snapshots)
  - [Health Check](#health-check)
  - [Environment Diff](#environment-diff)
  - [System Info](#system-info)
- [Design Philosophy &amp; Roadmap](#design-philosophy--roadmap)
- [Packaging &amp; Deployment](#packaging--deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Introduction

**EnvForge** is a lightweight environment management tool built for developers. It automatically scans project directories, identifies the tech stack in use, and generates standardized environment configuration files. Whether you are maintaining environment consistency across a team or migrating your development setup between devices, EnvForge has you covered.

**Why EnvForge?**

- **Zero core dependencies** &mdash; Built entirely with the Python standard library. No third-party packages required. Install and go.
- **Intelligent detection** &mdash; Automatically identifies tech stacks for 13+ programming languages.
- **One-command setup** &mdash; From detection to config generation, everything happens with a single command.
- **Reproducible environments** &mdash; The snapshot mechanism lets you export and restore your full development environment at any time.
- **Cross-platform** &mdash; Full support for Linux, macOS, and Windows.

---

## Core Features

### 🔍 Environment Detection Engine

Automatically scans project directories and accurately identifies the tech stack in use. Currently supports **13+ programming languages**:

Python, JavaScript, TypeScript, Go, Rust, Java, Ruby, PHP, Swift, Kotlin, Dart, Shell, and more.

```
$ envforge detect
[EnvForge] Scanning project directory...
[Detected] Python 3.11.5 (pyproject.toml, requirements.txt)
[Detected] Node.js 20.x (package.json)
[Detected] Docker (Dockerfile)
[Result] 3 tech stack components detected
```

### 🛠️ Configuration Generator

Generates standardized project configuration files based on detection results:

| File | Description |
|------|-------------|
| `.env.example` | Environment variable template |
| `Dockerfile` | Container build file |
| `docker-compose.yml` | Multi-service orchestration file |
| `.tool-versions` | Tool version management (asdf-compatible) |
| `Makefile` | Common command shortcuts |
| `.gitignore` | Git ignore rules |
| `devcontainer.json` | VS Code dev container configuration |

### 📸 Environment Snapshots

Export the complete configuration of your current development environment as a reproducible snapshot file, with full version history support. Snapshots include system information, installed toolchains, project dependencies, and all other critical data.

### 🔄 Environment Sync

Synchronize environment configurations across machines. Restore a complete development environment on a new device with a single command &mdash; no more "works on my machine" excuses.

### 🏥 Health Check

Comprehensive environment configuration assessment:

- Configuration file consistency checks
- Dependency version drift detection
- Security vulnerability scanning (hardcoded secrets, sensitive data exposure, etc.)
- Overall health score (0&ndash;100)

### 📊 Environment Diff

Compare environments between two machines and automatically generate a detailed migration guide, making environment migration straightforward and well-documented.

---

## Quick Start

### Prerequisites

- Python 3.9 or later
- pip package manager

### Installation

**Option 1: Install directly from GitHub**

```bash
pip install git+https://github.com/gitstq/EnvForge.git
```

**Option 2: Clone and install locally**

```bash
git clone https://github.com/gitstq/EnvForge.git
cd EnvForge
pip install -e .
```

### Three-Minute Tour

```bash
# 1. Detect the tech stack of your current project
envforge detect

# 2. Auto-generate configuration files
envforge generate

# 3. Check environment health
envforge health

# 4. Create an environment snapshot
envforge snapshot create

# 5. List all snapshots
envforge snapshot list
```

---

## Usage Guide

### Environment Detection

Scan a directory to automatically identify the project's tech stack.

```bash
# Detect the current directory
envforge detect

# Detect a specific directory
envforge detect -p /path/to/project

# Output in JSON format (for script integration)
envforge detect --json

# Quiet mode (key information only)
envforge detect --quiet
```

**Options:**

| Flag | Short | Description |
|------|-------|-------------|
| `--path` | `-p` | Specify the project directory path |
| `--json` | | Output results in JSON format |
| `--quiet` | | Quiet mode, reduce output |

### Configuration Generation

Generate various configuration files based on detection results.

```bash
# Generate all configuration files
envforge generate

# Generate specific configuration files
envforge generate --dockerfile
envforge generate --makefile
envforge generate --gitignore
envforge generate --env-example

# Dry-run mode (preview without writing files)
envforge generate --dry-run

# Force overwrite existing files
envforge generate --force
```

**Options:**

| Flag | Short | Description |
|------|-------|-------------|
| `--path` | `-p` | Specify the project directory path |
| `--dockerfile` | | Generate Dockerfile only |
| `--makefile` | | Generate Makefile only |
| `--gitignore` | | Generate .gitignore only |
| `--env-example` | | Generate .env.example only |
| `--dry-run` | | Preview mode, do not write files |
| `--force` | | Force overwrite existing files |

### Environment Snapshots

Manage development environment snapshots with create, view, and import operations.

```bash
# Create a new snapshot
envforge snapshot create

# List all snapshots
envforge snapshot list

# View snapshot details
envforge snapshot show <snapshot_name>

# Import from a snapshot file
envforge snapshot import <snapshot_file>
```

### Health Check

Perform a comprehensive health assessment of your project environment.

```bash
# Run health check
envforge health

# Check a specific directory
envforge health -p /path/to/project

# Output in JSON format
envforge health --json

# Filter by severity level (critical / warning / info)
envforge health -s critical
```

**Options:**

| Flag | Short | Description |
|------|-------|-------------|
| `--path` | `-p` | Specify the project directory path |
| `--json` | | Output results in JSON format |
| `--severity` | `-s` | Filter issues by severity level |

### Environment Diff

Compare differences between the current environment and a snapshot.

```bash
# Basic comparison
envforge diff snapshot.envforge

# Compare a specific directory
envforge diff snapshot.envforge -p /path/to/project

# Generate a migration guide
envforge diff snapshot.envforge --migration

# Output in JSON format
envforge diff snapshot.envforge --json
```

**Options:**

| Flag | Short | Description |
|------|-------|-------------|
| `SNAPSHOT_FILE` | | Path to the snapshot file (required) |
| `--path` | `-p` | Specify the project directory path |
| `--migration` | | Generate a migration guide |
| `--json` | | Output results in JSON format |

### System Info

View current system and toolchain information.

```bash
# View system information
envforge info

# Output in JSON format
envforge info --json
```

---

## Design Philosophy & Roadmap

### Design Philosophy

EnvForge is built around three core principles:

1. **Lightweight** &mdash; Zero core dependencies, pure standard library implementation, small install footprint, and fast startup.
2. **Intelligent** &mdash; File-signature-based tech stack detection that works even without the corresponding language runtime installed.
3. **Reproducible** &mdash; A snapshot mechanism that ensures development environments can be fully recorded and restored.

### Architecture

```
envforge/
├── cli/            # Command-line interface layer
├── detector/       # Environment detection engine
├── generator/      # Configuration file generators
├── snapshot/       # Snapshot management module
├── health/         # Health check module
├── sync/           # Environment sync module
└── utils/          # Common utility functions
```

### Roadmap

- **v1.0** &mdash; Core features: environment detection, config generation, snapshot management, health check, environment diff
- **v1.1** &mdash; Enhanced detection: support for more languages and frameworks, deep dependency analysis
- **v1.2** &mdash; Cloud sync: remote snapshot storage and team sharing
- **v2.0** &mdash; Plugin system: community-driven custom detection rules and generation templates

---

## Packaging & Deployment

### Distribute with pip

```bash
# Install build tools
pip install build

# Build sdist and wheel
python -m build

# Generated packages are in the dist/ directory
ls dist/
# envforge-1.0.0.tar.gz
# envforge-1.0.0-py3-none-any.whl
```

### Install with pipx (recommended for isolated installs)

```bash
pipx install git+https://github.com/gitstq/EnvForge.git
```

### Using with Docker

```bash
# Run inside a Docker container
docker run --rm -v $(pwd):/app python:3.11-slim bash -c \
  "pip install git+https://github.com/gitstq/EnvForge.git && envforge detect -p /app"
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Setup EnvForge
  run: pip install git+https://github.com/gitstq/EnvForge.git

- name: Detect Environment
  run: envforge detect --json > env-report.json

- name: Health Check
  run: envforge health -s critical
```

---

## Contributing

We welcome contributions of all kinds! Whether it's filing a bug report, improving documentation, or submitting a code PR.

### How to Contribute

1. **Fork** this repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push the branch: `git push origin feature/your-feature`
5. Submit a **Pull Request**

### Code Standards

- Follow PEP 8 coding conventions
- Use type hints
- Write unit tests for new features
- Maintain the zero-core-dependency principle

### Commit Convention

Please follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
feat: new feature
fix: bug fix
docs: documentation update
refactor: code refactoring
test: test-related changes
chore: build/tooling changes
```

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

```
MIT License

Copyright (c) 2024 gitstq

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  <strong>EnvForge</strong> is crafted with care by <a href="https://github.com/gitstq">gitstq</a>
</p>
