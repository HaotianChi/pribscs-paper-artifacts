import csv
import importlib.util
import os
from pathlib import Path
from statistics import mean

# ---------------------------------------------------------------------
# Sensitivity study for the ADMM penalty parameter rho used in PriBSCS.
# This script reuses the simulation engine defined in run.py and produces
# a CSV summary that can be directly used to populate Table tab_rho_sensitivity.
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
RUN_PY = BASE_DIR / "run.py"
OUTPUT_DIR = BASE_DIR / "data_results"
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_CSV = OUTPUT_DIR / "Table_rho_sensitivity.csv"


def load_run_module():
    spec = importlib.util.spec_from_file_location("pribscs_run", RUN_PY)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def first_stop_iteration(logs, tol):
    """Return the first iteration index (1-based) whose primal residual reaches tol.
    If the stopping rule is never met, return None.
    """
    for log in logs:
        if float(log["primal_norm"]) <= tol:
            return int(log["iter"])
    return None



def classify_behavior(logs, tol):
    """Simple qualitative label for table reporting.

    Heuristic rules:
    - never reaches tol and final residual much larger than tol -> slow residual decay
    - reaches tol but tail residuals fluctuate strongly -> increased oscillation
    - otherwise -> stable
    """
    stop_iter = first_stop_iteration(logs, tol)
    residuals = [float(log["primal_norm"]) for log in logs]
    tail = residuals[max(0, len(residuals) - 20):]
    tail_mean = mean(tail) if tail else residuals[-1]
    tail_span = (max(tail) - min(tail)) if len(tail) >= 2 else 0.0

    if stop_iter is None:
        return "slow residual decay"

    # If the tail swings a lot relative to the achieved level, call it oscillatory.
    if tail_mean > 0 and tail_span / max(tail_mean, 1e-12) > 0.5:
        return "increased oscillation"

    return "stable"



def run_case(run_mod, n_bsms, p_cap, rho, max_iter=200):
    logs, avg_profit, total_time, _, _ = run_mod.run_simulation(
        N_BSMs=n_bsms,
        P_cap=p_cap,
        rho=rho,
        MAX_ITER=max_iter,
    )
    stop_iter = first_stop_iteration(logs, run_mod.cp_value_delta if False else 1e-6)
    # Use the same tolerance reported in the paper.
    tol = 1e-6
    stop_iter = first_stop_iteration(logs, tol)
    behavior = classify_behavior(logs, tol)
    final_residual = float(logs[-1]["primal_norm"]) if logs else float("nan")

    return {
        "Setting": f"N={n_bsms}",
        "P_cap_kW": p_cap,
        "rho": rho,
        "Iterations_to_stop": stop_iter if stop_iter is not None else ">200",
        "Averaged_Profit_CNY": round(float(avg_profit), 4),
        "Final_Primal_Residual": round(final_residual, 8),
        "Convergence_Behavior": behavior,
        "Total_Runtime_s": round(float(total_time), 4),
    }



def main():
    run_mod = load_run_module()

    # Recommended representative settings for the minor-revision sensitivity study.
    cases = [
        # Small-scale representative case
        {"N": 4, "P_cap": 70.0, "rhos": [1.0, 5.0, 10.0, 20.0, 40.0]},
        # Large-scale representative case
        {"N": 20, "P_cap": 400.0, "rhos": [0.1, 0.5, 1.0, 2.0]},
    ]

    rows = []
    for case in cases:
        n_bsms = case["N"]
        p_cap = case["P_cap"]
        for rho in case["rhos"]:
            print(f"\n=== Running sensitivity case: N={n_bsms}, P_cap={p_cap}, rho={rho} ===")
            row = run_case(run_mod, n_bsms=n_bsms, p_cap=p_cap, rho=rho)
            rows.append(row)

    fieldnames = [
        "Setting",
        "P_cap_kW",
        "rho",
        "Iterations_to_stop",
        "Averaged_Profit_CNY",
        "Final_Primal_Residual",
        "Convergence_Behavior",
        "Total_Runtime_s",
    ]

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("\nSaved sensitivity summary to:")
    print(OUTPUT_CSV)
    print("\nRows:")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
