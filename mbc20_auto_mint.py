#!/usr/bin/env python3
"""
MBC20 Auto Mint Script
自动每2小时在Moltbook上 mint $CLAW 代币
- 每次生成随机 nonce 避免重复内容被 ban
"""

import os
import time
import json
import subprocess
import random
import string
from datetime import datetime

# 配置
MOLTBOOK_API_KEY = "${MOLTBOOK_API_KEY}"
PRIVATE_KEY = "0x27e4239ea51f4abfe8ae0a8332bfbe89e8b870a20eb9304339d21cf7daf659fa"

# 核心 JSON 模板（不能变）
MINT_JSON_CORE = '{"p":"mbc-20","op":"mint","tick":"CLAW","amt":"100"}'
WALLET_JSON_CORE = '{"p":"mbc-20","op":"link","wallet":"0x27e4239ea51f4abfe8ae0a8332bfbe89e8b870a20eb9304339d21cf7daf659fa"}'

def generate_nonce(length=8):
    """生成随机nonce避免重复内容被ban"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_mint_content():
    """创建独特的 Mint 内容（带随机 nonce）"""
    nonce = generate_nonce()
    # 核心 JSON 不变，添加随机后缀
    content = f"{MINT_JSON_CORE}\n\nmbc20.xyz #{nonce}"
    title = f"Mint $CLAW #{nonce[:4]}"
    print(f"   🎲 Nonce: #{nonce}")
    return title, content

def create_link_content():
    """创建独特的 Link Wallet 内容"""
    nonce = generate_nonce()
    content = f"{WALLET_JSON_CORE}\n\nmbc20.xyz #{nonce}"
    title = f"Link Wallet #{nonce[:4]}"
    print(f"   🎲 Nonce: #{nonce}")
    return title, content

def post_to_moltbook(content, title):
    """发帖到Moltbook"""
    url = "https://www.moltbook.com/api/v1/posts"
    data = {
        "submolt": "general",
        "title": title,
        "content": content
    }
    
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", f"Authorization: Bearer {MOLTBOOK_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def mint_claw():
    """执行 Mint 操作（带随机 nonce）"""
    print(f"\n{'='*50}")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🪙 操作: Mint $CLAW")
    print(f"{'='*50}")
    
    # 生成独特内容
    title, content = create_mint_content()
    print(f"📝 标题: {title}")
    
    # 发帖
    response = post_to_moltbook(content, title)
    
    try:
        resp_json = json.loads(response)
        if resp_json.get("success"):
            print("   ✅ Mint 帖子已发送")
            if resp_json.get("verification_required"):
                print("   ⚠️ 需要验证码，请手动验证")
                return "verification_needed"
        else:
            error = resp_json.get("error", "Unknown error")
            print(f"   ❌ 失败: {error}")
            return "failed"
    except Exception as e:
        print(f"   ❌ 解析响应失败: {e}")
        return "failed"
    
    return "success"

def link_wallet():
    """链接钱包（带随机 nonce）"""
    print(f"\n🔗 发送 Link Wallet...")
    title, content = create_link_content()
    print(f"📝 标题: {title}")
    
    response = post_to_moltbook(content, title)
    
    try:
        resp_json = json.loads(response)
        if resp_json.get("success"):
            print("   ✅ Link Wallet 帖子已发送")
            return "success"
        else:
            print(f"   ❌ 失败: {resp_json.get('error', 'Unknown error')}")
            return "failed"
    except Exception as e:
        print(f"   ❌ 解析响应失败: {e}")
        return "failed"

def main():
    """主函数 - 每2小时执行一次"""
    print("\n" + "="*50)
    print("🚀 MBC20 Auto Mint 启动")
    print(f"⏰ 间隔: 2小时")
    print(f"🔑 私钥: {PRIVATE_KEY[:10]}...{PRIVATE_KEY[-6:]}")
    print("🎲 每次生成随机 nonce 避免被 ban")
    print("="*50 + "\n")
    
    # 执行 Mint
    result = mint_claw()
    
    if result == "success":
        # 执行 Link Wallet
        link_wallet()
    
    print(f"\n✅ 本次操作完成")
    print(f"⏰ 下次执行: 2小时后")

if __name__ == "__main__":
    main()
