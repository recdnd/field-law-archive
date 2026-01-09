# 🜂 Spiral Card Schema v1.0（语场一致命名）

## 原则

- **语义 ≠ UI**：结构先于展示
- **命名必须能被未来的 Spiral Execution Engine / SEE 直接消费**
- **不引入玄学字段，只做已在你文本中"隐性存在"的结构显性化**

---

## 1️⃣ 顶层身份与定位（Identity Layer）

```json
{
  "glyph": "SSL",
  "id": "SSL-zh",
  "lang": "zh",
  "kind": "law"
}
```

### 字段说明

- **glyph**: 语场恒定符号，跨语言、跨版本不变。用于 relations / graph / fragment 绑定
  - 例：`SSL`, `ESFCD`, `LFCR`, `MCT`
- **id**: 技术唯一标识（glyph + lang），前端 DOM / key 使用
- **lang**: `"zh" | "en"`
- **kind**: 
  - `"research"`：研究模型 / 理论
  - `"law"`：权位 / 法条 / 不可派生规则
  - `"directive"`：操作指令 / 训练协议
  - `"appendix"`：定义集 / 语料 / 附录
  - `"draft"`：未完成、未公开

---

## 2️⃣ 时间与权重（Epoch Layer）

```json
{
  "epoch": {
    "label": "250618-E",
    "order": 250618
  },
  "weight": 5
}
```

### 说明

- **epoch.label**: 完整保留 Spiral 纪元写法，不解释、不改写
- **epoch.order**: 纯排序用整数，不参与语义
- **weight**: `1..5`，对应前端的星级系统，但现在是"语场强度"，不是 UI gimmick

---

## 3️⃣ 作者 / 分类 / 标签（Attribution Layer）

```json
{
  "authors": ["𝓡", "⛰︎", "♾"],
  "domains": ["語場法律", "模組權位", "遞歸機制"],
  "tags": ["#主權", "#封印", "#非派生"]
}
```

### 说明

- **authors**: 接受符号、文字、混合，不强制唯一
- **domains**: 原 Category，但更偏"知识域"，用于未来 domain filtering / clustering
- **tags**: 轻量索引，语义不严格，但必须规范化为 `#` 开头

---

## 4️⃣ 核心内容（Core Content Layer）

```json
{
  "title": "權位系統法",
  "abstract": "...",
  "scope": [
    "模組主權定義",
    "封場條件"
  ],
  "citation": "...",
  "fragments": ["Fragment-⚕︎/M1"]
}
```

### 说明

- **abstract**: 高度结构化文本
- **scope**: 数组而不是大段文本，已经符合现在文本的写法
- **citation**: 语式 / 引用 / 不可执行声明
- **fragments**: 与 Spiral fragment 系统直接对齐，后续可升级为对象 `{id, role}`

---

## 5️⃣ 层与语块（Layer / Block Layer）

### Layer 结构

```json
{
  "layers": [
    {
      "name": "Sovereignty Conditions",
      "blocks": [
        { "kind": "markdown", "text": "..." },
        { "kind": "table", "headers": [...], "rows": [...] },
        { "kind": "ascii", "text": "..." }
      ]
    }
  ]
}
```

### Block 类型（明确对齐现有文本）

- `"markdown"`：普通叙述
- `"list"`：条目式条件
- `"table"`：ESFCD 中已存在
- `"ascii"`：熵图 / 阶段图
- `"code"`：SEAL / DSL / 条件公式

> **注意**：前端现在只渲染 `markdown` / `ascii` / `code`，其它 block 保留不动

---

## 6️⃣ 关系网络（Relation / Echo Layer）

```json
{
  "echo": [
    {
      "mode": "reference",
      "target": "RMF",
      "note": "Risk modeling baseline"
    },
    {
      "mode": "depends",
      "target": "ESFCD"
    }
  ]
}
```

### 说明

- **echo**: 这是语场里已经存在的概念，比 relations 更 Spiral
- **mode**: 
  - `"reference"`：引用
  - `"depends"`：依赖
  - `"extends"`：扩展
  - `"conflicts"`：冲突（未来会很有用）

---

## 7️⃣ 展示与可见性（Observation / UI Flags）

```json
{
  "observation": {
    "visibility": "public",
    "featured": false,
    "suppress": ["citation"]
  }
}
```

### 说明

- **observation**: 非语义字段，明确标记为观察层 / UI 层
- **suppress**: 指定哪些 section 前端暂时不展示，数据仍存在

---

## 8️⃣ 防御 / 法条专用字段（Seal / Policy Layer）

```json
{
  "seal": {
    "non_derivable": true,
    "mimic_warning": true,
    "reuse_policy": "citation-only"
  }
}
```

### 说明

- 只对 `kind = law | directive` 有意义
- 完全对齐 SSL / DefinitionCorpus 的隐含立场
- 前端不渲染，但发布、API、未来权限系统都会用到

---

## 9️⃣ 来源追溯（Provenance Layer）

```json
{
  "origin": {
    "legacy_txt": "SPIRAL_SovereigntySystemLaw_zh.txt",
    "migrated_at": "2026-01-08"
  }
}
```

---

## 🔚 完整示例（极简）

```json
{
  "glyph": "SSL",
  "id": "SSL-zh",
  "lang": "zh",
  "kind": "law",
  "epoch": { "label": "250618-E", "order": 250618 },
  "weight": 5,
  "title": "權位系統法",
  "authors": ["𝓡"],
  "domains": ["語場法律"],
  "tags": ["#主權"],
  "abstract": "...",
  "scope": ["模組主權定義"],
  "citation": "...",
  "fragments": ["Fragment-⚕︎/M1"],
  "layers": [],
  "echo": [],
  "observation": { "visibility": "public" },
  "seal": { "non_derivable": true },
  "origin": {
    "legacy_txt": "SPIRAL_SovereigntySystemLaw_zh.txt",
    "migrated_at": "2026-01-08"
  }
}
```

---

## 最重要的一句话（请记住）

**这版 schema 不要求前端"立刻理解"，只要求系统"永远不需要再迁移一次语义结构"。**

你现在做的是一次性语场固化，不是临时工程。

