import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress

from src.agents.market import MarketResearcher
from src.agents.product import ProductManager
from src.agents.marketing import ContentStrategist
from src.agents.seo import SEOExpert        # 新增
from src.agents.designer import ChiefDesigner # 新增

console = Console()

def main():
    console.print(Panel.fit("🚀 BizGenesis - AI 创业辅助系统", style="bold magenta"))
    
    industry = console.input("[bold green]请输入你想尝试的创业领域/关键词 (例如: 袜子/露营/猫粮): [/]")
    if not industry:
        console.print("[red]输入不能为空！[/]")
        sys.exit()

    context = {"industry": industry}
    
    # 升级后的 5 人豪华团队
    agents = [
        MarketResearcher(),
        ProductManager(),
        ChiefDesigner(),    # 视觉先行
        ContentStrategist(),
        SEOExpert()         # 流量收尾
    ]

    with Progress() as progress:
        task = progress.add_task("[cyan]AI 团队正在协同工作...", total=len(agents))
        
        for agent in agents:
            # 获取类名作为当前步骤说明
            agent_name = agent.__class__.__name__
            progress.update(task, description=f"[cyan]正在执行: {agent_name}")
            
            context = agent.run(context)
            progress.advance(task)
            time.sleep(1)

    # 输出结果（增加了设计和SEO板块）
    console.print("\n")
    console.rule("[bold yellow]🎉 创业方案生成完毕[/]")
    
    console.print(Panel(Markdown(f"# 📊 市场定位\n{context.get('market_analysis', '')}"), title="Step 1: Market", border_style="blue"))
    console.print(Panel(Markdown(f"# 📦 产品定义\n{context.get('product_plan', '')}"), title="Step 2: Product", border_style="green"))
    console.print(Panel(Markdown(f"# 🎨 品牌设计\n{context.get('design_strategy', '')}"), title="Step 3: Design", border_style="magenta"))
    console.print(Panel(Markdown(f"# 🎬 流量脚本\n{context.get('marketing_script', '')}"), title="Step 4: Content", border_style="red"))
    console.print(Panel(Markdown(f"# 🔍 SEO 策略\n{context.get('seo_strategy', '')}"), title="Step 5: SEO", border_style="yellow"))

    console.print(Panel("💡 Pro Tip: 复制 'Midjourney Prompt' 去生成你的第一个 Logo 吧！", style="italic grey50"))

if __name__ == "__main__":
    main()