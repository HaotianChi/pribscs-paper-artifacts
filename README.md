# PriBSCS Reproducibility Package

[English](#pribscs-reproducibility-package) | [中文](#pribscs-复现实验包中文)

This repository contains the core scripts, result tables, and figure outputs for reproducing the PriBSCS paper experiments.

## Project Overview

The system model is shown below.

![PriBSCS system model](docs/system-model.png)

## Contents

- `run.py`: runs the main PriBSCS simulations and exports result CSV files.
- `sensitivity.py`: runs the ADMM penalty sensitivity study and exports Table-style CSV output.
- `plot.py`: generates paper-aligned figures from `data_results/`.
- `data_results/`: generated result data used for plots and reported metrics.
- `figures/`: generated figure files.
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

## Notes

- The code uses CVXPY with solver fallback where available.
- `gurobipy` requires a valid Gurobi installation and license.
- If some CSV files are missing, run `run.py` first and then run `plot.py`.

## Citation

If this codebase is useful in your research, citing the following paper is appreciated:

```bibtex
@article{chi2026pribscs,
  title={PriBSCS: privacy-preserving distributed coordination for battery swapping and charging systems},
  author={Chi, Haotian and Zuo, Fei and Sun, Zhuocheng and Geng, Haijun and Wang, Yuwei and Jiang, Shunrong},
  journal={Journal of King Saud University Computer and Information Sciences},
  year={2026},
  doi={10.1007/s44443-026-00761-z}
}
```

---

# PriBSCS 复现实验包（中文）

本仓库包含 PriBSCS 论文复现实验所需的核心代码、结果数据与图表输出文件。

## 项目简介

系统模型配图如下：

![PriBSCS system model](docs/system-model.png)

## 目录说明

- `run.py`：运行主实验并导出结果 CSV。
- `sensitivity.py`：运行 ADMM 罚参数敏感性实验并导出表格数据。
- `plot.py`：基于 `data_results/` 生成论文图表。
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

## 说明

- 代码通过 CVXPY 调用求解器，并在可用时使用回退链。
- 若使用 `gurobipy`，需要本机具备有效 Gurobi 安装与许可证。
- 若缺少绘图所需 CSV，请先运行 `run.py`，再运行 `plot.py`。

## 引用

如果本代码仓库对你的研究有帮助，欢迎引用以下论文：

```bibtex
@article{chi2026pribscs,
  title={PriBSCS: privacy-preserving distributed coordination for battery swapping and charging systems},
  author={Chi, Haotian and Zuo, Fei and Sun, Zhuocheng and Geng, Haijun and Wang, Yuwei and Jiang, Shunrong},
  journal={Journal of King Saud University Computer and Information Sciences},
  year={2026},
  doi={10.1007/s44443-026-00761-z}
}
```
