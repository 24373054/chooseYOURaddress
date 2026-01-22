import hexbytes

# ================= 填空区 (请务必填对) =================

# 1. 填入最开始 gen.py 生成的【基准私钥】(Base Private Key)
# 也就是你刚才保存在哪里的一长串字符
base_priv_hex = "0xb9b.........48c3ba3273ba198afd738f04" 

# 2. 填入 GPU 刚刚跑出来的【Private】(Offset)
# 就是 Score: 20 那一行显示的 Private
gpu_result_hex = "0x0000b502...........0a2f4b78ed75207a"

# 3. (可选) 填入 GPU 显示的【目标地址】
# 用来最后肉眼比对一下
target_address = "0xdac2..........bd6615f4b5a731ec7"

# ======================================================

def calc_final():
    try:
        # 以太坊椭圆曲线的阶 (N)
        curve_order = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        
        # 转换 16 进制字符串为大整数
        base_int = int(base_priv_hex, 16)
        gpu_int = int(gpu_result_hex, 16)
        
        # 核心融合：最终私钥 = (基准 + 偏移) % N
        final_int = (base_int + gpu_int) % curve_order
        
        # 转回 16 进制字符串 (去掉 0x, 补齐 64 位)
        final_hex = hex(final_int)[2:].zfill(64)
        
        print("\n" + "="*60)
        print("💎 任务完成！MISSION ACCOMPLISHED")
        print("="*60)
        print(f"🎯 目标地址: {target_address}")
        print("-" * 60)
        print(f"🔑 最终私钥: 0x{final_hex}")
        print("-" * 60)
        print("⚠️  安全警告: 请立即备份并删除此服务器上的所有脚本和日志！")
        print("="*60 + "\n")

        # 生成验证命令建议
        print("💡 验证方法 (如果你装了 cast):")
        print(f"cast wallet address --private-key 0x{final_hex}")
        
    except Exception as e:
        print(f"❌ 计算出错，请检查填写的格式是否正确 (比如是否漏了引号): {e}")

if __name__ == "__main__":
    calc_final()