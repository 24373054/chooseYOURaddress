#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键运行脚本 - 自动化生成 0xdAC 开头 31eC7 结尾的地址及其私钥
"""

import os
import sys
import json
import subprocess
import re
import shutil
import time

def print_step(step_num, description):
    """打印步骤信息"""
    print("\n" + "="*60)
    print(f"步骤 {step_num}: {description}")
    print("="*60)

def run_step1():
    """步骤1: 生成基准密钥"""
    print_step(1, "生成基准私钥和公钥")
    
    if not os.path.exists("2.py"):
        print("❌ 错误：找不到 2.py")
        return False, None
    
    try:
        result = subprocess.run([sys.executable, "2.py"], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        print(result.stdout)
        
        if not os.path.exists("key_data.json"):
            print("❌ 错误：2.py 未生成 key_data.json")
            return False, None
        
        # 读取生成的密钥
        with open("key_data.json", "r") as f:
            key_data = json.load(f)
        
        print(f"✅ 基准私钥已生成: {key_data['base_private_key'][:20]}...")
        print(f"✅ 基准公钥已生成: {key_data['base_public_key'][:40]}...")
        return True, key_data
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 运行 2.py 失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False, None
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False, None

def ensure_profanity_cl():
    """确保 profanity.cl 文件存在"""
    if os.path.exists("profanity.cl"):
        print("✅ profanity.cl 已存在")
        return True
    
    if os.path.exists("matrix.cl"):
        print("📋 从 matrix.cl 创建 profanity.cl...")
        shutil.copy("matrix.cl", "profanity.cl")
        print("✅ profanity.cl 已创建")
        return True
    
    print("❌ 错误：找不到 matrix.cl 或 profanity.cl")
    return False

def run_step2(key_data):
    """步骤2: 运行 GPU 搜索"""
    print_step(2, "运行 GPU 搜索 (这可能需要较长时间...)")
    
    if not os.path.exists("profanity2.x64"):
        print("❌ 错误：找不到 profanity2.x64")
        return False, None
    
    if not os.access("profanity2.x64", os.X_OK):
        print("⚠️  警告：profanity2.x64 没有执行权限，尝试添加...")
        os.chmod("profanity2.x64", 0o755)
    
    public_key = key_data["base_public_key"]
    
    # 构建命令
    cmd = [
        "CUDA_CACHE_DISABLE=1",
        "CL_CACHE_DISABLE=1",
        "./profanity2.x64",
        "--matching", "dac",
        "-z", public_key
    ]
    
    print(f"🚀 启动 GPU 搜索...")
    print(f"📝 命令: {' '.join(cmd[2:])}")  # 不显示环境变量
    print("⏳ 正在搜索，请耐心等待...")
    print("   (找到结果后会自动继续下一步)\n")
    
    try:
        # 使用 shell=True 来支持环境变量
        env = os.environ.copy()
        env["CUDA_CACHE_DISABLE"] = "1"
        env["CL_CACHE_DISABLE"] = "1"
        
        process = subprocess.Popen(
            ["./profanity2.x64", "--matching", "dac", "-z", public_key],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
            cwd=os.getcwd()
        )
        
        # 实时输出并解析结果
        gpu_result = None
        last_speed_time = 0
        speed_update_interval = 3  # 每3秒更新一次速度显示
        last_printed_speed = False  # 标记上次是否打印了速度信息
        
        for line in process.stdout:
            # 清理行内容：移除ANSI转义码、回车符等
            # 移除ANSI转义序列（如 \x1b[2K 用于清除行）
            line_clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', line)
            line_clean = line_clean.replace('\r', '').strip()
            
            # 过滤掉速度信息（减少刷屏）
            if "Total:" in line and "MH/s" in line:
                current_time = time.time()
                # 只每3秒显示一次速度
                if current_time - last_speed_time >= speed_update_interval:
                    # 使用 \r 覆盖显示，不换行
                    speed_display = line_clean.replace('\n', '')
                    print(f"\r⏳ {speed_display}", end='', flush=True)
                    last_speed_time = current_time
                    last_printed_speed = True
                continue
            
            # 跳过空行和只包含空白字符的行
            if not line_clean or line_clean.isspace():
                continue
            
            # 显示重要信息（非速度信息）
            # 如果之前打印了速度信息，先换行
            if last_printed_speed:
                print()  # 换行，避免与速度信息混在一起
                last_printed_speed = False
            
            # 打印重要信息（保留原始格式，但确保有内容）
            print(line.rstrip(), flush=True)
            
            # 解析输出格式: "  Time: Xs Score: Y Private: 0x... Address: 0x..."
            # 注意：Private 是64字符的十六进制（可能包含前导零），address 是40字符的十六进制
            # 匹配模式：Time: ... Score: ... Private: 0x... Address: 0x...
            
            # 首先尝试精确匹配
            match = re.search(
                r'Time:\s*\d+s\s+Score:\s*(\d+)\s+Private:\s*(0x[a-fA-F0-9]+)\s+Address:\s*(0x[a-fA-F0-9]{40})',
                line,
                re.IGNORECASE
            )
            
            # 如果上面的正则没匹配到，尝试更宽松的匹配（可能格式略有不同）
            if not match:
                match = re.search(
                    r'Score:\s*(\d+).*?Private:\s*(0x[a-fA-F0-9]+).*?(?:Address|matching):\s*(0x[a-fA-F0-9]{40})',
                    line,
                    re.IGNORECASE
                )
            
            # 如果还是没匹配到，尝试最简单的匹配
            if not match:
                match = re.search(
                    r'Score:\s*(\d+).*?Private:\s*(0x[a-fA-F0-9]+).*?0x([a-fA-F0-9]{40})',
                    line,
                    re.IGNORECASE
                )
            
            if match:
                score = int(match.group(1))
                private_key = match.group(2)
                address = match.group(3)
                
                # 确保 private_key 是64字符（补齐前导零）
                if private_key.startswith("0x"):
                    private_key = "0x" + private_key[2:].zfill(64)
                else:
                    private_key = "0x" + private_key.zfill(64)
                
                print(f"\n\n{'='*60}")
                print(f"🎉 找到目标结果！")
                print(f"{'='*60}")
                print(f"   分数: {score}")
                print(f"   地址: {address}")
                print(f"   偏移: {private_key}")
                print(f"{'='*60}\n")
                
                if score >= 20:  # 找到目标
                    gpu_result = {
                        "private_key": private_key,
                        "address": address,
                        "score": score
                    }
                    
                    # 保存结果
                    with open("gpu_result.json", "w") as f:
                        json.dump(gpu_result, f, indent=2)
                    
                    print("✅ 结果已保存到 gpu_result.json")
                    
                    # 终止进程
                    print("🛑 正在停止 GPU 搜索...")
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    
                    return True, gpu_result
                else:
                    print(f"⚠️  分数 {score} 低于阈值 20，继续搜索...")
        
        # 等待进程结束（如果还在运行）
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            # 进程还在运行，这不应该发生（应该在找到结果时已终止）
            process.terminate()
            process.wait()
        
        # 如果进程正常结束但没有找到结果
        if gpu_result is None:
            print("\n\n❌ GPU 搜索完成但未找到目标结果")
            print("   请检查 matrix.cl 中的匹配逻辑是否正确配置")
            return False, None
        
        return True, gpu_result
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断了 GPU 搜索")
        if 'process' in locals():
            try:
                process.terminate()
                process.wait(timeout=2)
            except:
                try:
                    process.kill()
                except:
                    pass
        return False, None
    except Exception as e:
        print(f"\n❌ GPU 搜索出错: {e}")
        import traceback
        traceback.print_exc()
        if 'process' in locals():
            try:
                process.terminate()
                process.wait(timeout=2)
            except:
                try:
                    process.kill()
                except:
                    pass
        return False, None

def run_step3():
    """步骤3: 计算最终私钥"""
    print_step(3, "计算最终私钥")
    
    if not os.path.exists("3.py"):
        print("❌ 错误：找不到 3.py")
        return False
    
    try:
        result = subprocess.run([sys.executable, "3.py"], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        print(result.stdout)
        
        if result.stderr:
            print("警告:", result.stderr)
        
        if not os.path.exists("final_result.json"):
            print("❌ 错误：3.py 未生成 final_result.json")
            return False
        
        print("✅ 最终私钥计算完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 运行 3.py 失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False

def run_step4():
    """步骤4: 验证最终结果"""
    print_step(4, "验证最终结果")
    
    if not os.path.exists("v.py"):
        print("❌ 错误：找不到 v.py")
        return False
    
    try:
        result = subprocess.run([sys.executable, "v.py"], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        print(result.stdout)
        
        if result.stderr:
            print("警告:", result.stderr)
        
        # 检查验证结果
        if "完美" in result.stdout or "🎉" in result.stdout:
            print("\n✅ 验证通过！")
            return True
        else:
            print("\n⚠️  验证可能有问题，请检查输出")
            return False
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 运行 v.py 失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False

def print_final_summary():
    """打印最终摘要"""
    print("\n" + "="*60)
    print("📋 最终结果摘要")
    print("="*60)
    
    if os.path.exists("final_result.json"):
        with open("final_result.json", "r") as f:
            result = json.load(f)
        
        print(f"\n🎯 目标地址: {result.get('target_address', '未知')}")
        print(f"🔑 最终私钥: {result.get('final_private_key', '未知')}")
        print(f"\n📁 所有结果已保存在以下文件中:")
        print(f"   - key_data.json (基准密钥)")
        print(f"   - gpu_result.json (GPU搜索结果)")
        print(f"   - final_result.json (最终结果)")
        print("\n⚠️  安全提示: 请立即备份私钥并删除服务器上的敏感文件！")
    else:
        print("❌ 未找到最终结果文件")
    
    print("="*60 + "\n")

def main():
    """主函数"""
    print("\n" + "🚀" * 30)
    print("   一键生成 0xdAC 开头 31eC7 结尾的地址及其私钥")
    print("🚀" * 30)
    
    # 检查必要文件
    required_files = ["2.py", "3.py", "v.py", "profanity2.x64"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ 错误：缺少必要文件: {', '.join(missing_files)}")
        return 1
    
    # 确保 profanity.cl 存在
    if not ensure_profanity_cl():
        return 1
    
    # 步骤1: 生成基准密钥
    success, key_data = run_step1()
    if not success or key_data is None:
        return 1
    
    # 步骤2: GPU 搜索
    success, gpu_result = run_step2(key_data)
    if not success or gpu_result is None:
        return 1
    
    # 步骤3: 计算最终私钥
    if not run_step3():
        return 1
    
    # 步骤4: 验证
    if not run_step4():
        return 1
    
    # 打印最终摘要
    print_final_summary()
    
    print("✅ 所有步骤完成！")
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断了程序")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
