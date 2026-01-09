# Redirect Strategy: spirallab.org → law.spiral.ooo

本文档提供了将 `spirallab.org` 重定向到 `law.spiral.ooo` 的两种方案。

## Option 1: Domain-Level 301 Redirect (推荐)

这是最佳方案，在 DNS/域名管理层面实现永久重定向。

### 步骤

1. **登录域名注册商或 DNS 提供商**（如 Cloudflare、Namecheap、GoDaddy）

2. **配置域名重定向**
   - 在域名管理面板中找到 "Redirects" 或 "Forwarding" 选项
   - 设置 `spirallab.org` → `https://law.spiral.ooo/` 301 永久重定向
   - 确保选择 "301 Permanent Redirect"
   - 勾选 "Preserve Path"（如果希望 `/path` 也重定向到 `law.spiral.ooo/path`）

3. **Cloudflare 用户**（如果使用 Cloudflare）：
   - 进入 DNS 设置
   - 添加 Page Rule：
     - URL Pattern: `*spirallab.org/*`
     - Setting: Forwarding URL
     - Status Code: 301 Permanent Redirect
     - Destination URL: `https://law.spiral.ooo/$1`

4. **验证**
   - 访问 `http://spirallab.org` 应该自动跳转到 `https://law.spiral.ooo`
   - 使用浏览器开发者工具检查 HTTP 状态码为 301

### 优势
- SEO 友好（301 永久重定向）
- 服务器性能好（不依赖 JavaScript）
- 适用于所有路径
- 自动处理 HTTP → HTTPS

---

## Option 2: GitHub Pages Redirect-Only Site

如果无法在 DNS 层面配置 301 重定向，可以使用这个方案。

### 步骤

1. **创建重定向仓库**（或在新分支）

   在 `spirallab.org` 的 GitHub Pages 仓库中创建 `index.html`：

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=https://law.spiral.ooo/">
  <link rel="canonical" href="https://law.spiral.ooo/">
  <title>Redirecting to Field Law Archive</title>
  <script>
    window.location.replace('https://law.spiral.ooo' + window.location.pathname + window.location.search);
  </script>
</head>
<body>
  <p>Redirecting to <a href="https://law.spiral.ooo/">Field Law Archive</a>...</p>
</body>
</html>
```

2. **配置 GitHub Pages**
   - 在 `spirallab.org` 仓库的 Settings → Pages
   - 设置 Source 为包含上述 `index.html` 的分支/目录
   - 确保 Custom domain 设置为 `spirallab.org`

3. **验证**
   - 访问 `https://spirallab.org` 应该跳转到 `https://law.spiral.ooo`

### 优势
- 不需要 DNS 提供商支持重定向功能
- 快速实施
- 可以处理所有路径

### 劣势
- 非标准 HTTP 状态码（使用 meta refresh + JS）
- 对 SEO 不如 301 重定向友好
- 依赖客户端 JavaScript（虽然有关 meta refresh 后备）

---

## 推荐实施顺序

1. **首选 Option 1**（如果 DNS 提供商支持）
2. **备选 Option 2**（如果 Option 1 不可用）

---

## 注意事项

- 确保 `law.spiral.ooo` 已正确配置并可访问
- 重定向可能需要一些时间传播（DNS 变更通常需要几分钟到几小时）
- 建议在重定向生效后测试所有主要路径
- 保留 `spirallab.org` 的 DNS 记录，直到确认重定向工作正常

