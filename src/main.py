"""
主程序入口
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import load_config
from src.agents.market import MarketResearchAgent
from src.agents.product import ProductManagerAgent
from src.agents.marketing import MarketingAgent


def main():
    """主函数"""
    print("=" * 50)
    print("欢迎使用 BizGenesis - AI 商业分析系统")
    print("=" * 50)
    
    # 加载配置
    config = load_config()
    print(f"\n✓ 配置加载完成")
    
    # 初始化智能体
    market_agent = MarketResearchAgent(config)
    product_agent = ProductManagerAgent(config)
    marketing_agent = MarketingAgent(config)
    
    print("✓ 智能体初始化完成")
    print("\n可用智能体:")
    print("  1. 市场调研智能体")
    print("  2. 产品经理智能体")
    print("  3. 营销内容智能体")
    
    # TODO: 实现具体的业务流程
    print("\n系统准备就绪！")


if __name__ == "__main__":
    main()
