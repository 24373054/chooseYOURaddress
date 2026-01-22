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
    
    # 从配置文件读取目标格式
    prefix_hex = ""
    suffix_hex = ""
    config_file = "address_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                prefix_hex = config.get('prefix_hex', '').lower()
                suffix_hex = config.get('suffix_hex', '').lower()
        except:
            pass
    
    # 验证地址格式
    address_lower = acct.address.lower().replace('0x', '')
    match = True
    match_details = []
    
    if prefix_hex:
        expected_prefix = prefix_hex.lower()
        actual_prefix = address_lower[:len(expected_prefix)]
        if actual_prefix == expected_prefix:
            match_details.append(f"✅ 前缀匹配: {expected_prefix}")
        else:
            match = False
            match_details.append(f"❌ 前缀不匹配: 期望 {expected_prefix}, 实际 {actual_prefix}")
    
    if suffix_hex:
        expected_suffix = suffix_hex.lower()
        actual_suffix = address_lower[-len(expected_suffix):]
        if actual_suffix == expected_suffix:
            match_details.append(f"✅ 后缀匹配: {expected_suffix}")
        else:
            match = False
            match_details.append(f"❌ 后缀不匹配: 期望 {expected_suffix}, 实际 {actual_suffix}")
    
    print("\n📋 格式验证:")
    for detail in match_details:
        print(f"   {detail}")
    
    if match:
        format_desc = f"{prefix_hex or ''}...{suffix_hex or ''}" if (prefix_hex and suffix_hex) else (prefix_hex or suffix_hex)
        print(f"\n🎉 完美！这就是你要的【{format_desc}】靓号！")
        
        # 如果GPU结果中有地址，也进行比对
        if expected_address and expected_address.lower() != acct.address.lower():
            print(f"⚠️  警告：GPU显示的地址 ({expected_address}) 与计算出的地址不匹配")
        elif expected_address:
            print(f"✅ 地址匹配：与GPU结果一致")
    else:
        print("\n🤔 格式验证失败，请检查之前的步骤。")
        print(f"   实际地址: {acct.address}")
        
except Exception as e:
    print(f"❌ 发生错误: {e}")
    import traceback
    traceback.print_exc()