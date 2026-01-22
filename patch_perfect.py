import os

# 注意：你之前改名成了 matrix.cl
file_path = "matrix.cl"

# 完美过滤逻辑：
# 1. 前缀 dac -> hash[0]=0xda, hash[1]的高4位=0xc
# 2. 后缀 31ec7 -> hash[19]=0xc7, hash[18]=0x1e, hash[17]低4位=0x03
perfect_kernel = """
__kernel void profanity_score_matching(__global mp_number * const pInverse, __global result * const pResult, __constant const uchar * const data1, __constant const uchar * const data2, const uchar scoreMax) {
    const size_t id = get_global_id(0);
    __global const uchar * const hash = pInverse[id].d;

    // --- [Matrix Perfect Patch] ---
    
    // 1. 检查前缀: dac (0xda, 0xc...)
    bool match_prefix = (hash[0] == 0xda) && ((hash[1] & 0xF0) == 0xc0);
    
    // 2. 检查后缀: 31ec7 (...3, 1e, c7)
    bool match_suffix = (hash[19] == 0xc7) && (hash[18] == 0x1e) && ((hash[17] & 0x0F) == 0x03);

    if (match_prefix && match_suffix) {
        // 只有前后都匹配，才给满分上报
        profanity_result_update(id, hash, pResult, 20, scoreMax);
    }
    
    // 其他情况直接丢弃，不给 CPU 任何负担
    // --- [End Patch] ---
}
"""

with open(file_path, "r") as f:
    content = f.read()

# 定位替换区域
start_sig = "__kernel void profanity_score_matching"
end_sig = "__kernel void profanity_score_leading"

start_idx = content.find(start_sig)
end_idx = content.find(end_sig)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + perfect_kernel + "\n" + content[end_idx:]
    with open(file_path, "w") as f:
        f.write(new_content)
    print("✅ 完美！内核已修改为【必须 dac 开头 且 31ec7 结尾】。")
else:
    print("❌ 文件定位失败，请检查 matrix.cl")
