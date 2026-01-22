# patch_smart.py
import os

file_path = "profanity.cl"

# 我们修改 profanity_score_matching 函数
# 逻辑：
# 1. 让程序正常计算 dac 的分数 (score)
# 2. 额外检查 31ec7 后缀
# 3. 如果后缀不匹配，直接把 score 变成 0 (CPU就不会打印了)
# 4. 如果后缀匹配，保留高分，CPU 就会立刻打印

with open(file_path, "r") as f:
    content = f.read()

target_str = "profanity_result_update(id, hash, pResult, score, scoreMax);"

# 注入过滤逻辑：在提交结果前，先进行“死刑复核”
patch_code = """
    // --- [Smart Filter Patch] ---
    // 检查后缀: 31ec7
    // hash[19]=0xc7, hash[18]=0x1e, hash[17]低4位=0x03
    bool suffix_match = (hash[19] == 0xc7 && hash[18] == 0x1e && (hash[17] & 0x0F) == 0x03);
    
    if (!suffix_match) {
        score = 0; // 后缀不对，分数清零，不汇报！
    } else {
        score = 20; // 后缀对，强制满分，立即汇报！
    }
    // --- [End Patch] ---

    profanity_result_update(id, hash, pResult, score, scoreMax);
"""

if target_str in content:
    # 只替换 profanity_score_matching 里面的那一次调用
    # 为了保险，我们先找到函数体，再替换
    func_start = content.find("__kernel void profanity_score_matching")
    if func_start != -1:
        # 在函数范围内寻找替换点
        replace_idx = content.find(target_str, func_start)
        if replace_idx != -1:
            new_content = content[:replace_idx] + patch_code + content[replace_idx + len(target_str):]
            with open(file_path, "w") as f:
                f.write(new_content)
            print("✅ 智能过滤器已植入！显卡现在只输出 ...31ec7 的结果。")
        else:
            print("❌ 替换点定位失败。")
    else:
        print("❌ 函数定位失败。")
else:
    print("❌ 没找到 result_update 调用。")