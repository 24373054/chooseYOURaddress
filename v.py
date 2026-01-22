# verify.py
from eth_account import Account
import json
import os

try:
    # 自动从文件读取最终私钥
    if not os.path.exists("final_result.json"):
        print("❌ 错误：找不到 final_result.json，请先运行 3.py")
        exit(1)
    
    with open("final_result.json", "r") as f:
        result_data = json.load(f)
        priv_key = result_data["final_private_key"]
        expected_address = result_data.get("target_address", "")
    
    # 从私钥推导账户
    acct = Account.from_key(priv_key)
    
    print("\n" + "="*50)
    print("✅ 验证结果：")
    print(f"🔑 私钥: {priv_key}")
    print(f"🏠 地址: {acct.address}")
    print("="*50)
    
    # 自动检查是不是我们要的 31ec7
    address_lower = acct.address.lower()
    if address_lower.endswith("31ec7") and address_lower.startswith("0xdac"):
        print("🎉 完美！这就是你要的【dac...31ec7】靓号！")
        
        # 如果GPU结果中有地址，也进行比对
        if expected_address and expected_address.lower() != address_lower:
            print(f"⚠️  警告：GPU显示的地址 ({expected_address}) 与计算出的地址不匹配")
        elif expected_address:
            print(f"✅ 地址匹配：与GPU结果一致")
    else:
        print("🤔 好像有点不对？请检查之前的步骤。")
        print(f"   期望: 0xdac...31ec7")
        print(f"   实际: {acct.address}")
        
except Exception as e:
    print(f"❌ 发生错误: {e}")
    import traceback
    traceback.print_exc()