# 👨‍👩‍👧‍👦 大家庭成员记录

一个简单、优雅、全自动的大家庭照片管理系统。只需将照片放入文件夹，即可生成美观的相册网页。

![版本](https://img.shields.io/badge/版本-2.0.0-orange)
![Python](https://img.shields.io/badge/Python-3.6+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ 功能特点

- 📱 **手机优先** - 完美适配各种屏幕，支持20人同时显示
- 🔐 **密码保护** - 访问需要密码（默认：`20031023`）
- 🎨 **暖色调设计** - 米白背景，橙色点缀，温馨舒适
- 📅 **EXIF拍摄日期** - 自动读取照片拍摄时间，非文件保存时间
- 🎬 **视频支持** - 支持 MP4/MOV/AVI 等视频格式
- 🖼️ **原比例显示** - 照片保持原始比例，不裁剪
- 🚀 **零代码维护** - 只需往文件夹丢照片/视频，自动更新
- 👁️ **实时监控** - 文件变动自动重新生成数据
- 🌐 **GitHub Pages** - 纯静态，免费部署

---

## 📁 项目结构

```
family-album/
├── index.html              # 首页：成员网格
├── member.html             # 详情页：个人时间轴
├── css/
│   └── style.css           # 样式（手机优先，响应式）
├── js/
│   ├── app.js              # 首页逻辑：渲染成员墙
│   └── gallery.js          # 详情页逻辑：渲染时间轴
├── data/
│   └── gallery-data.json   # Python生成的数据文件
├── images/                 # 照片存放目录
│   ├── 妈妈/               # 成员文件夹（可用中文）
│   │   ├── avatar.jpg      # 成员头像（必须）
│   │   ├── 2024-02-15_生日聚餐.jpg
│   │   ├── 2023-12-20_公园散步.mp4   # 视频也支持
│   │   └── ...
│   ├── 爸爸/
│   └── ...其他成员
├── generate_data.py        # 数据生成脚本
├── watch.py                # 文件夹监控脚本（可选）
├── requirements.txt        # Python依赖
└── README.md               # 本文件
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 添加照片/视频

#### 创建成员文件夹

在 `images/` 目录下创建子文件夹，每个文件夹代表一个家庭成员：

```bash
mkdir images/妈妈
mkdir images/爸爸
mkdir images/宝宝
```

#### 添加头像

每个成员文件夹中必须有一个头像文件，命名为 `avatar.jpg`：

```bash
cp 妈妈头像.jpg images/妈妈/avatar.jpg
cp 爸爸头像.jpg images/爸爸/avatar.jpg
```

#### 添加照片

照片文件名建议包含日期和描述：

| 文件名格式 | 示例 | 解析结果 |
|-----------|------|---------|
| `YYYY-MM-DD_描述.jpg` | `2024-02-15_妈妈生日聚餐.jpg` | 日期: 2024-02-15, 描述: 妈妈生日聚餐 |
| `YYYY年MM月DD日_描述.jpg` | `2024年2月15日_妈妈生日聚餐.jpg` | 日期: 2024-02-15, 描述: 妈妈生日聚餐 |

**注意**：如果没有日期，会自动读取照片的 EXIF 拍摄日期。

#### 添加视频

支持格式：`.mp4` `.mov` `.avi` `.mkv` `.flv` `.wmv` `.m4v` `.3gp`

```bash
cp 视频.mp4 "images/妈妈/2024-02-15_生日视频.mp4"
```

### 3. 生成数据

```bash
python generate_data.py
```

输出示例：

```
👨‍👩‍👧‍👦 大家庭成员记录 - 数据生成脚本
==================================================

🔍 正在扫描目录: images/
  ✅ 妈妈: 5 张照片, 1 个视频
  ✅ 爸爸: 3 张照片

💾 正在保存数据: data/gallery-data.json
✅ 数据保存成功!

==================================================
📊 统计信息
==================================================
👨‍👩‍👧‍👦 家庭成员: 2 人
📷 照片总数: 8 张
🎬 视频总数: 1 个
==================================================
```

---

## 📅 日期识别说明

脚本会按以下优先级获取日期：

1. **文件名中的日期** - 如 `2024-02-15_生日聚餐.jpg`
2. **EXIF拍摄日期** - 从照片元数据读取（需安装 Pillow）
3. **文件修改时间** - 最后 fallback

页面上会显示日期来源：
- `(EXIF)` - 来自照片拍摄日期
- `(文件日期)` - 来自文件修改时间

---

## 👁️ 实时监控（可选）

```bash
python watch.py
```

每当你添加/删除/修改照片或视频时，会自动重新生成数据。

---

## 🌐 部署到 GitHub Pages

### 1. 创建 GitHub 仓库

创建新仓库，命名为 `family-album`。

### 2. 推送代码

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/family-album.git
git push -u origin main
```

### 3. 启用 GitHub Pages

1. 打开仓库 Settings → Pages
2. Source 选择 Deploy from a branch
3. Branch 选择 main，文件夹选择 /(root)
4. 点击 Save

访问地址：`https://你的用户名.github.io/family-album/`

---

## 🔧 高级配置

### 修改访问密码

编辑 `index.html` 和 `member.html`：

```javascript
const CORRECT_PASSWORD = '20031023';  // 修改这里
```

### 修改主题名称

编辑 `index.html` 和 `member.html` 中的标题文字。

---

## ❓ 常见问题

### Q: 照片日期显示不正确？

A: 确保安装了 Pillow：`pip install Pillow`，这样可以从 EXIF 读取拍摄日期。

### Q: 照片被裁剪了？

A: 新版已改为保持原比例显示（`object-fit: contain`），不会裁剪照片。

### Q: 视频无法播放？

A: 确保视频格式是浏览器支持的（推荐 MP4/H.264 编码）。

### Q: 如何支持20人显示？

A: 新版已优化布局，大屏幕可显示 8 列，支持 20+ 人同时显示。

---

## 📝 更新日志

### v2.0.0 (2024)

- ✅ 读取 EXIF 拍摄日期
- ✅ 支持视频文件（MP4/MOV/AVI等）
- ✅ 图片保持原比例显示
- ✅ 优化20人布局
- ✅ 移除懒加载，直接加载
- ✅ 显示日期来源标记

---

## 📄 许可证

MIT License - 自由使用

---

**👨‍👩‍👧‍👦 记录美好，珍藏回忆** ❤️
