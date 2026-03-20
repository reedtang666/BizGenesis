# 🚀 BizGenesis - AI 创业辅助系统

让 AI 团队帮你从想法到完整商业方案！

## 📊 系统流程图

```mermaid
flowchart TB
    subgraph Input["📥 用户输入"]
        A[创业想法/关键词]
    end
    
    subgraph AI_Team["🤖 AI 虚拟团队"]
        B[🕵️ 市场研究员<br/>Market Researcher]
        C[📦 产品经理<br/>Product Manager]
        D[🎨 首席设计师<br/>Chief Designer]
        E[🎬 流量操盘手<br/>Content Strategist]
        F[🔍 SEO 专家<br/>SEO Expert]
    end
    
    subgraph Tools["🛠️ 工具层"]
        G[Web 搜索<br/>Serper/DuckDuckGo]
        H[LLM<br/>GPT-4o-mini]
    end
    
    subgraph Output["📄 输出方案"]
        I[📊 市场定位分析]
        J[📦 产品定义方案]
        K[🎨 品牌设计概念]
        L[🎬 带货脚本]
        M[🔍 SEO 关键词]
    end
    
    A --> B
    B -->|市场趋势搜索| G
    G --> H
    H --> B
    B -->|市场分析结果| C
    C --> H
    H --> C
    C -->|产品方案| D
    D --> H
    H --> D
    D -->|设计方案| E
    E --> H
    H --> E
    E -->|营销脚本| F
    F --> H
    H --> F
    
    B --> I
    C --> J
    D --> K
    E --> L
    F --> M
    
    style A fill:#e1f5fe
    style I fill:#c8e6c9
    style J fill:#c8e6c9
    style K fill:#c8e6c9
    style L fill:#c8e6c9
    style M fill:#c8e6c9
```

## 🔄 数据流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant M as 市场研究员
    participant S as 搜索API
    participant L as LLM
    participant P as 产品经理
    participant D as 设计师
    participant C as 内容策略
    participant SE as SEO专家
    
    U->>M: 输入创业想法
    M->>S: 搜索市场趋势
    S-->>M: 返回搜索结果
    M->>L: 分析市场数据
    L-->>M: 市场分析报告
    M->>P: 传递市场洞察
    
    P->>L: 定义产品概念
    L-->>P: 产品方案
    P->>D: 传递产品定位
    
    D->>L: 生成品牌设计
    L-->>D: Logo概念 + Midjourney提示词
    D->>C: 传递品牌调性
    
    C->>L: 创作营销内容
    L-->>C: TikTok/抖音脚本
    C->>SE: 传递内容关键词
    
    SE->>L: 提取SEO关键词
    L-->>SE: 长尾词 + Hashtag
    
    SE-->>U: 完整商业方案
```

## ✨ 功能

| Agent | 角色 | 输出 |
|-------|------|------|
| 🕵️ 市场研究员 | 分析市场趋势，找到细分利基 | 市场定位分析 |
| 📦 产品经理 | 打造差异化产品概念 | 产品定义方案 |
| 🎨 首席设计师 | 生成 Logo 概念 | 品牌设计 + Midjourney Prompt |
| 🎬 流量操盘手 | 写爆款带货脚本 | TikTok/抖音脚本 |
| 🔍 SEO 专家 | 挖掘高转化关键词 | 长尾词 + Hashtag |

## 🛠️ 快速开始

### 方式 1: 命令行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 OPENAI_API_KEY

# 3. 运行
python -m src.main
```

### 方式 2: Web UI (Streamlit)

```bash
# 安装依赖后运行
streamlit run src/ui/app.py
```

### 方式 3: Docker

```bash
# 构建并运行
docker-compose up --build

# 访问 http://localhost:8501
```

## 📁 项目结构

```
BizGenesis/
├── src/
│   ├── main.py          # CLI 入口
│   ├── config.py        # 配置管理
│   ├── models.py        # Pydantic 模型
│   ├── agents/          # AI Agent 实现
│   │   ├── base.py      # 基类（日志、重试、记忆）
│   │   ├── market.py    # 市场研究员
│   │   ├── product.py   # 产品经理
│   │   ├── designer.py  # 首席设计
│   │   ├── marketing.py # 流量操盘手
│   │   └── seo.py       # SEO 专家
│   ├── tools/           # 工具模块
│   │   ├── search.py    # 搜索工具
│   │   └── calculator.py
│   └── ui/              # Streamlit UI
│       └── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔑 环境变量

| 变量             | 必填 | 说明                        |
| ---------------- | ---- | --------------------------- |
| OPENAI_API_KEY   | ✅   | OpenAI API Key              |
| OPENAI_MODEL     | ❌   | 模型名称，默认 gpt-4o-mini  |
| SERPER_API_KEY   | ❌   | Serper API Key（可选搜索）   |

## 🌐 搜索 API

默认使用 **DuckDuckGo** 免费搜索。配置 SERPER_API_KEY 可使用 Google 搜索，更快更准。

获取 Serper API Key: https://serper.dev/

## 📝 使用示例

```
输入: 猫粮

输出:
📊 市场定位: 高端无谷猫粮细分市场
📦 产品定义: "喵星优选" - 订阅制个性化猫粮
🎨 品牌设计: Logo 概念 + Midjourney Prompt
🎬 流量脚本: TikTok 3秒黄金开场脚本
🔍 SEO 策略: 长尾关键词 + Hashtag 推荐
```

## 🛡️ 技术栈

- **LangChain** - LLM 编排框架
- **Streamlit** - Web UI
- **Pydantic** - 数据验证
- **Loguru** - 日志系统
- **Tenacity** - 重试机制

## 📄 License

MIT License

## 🤝 贡献

欢迎 PR 和 Issue！
