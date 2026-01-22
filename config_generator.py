#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地址格式配置生成器
支持自定义前缀、后缀、前后位数
"""

import re
import os

def hex_string_to_bytes(hex_str):
    """
    将十六进制字符串转换为字节列表
    支持带或不带 0x 前缀
    """
    hex_str = hex_str.replace('0x', '').replace(' ', '').lower()
    if not all(c in '0123456789abcdef' for c in hex_str):
        raise ValueError(f"无效的十六进制字符串: {hex_str}")
    
    # 补齐到偶数长度
    if len(hex_str) % 2 == 1:
        hex_str = '0' + hex_str
    
    bytes_list = []
    for i in range(0, len(hex_str), 2):
        bytes_list.append(int(hex_str[i:i+2], 16))
    
    return bytes_list

def generate_matching_code(prefix_hex="", suffix_hex="", prefix_len=0, suffix_len=0):
    """
    生成 OpenCL 匹配代码
    
    参数:
    - prefix_hex: 前缀十六进制字符串（如 "dac" 或 "0000"）
    - suffix_hex: 后缀十六进制字符串（如 "31ec7" 或 "1234"）
    - prefix_len: 前缀字符数（如果指定，会匹配前N个字符，忽略大小写）
    - suffix_len: 后缀字符数（如果指定，会匹配后N个字符，忽略大小写）
    
    返回: OpenCL 代码字符串
    """
    prefix_conditions = []
    suffix_conditions = []
    
    # 处理前缀匹配
    if prefix_hex:
        prefix_clean = prefix_hex.replace('0x', '').replace(' ', '').lower()
        prefix_len_actual = len(prefix_clean)
        
        # 处理完整字节
        full_bytes = prefix_len_actual // 2
        for i in range(full_bytes):
            byte_val = int(prefix_clean[i*2:(i+1)*2], 16)
            prefix_conditions.append(f"(hash[{i}] == 0x{byte_val:02x})")
        
        # 处理最后一个半字节（如果有）
        if prefix_len_actual % 2 == 1:
            nibble = int(prefix_clean[-1], 16)
            byte_index = full_bytes
            prefix_conditions.append(f"((hash[{byte_index}] & 0xF0) == 0x{nibble << 4:02x})")
    
    # 处理后缀匹配
    if suffix_hex:
        suffix_clean = suffix_hex.replace('0x', '').replace(' ', '').lower()
        suffix_len_actual = len(suffix_clean)
        
        # 计算起始字节索引（从地址末尾开始）
        # 以太坊地址是40个十六进制字符 = 20个字节
        # 如果后缀是5个字符，需要匹配最后2.5个字节
        full_bytes = suffix_len_actual // 2
        start_byte = 20 - full_bytes - (1 if suffix_len_actual % 2 == 1 else 0)
        
        # 处理第一个半字节（如果有奇数个字符）
        if suffix_len_actual % 2 == 1:
            nibble = int(suffix_clean[0], 16)
            suffix_conditions.append(f"((hash[{start_byte}] & 0x0F) == 0x{nibble:02x})")
            byte_offset = 1
        else:
            byte_offset = 0
        
        # 处理完整字节
        for i in range(full_bytes):
            byte_index = start_byte + byte_offset + i
            hex_start = (suffix_len_actual % 2) + i * 2
            byte_val = int(suffix_clean[hex_start:hex_start+2], 16)
            suffix_conditions.append(f"(hash[{byte_index}] == 0x{byte_val:02x})")
    
    # 生成匹配代码
    if prefix_conditions and suffix_conditions:
        code = "    bool match_prefix = " + " && ".join(prefix_conditions) + ";\n"
        code += "    bool match_suffix = " + " && ".join(suffix_conditions) + ";\n"
        code += "    if (match_prefix && match_suffix) {\n"
        code += "        profanity_result_update(id, hash, pResult, 20, scoreMax);\n"
        code += "    }\n"
    elif prefix_conditions:
        code = "    bool match_prefix = " + " && ".join(prefix_conditions) + ";\n"
        code += "    if (match_prefix) {\n"
        code += "        profanity_result_update(id, hash, pResult, 20, scoreMax);\n"
        code += "    }\n"
    elif suffix_conditions:
        code = "    bool match_suffix = " + " && ".join(suffix_conditions) + ";\n"
        code += "    if (match_suffix) {\n"
        code += "        profanity_result_update(id, hash, pResult, 20, scoreMax);\n"
        code += "    }\n"
    else:
        raise ValueError("必须指定前缀或后缀")
    
    return code

def generate_matrix_cl(prefix_hex="", suffix_hex="", prefix_len=0, suffix_len=0, template_file="matrix.cl"):
    """
    根据配置生成新的 matrix.cl 文件
    
    参数:
    - prefix_hex: 前缀十六进制字符串
    - suffix_hex: 后缀十六进制字符串
    - prefix_len: 前缀字符数（如果指定，会匹配前N个字符）
    - suffix_len: 后缀字符数（如果指定，会匹配后N个字符）
    - template_file: 模板文件路径
    """
    # 读取模板文件
    if not os.path.exists(template_file):
        raise FileNotFoundError(f"模板文件不存在: {template_file}")
    
    with open(template_file, 'r') as f:
        content = f.read()
    
    # 生成匹配代码
    matching_code = generate_matching_code(prefix_hex, suffix_hex, prefix_len, suffix_len)
    
    # 找到 profanity_score_matching 函数并替换
    start_sig = "__kernel void profanity_score_matching"
    end_sig = "__kernel void profanity_score_leading"
    
    start_idx = content.find(start_sig)
    end_idx = content.find(end_sig)
    
    if start_idx == -1 or end_idx == -1:
        raise ValueError("无法找到 profanity_score_matching 函数")
    
    # 提取函数签名和参数
    func_start = content.find('{', start_idx)
    if func_start == -1:
        raise ValueError("无法找到函数体开始")
    
    # 构建新函数
    func_signature = content[start_idx:func_start+1]
    new_function = func_signature + "\n"
    new_function += "    const size_t id = get_global_id(0);\n"
    new_function += "    __global const uchar * const hash = pInverse[id].d;\n\n"
    new_function += "    // --- [Dynamic Matching Patch] ---\n"
    new_function += "    // 前缀: " + (prefix_hex or f"前{prefix_len}位") + "\n"
    new_function += "    // 后缀: " + (suffix_hex or f"后{suffix_len}位") + "\n"
    new_function += matching_code
    new_function += "    // --- [End Patch] ---\n"
    new_function += "}\n"
    
    # 替换原函数
    new_content = content[:start_idx] + new_function + content[end_idx:]
    
    return new_content

def parse_address_pattern(pattern):
    """
    解析地址模式字符串
    支持格式：
    - "0x0000...1234" (前缀和后缀)
    - "0x0000" (只有前缀)
    - "...1234" (只有后缀)
    - "前4位:0000,后4位:1234" (明确指定)
    
    返回: (prefix_hex, suffix_hex, prefix_len, suffix_len)
    """
    prefix_hex = ""
    suffix_hex = ""
    prefix_len = 0
    suffix_len = 0
    
    # 移除 0x 前缀（如果有）
    pattern = pattern.replace('0x', '').replace('0X', '')
    
    # 检查是否包含 ...
    if '...' in pattern:
        parts = pattern.split('...')
        if len(parts) == 2:
            prefix_hex = parts[0].strip()
            suffix_hex = parts[1].strip()
        elif len(parts) == 1:
            if pattern.startswith('...'):
                suffix_hex = parts[0].strip()
            else:
                prefix_hex = parts[0].strip()
    else:
        # 没有 ...，可能是完整地址或只有前缀
        prefix_hex = pattern.strip()
    
    return prefix_hex, suffix_hex, prefix_len, suffix_len

if __name__ == "__main__":
    # 测试
    prefix = "dac"
    suffix = "31ec7"
    code = generate_matching_code(prefix, suffix)
    print("生成的匹配代码:")
    print(code)
