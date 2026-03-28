# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Report generation and saving for MR Dang stock analysis."""

import os
from datetime import datetime
from pathlib import Path
from typing import Any


def get_reports_dir() -> Path:
    """Get the reports directory path.

    Returns:
        Path to reports directory (current working directory)
    """
    return Path.cwd()


def generate_report_filename(stock_name: str, ts_code: str) -> str:
    """Generate a filename for the report.

    Args:
        stock_name: Stock name
        ts_code: Tushare stock code

    Returns:
        Filename string
    """
    date_str = datetime.now().strftime("%Y%m%d")
    # Clean stock name for filename
    safe_name = "".join(c for c in stock_name if c.isalnum() or c in "._-")
    return f"{safe_name}_{ts_code.split('.')[0]}_{date_str}.md"


def format_value(value: Any, default: str = "N/A") -> str:
    """Format a value for display.

    Args:
        value: Value to format
        default: Default string if value is None

    Returns:
        Formatted string
    """
    if value is None:
        return default
    if isinstance(value, float):
        if abs(value) >= 1e8:
            return f"{value / 1e8:.2f}亿"
        elif abs(value) >= 1e4:
            return f"{value / 1e4:.2f}万"
        else:
            return f"{value:.2f}"
    return str(value)


def generate_report(
    stock_name: str,
    ts_code: str,
    industry: str,
    data: dict[str, Any],
    search_results: dict[str, list[dict[str, Any]]],
    scores: dict[str, Any],
    screening: dict[str, str],
    checklist: dict[str, str],
    conclusion: str,
) -> str:
    """Generate the full markdown report.

    Args:
        stock_name: Stock name
        ts_code: Tushare stock code
        industry: Industry classification
        data: Stock data from Tushare
        search_results: Search results from Tavily
        scores: Scoring results
        screening: Screening results
        checklist: Checklist verification results
        conclusion: Final conclusion

    Returns:
        Markdown report string
    """
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Extract data
    basic = data.get("basic", {})
    daily = data.get("daily_basic", {})
    financial = data.get("financial", {})
    dividend = data.get("dividend", {})
    price_pos = data.get("price_position", {})

    # Build report
    lines = [
        f"# MR Dang 选股打分报告",
        "",
        f"【标的】{stock_name}（{ts_code}）",
        f"【行业归类】{industry}",
        f"【分析日期】{date_str}",
        "",
        "---",
        "",
        "## 一、基础筛查结果",
        "",
        "| 筛查项 | 结果 | 说明 |",
        "|--------|------|------|",
    ]

    # Add screening results
    for item, result in screening.items():
        if result == "通过":
            status = "✅ 通过"
        elif result == "存疑":
            status = "⚠️ 存疑"
        else:
            status = "❌ 淘汰"
        lines.append(f"| {item} | {status} | |")

    screening_passed = all(r == "通过" for r in screening.values())
    screening_conclusion = "✅ 全部通过" if screening_passed else f"❌ 淘汰（原因：{[k for k, v in screening.items() if v != '通过'][0]}）"
    lines.extend([
        "",
        f"**筛查结论**：{screening_conclusion}",
        "",
        "---",
        "",
        "## 二、核心数据概览",
        "",
        "### 估值指标",
        "| 指标 | 数值 | 说明 |",
        "|------|------|------|",
        f"| PE(TTM) | {format_value(daily.get('pe_ttm'))} | |",
        f"| PB | {format_value(daily.get('pb'))} | |",
        f"| 总市值 | {format_value(daily.get('total_mv'))} | |",
        f"| 流通市值 | {format_value(daily.get('circ_mv'))} | |",
        "",
        "### 财务指标",
        "| 指标 | 数值 | 说明 |",
        "|------|------|------|",
        f"| 股息率(TTM) | {format_value(daily.get('dv_ratio'))}% | |",
        f"| 资产负债率 | {format_value(financial.get('debt_to_assets'))}% | |",
        f"| ROE | {format_value(financial.get('roe'))}% | |",
        f"| 经营现金流/股 | {format_value(financial.get('ocfps'))} | |",
        "",
        "### 分红历史",
        "| 指标 | 数值 | 说明 |",
        "|------|------|------|",
        f"| 近3年分红次数 | {dividend.get('dividend_count', 0)} | |",
        f"| 分红稳定性 | {dividend.get('dividend_stability', 'N/A')} | |",
        "",
    ])

    # Add price position
    if price_pos:
        lines.extend([
            "### 股价位置",
            "| 指标 | 数值 | 说明 |",
            "|------|------|------|",
            f"| 最新收盘价 | {format_value(price_pos.get('latest_close'))} | |",
            f"| 52周高点 | {format_value(price_pos.get('high_52w'))} | |",
            f"| 52周低点 | {format_value(price_pos.get('low_52w'))} | |",
            f"| 价格分位 | {format_value(price_pos.get('price_position_pct'))}% | {price_pos.get('position_level', '')} |",
            "",
        ])

    # Add business info from search
    lines.extend([
        "### 业务概况",
        f"- **主营业务**：{search_results.get('business_summary', 'N/A')}",
        f"- **行业地位**：{search_results.get('position_summary', 'N/A')}",
        "",
        "---",
        "",
        "## 三、维度打分明细",
        "",
        "| 维度 | 得分 | 满分 | 评分依据 |",
        "|------|------|------|----------|",
    ])

    # Add scores
    total_score = 0
    max_score = 0
    for dim, info in scores.items():
        score = info.get("score", 0)
        max_s = info.get("max", 0)
        reason = info.get("reason", "")
        total_score += score
        max_score += max_s
        lines.append(f"| {dim} | {score} | {max_s} | {reason} |")

    # Determine rating
    if total_score >= 80:
        rating = "⭐⭐⭐⭐⭐ 优秀"
        suggestion = "重点关注、可建仓"
    elif total_score >= 60:
        rating = "⭐⭐⭐⭐ 良好"
        suggestion = "可分批买入"
    elif total_score >= 40:
        rating = "⭐⭐⭐ 一般"
        suggestion = "谨慎观察"
    elif total_score >= 20:
        rating = "⭐⭐ 较差"
        suggestion = "建议回避"
    else:
        rating = "⭐ 极差"
        suggestion = "直接排除"

    lines.extend([
        "",
        f"**总分：{total_score} / {max_score}**",
        f"**评级：{rating}**",
        "",
        "---",
        "",
        "## 四、操作建议",
        "",
        suggestion,
        "",
        "---",
        "",
        "## 五、买入前清单核验",
        "",
        "| 清单项 | 状态 | 说明 |",
        "|--------|------|------|",
    ])

    # Add checklist
    passed_count = 0
    for item, status in checklist.items():
        status_icon = "✅ 达标" if status == "达标" else "⚠️ 存疑" if status == "存疑" else "❌ 不达标"
        lines.append(f"| {item} | {status_icon} | |")
        if status == "达标":
            passed_count += 1

    lines.extend([
        "",
        f"**达标项：{passed_count} / {len(checklist)}**",
        "",
        "---",
        "",
        "## 六、综合结论",
        "",
        conclusion,
        "",
        "---",
        "",
        "**风险提示**：本报告基于公开数据分析，不构成投资建议。投资有风险，入市需谨慎。",
        "",
    ])

    return "\n".join(lines)


