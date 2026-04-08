# 部署指南 / Deployment Guide

## 概述 / Overview

这个仓库包含一个名为 "米粒太声乐助手" 的网页应用，可以通过 GitHub Pages 进行部署。

This repository contains a web application called "Music Vocal Assistant" that can be deployed via GitHub Pages.

## 部署步骤 / Deployment Steps

### 1. 合并 Pull Request / Merge the Pull Request

首先，将这个 Pull Request 合并到主分支（main 或 master）。

First, merge this Pull Request into the main branch (main or master).

### 2. 启用 GitHub Pages / Enable GitHub Pages

合并后，需要在仓库设置中启用 GitHub Pages：

After merging, you need to enable GitHub Pages in repository settings:

1. 访问仓库页面：https://github.com/u2017310234/codex
   Visit the repository page: https://github.com/u2017310234/codex

2. 点击 **Settings**（设置）标签
   Click on the **Settings** tab

3. 在左侧菜单中找到 **Pages**
   Find **Pages** in the left sidebar menu

4. 在 "Build and deployment" 部分：
   In the "Build and deployment" section:
   - **Source**: 选择 "GitHub Actions" / Select "GitHub Actions"
   
5. 保存设置
   Save the settings

### 3. 触发部署 / Trigger Deployment

有两种方式触发部署：

There are two ways to trigger deployment:

#### 方式 A：自动部署 / Method A: Automatic Deployment
当你推送代码到主分支时，会自动触发部署。

Deployment is automatically triggered when you push to the main branch.

#### 方式 B：手动部署 / Method B: Manual Deployment

1. 访问 Actions 页面：https://github.com/u2017310234/codex/actions
   Visit the Actions page: https://github.com/u2017310234/codex/actions

2. 在左侧选择 "Deploy to GitHub Pages" workflow
   Select the "Deploy to GitHub Pages" workflow on the left

3. 点击右侧的 "Run workflow" 按钮
   Click the "Run workflow" button on the right

4. 选择分支并点击绿色的 "Run workflow" 按钮
   Select the branch and click the green "Run workflow" button

### 4. 查看部署状态 / Check Deployment Status

1. 访问 Actions 页面查看工作流运行状态
   Visit the Actions page to view the workflow run status

2. 等待部署完成（通常需要 1-2 分钟）
   Wait for the deployment to complete (usually takes 1-2 minutes)

3. 部署成功后，你的网站将在以下地址可用：
   After successful deployment, your site will be available at:
   
   **https://u2017310234.github.io/codex/**

## 本地测试 / Local Testing

如果你想在本地测试网站，可以使用任何静态文件服务器：

If you want to test the site locally, you can use any static file server:

```bash
# 使用 Python / Using Python
python3 -m http.server 8080

# 使用 Node.js / Using Node.js
npx http-server -p 8080

# 使用 PHP / Using PHP  
php -S localhost:8080
```

然后在浏览器中访问 http://localhost:8080

Then visit http://localhost:8080 in your browser

## 功能说明 / Features

这个应用包含以下功能：

This application includes the following features:

- 🎤 音频录制 / Audio Recording
- 📁 音频文件上传 / Audio File Upload
- 🎵 音频播放控制 / Audio Playback Controls
- 📊 音高分析和可视化 / Pitch Analysis and Visualization
- 🌍 多语言支持（中文/英文）/ Multi-language Support (Chinese/English)
- 📱 响应式设计（支持手机和桌面）/ Responsive Design (Mobile and Desktop)

## 故障排除 / Troubleshooting

### 部署失败 / Deployment Fails

如果部署失败，请检查：

If deployment fails, please check:

1. GitHub Pages 是否已在设置中启用
   Whether GitHub Pages is enabled in settings

2. 仓库是否有 "pages" 权限
   Whether the repository has "pages" permissions

3. 查看 Actions 日志了解具体错误
   Check Actions logs for specific errors

### 网站无法访问 / Site Not Accessible

如果网站部署成功但无法访问：

If the site is deployed successfully but not accessible:

1. 等待几分钟，DNS 传播需要时间
   Wait a few minutes, DNS propagation takes time

2. 清除浏览器缓存
   Clear browser cache

3. 确认 URL 正确：https://u2017310234.github.io/codex/
   Confirm the URL is correct: https://u2017310234.github.io/codex/

## 更新网站 / Updating the Site

修改 `index.html` 文件后：

After modifying the `index.html` file:

1. 提交并推送更改到主分支
   Commit and push changes to the main branch

2. GitHub Actions 会自动重新部署
   GitHub Actions will automatically redeploy

3. 等待 1-2 分钟后，刷新网站查看更新
   Wait 1-2 minutes, then refresh the site to see updates
