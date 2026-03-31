# PROJECT KNOWLEDGE BASE

**Generated:** 2026-03-31
**Commit:** ffe3392
**Branch:** main

## OVERVIEW

个人技能仓库 — 用于增强 AI 辅助工作流的 Claude Code skills 集合。当前仅含 mrdang（A 股价值选股打分）一项技能。

## STRUCTURE

```
./
├── README.md            # 仓库级说明：安装方式、可用技能列表
├── .gitignore           # Python/IDE/OS/reports/env 忽略规则
└── mrdang/              # MR Dang 价值选股技能
    ├── SKILL.md         # Claude Code 技能定义（触发词、执行流程、评分规则）
    ├── README.md        # 技能安装与使用说明
    └── scripts/         # Python 脚本（PEP 723 内联依赖声明）
        ├── __init__.py  # 包导出
        ├── data.py      # Tushare 数据获取
        └── search.py    # Tavily 网络搜索
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| 添加新技能 | 根目录下新建 `<skill-name>/` | 需包含 SKILL.md + README.md |
| 修改 mrdang 评分逻辑 | `mrdang/SKILL.md` | 评分规则 + 输出格式均在此 |
| 修改数据获取逻辑 | `mrdang/scripts/data.py` | Tushare API 封装 |
| 修改搜索逻辑 | `mrdang/scripts/search.py` | Tavily API 封装 |

## CONVENTIONS

- Python 脚本使用 **PEP 723** 内联依赖声明（`# /// script` 块），可用 `uv run` 直接执行
- 文件需遵循 **ruff** 格式化（line-length 100）
- 依赖管理使用 **uv**（非 pip）

## ANTI-PATTERNS

- 禁止硬编码 `TUSHARE_TOKEN` / `TAVILY_API_KEY`，必须从环境变量读取
- 禁止在根目录生成 `reports/`（已在 .gitignore 排除）
- 禁止删除测试来通过检查

## COMMANDS

```bash
# mrdang 数据获取
uv run mrdang/scripts/data.py search <关键词>
uv run mrdang/scripts/data.py get <ts_code> --type all

# mrdang 网络搜索
uv run mrdang/scripts/search.py company <公司名> --industry <行业>

# 格式化
ruff format --line-length 100 mrdang/scripts/
ruff check --fix mrdang/scripts/
```

## NOTES

- 脚本在模块级初始化 Tushare 连接（`data.py` 顶部），缺少 `TUSHARE_TOKEN` 会立即 raise
- `report.py` 已在最近一次提交中移除，保存报告功能不再内置
