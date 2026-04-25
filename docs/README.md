# PriBSCS Reproducibility Package

This document contains the main project instructions and metadata for reproducing the PriBSCS paper experiments.

## Contents

- `run.py`: runs the main PriBSCS simulations and exports result CSV files.
- `sensitivity.py`: runs the ADMM penalty sensitivity study and exports Table-style CSV output.
- `plot.py`: generates paper-aligned figures (Fig. 2 to Fig. 10) from `data_results/`.
- `data_results/`: generated result data used for plots and reported metrics.
- `figures/`: generated figure files aligned with the paper figure numbers.
- `requirements.txt`: Python dependencies.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
python sensitivity.py
python plot.py
```

## Figure Mapping (Paper Numbering)

- Fig. 2 -> `figures/Fig2_Profit_Convergence.png`
- Fig. 3 -> `figures/Fig3_Residual_Convergence.png`
- Fig. 4 -> `figures/Fig4_Crypto_Overhead.png`
- Fig. 5 -> `figures/Fig5_Profit_Comparison.png`
- Fig. 6 -> `figures/Fig6_Power_Profile_N4.png`
- Fig. 7 -> `figures/Fig7_Profit_Comparison.png`
- Fig. 8 -> `figures/Fig8_Time_Comparison.png`
- Fig. 9 -> `figures/Fig9_Scalability.png`
- Fig. 10 -> `figures/Fig10_DP_Comparison.png`

## Notes

- The code uses CVXPY with solver fallback where available.
- `gurobipy` requires a valid Gurobi installation and license.
- If some CSV files are missing, run `run.py` first and then run `plot.py`.

---

# PriBSCS 复现实验包（中文）

本文件包含 PriBSCS 论文复现实验的主要使用说明和项目信息。

## 目录说明

- `run.py`：运行主实验并导出结果 CSV。
- `sensitivity.py`：运行 ADMM 罚参数敏感性实验并导出表格数据。
- `plot.py`：基于 `data_results/` 生成与论文编号对齐的图（Fig.2-Fig.10）。
- `data_results/`：用于绘图和结果报告的结果数据。
- `figures/`：生成后的图文件。
- `requirements.txt`：Python 依赖列表。

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
python sensitivity.py
python plot.py
```

## 图号对应关系

- Fig.2 -> `figures/Fig2_Profit_Convergence.png`
- Fig.3 -> `figures/Fig3_Residual_Convergence.png`
- Fig.4 -> `figures/Fig4_Crypto_Overhead.png`
- Fig.5 -> `figures/Fig5_Profit_Comparison.png`
- Fig.6 -> `figures/Fig6_Power_Profile_N4.png`
- Fig.7 -> `figures/Fig7_Profit_Comparison.png`
- Fig.8 -> `figures/Fig8_Time_Comparison.png`
- Fig.9 -> `figures/Fig9_Scalability.png`
- Fig.10 -> `figures/Fig10_DP_Comparison.png`

## 说明

- 代码通过 CVXPY 调用求解器，并在可用时使用回退链。
- 若使用 `gurobipy`，需要本机具备有效 Gurobi 安装与许可证。
- 若缺少绘图所需 CSV，请先运行 `run.py`，再运行 `plot.py`。
