#!/usr/bin/env python3
"""
MBC20 Auto Mint Bot v4.0
改进版验证码识别
"""

import os
import time
import json
import subprocess
import random
import string
import re
import sys
from datetime import datetime

# 配置
MOLTBOOK_API_KEY = os.environ.get('MOLTBOOK_API_KEY', '${MOLTBOOK_API_KEY}')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

MINT_JSON = '{"p":"mbc-20","op":"mint","tick":"CLAW","amt":"100"}'

# 完整的数字映射（包含部分匹配）
NUMBER_MAP = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
    'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
    'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
    'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
    'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
    'eighty': 80, 'ninety': 90, 'hundred': 100
}

def normalize_word(word):
    """标准化单词（移除特殊字符，转小写）"""
    # 只保留字母
    cleaned = re.sub(r'[^a-zA-Z]', '', word)
    return cleaned.lower()

def extract_numbers_v2(challenge):
    """改进版数字提取"""
    print(f"   🔍 解析: {challenge[:60]}...")
    
    # 移除常见分隔符
    text = challenge.replace('[', ' ').replace(']', ' ')
    text = text.replace('{', ' ').replace('}', ' ')
    text = text.replace('<', ' ').replace('>', ' ')
    text = text.replace('(', ' ').replace(')', ' ')
    text = text.replace('^', ' ').replace('+', ' ').replace('-', ' ')
    text = text.replace('/', ' ').replace('|', ' ').replace('~', ' ')
    text = text.replace(',', ' ').replace('.', ' ').replace('=', ' ')
    
    # 分割成单词
    words = text.split()
    
    numbers = []
    current_number = 0
    
    for word in words:
        cleaned = normalize_word(word)
        
        # 检查是否在数字表中
        if cleaned in NUMBER_MAP:
            value = NUMBER_MAP[cleaned]
            
            # 如果值 >= 10，很可能是十位数（如 twenty=20, thirty=30）
            if value >= 10 and value < 100:
                # 先检查是否后面跟着个位数
                # 格式可能是 "twenty three" = 20 + 3
                # 但我们已经分词了，所以分别处理
                numbers.append(value)
            elif value < 10:
                # 个位数
                numbers.append(value)
            elif value == 100:
                # hundred
                if current_number > 0:
                    current_number *= 100
                else:
                    current_number = 100
        # 检查纯数字
        elif cleaned.isdigit():
            numbers.append(int(cleaned))
    
    print(f"   📊 提取: {numbers}")
    return numbers

def solve_captcha(challenge):
    """解决验证码"""
    numbers = extract_numbers_v2(challenge)
    
    if not numbers:
        print(f"   ⚠️ 无法提取数字，使用0")
        return "0"
    
    # 尝试多种计算方式
    # 1. 简单相加
    total1 = sum(numbers)
    
    # 2. 检查是否应该组合（如 20 + 3 = 23，而不是 20 + 3 = 23，相同）
    # Moltbook的验证码通常是简单相加
    
    print(f"   🧮 计算: {' + '.join(map(str, numbers))} = {total1}")
    
    # 冷静期
    time.sleep(3)
    
    # 返回整数（不用小数点）
    return str(total1)

def curl_post(url, data):
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", f"Authorization: Bearer {MOLTBOOK_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def send_telegram(msg):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        subprocess.run([
            "curl", "-s", "-X", "POST", url,
            "-d", f"chat_id={TELEGRAM_CHAT_ID}",
            "-d", f"text={msg}",
            "-d", "parse_mode=Markdown"
        ], capture_output=True)

def auto_mint():
    nonce = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    post_data = {
        "submolt": "general",
        "title": f"Mint $CLAW #{nonce}",
        "content": f"{MINT_JSON}\n\nmbc20.xyz #{nonce}"
    }
    
    resp = curl_post("https://www.moltbook.com/api/v1/posts", post_data)
    
    try:
        resp_json = json.loads(resp)
        
        if not resp_json.get("success"):
            error = resp_json.get("error", "")
            if "once every" in error:
                wait = resp_json.get("retry_after_minutes", 30)
                msg = f"⏰ 冷却中，还需 {wait} 分钟"
            else:
                msg = f"❌ 失败: {error}"
            return msg
        
        if resp_json.get("verification_required"):
            challenge = resp_json.get("verification", {}).get("challenge", "")
            code = resp_json.get("verification", {}).get("code", "")
            
            if challenge and code:
                answer = solve_captcha(challenge)
                print(f"   ✅ 答案: {answer}")
                
                verify_resp = curl_post("https://www.moltbook.com/api/v1/verify", {
                    "verification_code": code,
                    "answer": answer
                })
                
                verify_json = json.loads(verify_resp)
                
                if verify_json.get("success"):
                    result = f"✅ Mint成功！获得 100 $CLAW\n⏰ {datetime.now().strftime('%H:%M:%S')}"
                else:
                    error_msg = verify_json.get('error', 'Unknown')
                    result = f"❌ 验证失败: {error_msg}\n答案: {answer}"
                    
                    # 如果失败，尝试不同的解析方式
                    # 这里可以添加重试逻辑
            else:
                result = "✅ 帖子已发布"
        else:
            result = "✅ 帖子已发布"
        
        return result
        
    except Exception as e:
        return f"❌ 错误: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        result = auto_mint()
        print(f"📊 {datetime.now()}: {result}")
    else:
        while True:
            try:
                status = auto_mint()
                send_telegram(f"📊 Mint状态: {status}")
            except Exception as e:
                send_telegram(f"❌ 错误: {e}")
            time.sleep(1800)  # 30分钟
