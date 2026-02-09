# OpenClaw 强调版优化配置

> 基于 ZenMux + QMD 优化方案
> 目标：省 20 倍 Token，最强 Agent 能力

---

## 🚀 第一步：安装技能

### ClawHub 技能安装
```bash
# 1. 搜索和安装技能
clawhub install tavily-search      # 强大搜索能力
clawhub install find-skills        # 技能发现
clawhub install proactive-agent-1-2-4  # 主动代理

# 2. 安装 QMD 内存管理
bun install -g github:tobi/qmd     # 量子内存驱动

# 3. 配置 QMD 集合
qmd collection add memory --name daily-logs --mask "/*.md"
```

---

## 🧠 第二步：内存配置 (memory)

### 优化版 memory 配置
```yaml
memory: {
  backend: "qmd",
  citations: "auto",
  qmd: {
    includeDefaultMemory: true,
    update: {
      interval: "5m",
      debounceMs: 15000
    },
    limits: {
      maxResults: 6,
      timeoutMs: 4000
    },
    scope: {
      default: "deny",
      rules: [
        {
          action: "allow",
          match: {
            chatType: "direct"
          }
        }
      ]
    },
    paths: [
      {
        name: "docs",
        path: "~/notes",
        pattern: "/*.md"
      }
    ]
  }
}
```

### 文件路径配置
```yaml
paths: [
  {
    name: "obsidian",
    path: "~/Obsidian/MyVault",
    pattern: "/*.md"
  },
  {
    name: "docs",
    path: "~/Documents/技术文档",
    pattern: "/*.md"
  }
]
```

---

## 🤖 第三步：模型配置 (models)

### ZenMux 免费模型聚合
```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "zenmux": {
        "baseUrl": "http://zenmux.ai/api/v1",
        "apiKey": "sk-ss-v1-YOUR-ZENMUX-API-KEY",
        "api": "openai-completions",
        "models": [
          {
            "id": "deepseek/deepseek-chat",
            "name": "DeepSeek Chat via ZenMux",
            "reasoning": false,
            "input": ["text"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 64000,
            "maxTokens": 8192
          },
          {
            "id": "openai/gpt-5.2",
            "name": "GPT-5.2 via ZenMux",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 200000,
            "maxTokens": 8192
          },
          {
            "id": "google/gemini-3-pro-preview",
            "name": "Gemini 3 Pro via ZenMux",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 200000,
            "maxTokens": 8192
          },
          {
            "id": "anthropic/claude-opus-4.6",
            "name": "Claude Opus 4.6 via ZenMux",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 200000,
            "maxTokens": 8192
          }
        ]
      }
    }
  }
}
```

---

## ⚙️ 第四步：代理默认配置 (agents)

### 最强代理配置
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "zenmux/anthropic/claude-opus-4.6"
      },
      "models": {
        "zenmux/deepseek/deepseek-chat": {},
        "zenmux/openai/gpt-5.2": {},
        "zenmux/google/gemini-3-pro-preview": {},
        "zenmux/anthropic/claude-opus-4.6": {}
      }
    }
  }
}
```

---

## 📋 完整配置模板

### 1. ZenMux API Key 获取
1. 订阅 ZenMux AI
2. 访问订阅页面
3. 创建 API Key
4. 替换配置中的 `sk-ss-v1-YOUR-ZENMUX-API-KEY`

### 2. 应用配置步骤

#### A. 安装 ClawHub 技能
```bash
# 在 OpenClaw 终端中运行
clawhub install tavily-search
clawhub install find-skills
clawhub install proactive-agent-1-2-4
```

#### B. 安装 QMD
```bash
# 安装 QMD
bun install -g github:tobi/qmd

# 配置内存集合
qmd collection add memory --name daily-logs --mask "/*.md"
```

#### C. 更新 OpenClaw 配置

**memory 配置：**
```yaml
# ~/.config/openclaw/memory.yaml
memory: {
  backend: "qmd",
  citations: "auto",
  qmd: {
    includeDefaultMemory: true,
    update: {
      interval: "5m",
      debounceMs: 15000
    },
    limits: {
      maxResults: 6,
      timeoutMs: 4000
    },
    scope: {
      default: "deny",
      rules: [
        {
          action: "allow",
          match: {
            chatType: "direct"
          }
        }
      ]
    },
    paths: [
      {
        name: "docs",
        path: "~/notes",
        pattern: "/*.md"
      }
    ]
  }
}
```

**paths 配置：**
```yaml
# ~/.config/openclaw/paths.yaml
paths: [
  {
    name: "obsidian",
    path: "~/Obsidian/MyVault",
    pattern: "/*.md"
  },
  {
    name: "docs",
    path: "~/Documents/技术文档",
    pattern: "/*.md"
  }
]
```

**models 配置：**
```json
// ~/.config/openclaw/models.json
{
  "models": {
    "mode": "merge",
    "providers": {
      "zenmux": {
        "baseUrl": "http://zenmux.ai/api/v1",
        "apiKey": "sk-ss-v1-YOUR-ZENMUX-API-KEY",
        "api": "openai-completions",
        "models": [
          {
            "id": "deepseek/deepseek-chat",
            "name": "DeepSeek Chat via ZenMux",
            "reasoning": false,
            "input": ["text"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 64000,
            "maxTokens": 8192
          },
          {
            "id": "openai/gpt-5.2",
            "name": "GPT-5.2 via ZenMux",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 200000,
            "maxTokens": 8192
          },
          {
            "id": "google/gemini-3-pro-preview",
            "name": "Gemini 3 Pro via ZenMux",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 200000,
            "maxTokens": 8192
          },
          {
            "id": "anthropic/claude-opus-4.6",
            "name": "Claude Opus 4.6 via ZenMux",
            "reasoning": false,
            "input": ["text", "image"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 200000,
            "maxTokens": 8192
          }
        ]
      }
    }
  }
}
```

**agents 配置：**
```json
// ~/.config/openclaw/agents.json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "zenmux/anthropic/claude-opus-4.6"
      },
      "models": {
        "zenmux/deepseek/deepseek-chat": {},
        "zenmux/openai/gpt-5.2": {},
        "zenmux/google/gemini-3-pro-preview": {},
        "zenmux/anthropic/claude-opus-4.6": {}
      }
    }
  }
}
```

---

## 🎯 预期效果

### Token 节省
- **之前**: ~500k tokens/会话
- **之后**: ~25k tokens/会话
- **节省**: ~20倍 (95%)

### 能力提升
- ✅ Tavily 搜索 → 强大网络搜索
- ✅ QMD 内存 → 智能上下文管理
- ✅ ZenMux 聚合 → 免费顶级模型
- ✅ Claude Opus 4.6 → 最强推理能力

---

## ⚠️ 注意事项

1. **API Key 安全**: 不要分享您的 ZenMux API Key
2. **免费模型**: ZenMux 提供免费额度，超限需付费
3. **路径调整**: 根据您的实际环境调整文件路径
4. **备份配置**: 应用前备份现有配置

---

## 📞 获取帮助

- **TG**: @ZenMuxAI
- **DC**: Discord 服务器
- **官网**: https://zenmux.ai

---

**创建时间**: 2026-02-08
**配置版本**: v1.0
**基于**: Twitter @0xKingsKuan 的优化方案
