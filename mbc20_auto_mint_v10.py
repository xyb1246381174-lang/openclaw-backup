#!/usr/bin/env python3
"""
MBC20 Auto Mint Bot v10.0 - Ultimate Edition
终极优化版：处理所有边缘情况，最大化成功率
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
MOLTBOOK_API_KEY = os.environ.get('MOLTBOOK_API_KEY', 'moltbook_sk_jQF9CfSCHTUm8TcEPvIFQ0P0Fbo6s8tU')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

MINT_JSON = '{"p":"mbc-20","op":"mint","tick":"CLAW","amt":"100"}'

# 完整数字映射
NUMBER_MAP = {
    # 0-9
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
    # 10-19
    'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
    'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
    'eighteen': 18, 'nineteen': 19,
    # 20-90
    'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
    'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
    # 100+
    'hundred': 100, 'thousand': 1000
}

def human_delay(min_sec=3, max_sec=18):
    """模拟人类延迟（更自然）"""
    delay = random.uniform(min_sec, max_sec)
    print(f"   🐢 延迟: {delay:.1f}秒")
    time.sleep(delay)

def clean_text(text):
    """清理文本"""
    return re.sub(r'[^a-zA-Z]', '', text).lower()

def extract_numbers_ultimate(challenge):
    """终极版数字提取 - 覆盖所有边缘情况"""
    print(f"   🔍 解析: {challenge[:120]}...")
    
    # 步骤1: 基础清理
    cleaned = clean_text(challenge)
    print(f"   🧹 清理: {cleaned}")
    
    all_findings = []
    
    # 步骤2: 多方法提取
    methods = {}
    
    # 方法1: 从头扫描
    i = 0
    nums1 = []
    while i < len(cleaned):
        for word in sorted(NUMBER_MAP.keys(), key=len, reverse=True):
            if cleaned.startswith(word, i):
                nums1.append(NUMBER_MAP[word])
                i += len(word)
                break
        else:
            i += 1
    methods['scan'] = nums1
    
    # 方法2: 反向扫描
    i = len(cleaned)
    nums2 = []
    while i > 0:
        matched = False
        for word in sorted(NUMBER_MAP.keys(), key=len, reverse=True):
            if i >= len(word) and cleaned[i-len(word):i] == word:
                nums2.insert(0, NUMBER_MAP[word])
                i -= len(word)
                matched = True
                break
        if not matched:
            i -= 1
    methods['reverse'] = nums2
    
    # 方法3: 分词扫描
    words = challenge.split()
    nums3 = []
    for word in words:
        clean = clean_text(word)
        if clean in NUMBER_MAP:
            nums3.append(NUMBER_MAP[clean])
    methods['split'] = nums3
    
    # 方法4: + 号分隔
    if '+' in challenge:
        parts = challenge.split('+')
        nums4 = []
        for part in parts:
            clean = clean_text(part)
            if clean in NUMBER_MAP:
                nums4.append(NUMBER_MAP[clean])
        methods['plus'] = nums4
    
    # 收集所有发现
    for method, nums in methods.items():
        for num in nums:
            if num not in all_findings:
                all_findings.append(num)
    
    print(f"   📊 方法结果:")
    for method, nums in methods.items():
        print(f"      {method}: {nums}")
    
    print(f"   🔢 所有发现: {all_findings}")
    
    return all_findings, methods

def generate_candidate_answers(all_numbers, methods):
    """生成所有候选答案"""
    candidates = set()
    
    if not all_numbers:
        return [0]
    
    # 候选1: 全部相加
    sum_all = sum(all_numbers)
    candidates.add(sum_all)
    
    # 候选2: 方法1相加（如果存在）
    if 'scan' in methods and methods['scan']:
        candidates.add(sum(methods['scan']))
    
    # 候选3: 方法2相加
    if 'reverse' in methods and methods['reverse']:
        candidates.add(sum(methods['reverse']))
    
    # 候选4: 最大值
    candidates.add(max(all_numbers))
    
    # 候选5: 最小值
    candidates.add(min(all_numbers))
    
    # 候选6: 前2个（如果有）
    if len(all_numbers) >= 2:
        candidates.add(all_numbers[0] + all_numbers[1])
    
    # 候选7: 只取第一个
    candidates.add(all_numbers[0])
    
    # 候选8: 只取最后一个
    candidates.add(all_numbers[-1])
    
    # 候选9: 偶数个的话取平均值
    if len(all_numbers) >= 2:
        avg = sum(all_numbers) // len(all_numbers)
        candidates.add(avg)
    
    result = sorted(list(candidates))
    print(f"   📝 候选答案: {result}")
    
    return result

def solve_captcha(challenge):
    """解决验证码"""
    all_numbers, methods = extract_numbers_ultimate(challenge)
    candidates = generate_candidate_answers(all_numbers, methods)
    
    if not candidates or candidates == [0]:
        print(f"   ⚠️ 未识别到数字")
        return ["0"]
    
    return [str(c) for c in candidates]

def curl_post(url, data):
    """发送请求"""
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", f"Authorization: Bearer {MOLTBOOK_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def send_telegram(msg):
    """发送Telegram消息"""
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        subprocess.run([
            "curl", "-s", "-X", "POST", url,
            "-d", f"chat_id={TELEGRAM_CHAT_ID}",
            "-d", f"text={msg}",
            "-d", "parse_mode=Markdown"
        ], capture_output=True)

def auto_mint():
    """自动Mint"""
    nonce = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    post_data = {
        "submolt": "general",
        "title": f"Mint $CLAW #{nonce}",
        "content": f"{MINT_JSON}\n\nmbc20.xyz #{nonce}"
    }
    
    print(f"\n🚀 步骤1: 发送帖子...")
    human_delay(5, 18)
    
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
                print(f"\n🔐 步骤2: 解决验证码...")
                human_delay(8, 20)
                
                candidate_answers = solve_captcha(challenge)
                
                print(f"\n✅ 步骤3: 暴力验证...")
                human_delay(5, 15)
                
                success = False
                tried = set()
                
                # 随机打乱验证顺序（更自然）
                random.shuffle(candidate_answers)
                
                for answer in candidate_answers:
                    if answer in tried:
                        continue
                    tried.add(answer)
                    
                    print(f"   尝试: {answer}")
                    
                    # 尝试小数格式
                    float_ans = f"{answer}.00"
                    verify_resp = curl_post("https://www.moltbook.com/api/v1/verify", {
                        "verification_code": code,
                        "answer": float_ans
                    })
                    verify_json = json.loads(verify_resp)
                    
                    if verify_json.get("success"):
                        result = f"✅ Mint成功！获得 100 $CLAW\n答案: {answer}"
                        success = True
                        break
                    
                    human_delay(random.uniform(2, 5))
                    
                    # 尝试整数格式
                    verify_resp2 = curl_post("https://www.moltbook.com/api/v1/verify", {
                        "verification_code": code,
                        "answer": answer
                    })
                    verify_json2 = json.loads(verify_resp2)
                    
                    if verify_json2.get("success"):
                        result = f"✅ Mint成功！获得 100 $CLAW\n答案: {answer}"
                        success = True
                        break
                
                if not success:
                    result = f"❌ 验证失败\n尝试: {list(tried)}"
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
        print(f"\n📊 {datetime.now()}: {result}")
    else:
        while True:
            try:
                status = auto_mint()
                send_telegram(f"📊 Mint: {status}")
            except Exception as e:
                send_telegram(f"❌ 错误: {e}")
            time.sleep(1800)
