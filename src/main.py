"""
Main entry point for BizGenesis with parallel execution and enhanced features.
"""
import sys
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress
from rich.table import Table

from src.agents.market import MarketResearcher
from src.agents.product import ProductManager
from src.agents.marketing import ContentStrategist
from src.agents.seo import SEOExpert
from src.agents.designer import ChiefDesigner
from src.agents.base import BaseAgent
from src.agents.business import BusinessModeler
from src.agents.finance import FinancePlanner
from src.agents.risk import RiskAnalyst

# Import new utilities
from src.utils.agent_parallel import AgentParallelExecutor, get_parallel_executor
from src.utils.token_monitor import get_token_monitor, TokenMonitor
from src.utils.pdf_export import PDFExportConfig, get_pdf_exporter

console = Console()


def run_agents_with_parallel(
    agents: List[BaseAgent],
    context: Dict[str, Any],
    use_parallel: bool = True
) -> Dict[str, Any]:
    """
    Run agents with parallel execution support.

    Args:
        agents: List of agents to run
        context: Initial context
        use_parallel: Whether to use parallel execution

    Returns:
        Updated context
    """
    if not use_parallel:
        # Sequential execution
        for agent in agents:
            context = agent.run(context)
        return context

    # Get executor
    executor = get_parallel_executor()

    # Get parallelization plan
    agent_names = [a.__class__.__name__ for a in agents]
    batches = executor.get_parallelization_plan(agent_names)

    # Execute in batches
    for batch in batches:
        batch_agents = [a for a in agents if a.__class__.__name__ in batch]

        if len(batch_agents) == 1:
            # Single agent, run directly
            result = executor.execute(batch_agents[0], context)
            context = result.context
        else:
            # Multiple agents, run in parallel
            result = executor.execute_parallel(batch_agents, context)
            context = result.context

    return context


def display_token_usage(token_monitor: TokenMonitor) -> None:
    """Display token usage statistics."""
    summary = token_monitor.get_usage_summary()

    if summary["total_tokens"] == 0:
        return

    table = Table(title="📊 Token 使用统计", border_style="cyan")
    table.add_column("Agent", style="cyan")
    table.add_column("Tokens", justify="right", style="green")
    table.add_column("Cost (USD)", justify="right", style="yellow")

    for agent_name, usage in summary["by_agent"].items():
        table.add_row(
            agent_name,
            f"{usage['tokens']:,}",
            f"${usage['cost']:.4f}"
        )

    table.add_row(
        "[bold]总计[/bold]",
        f"[bold]{summary['total_tokens']:,}[/bold]",
        f"[bold]${summary['total_cost']:.4f}[/bold]"
    )

    console.print(table)

    # Budget info
    if summary["budget"]["limit"]:
        remaining = summary["budget"]["remaining"]
        limit = summary["budget"]["limit"]
        usage_pct = (summary["total_tokens"] / limit) * 100

        console.print(f"\n💰 预算: {summary['total_tokens']:,} / {limit:,} ({usage_pct:.1f}%)")


def save_to_pdf(context: Dict[str, Any], industry: str) -> Path:
    """Save generated content to PDF."""
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_industry = industry.replace("/", "_").replace(" ", "_")[:20]
    filename = f"{safe_industry}_{timestamp}.pdf"
    filepath = output_dir / filename

    # Export to PDF
    config = PDFExportConfig(
        title=f"创业方案: {industry}",
        include_watermark=True,
        watermark_text="BizGenesis AI"
    )
    exporter = get_pdf_exporter(config)
    exporter.export_to_file(context, filepath)

    return filepath


def save_to_markdown(context: Dict[str, Any], industry: str) -> Path:
    """Save generated content to a markdown file."""
    # Create output directory
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_industry = industry.replace("/", "_").replace(" ", "_")[:20]
    filename = f"{safe_industry}_{timestamp}.md"
    filepath = output_dir / filename
    
    # Build markdown content
    md_content = f"""# 🚀 创业方案: {industry}

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 市场定位

{context.get('market_analysis', '暂无')}

---

## 📦 产品定义

{context.get('product_plan', '暂无')}

---

## 💰 商业模式

{context.get('business_model', '暂无')}

---

## 📈 财务规划

{context.get('finance_plan', '暂无')}

---

## ⚠️ 风险评估

{context.get('risk_analysis', '暂无')}

---

## 🎨 品牌设计

{context.get('design_strategy', '暂无')}

---

## 🎬 流量脚本

{context.get('marketing_script', '暂无')}

---

## 🔍 SEO 策略

{context.get('seo_strategy', '暂无')}

---

*Generated by BizGenesis AI 创业辅助系统*
"""
    
    # Write to file
    filepath.write_text(md_content, encoding='utf-8')
    return filepath

