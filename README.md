# BizGenesis

## 项目简介

BizGenesis 是一个基于 AI 智能体的商业分析系统，通过多个专业智能体协同工作，帮助用户进行市场调研、产品规划和营销策略制定。

## 功能特点

- 🔍 **市场调研智能体**：分析市场趋势和竞争对手
- 💡 **产品经理智能体**：制定产品策略和功能规划
- 📣 **营销内容智能体**：生成营销文案和推广方案

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 文件为 `.env`，并填入你的 API Key：

```bash
cp .env.example .env
```

### 3. 运行程序

```bash
python src/main.py
```

## 项目结构

```
BizGenesis/
├── .env.example             # 环境变量模版
├── .gitignore               # Git忽略文件
├── README.md                # 项目说明书
├── requirements.txt         # 依赖库列表
└── src/
    ├── __init__.py
    ├── main.py              # 主程序入口
    ├── config.py            # 配置加载
    └── agents/              # 智能体目录
        ├── __init__.py
        ├── base.py          # 智能体基类
        ├── market.py        # 市场调研智能体
        ├── product.py       # 产品经理智能体
        └── marketing.py     # 营销内容智能体
```

## 开发说明

- Python 版本：3.8+
- 主要依赖：openai, anthropic, python-dotenv

## License

MIT
