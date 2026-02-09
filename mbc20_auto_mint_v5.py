#!/usr/bin/env python3
"""
MBC20 Auto Mint Bot v5.0
修复复合数字识别问题
"""

import os
import time
import json
import subprocess
import random
import string
import re
from datetime import datetime

# 配置
MOLTBOOK_API_KEY = os.environ.get('MOLTBOOK_API_KEY', '${MOLTBOOK_API_KEY}')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

MINT_JSON = '{"p":"mbc-20","op":"mint","tick":"CLAW","amt":"100"}'

# 数字映射
NUMBER_MAP = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
    'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
    'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
    'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
    'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
    'eighty': 80, 'ninety': 90
}

# 十位数（用于组合）
TENS = {'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90}
ONES = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9}

def normalize(word):
    return re.sub(r'[^a-zA-Z]', '', word).lower()

def extract_numbers_v3(challenge):
    """v3: 正确处理复合数字"""
    print(f"   🔍 解析: {challenge[:60]}...")
    
    # 清理：只保留字母和空格
    text = re.sub(r'[^a-zA-Z\s]', ' ', challenge)
    words = text.split()
    
    numbers = []
    i = 0
    while i < len(words):
        word = normalize(words[i])
        
        # 检查是否是十位数 + 个位数（如 twenty three = 23）
        if word in TENS:
            tens_value = TENS[word]
            # 检查下一个词是否是个位数
            if i + 1 < len(words):
                next_word = normalize(words[i + 1])
                if next_word in ONES:
                    # 组合：twenty three = 20 + 3 = 23
                    combined = tens_value + ONES[next_word]
                    numbers.append(combined)
                    print(f"   📝 组合: {word} + {next_word} = {combined}")
                    i += 2
                    continue
            
            # 只有十位数（如 twenty = 20）
            numbers.append(tens_value)
            print(f"   📝 十位: {word} = {tens_value}")
        
        # 检查其他数字
        elif word in NUMBER_MAP:
            numbers.append(NUMBER_MAP[word])
            print(f"   📝 数字: {word} = {NUMBER_MAP[word]}")
        
        # 纯数字
        elif word.isdigit():
            numbers.append(int(word))
            print(f"   📝 纯数字: {word}")
        
        i += 1
    
    print(f"   📊 结果: {numbers} = {sum(numbers)}")
    return numbers

def solve_captcha(challenge):
    numbers = extract_numbers_v3(challenge)
    if not numbers:
        return "0"
    
    total = sum(numbers)
    time.sleep(3)  # 冷静期
    
    print(f"   ✅ 最终答案: {total}")
    return str(total)

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
                
                verify_resp = curl_post("https://www.moltbook.com/api/v1/verify", {
                    "verification_code": code,
                    "answer": answer
                })
                
                verify_json = json.loads(verify_resp)
                
                if verify_json.get("success"):
                    result = f"✅ Mint成功！获得 100 $CLAW\n⏰ {datetime.now().strftime('%H:%M:%S')}"
                else:
                    result = f"❌ 验证失败: {answer}"
            else:
                result = "✅ 帖子已发布"
        else:
            result = "✅ 帖子已发布"
        
        return result
        
    except Exception as e:
        return f"❌ 错误: {e}"

if __name__ == "__main__":
    import sys
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
            time.sleep(1800)