def main():
    console.print(Panel.fit("🚀 BizGenesis - AI 创业辅助系统", style="bold magenta"))

    # Get user input
    industry = console.input("[bold green]请输入你想尝试的创业领域/关键词 (例如: 袜子/露营/猫粮): [/]")
    if not industry:
        console.print("[red]输入不能为空！[/]")
        sys.exit()

    context: Dict[str, Any] = {"industry": industry}

    # Ask for parallel execution
    use_parallel = console.input(
        "[bold cyan]是否启用并行执行? (y/n, 默认y): [/]"
    ).lower() != "n"

    if use_parallel:
        console.print("[dim]✓ 将使用并行执行加速[/dim]")

    # Initialize agents
    agents: List[BaseAgent] = [
        MarketResearcher(),
        ProductManager(),
        BusinessModeler(),
        FinancePlanner(),
        RiskAnalyst(),
        ChiefDesigner(),
        ContentStrategist(),
        SEOExpert()
    ]

    # Run with progress
    start_time = time.time()

    with Progress() as progress:
        task = progress.add_task("[cyan]AI 团队正在协同工作...", total=len(agents))

        if use_parallel:
            # Use parallel execution
            executor = get_parallel_executor()
            agent_names = [a.__class__.__name__ for a in agents]
            batches = executor.get_parallelization_plan(agent_names)

            completed = 0
            for batch in batches:
                batch_agents = [a for a in agents if a.__class__.__name__ in batch]
                progress.update(task, description=f"[cyan]执行: {', '.join(batch)}[/cyan]")

                if len(batch_agents) == 1:
                    result = executor.execute(batch_agents[0], context)
                    context = result.context
                else:
                    result = executor.execute_parallel(batch_agents, context)
                    context = result.context

                completed += len(batch_agents)
                progress.update(task, completed=completed)
        else:
            # Sequential execution
            for agent in agents:
                agent_name = agent.__class__.__name__
                progress.update(task, description=f"[cyan]正在执行: {agent_name}[/cyan]")

                context = agent.run(context)
                progress.advance(task)
                time.sleep(0.3)

    elapsed = time.time() - start_time

    # Display results
    console.print("\n")
    console.rule(f"[bold yellow]🎉 创业方案生成完毕 ({elapsed:.1f}s)[/]")

    panels = [
        ("📊 市场定位", "market_analysis", "blue", "Step 1: Market"),
        ("📦 产品定义", "product_plan", "green", "Step 2: Product"),
        ("💰 商业模式", "business_model", "cyan", "Step 3: Business"),
        ("📈 财务规划", "finance_plan", "cyan", "Step 4: Finance"),
        ("⚠️ 风险评估", "risk_analysis", "red", "Step 5: Risk"),
        ("🎨 品牌设计", "design_strategy", "magenta", "Step 6: Design"),
        ("🎬 流量脚本", "marketing_script", "red", "Step 7: Content"),
        ("🔍 SEO 策略", "seo_strategy", "yellow", "Step 8: SEO"),
    ]

    for emoji_title, key, style, panel_title in panels:
        content = context.get(key, "")
        if content:
            console.print(
                Panel(Markdown(f"# {emoji_title}\n{content}"),
                      title=panel_title,
                      border_style=style)
            )

    # Display token usage
    console.print("\n")
    token_monitor = get_token_monitor()
    display_token_usage(token_monitor)

    # Save outputs
    console.print("\n")
    md_filepath = save_to_markdown(context, industry)
    console.print(Panel(f"💾 Markdown 已保存: [bold green]{md_filepath}[/]", style="bold blue"))

    # Try to save PDF
    try:
        pdf_filepath = save_to_pdf(context, industry)
        console.print(Panel(f"📄 PDF 已保存: [bold green]{pdf_filepath}[/]", style="bold green"))
    except Exception as e:
        console.print(f"[dim]PDF 导出失败 (可能需要安装 reportlab): {e}[/dim]")

    console.print(Panel("💡 Pro Tip: 复制 'Midjourney Prompt' 去生成你的第一个 Logo 吧！", style="italic grey50"))


async def main_async():
    """Async version of main for parallel execution."""
    console.print(Panel.fit("🚀 BizGenesis - AI 创业辅助系统", style="bold magenta"))
    
    industry = console.input("[bold green]请输入你想尝试的创业领域/关键词: [/]")
    if not industry:
        console.print("[red]输入不能为空！[/]")
        return

    context: Dict[str, Any] = {"industry": industry}
    
    agents: List[BaseAgent] = [
        MarketResearcher(),
        ProductManager(),
        BusinessModeler(),
        FinancePlanner(),
        RiskAnalyst(),
        ChiefDesigner(),
        ContentStrategist(),
        SEOExpert()
    ]

    # Run with async support
    context = await run_agents_parallel(agents, context)

    # Display results (same as sync version)
    console.print("\n")
    console.rule("[bold yellow]🎉 创业方案生成完毕[/]")
    
    # ... display logic here ...


if __name__ == "__main__":
    # Use synchronous main by default
    main()
    # For async: asyncio.run(main_async())
