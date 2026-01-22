import os

file_path = "profanity.cl"

# 新的内核函数代码：只找 31ec7，找到给 20 分，否则给 0 分
new_kernel_logic = """
__kernel void profanity_score_matching(__global mp_number * const pInverse, __global result * const pResult, __constant const uchar * const data1, __constant const uchar * const data2, const uchar scoreMax) {
    const size_t id = get_global_id(0);
    __global const uchar * const hash = pInverse[id].d;

    // --- [Matrix Final Patch] ---
    // 目标后缀: 31ec7
    // hash[19]=0xc7, hash[18]=0x1e, hash[17]低4位=0x03
    if (hash[19] == 0xc7 && hash[18] == 0x1e && (hash[17] & 0x0F) == 0x03) {
        // 命中目标！强制上报 Score=20 (满分)
        // 这样 C++ 端一定会把它打印出来
        profanity_result_update(id, hash, pResult, 20, scoreMax);
    }
    // 未命中？直接结束，Score 默认为 0，CPU 不会收到任何垃圾信息
}
"""

with open(file_path, "r") as f:
    content = f.read()

# 定位原始函数的头部
start_sig = "__kernel void profanity_score_matching"
# 定位下一个函数的头部（作为结束标记）
end_sig = "__kernel void profanity_score_leading"

start_idx = content.find(start_sig)
end_idx = content.find(end_sig)

if start_idx != -1 and end_idx != -1:
    # 保留头部之前和尾部之后的内容，中间替换成我们的新逻辑
    new_content = content[:start_idx] + new_kernel_logic + "\n" + content[end_idx:]
    
    with open(file_path, "w") as f:
        f.write(new_content)
    print("✅ 成功！显卡内核已修改为【只输出 31ec7】模式。")
else:
    print("❌ 定位失败，请手动修改 profanity.cl")
