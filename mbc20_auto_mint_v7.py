#!/usr/bin/env python3
"""
MBC20 Auto Mint Bot v7.0
终极版：带完整调试信息
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

# 所有数字关键词
ALL_NUMBERS = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
    'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
    'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
    'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
    'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
    'eighty': 80, 'ninety': 90, 'hundred': 100
}

def extract_numbers_debug(challenge):
    """带调试的数字提取"""
    print(f"   🔍 原题: {challenge[:80]}...")
    
    # 步骤1: 移除所有非字母
    cleaned = re.sub(r'[^a-zA-Z]', '', challenge).lower()
    print(f"   🧹 清理: {cleaned}")
    
    numbers = []
    i = 0
    found_words = []
    
    while i < len(cleaned):
        matched = False
        
        # 优先匹配长词
        for word in sorted(ALL_NUMBERS.keys(), key=len, reverse=True):
            if cleaned.startswith(word, i):
                numbers.append(ALL_NUMBERS[word])
                found_words.append(f"{word}({ALL_NUMBERS[word]})")
                print(f"   📝 找到: {word} = {ALL_NUMBERS[word]}")
                i += len(word)
                matched = True
                break
        
        if not matched:
            i += 1
    
    print(f"   📊 识别: {' + '.join(map(str, numbers))} = {sum(numbers)}")
    return numbers

def solve_captcha(challenge):
    numbers = extract_numbers_debug(challenge)
    
    if not numbers:
        print(f"   ⚠️ 未识别到数字")
        return "0"
    
    total = sum(numbers)
    print(f"   ✅ 答案: {total}")
    
    # 冷静期
    time.sleep(3)
    
    # 返回整数和小数两种格式
    return str(total), f"{total}.00"

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
                int_answer, float_answer = solve_captcha(challenge)
                
                # 尝试小数格式
                verify_resp = curl_post("https://www.moltbook.com/api/v1/verify", {
                    "verification_code": code,
                    "answer": float_answer
                })
                
                verify_json = json.loads(verify_resp)
                
                if verify_json.get("success"):
                    result = f"✅ Mint成功！获得 100 $CLAW\n答案: {float_answer}"
                else:
                    # 如果小数格式失败，尝试整数格式
                    print(f"   ⚠️ 小数格式失败，尝试整数...")
                    verify_resp2 = curl_post("https://www.moltbook.com/api/v1/verify", {
                        "verification_code": code,
                        "answer": int_answer
                    })
                    verify_json2 = json.loads(verify_resp2)
                    
                    if verify_json2.get("success"):
                        result = f"✅ Mint成功！获得 100 $CLAW\n答案: {int_answer}"
                    else:
                        result = f"❌ 验证失败\n小数: {float_answer}\n整数: {int_answer}"
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
                send_telegram(f"📊 Mint: {status}")
            except Exception as e:
                send_telegram(f"❌ 错误: {e}")
            time.sleep(1800)
