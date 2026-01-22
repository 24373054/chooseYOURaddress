# verify.py
from eth_account import Account

# 你的最终私钥
priv_key = "0xb9bc50............6a88807de96503eae8af7e"

try:
    # 从私钥推导账户
    acct = Account.from_key(priv_key)
    
    print("\n" + "="*50)
    print("✅ 验证结果：")
    print(f"🔑 私钥: {priv_key}")
    print(f"🏠 地址: {acct.address}")
    print("="*50)
    
    # 自动检查是不是我们要的 31ec7
    if acct.address.lower().endswith("31ec7") and acct.address.lower().startswith("0xdac"):
        print("🎉 完美！这就是你要的【dac...31ec7】靓号！")
    else:
        print("🤔 好像有点不对？请检查之前的步骤。")
        
except Exception as e:
    print(f"❌ 发生错误: {e}")