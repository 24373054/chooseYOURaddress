import os

file_path = "profanity.cpp"

with open(file_path, "r") as f:
    content = f.read()

# 1. 阉割二进制缓存加载逻辑 (强制它认为没有缓存)
# 查找: if (vDeviceBinary.size() == vDevices.size())
# 替换: if (false)
target_if = "if (vDeviceBinary.size() == vDevices.size())"
replace_if = "if (false)"

# 2. 修正内核源码读取路径 (配合你之前的 mv 操作)
# 查找: readFile("profanity.cl")
# 替换: readFile("matrix.cl")
target_read = 'readFile("profanity.cl")'
replace_read = 'readFile("matrix.cl")'

new_content = content

# 执行替换
if target_if in new_content:
    new_content = new_content.replace(target_if, replace_if)
    print("✅ 成功禁用二进制缓存加载！(if -> false)")
else:
    print("⚠️ 警告：未找到缓存加载判断语句，可能代码已修改。")

if target_read in new_content:
    new_content = new_content.replace(target_read, replace_read)
    print("✅ 成功将源码路径指向 matrix.cl！")
else:
    print("ℹ️ 源码路径无需修改 (可能已经是 matrix.cl)。")

# 写入文件
with open(file_path, "w") as f:
    f.write(new_content)
