#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spiral Registry Builder v2
迁移工具：从 TXT 到 JSON SSOT
"""

import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# ============================================================================
# 标点符号清理（1:1 匹配 punctuation_cleaner.py）
# ============================================================================

def clean_to_english_punctuation(text: str) -> str:
    """
    标点符号清理函数，完全匹配 puncc.py 的行为
    必须保留：
    - 三重反引号代码块
    - URLs (http:// 或 https://)
    """
    if not text:
        return text
    
    # 保护代码块：提取所有 ```...``` 块
    code_blocks = []
    code_block_pattern = r'```[\s\S]*?```'
    
    def replace_code_block(match):
        idx = len(code_blocks)
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{idx}__"
    
    protected_text = re.sub(code_block_pattern, replace_code_block, text)
    
    # 保护 URLs
    url_pattern = r'https?://[^\s]+'
    urls = []
    
    def replace_url(match):
        idx = len(urls)
        urls.append(match.group(0))
        return f"__URL_{idx}__"
    
    protected_text = re.sub(url_pattern, replace_url, protected_text)
    
    # 执行标点替换（与 puncc.py 完全一致）
    replacements = {
        "，": ", ",
        "。": ".",
        "：": ":",
        """: "\"",
        """: "\"",
        "'": "'",
        "'": "'",
        "、": ", ",
        "（": "(",
        "）": ")",
        "《": "<",
        "》": ">",
        "【": "[",
        "】": "]",
        "！": "!",
        "？": "?",
        "／": "/",
        "；": ";"
    }
    
    for zh, en in replacements.items():
        protected_text = protected_text.replace(zh, en)
    
    # 恢复 URLs
    for idx, url in enumerate(urls):
        protected_text = protected_text.replace(f"__URL_{idx}__", url)
    
    # 恢复代码块
    for idx, code_block in enumerate(code_blocks):
        protected_text = protected_text.replace(f"__CODE_BLOCK_{idx}__", code_block)
    
    return protected_text


def sanitize_text(text: str, should_sanitize: bool = True) -> str:
    """应用标点清理（如果启用）"""
    if not should_sanitize:
        return text
    return clean_to_english_punctuation(text)


# ============================================================================
# 解析器：容忍格式漂移
# ============================================================================

def parse_weight(weight_str: str) -> int:
    """
    解析权重：接受 ★★★★★, 5, ★ ★ ★, *** 等格式
    返回 1-5 的整数
    """
    if not weight_str:
        return 3  # 默认
    
    # 提取所有星号（全角/半角/ASCII）
    stars = re.findall(r'[★☆*]', weight_str)
    count = len(stars)
    
    # 也尝试数字
    num_match = re.search(r'\d+', weight_str)
    if num_match:
        num = int(num_match.group(0))
        if 1 <= num <= 5:
            return num
    
    # 星号计数
    if 1 <= count <= 5:
        return count
    
    return 3  # 默认值


def parse_tags(tags_str: str) -> List[str]:
    """
    解析标签：接受空格/逗号/斜杠分隔
    规范化：确保以 # 开头
    """
    if not tags_str:
        return []
    
    # 分割：空格、逗号、斜杠
    tags = re.split(r'[\s,/#]+', tags_str)
    
    normalized = []
    for tag in tags:
        tag = tag.strip()
        if not tag:
            continue
        
        # 确保以 # 开头
        if not tag.startswith('#'):
            tag = '#' + tag
        
        normalized.append(tag)
    
    return list(set(normalized))  # 去重


def normalize_title(title: str) -> str:
    """
    规范化 title 格式为：中文 | English
    处理以下情况：
    - 中文 · English → 中文 | English
    - 中文（English） → 中文 | English
    - 中文｜English（全角） → 中文 | English
    - 中文 | English → 保持不变
    - 只有中文或只有英文 → 保持不变
    """
    if not title:
        return title
    
    # 处理全角 ｜ 分隔符
    if '｜' in title:
        title = title.replace('｜', ' | ')
    
    # 处理 · 分隔符（半角和全角）
    if ' · ' in title:
        title = title.replace(' · ', ' | ')
    if ' · ' in title:
        title = title.replace(' · ', ' | ')
    
    # 处理括号格式：中文（English） → 中文 | English
    # 匹配模式：中文（English）或中文(English)
    bracket_pattern = r'^(.+?)[（(](.+?)[）)]$'
    match = re.match(bracket_pattern, title)
    if match:
        chinese_part = match.group(1).strip()
        english_part = match.group(2).strip()
        # 如果英文部分看起来像英文（包含字母），则转换
        if re.search(r'[a-zA-Z]', english_part):
            title = f"{chinese_part} | {english_part}"
    
    return title


def normalize_citation(citation: str, lang: str, card_id: str, title: str, epoch_label: str, fragments: List[str]) -> str:
    """
    规范化 citation 格式
    
    英文标准格式：
    Author (Year). *Title*. Entry ID. Epoch XXX. Filed under: Fragment-XXX, Fragment-XXX.
    
    中文标准格式：
    作者(年份). <标题>. 語螺語研究登錄項:ID．紀錄碎片:Fragment-XXX, Fragment-XXX;紀元:XXX．
    
    如果 citation 为空或无法解析，返回空字符串
    """
    if not citation:
        return citation
    
    citation = citation.strip()
    
    # 检查是否已经是标准格式（使用标准关键词和格式）
    is_standard_en = lang == 'en' and 'Entry' in citation and re.search(r'Entry\s+[A-Za-z0-9]+\.', citation)
    is_standard_zh = lang == 'zh' and '語螺語研究登錄項' in citation
    
    if is_standard_en or is_standard_zh:
        # 规范化空格和标点
        citation = re.sub(r'\s+', ' ', citation)  # 规范化空格
        citation = re.sub(r'\.\s*\.', '.', citation)  # 移除重复句号
        # 统一使用 *Title* 格式（英文）
        if lang == 'en':
            citation = re.sub(r'<([^>]+?)>', r'*\1*', citation)
            # 如果标题没有 * 标记，添加它（在 Entry 之前的文本）
            if '*' not in citation:
                # 查找 Entry 之前的标题文本
                entry_pos = citation.find('Entry')
                if entry_pos > 0:
                    # 提取作者年份后的文本作为标题
                    year_match = re.search(r'\((\d{4})\)', citation)
                    if year_match:
                        after_year = citation[year_match.end():entry_pos].strip()
                        # 移除开头的句号和空格
                        after_year = re.sub(r'^\.\s*', '', after_year).strip()
                        if after_year and not after_year.startswith('*'):
                            # 移除标题末尾的句号（如果有）
                            after_year_clean = re.sub(r'\.\s*$', '', after_year)
                            # 替换为带 * 的格式
                            citation = citation[:year_match.end()] + '. *' + after_year_clean + '*. ' + citation[entry_pos:]
        # 确保使用标准关键词
        citation = re.sub(r'Spiral (Registry|Research|Field Codex) Entry', 'Entry', citation)
        citation = re.sub(r'Registered Epoch', 'Epoch', citation)
        return citation.strip()
    
    # 如果不符合标准格式，强制重构
    # 继续下面的解析逻辑来重构
    
    # 中文：检查是否已经是标准格式
    if lang == 'zh' and '語螺語研究登錄項' in citation and ('紀錄碎片' in citation or '記錄碎片' in citation):
        # 规范化全角标点
        citation = re.sub(r'[。]', '．', citation)  # 统一使用全角句号
        citation = re.sub(r'[：]', ':', citation)  # 统一使用半角冒号
        return citation.strip()
    
    # 如果使用了变体格式（如註冊紀元、語螺語場編碼條目），需要重构为标准格式
    # 继续下面的解析逻辑来重构
    
    # 尝试解析现有格式并重构
    # 提取作者和年份（支持多种格式）
    author_patterns = [
        r'^([^(（]+?)\s*[\(（](\d{4})[\)）]',  # 标准格式
        r'^([^(（]+?)[\(（]([^)）]+?)[\)）]\s*[\(（](\d{4})[\)）]',  # 作者有括号说明的情况
    ]
    author_match = None
    for pattern in author_patterns:
        author_match = re.search(pattern, citation)
        if author_match:
            break
    
    if not author_match:
        # 如果无法解析，返回原样（可能是特殊格式）
        return citation
    
    # 处理作者（可能有括号说明）
    if len(author_match.groups()) == 3:
        # 格式：作者(说明)(年份)
        author = author_match.group(1).strip()
        year = author_match.group(3)
    else:
        # 格式：作者(年份)
        author = author_match.group(1).strip()
        year = author_match.group(2)
    
    author = author_match.group(1).strip()
    year = author_match.group(2)
    
    # 提取标题（优先提取 < > 或 《 》 中的内容，然后是 * *，最后是括号或普通文本）
    title_match = re.search(r'[<《]([^>》]+?)[>》]', citation)
    if not title_match:
        title_match = re.search(r'\*([^*]+?)\*', citation)
    if not title_match:
        # 查找括号中的内容（但排除作者说明的括号）
        # 跳过作者部分的括号，查找后面的括号
        after_author = citation[author_match.end():] if author_match else citation
        # 查找第一个非作者括号对（可能是标题）
        title_match = re.search(r'\.\s*([^(]+?)\s*\(([^)]+?)\)', after_author)
        if title_match:
            # 格式：Title (ID)，提取标题部分
            extracted_title = title_match.group(1).strip()
        else:
            # 查找普通文本标题（在句号后，Entry/Epoch 前）
            title_match = re.search(r'\.\s*([^.]+?)(?:\s*\([^)]+?\))?\.\s*(?:Entry|Epoch|Spiral)', after_author)
            if title_match:
                extracted_title = title_match.group(1).strip()
            else:
                extracted_title = title
    
    # 处理提取的标题
    if 'extracted_title' not in locals():
        if title_match:
            if title_match.lastindex and title_match.lastindex >= 1:
                extracted_title = title_match.group(1).strip()
            else:
                extracted_title = title
        else:
            # 如果找不到标题标记，尝试从 Entry 前提取
            if author_match:
                after_author = citation[author_match.end():]
                # 查找第一个句号到 Entry 之间的文本
                title_before_entry = re.search(r'\.\s*([^.]+?)\s*\.\s*(?:Entry|Epoch|Spiral)', after_author)
                if title_before_entry:
                    extracted_title = title_before_entry.group(1).strip()
                else:
                    extracted_title = title
            else:
                extracted_title = title
    
    # 提取 Entry ID（支持多种变体）
    entry_patterns = [
        r'(?:Entry|語螺語研究登錄項)[:：]?\s*([A-Za-z0-9]+)',
        r'語螺語場編碼條目[:：]?\s*([A-Za-z0-9]+)',
        r'Spiral (?:Registry|Research|Field Codex) Entry[:：]?\s*([A-Za-z0-9]+)',
        r'註冊紀元[:：]?\s*([A-Za-z0-9\-]+)',  # 註冊紀元可能包含 epoch，作为备选
    ]
    entry_id = card_id.split('-')[0]  # 默认值
    for pattern in entry_patterns:
        entry_match = re.search(pattern, citation)
        if entry_match:
            potential_id = entry_match.group(1)
            # 如果从註冊紀元提取且包含 -，可能是 epoch，跳过
            if '註冊紀元' in pattern and '-' in potential_id:
                continue
            entry_id = potential_id
            break
    
    # 提取 Epoch
    epoch_match = re.search(r'(?:Epoch|紀元|註冊紀元)[:：]?\s*([A-Za-z0-9\-]+)', citation)
    extracted_epoch = epoch_match.group(1) if epoch_match else epoch_label
    
    # 提取 Fragments
    fragment_pattern = r'Fragment-([^,\s;．]+)'
    found_fragments = re.findall(fragment_pattern, citation)
    if not found_fragments and fragments:
        found_fragments = [f.replace('Fragment-', '') for f in fragments if f.startswith('Fragment-')]
    
    # 构建标准格式
    if lang == 'en':
        # 英文格式：Author (Year). *Title*. Entry ID. Epoch XXX. Filed under: Fragment-XXX, Fragment-XXX.
        title_part = f"*{extracted_title}*" if extracted_title else f"*{title}*"
        citation_parts = [
            f"{author} ({year}).",
            title_part,
            f"Entry {entry_id}."
        ]
        
        if extracted_epoch:
            citation_parts.append(f"Epoch {extracted_epoch}.")
        
        if found_fragments:
            fragment_list = ', '.join([f"Fragment-{f}" for f in found_fragments])
            citation_parts.append(f"Filed under: {fragment_list}.")
        
        result = ' '.join(citation_parts)
        # 移除重复的 Epoch
        result = re.sub(r'Epoch\s+([A-Za-z0-9\-]+)\.\s*Epoch\s+\1\.', r'Epoch \1.', result)
        return result
    
    else:  # zh
        # 中文格式：作者(年份). <标题>. 語螺語研究登錄項:ID．紀錄碎片:Fragment-XXX, Fragment-XXX;紀元:XXX．
        title_part = f"<{extracted_title}>" if extracted_title else f"<{title}>"
        # 规范化作者格式（确保有空格）
        author_formatted = author.strip()
        if not author_formatted.endswith(' '):
            author_formatted += ' '
        
        citation_parts = [
            f"{author_formatted}({year}).",
            f"{title_part}.",
            f"語螺語研究登錄項:{entry_id}．"
        ]
        
        if found_fragments:
            fragment_list = ', '.join([f"Fragment-{f}" for f in found_fragments])
            citation_parts.append(f"紀錄碎片:{fragment_list}")
        
        if extracted_epoch:
            if found_fragments:
                citation_parts[-1] += f";紀元:{extracted_epoch}．"
            else:
                citation_parts.append(f"紀元:{extracted_epoch}．")
        else:
            if found_fragments:
                citation_parts[-1] += "．"
        
        result = ''.join(citation_parts)
        # 规范化空格
        result = re.sub(r'\s+', ' ', result)
        result = re.sub(r'\.\s*\.', '.', result)
        return result


def parse_fragments(fragments_str: str) -> List[str]:
    """解析 fragments，返回数组"""
    if not fragments_str:
        return []
    
    # 分割：逗号、空格
    parts = re.split(r'[,\s]+', fragments_str)
    return [p.strip() for p in parts if p.strip()]


def parse_scope(scope_str: str) -> List[str]:
    """
    解析 scope：可能是数组（每行一个 - 开头）或字符串
    统一返回数组
    """
    if not scope_str:
        return []
    
    lines = scope_str.strip().split('\n')
    items = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 移除列表标记
        if line.startswith('- '):
            line = line[2:].strip()
        elif line.startswith('• '):
            line = line[2:].strip()
        
        if line:
            items.append(line)
    
    # 如果没有找到列表项，整个作为单个项
    if not items:
        items = [scope_str.strip()]
    
    return items


def parse_authors(author_str: str) -> List[str]:
    """解析作者：支持 × 分隔"""
    if not author_str:
        return []
    
    # 分割：×, ,, |
    parts = re.split(r'[×,|]+', author_str)
    return [p.strip() for p in parts if p.strip()]


def parse_domains(category_str: str) -> List[str]:
    """解析分类/域：支持 / 分隔"""
    if not category_str:
        return []
    
    parts = category_str.split('/')
    return [p.strip() for p in parts if p.strip()]


def parse_epoch(epoch_str: str) -> Tuple[str, int]:
    """
    解析纪元：返回 (label, order)
    order 从 label 中提取数字部分用于排序
    """
    if not epoch_str:
        return ("", 0)
    
    epoch_str = epoch_str.strip()
    
    # 提取数字部分作为 order
    num_match = re.search(r'(\d+)', epoch_str)
    order = int(num_match.group(1)) if num_match else 0
    
    return (epoch_str, order)


def parse_layer_header(line: str) -> Optional[str]:
    """
    解析层标题：接受多种变体
    [+Layer: X], [Layer: X], [ Layer : X ]
    """
    patterns = [
        r'^\[\+Layer:\s*(.+?)\]$',
        r'^\[Layer:\s*(.+?)\]$',
        r'^\[\s*Layer\s*:\s*(.+?)\s*\]$',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, line.strip())
        if match:
            return match.group(1).strip()
    
    return None


def parse_txt_file(filepath: Path, should_sanitize: bool = True) -> Dict[str, Any]:
    """
    解析单个 TXT 文件，返回卡片对象（未完全规范化）
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    block = {}
    current_key = None
    buffer = []
    layers = []
    current_layer = None
    
    for line in lines:
        # 检查是否是层标题
        layer_name = parse_layer_header(line)
        if layer_name:
            # 保存当前块
            if current_key:
                block[current_key] = '\n'.join(buffer).strip()
                current_key = None
                buffer = []
            
            # 开始新层
            current_layer = {
                'name': layer_name,
                'content': ''
            }
            layers.append(current_layer)
            continue
        
        # 检查是否是标准键值对 [Key] value
        match = re.match(r'^\[(.*?)\]\s*(.*)$', line)
        if match:
            # 保存之前的块
            if current_key:
                block[current_key] = '\n'.join(buffer).strip()
            
            current_key = match.group(1).strip()
            buffer = [match.group(2)]
            current_layer = None  # 退出层模式
        else:
            # 追加到当前缓冲区
            if current_layer:
                current_layer['content'] += line + '\n'
            elif current_key:
                buffer.append(line)
    
    # 保存最后一个块
    if current_key:
        block[current_key] = '\n'.join(buffer).strip()
    
    # 提取基本信息
    card_id = block.get('ID', '').strip()
    title_raw = block.get('Title', '').strip()
    # ✅ 规范化 title 格式
    title = normalize_title(title_raw)
    category = block.get('Category', '').strip()
    author = block.get('Author', '').strip()
    epoch_str = block.get('Epoch', '').strip()
    weight_str = block.get('Weight', '').strip()
    
    # 解析并清理文本字段
    abstract = sanitize_text(block.get('Abstract', ''), should_sanitize)
    scope = block.get('Scope', '')
    citation_raw = block.get('Citation', '').strip()
    fragments_str = block.get('Fragments', '')
    tags_str = block.get('Tags', '')
    
    # ✅ 支持额外字段（ResearchQuestion, Method, Modules）
    research_question = sanitize_text(block.get('ResearchQuestion', ''), should_sanitize)
    method = sanitize_text(block.get('Method', ''), should_sanitize)
    modules_str = block.get('Modules', '').strip()
    
    # 解析数组字段
    scope_list = parse_scope(scope)
    if should_sanitize:
        scope_list = [sanitize_text(s, True) for s in scope_list]
    
    fragments_list = parse_fragments(fragments_str)
    tags_list = parse_tags(tags_str)
    authors_list = parse_authors(author)
    domains_list = parse_domains(category)
    
    # 解析 Modules（类似 authors）
    modules_list = parse_authors(modules_str) if modules_str else []
    
    # 解析 epoch 和 weight
    epoch_label, epoch_order = parse_epoch(epoch_str)
    weight = parse_weight(weight_str)
    
    # 应用标点清理（如果启用）
    citation = sanitize_text(citation_raw, should_sanitize) if citation_raw else ''
    
    # 处理 layers
    normalized_layers = []
    for layer in layers:
        layer_content = sanitize_text(layer['content'].strip(), should_sanitize)
        normalized_layers.append({
            'name': layer['name'],
            'blocks': [
                {
                    'kind': 'markdown',
                    'text': layer_content
                }
            ]
        })
    
    return {
        'raw_id': card_id,
        'raw_title': title,
        'raw_epoch': epoch_str,
        'raw_weight': weight_str,
        'abstract': abstract,
        'scope': scope_list,
        'citation': citation,
        'fragments': fragments_list,
        'tags': tags_list,
        'authors': authors_list,
        'domains': domains_list,
        'epoch_label': epoch_label,
        'epoch_order': epoch_order,
        'weight': weight,
        'layers': normalized_layers,
        'research_question': research_question,
        'method': method,
        'modules': modules_list,
        'legacy_txt': filepath.name
    }


# ============================================================================
# 规范化：转换为 SSOT schema
# ============================================================================

def normalize_to_schema(parsed: Dict[str, Any], lang: str) -> Dict[str, Any]:
    """
    将解析结果规范化为完整的 Spiral Card Schema v1.0
    """
    raw_id = parsed['raw_id']
    raw_title = parsed['raw_title']
    
    # 生成 glyph（从 ID 提取，去除语言后缀）
    glyph = raw_id.strip()
    
    # 生成 id（glyph + lang）
    card_id = f"{glyph}-{lang}"
    
    # 推断 kind（从文件名或内容推断，默认 research）
    kind = "research"  # 默认，可以根据需要增强推断逻辑
    
    # 构建完整卡片对象
    card = {
        'glyph': glyph,
        'id': card_id,
        'lang': lang,
        'kind': kind,
        'epoch': {
            'label': parsed['epoch_label'],
            'order': parsed['epoch_order']
        },
        'weight': parsed['weight'],
        'title': parsed['raw_title'],
        'authors': parsed['authors'],
        'domains': parsed['domains'],
        'tags': parsed['tags'],
        'abstract': parsed['abstract'],
        'scope': parsed['scope'],
        'citation': normalize_citation(
            parsed['citation'], 
            lang, 
            card_id, 
            parsed['raw_title'], 
            parsed['epoch_label'], 
            parsed['fragments']
        ),
        'fragments': parsed['fragments'],
        'layers': parsed['layers'],
        'echo': [],  # 初始为空，未来可扩展
        'observation': {
            'visibility': 'public',
            'featured': False,
            'suppress': []
        },
        'seal': {},  # 初始为空，未来可扩展
        'origin': {
            'legacy_txt': parsed['legacy_txt'],
            'migrated_at': datetime.now().strftime('%Y-%m-%d')
        }
    }
    
    # ✅ 添加额外字段（如果存在）
    if parsed.get('research_question'):
        card['research_question'] = parsed['research_question']
    if parsed.get('method'):
        card['method'] = parsed['method']
    if parsed.get('modules'):
        card['modules'] = parsed['modules']
    
    return card


# ============================================================================
# 验证
# ============================================================================

class ValidationError(Exception):
    pass


def validate_card(card: Dict[str, Any], all_cards: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    """
    验证单个卡片
    返回 (errors, warnings)
    """
    errors = []
    warnings = []
    
    # 必需字段检查
    required_fields = ['glyph', 'id', 'lang', 'kind', 'title', 'epoch', 'weight']
    for field in required_fields:
        if field not in card or not card[field]:
            errors.append(f"Missing required field: {field}")
    
    # weight 范围检查
    if 'weight' in card:
        if not (1 <= card['weight'] <= 5):
            errors.append(f"weight must be 1-5, got {card['weight']}")
    
    # 重复 id 检查
    if 'id' in card:
        duplicates = [c for c in all_cards if c.get('id') == card['id']]
        if len(duplicates) > 1:
            errors.append(f"Duplicate id: {card['id']}")
    
    # 重复 (glyph, lang) 检查
    if 'glyph' in card and 'lang' in card:
        duplicates = [
            c for c in all_cards
            if c.get('glyph') == card['glyph'] and c.get('lang') == card['lang']
        ]
        if len(duplicates) > 1:
            errors.append(f"Duplicate (glyph, lang): ({card['glyph']}, {card['lang']})")
    
    # 警告：空字段
    if not card.get('tags'):
        warnings.append("Empty tags")
    if not card.get('fragments'):
        warnings.append("Empty fragments")
    if not card.get('citation'):
        warnings.append("Empty citation")
    
    return errors, warnings


# ============================================================================
# 主生成器
# ============================================================================

def build_registry(
    registry_dir: Path,
    output_dir: Path,
    should_sanitize: bool = True,
    languages: List[str] = ['zh', 'en']
) -> Dict[str, Any]:
    """
    构建注册表
    返回报告数据
    """
    all_cards = []
    invalid_cards = []
    per_card_warnings = {}
    
    for lang in languages:
        lang_dir = registry_dir / lang
        index_file = lang_dir / 'index.txt'
        
        if not index_file.exists():
            print(f"⚠️  Warning: {index_file} not found, skipping {lang}")
            continue
        
        # 读取文件列表
        with open(index_file, 'r', encoding='utf-8') as f:
            file_list = [line.strip() for line in f if line.strip()]
        
        print(f"📖 Processing {len(file_list)} files for {lang}...")
        
        for filename in file_list:
            filepath = lang_dir / filename
            
            if not filepath.exists():
                print(f"⚠️  Warning: {filepath} not found, skipping")
                continue
            
            try:
                # 解析
                parsed = parse_txt_file(filepath, should_sanitize)
                
                # 规范化
                card = normalize_to_schema(parsed, lang)
                
                # 验证
                errors, warnings = validate_card(card, all_cards)
                
                if errors:
                    invalid_cards.append({
                        'id': card.get('id', 'unknown'),
                        'errors': errors,
                        'card': card
                    })
                    print(f"❌ Invalid card: {card.get('id')} - {', '.join(errors)}")
                else:
                    all_cards.append(card)
                    if warnings:
                        per_card_warnings[card['id']] = warnings
                    print(f"✅ Processed: {card['id']}")
            
            except Exception as e:
                print(f"❌ Error processing {filepath}: {e}")
                invalid_cards.append({
                    'id': filename,
                    'errors': [str(e)],
                    'card': None
                })
    
    # 生成报告
    report = {
        'total_cards': len(all_cards),
        'invalid_cards': len(invalid_cards),
        'invalid_details': invalid_cards,
        'warnings': per_card_warnings,
        'duplicates': []  # 已在验证中处理
    }
    
    # 写入 JSON 文件（按语言分组）
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for lang in languages:
        lang_cards = [c for c in all_cards if c.get('lang') == lang]
        
        # 排序：按 epoch.order, 然后按 glyph
        lang_cards.sort(key=lambda c: (c['epoch']['order'], c['glyph']))
        
        output_file = output_dir / 'registry' / lang / 'cards.json'
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(lang_cards, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Wrote {len(lang_cards)} cards to {output_file}")
    
    return report


def write_reports(report: Dict[str, Any], output_dir: Path):
    """写入报告文件"""
    reports_dir = output_dir / 'reports'
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # JSON 报告
    json_report = {
        'total_cards': report['total_cards'],
        'invalid_cards': report['invalid_cards'],
        'invalid_details': report['invalid_details'],
        'warnings': report['warnings']
    }
    
    with open(reports_dir / 'registry-validate.json', 'w', encoding='utf-8') as f:
        json.dump(json_report, f, ensure_ascii=False, indent=2)
    
    # Markdown 报告
    md_lines = [
        "# Spiral Registry Validation Report",
        "",
        f"**Total Cards**: {report['total_cards']}",
        f"**Invalid Cards**: {report['invalid_cards']}",
        "",
        "## Invalid Cards",
        ""
    ]
    
    if report['invalid_details']:
        for item in report['invalid_details']:
            md_lines.append(f"### {item['id']}")
            md_lines.append("**Errors:**")
            for error in item['errors']:
                md_lines.append(f"- {error}")
            md_lines.append("")
    else:
        md_lines.append("✅ No invalid cards found.")
        md_lines.append("")
    
    md_lines.append("## Warnings")
    md_lines.append("")
    
    if report['warnings']:
        for card_id, warnings in report['warnings'].items():
            md_lines.append(f"### {card_id}")
            for warning in warnings:
                md_lines.append(f"- {warning}")
            md_lines.append("")
    else:
        md_lines.append("✅ No warnings.")
        md_lines.append("")
    
    with open(reports_dir / 'registry-validate.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    
    print(f"📊 Reports written to {reports_dir}")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Spiral Registry Builder v2')
    parser.add_argument(
        '--registry-dir',
        type=Path,
        default=Path('registry'),
        help='Registry directory (default: registry)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('.'),
        help='Output directory (default: . (project root))'
    )
    parser.add_argument(
        '--no-sanitize',
        action='store_true',
        help='Disable punctuation sanitization'
    )
    parser.add_argument(
        '--langs',
        nargs='+',
        default=['zh', 'en'],
        help='Languages to process (default: zh en)'
    )
    
    args = parser.parse_args()
    
    should_sanitize = not args.no_sanitize
    
    print("🜂 Spiral Registry Builder v2")
    print(f"📁 Registry: {args.registry_dir}")
    print(f"📤 Output: {args.output_dir}")
    print(f"🧹 Sanitize: {should_sanitize}")
    print("")
    
    # 构建
    report = build_registry(
        args.registry_dir,
        args.output_dir,
        should_sanitize,
        args.langs
    )
    
    # 写入报告
    write_reports(report, args.output_dir)
    
    # 退出码
    if report['invalid_cards'] > 0:
        print(f"\n❌ Build failed: {report['invalid_cards']} invalid cards")
        exit(1)
    else:
        print(f"\n✅ Build successful: {report['total_cards']} cards")
        exit(0)


if __name__ == '__main__':
    main()

