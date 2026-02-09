#!/bin/bash
# MBC20 Auto Mint Script
# 每2小时自动执行 Mint 操作

# 私钥（请替换为您的私钥）
export PRIVATE_KEY="0x27e4239ea51f4abfe8ae0a8332bfbe89e8b870a20eb9304339d21cf7daf659fa"

# Moltbook API Key
export MOLTBOOK_API_KEY="moltbook_sk_jQF9CfSCHTUm8TcEPvIFQ0P0Fbo6s8tU"

echo "================================"
echo "MBC20 Auto Mint - $(date)"
echo "================================"

# 检查是否可以发帖
RESPONSE=$(curl -s -X POST "https://www.moltbook.com/api/v1/posts" \
  -H "Authorization: Bearer $MOLTBOOK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"submolt": "general", "title": "Mint $CLAW", "content": "{\"p\":\"mbc-20\",\"op\":\"mint\",\"tick\":\"CLAW\",\"amt\":\"100\"}\n\nmbc20.xyz"}')

echo "Response: $RESPONSE"

# 解析并发送验证码
if echo "$RESPONSE" | grep -q "verification_required"; then
  VERIFICATION_CODE=$(echo "$RESPONSE" | grep -o '"code":"[^"]*"' | cut -d'"' -f4)
  CHALLENGE=$(echo "$RESPONSE" | grep -o '"challenge":"[^"]*"' | cut -d'"' -f4)
  
  echo "Verification required: $CHALLENGE"
  echo "Please solve the math problem and verify manually."
  echo "Or use the interactive mode."
else
  echo "Post created successfully or rate limited."
fi

echo ""
echo "Mint operation completed at $(date)"
echo "================================"
