# DNS Setup for law.spiral.ooo

本文档说明如何配置 DNS 和 GitHub Pages 以使用自定义域名 `law.spiral.ooo`。

## DNS 配置

### 步骤 1: 添加 CNAME 记录

在您的 DNS 提供商（如 Cloudflare、Namecheap、GoDaddy 等）中添加以下 DNS 记录：

- **Type**: `CNAME`
- **Name/Host**: `law`
- **Target/Value**: `recdnd.github.io`
- **TTL**: 默认（通常 3600 秒）

### 步骤 2: 验证 DNS 记录

等待 DNS 传播（可能需要几分钟到几小时），然后验证：

```bash
# 在命令行中运行
dig law.spiral.ooo CNAME
# 或
nslookup law.spiral.ooo
```

应该看到指向 `recdnd.github.io` 的 CNAME 记录。

---

## GitHub Pages 配置

### 步骤 1: 确认仓库设置

1. 前往 GitHub 仓库：`https://github.com/recdnd/field-law-archive`
2. 进入 **Settings** → **Pages**

### 步骤 2: 配置发布源

- **Source**: 选择 `Deploy from a branch`
- **Branch**: `main` / `root`（因为 `index.html` 在根目录）

### 步骤 3: 设置自定义域名

1. 在 **Custom domain** 字段中输入：`law.spiral.ooo`
2. 勾选 **Enforce HTTPS**（重要！）
3. 点击 **Save**

### 步骤 4: 验证配置

GitHub 会自动验证域名：
- ✅ 如果看到绿色勾号，DNS 配置正确
- ⚠️ 如果看到警告，检查：
  - DNS 记录是否正确配置
  - 是否等待了足够的传播时间（可能需要几小时）
  - CNAME 文件是否存在于仓库根目录且内容为 `law.spiral.ooo`

---

## 验证清单

- [ ] DNS CNAME 记录已添加：`law` → `recdnd.github.io`
- [ ] 仓库根目录存在 `CNAME` 文件，内容为 `law.spiral.ooo`
- [ ] GitHub Pages 设置中 Custom domain 已设置为 `law.spiral.ooo`
- [ ] **Enforce HTTPS** 已启用
- [ ] 可以访问 `https://law.spiral.ooo`（HTTP 会自动跳转到 HTTPS）

---

## 故障排除

### 问题：GitHub Pages 显示 DNS 配置错误

**解决方案**：
1. 确认 CNAME 记录的 Target 是 `recdnd.github.io`（不是 `recdnd.github.io.`，注意末尾没有点）
2. 等待 DNS 传播（最多 48 小时，通常几分钟到几小时）
3. 确认没有 A 记录冲突（应该只有 CNAME 记录）

### 问题：HTTPS 证书未生成

**解决方案**：
1. 确保 **Enforce HTTPS** 已勾选
2. 等待 GitHub 自动生成 Let's Encrypt 证书（可能需要几分钟）
3. 如果长时间未生成，可以临时取消勾选再重新勾选

### 问题：访问时显示 404

**解决方案**：
1. 确认 `index.html` 存在于仓库根目录
2. 确认 GitHub Pages 的 Source 分支设置正确
3. 检查 Pages 构建日志（Settings → Pages → 查看最近部署）

---

## 安全注意事项

- **始终使用 HTTPS**：确保 "Enforce HTTPS" 已启用
- **CNAME 文件内容**：确保 `CNAME` 文件内容仅包含域名，没有多余空格或换行
- **DNS 安全**：建议使用 DNS 提供商的 DNSSEC 功能（如果可用）

---

## 完成后

配置完成后，站点将在以下地址可访问：
- 主域名：`https://law.spiral.ooo`
- GitHub Pages 默认地址：`https://recdnd.github.io/field-law-archive`（如果未禁用）

建议在 DNS 和 GitHub Pages 都配置完成后，等待 24 小时再进行 SEO 和性能测试。

