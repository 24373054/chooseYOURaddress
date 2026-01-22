# gen.py - 生成基准钥匙
import os
import binascii
try:
    from coincurve import PublicKey
except ImportError:
    print("请先运行: pip install coincurve")
    exit()

# 1. 生成 32 字节的安全随机私钥
base_priv_bytes = os.urandom(32)
base_priv_hex = binascii.hexlify(base_priv_bytes).decode()

# 2. 推导公钥 (非压缩格式)
# Profanity2 需要 128 字符的公钥 (去掉开头的 04)
public_key_bytes = PublicKey.from_secret(base_priv_bytes).format(compressed=False)[1:]
public_key_hex = binascii.hexlify(public_key_bytes).decode()

print("\n" + "="*50)
print("🔑 第一步：保存好你的基准私钥 (千万别丢，别给别人看)")
print(f"基准私钥: 0x{base_priv_hex}")
print("-" * 50)
print("🖥️  第二步：把下面这个公钥复制到 GPU 命令的 -z 后面")
print(f"基准公钥: {public_key_hex}")
print("="*50 + "\n")