def save_report(
    stock_name: str,
    ts_code: str,
    industry: str,
    data: dict[str, Any],
    search_results: dict[str, list[dict[str, Any]]],
    scores: dict[str, Any],
    screening: dict[str, str],
    checklist: dict[str, str],
    conclusion: str,
    output_dir: str | Path | None = None,
) -> Path:
    """Generate and save the report to disk.

    Args:
        stock_name: Stock name
        ts_code: Tushare stock code
        industry: Industry classification
        data: Stock data from Tushare
        search_results: Search results from Tavily
        scores: Scoring results
        screening: Screening results
        checklist: Checklist verification results
        conclusion: Final conclusion
        output_dir: Output directory (defaults to current working directory)

    Returns:
        Path to saved report file
    """
    # Determine output directory
    if output_dir is None:
        output_dir = get_reports_dir()
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Generate report content
    content = generate_report(
        stock_name=stock_name,
        ts_code=ts_code,
        industry=industry,
        data=data,
        search_results=search_results,
        scores=scores,
        screening=screening,
        checklist=checklist,
        conclusion=conclusion,
    )

    # Generate filename and save
    filename = generate_report_filename(stock_name, ts_code)
    filepath = output_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


def main() -> None:
    """CLI entry point for report generation."""
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Generate MR Dang stock analysis report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate report from JSON data file
  uv run scripts/report.py generate --data <json文件> --output <目录>

  # Preview report content (print to stdout)
  uv run scripts/report.py preview --data <json文件>

