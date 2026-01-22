import hexbytes
import json
import os

def calc_final():
    try:
        # 自动从文件读取数据
        if not os.path.exists("key_data.json"):
            print("❌ 错误：找不到 key_data.json，请先运行 2.py")
            return
        
        if not os.path.exists("gpu_result.json"):
            print("❌ 错误：找不到 gpu_result.json，GPU 尚未找到结果")
            return
        
        # 读取基准私钥
        with open("key_data.json", "r") as f:
            key_data = json.load(f)
            base_priv_hex = key_data["base_private_key"]
        
        # 读取GPU结果
        with open("gpu_result.json", "r") as f:
            gpu_data = json.load(f)
            gpu_result_hex = gpu_data["private_key"]
            target_address = gpu_data.get("address", "未知")
        
        # 以太坊椭圆曲线的阶 (N)
        curve_order = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        
        # 转换 16 进制字符串为大整数
        base_int = int(base_priv_hex, 16)
        gpu_int = int(gpu_result_hex, 16)
        
        # 核心融合：最终私钥 = (基准 + 偏移) % N
        final_int = (base_int + gpu_int) % curve_order
        
        # 转回 16 进制字符串 (去掉 0x, 补齐 64 位)
        final_hex = hex(final_int)[2:].zfill(64)
        
        # 保存最终结果
        final_data = {
            "final_private_key": f"0x{final_hex}",
            "target_address": target_address,
            "base_private_key": base_priv_hex,
            "gpu_offset": gpu_result_hex
        }
        with open("final_result.json", "w") as f:
            json.dump(final_data, f, indent=2)
        
        print("\n" + "="*60)
        print("💎 任务完成！MISSION ACCOMPLISHED")
        print("="*60)
        print(f"🎯 目标地址: {target_address}")
        print("-" * 60)
        print(f"🔑 最终私钥: 0x{final_hex}")
        print("-" * 60)
        print("✅ 结果已保存到 final_result.json")
        print("⚠️  安全警告: 请立即备份并删除此服务器上的所有脚本和日志！")
        print("="*60 + "\n")

        # 生成验证命令建议
        print("💡 验证方法 (如果你装了 cast):")
        print(f"cast wallet address --private-key 0x{final_hex}")
        
    except Exception as e:
        print(f"❌ 计算出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    calc_final()