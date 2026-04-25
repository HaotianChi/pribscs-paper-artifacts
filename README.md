# PriBSCS Reproducibility Package

This repository contains the code and data package for reproducing the PriBSCS paper experiments.

## Project Overview

The system model is shown below.

![PriBSCS system model](docs/system-model.png)

Main documentation has been moved to:
- English + 中文: `docs/README.md`

## Quick Links

- Core scripts: `run.py`, `sensitivity.py`, `plot.py`
- Results data: `data_results/`
- Figures: `figures/`
- Dependencies: `requirements.txt`

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
python sensitivity.py
python plot.py
```

---

# PriBSCS 复现实验包（中文）

本仓库用于复现 PriBSCS 论文实验。

## 项目简介

系统模型配图如下：

![PriBSCS system model](docs/system-model.png)

主要说明文档已迁移至：
- 英文 + 中文：`docs/README.md`