The JSON data file should contain:
  {
    "stock_name": "<股票名称>",
    "ts_code": "<ts_code>",
    "industry": "<行业>",
    "data": {...},
    "search_results": {...},
    "scores": {...},
    "screening": {...},
    "checklist": {...},
    "conclusion": "..."
  }
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate and save report")
    gen_parser.add_argument("--data", required=True, help="Path to JSON data file")
    gen_parser.add_argument("--output", default=".", help="Output directory (default: current)")

    # Preview command
    preview_parser = subparsers.add_parser("preview", help="Preview report content")
    preview_parser.add_argument("--data", required=True, help="Path to JSON data file")

    args = parser.parse_args()

    # Load data from JSON file
    with open(args.data, encoding="utf-8") as f:
        params = json.load(f)

    # Support multiple JSON formats
    stock_name = params.get("stock_name") or params.get("stock", {}).get("name", "Unknown")
    ts_code = params.get("ts_code") or params.get("stock", {}).get("ts_code", "")
    industry = params.get("industry") or params.get("stock", {}).get("industry", "")

    # Handle data format - support nested or flat structure
    data = params.get("data", {})
    if "valuation" in data:
        # Transform nested format to expected format
        valuation = data.get("valuation", {})
        dividend = data.get("dividend", {})
        price = data.get("price", {})

        data = {
            "basic": params.get("stock", {}),
            "daily_basic": {
                "pe_ttm": valuation.get("pe_ttm"),
                "pb": valuation.get("pb"),
                "total_mv": valuation.get("total_mv"),
                "circ_mv": valuation.get("circ_mv"),
                "dv_ratio": dividend.get("dv_ttm"),  # Map dv_ttm to dv_ratio
            },
            "financial": data.get("financial", {}),
            "dividend": {
                "dividend_count": dividend.get("dividend_count_3y", dividend.get("dividend_count", 0)),
                "dividend_stability": dividend.get("dividend_stability", "N/A"),
            },
            "price_position": {
                "latest_close": price.get("close"),
                "high_52w": price.get("high_52w"),
                "low_52w": price.get("low_52w"),
                "price_position_pct": price.get("position_pct"),
                "position_level": price.get("position_level", ""),
            },
        }

    # Handle screening format - support nested with result or flat string
    screening_raw = params.get("screening", {})
    screening = {}
    for key, value in screening_raw.items():
        if isinstance(value, dict):
            screening[key] = value.get("result", value.get("status", "通过"))
        else:
            screening[key] = value

    # Handle scores format - support nested with score/max/reason
    scores_raw = params.get("scores", {})
    scores = {}
    for key, value in scores_raw.items():
        if isinstance(value, dict):
            scores[key] = value
        else:
            scores[key] = {"score": value, "max": 0, "reason": ""}

    # Handle checklist format - support nested with status or flat string
    checklist_raw = params.get("checklist", {})
    checklist = {}
    for key, value in checklist_raw.items():
        if isinstance(value, dict):
            checklist[key] = value.get("status", value.get("result", "存疑"))
        else:
            checklist[key] = value

    # Handle search_results - optional
    search_results = params.get("search_results", {})
    web_info = params.get("web_info", {})
    if web_info and not search_results:
        search_results = {
            "business_summary": web_info.get("main_business", ""),
            "position_summary": web_info.get("industry_position", ""),
        }

    # Handle conclusion - optional
    conclusion = params.get("conclusion", params.get("suggestion", ""))

    if args.command == "generate":
        filepath = save_report(
            stock_name=stock_name,
            ts_code=ts_code,
            industry=industry,
            data=data,
            search_results=search_results,
            scores=scores,
            screening=screening,
            checklist=checklist,
            conclusion=conclusion,
            output_dir=args.output,
        )
        print(f"Report saved to: {filepath}")

    elif args.command == "preview":
        content = generate_report(
            stock_name=stock_name,
            ts_code=ts_code,
            industry=industry,
            data=data,
            search_results=search_results,
            scores=scores,
            screening=screening,
            checklist=checklist,
            conclusion=conclusion,
        )
        print(content)


if __name__ == "__main__":
    main()
