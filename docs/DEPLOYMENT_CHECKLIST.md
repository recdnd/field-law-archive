# Deployment Checklist: Field Law Archive

## ✅ 已完成配置

### A) 仓库结构
- ✅ `index.html` 位于仓库根目录
- ✅ GitHub Pages 发布源应设置为：**main / root**

### B) 自定义域名
- ✅ `CNAME` 文件已创建，内容：`law.spiral.ooo`
- ✅ 文件位置：仓库根目录

### C) SEO 配置
- ✅ `<title>` 已设置为 "Field Law Archive"
- ✅ Meta description 已添加
- ✅ Canonical URL 已添加（动态更新）
- ✅ Open Graph 标签已配置
- ✅ Twitter Card 标签已配置
- ✅ `robots.txt` 已创建
- ✅ `sitemap.xml` 已创建

### D) UI 文本更新
- ✅ 主标题已更新为 "Field Law Archive"（英文）
- ✅ 中文标题已更新为 "語場法律檔案庫"
- ✅ 副标题保持为 "NON-EXECUTABLE OBSERVATION LAYER · STRUCTURAL VIEW ONLY"

### E) 重定向方案
- ✅ `docs/REDIRECT_SPIRALLAB.md` 已创建（包含两种方案）
- ✅ `docs/redirect-spirallab-index.html` 已创建（Option 2 示例）

### F) DNS 设置文档
- ✅ `docs/DNS_SETUP.md` 已创建（包含完整 DNS 和 GitHub Pages 配置步骤）

---

## 🚀 下一步操作

### 1. GitHub Pages 配置

1. 前往仓库：https://github.com/recdnd/field-law-archive
2. Settings → Pages
3. Source: **Deploy from a branch** → **main** → **/ (root)**
4. Custom domain: 输入 `law.spiral.ooo`
5. 勾选 **Enforce HTTPS**
6. 保存

### 2. DNS 配置

按照 `docs/DNS_SETUP.md` 中的说明：
- 添加 CNAME 记录：`law` → `recdnd.github.io`
- 等待 DNS 传播
- 验证 GitHub Pages 显示域名已验证

### 3. 验证

- [ ] 访问 `https://law.spiral.ooo` 可正常加载
- [ ] 页面标题显示 "Field Law Archive"
- [ ] HTTPS 证书有效
- [ ] `robots.txt` 可访问：`https://law.spiral.ooo/robots.txt`
- [ ] `sitemap.xml` 可访问：`https://law.spiral.ooo/sitemap.xml`

### 4. 重定向配置（可选）

如需配置 `spirallab.org` → `law.spiral.ooo` 重定向：
- 参考 `docs/REDIRECT_SPIRALLAB.md`
- 推荐使用 Option 1（DNS 层面 301 重定向）

---

## 📝 文件变更清单

### 修改的文件
- `CNAME` - 更新为 `law.spiral.ooo`
- `index.html` - 更新标题、SEO 标签、UI 文本

### 新创建的文件
- `robots.txt` - SEO 爬虫配置
- `sitemap.xml` - 站点地图
- `docs/DNS_SETUP.md` - DNS 配置文档
- `docs/REDIRECT_SPIRALLAB.md` - 重定向方案文档
- `docs/redirect-spirallab-index.html` - 重定向示例 HTML
- `docs/DEPLOYMENT_CHECKLIST.md` - 本清单

---

## 提交信息建议

可以按照以下方式提交：

```bash
# B) 自定义域名
git add CNAME
git commit -m "Configure custom domain law.spiral.ooo"

# C) SEO 配置
git add robots.txt sitemap.xml index.html
git commit -m "SEO: canonical, sitemap, robots"

# D) UI 文本更新
git add index.html
git commit -m "Rename UI to Field Law Archive"

# E) 文档
git add docs/
git commit -m "Add DNS setup and redirect documentation"
```

