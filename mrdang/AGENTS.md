# MR Dang 价值选股技能

## OVERVIEW

A 股价值选股打分助手 — 通过 Tushare 获取财务数据 + Jina 搜索补充信息，按 8 维度评分体系输出投资评级。

## STRUCTURE

```
mrdang/
├── SKILL.md         # 技能定义（触发词、执行流程、评分规则、输出模板）
├── README.md        # 安装指南 + API 函数文档
└── scripts/
    ├── __init__.py  # 包导出（data/search/report 的公共 API）
    ├── data.py      # Tushare 数据获取（402 行，含 CLI）
    └── search.py    # Jina 网络搜索（308 行，含 CLI）
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| 修改评分规则 | `SKILL.md` | 8 维度打分 + 评级标准 + 买入前清单 |
| 修改数据获取 | `scripts/data.py` | Tushare pro_api 封装 |
| 修改搜索逻辑 | `scripts/search.py` | Jina API 封装 |
| 添加新数据源 | `scripts/` 下新建文件 | 遵循 PEP 723 内联依赖 |

## CONVENTIONS

- 所有脚本遵循 **PEP 723**（`# /// script` 块声明依赖），用 `uv run` 直接执行
- 环境变量读取采用 fast-fail：模块级检查，缺失立即 raise
- CLI 使用 `argparse` + subparsers，每个脚本独立入口
- 函数返回类型：单条数据用 `dict[str, Any]`，多条用 `pd.DataFrame`

## ANTI-PATTERNS

- 禁止硬编码 API Token，必须从 `os.environ` 读取
- 禁止在 `__init__.py` 中导入不存在的模块（`report.py` 已移除）
- 禁止美化评分结果，严格按 SKILL.md 规则执行
- 数据缺失标注【数据不足】，不隐瞒

## COMMANDS

```bash
# 搜索股票代码
uv run scripts/data.py search <关键词>

# 获取股票全部数据
uv run scripts/data.py get <ts_code> --type all

# 搜索公司信息
uv run scripts/search.py company <公司名> --industry <行业>
```

## NOTES

- `data.py` 顶部模块级初始化 Tushare 连接，无 `TUSHARE_TOKEN` 会立即失败
- SKILL.md 包含完整输出模板，生成报告时必须严格遵循该格式
- 银行股有特殊处理逻辑（地域因素、房地产风险搜索）
