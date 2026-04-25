import numpy as np
import cvxpy as cp
from phe import paillier
import time
import os
import csv

# =====================================================================
# Module 1: Global experiment configuration (Section 6.1)
# =====================================================================
T = 168  
theta_0_new = 0.40  
TOU_price = np.concatenate([np.full(72, 0.3), np.full(48, 0.6), np.full(48, 0.9)])
alpha = 0.00015     
E_b = 50.0          
delta_SoC = 0.6     
eta_c = 0.9
S_bays = 4         
np.random.seed(42)  
D_t = np.round(np.random.normal(S_bays, 2, T)) 
D_t = np.clip(D_t, 0, S_bays) 

N_capacity = 40  # Physical battery inventory capacity


def solve_with_fallback(problem, primary_solver, fallback_solvers=None, verbose=False):
    """
    Solve a CVXPY problem with ordered solver fallback.
    Returns (solver_name, status).
    """
    if fallback_solvers is None:
        fallback_solvers = []

    solvers = [primary_solver] + list(fallback_solvers)
    last_error = None

    for solver in solvers:
        try:
            problem.solve(solver=solver, verbose=verbose)
            return solver, problem.status
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"All solvers failed. Last error: {last_error}")

# =====================================================================
# Module 2: RBUS baseline simulator
# =====================================================================
def run_rbus(N_BSMs, P_cap):
    total_profit = 0.0
    bcm_inventory = 0.0 
    bsm_inventories = np.full(N_BSMs, 10.0)
    P_c_record = np.zeros(T)

    for t in range(T):
        P_charge = P_cap if TOU_price[t] <= 0.6 else 0.0
        P_c_record[t] = P_charge
        
        produced_batteries = (P_charge * (5/60) * eta_c) / (E_b * delta_SoC)
        bcm_inventory += produced_batteries
        
        dispatch_per_bsm = bcm_inventory / N_BSMs
        for i in range(N_BSMs):
            bsm_inventories[i] = min(bsm_inventories[i] + dispatch_per_bsm, N_capacity)
        bcm_inventory = 0.0 
        
        for i in range(N_BSMs):
            actual_demand = D_t[t]
            served = min(actual_demand, bsm_inventories[i])
            bsm_inventories[i] -= served
            total_profit += served * ((theta_0_new + TOU_price[t]) * E_b * delta_SoC)
        total_profit -= P_charge * (5/60) * TOU_price[t]
        total_profit -= P_charge * (5/60) * alpha
        
    return total_profit, P_c_record

# =====================================================================
# Module 3: Optimization model and subsystem solvers
# =====================================================================
class BCM_Subsystem:
    def __init__(self, P_cap):
        self.pub_key, self.priv_key = paillier.generate_paillier_keypair(n_length=1024)
        self.delta_Q_val = np.zeros(T) 
        self.dual_lambda = np.zeros(T)
        self.P_cap = P_cap
        self.current_P_c = np.zeros(T) # Track physical charging profile

    def local_optimization(self, residual_prev, rho):
        t0 = time.time()
        P_c = cp.Variable(T)                          
        delta_Q3 = cp.Variable(T)  
        
        constraints = [P_c >= 0, P_c <= self.P_cap, delta_Q3 >= 0]
        delta_t = 5 / 60  
        constraints += [P_c * delta_t * eta_c >= delta_Q3 * E_b * delta_SoC]
        
        imbalance = delta_Q3 - self.delta_Q_val + residual_prev
        energy_kWh = P_c * delta_t
        cost_ch = cp.sum(cp.multiply(TOU_price, energy_kWh)) 
        cost_deg = alpha * cp.sum(energy_kWh)                  
        
        objective = cp.Minimize(cost_ch + cost_deg + self.dual_lambda.T @ imbalance + (rho / 2) * cp.sum_squares(imbalance))
        prob = cp.Problem(objective, constraints)
        prob.solve(solver=cp.CLARABEL, verbose=False)
        
        self.raw_delta_Q = delta_Q3.value if delta_Q3.value is not None else np.zeros(T)
        self.delta_Q_val = np.round(self.raw_delta_Q * 1000) / 1000
        self.current_P_c = P_c.value if P_c.value is not None else np.zeros(T)

        pure_cost = (cost_ch.value + cost_deg.value) if cost_ch.value is not None else 0.0
        return pure_cost, time.time() - t0

    def encrypt_state(self):
        t0 = time.time()
        enc = [self.pub_key.encrypt(float(x)) for x in self.delta_Q_val]
        return enc, time.time() - t0

    def decrypt_and_update_dual(self, enc_residual_array, rho, dp_noise_scale=0.0):
        t0 = time.time()
        residual = np.array([self.priv_key.decrypt(enc_val) for enc_val in enc_residual_array])
        if dp_noise_scale > 0:
            residual += np.random.laplace(0, dp_noise_scale, T)
        self.dual_lambda += rho * residual
        return residual, time.time() - t0

class BSM_Subsystem:
    def __init__(self, id, pub_key):
        self.id = id
        self.pub_key = pub_key
        self.v_val = np.zeros(T) 
        self.current_S_swap = np.zeros(T)

    def local_optimization(self, residual_prev, dual_lambda, rho):
        t0 = time.time()
        S_swap = cp.Variable(T) 
        c_inv = cp.Variable(T)  
        v = cp.Variable(T)                    
        
        constraints = [
            S_swap >= 0, S_swap <= D_t, 
            c_inv >= 0, c_inv <= N_capacity, c_inv[0] == 10, 
            v >= 0
        ]

        for t in range(T - 1):
            constraints += [v[t] == c_inv[t+1] - c_inv[t] + S_swap[t]]
        constraints += [v[T-1] == S_swap[T-1]] 
        
        imbalance = residual_prev + self.v_val - v
        revenue = cp.sum(cp.multiply((theta_0_new + TOU_price), S_swap) * E_b * delta_SoC)
        
        objective = cp.Minimize(-revenue + dual_lambda.T @ imbalance + (rho / 2) * cp.sum_squares(imbalance))
        prob = cp.Problem(objective, constraints)
        prob.solve(solver=cp.CLARABEL, verbose=False)
        
        self.raw_v_val = v.value if v.value is not None else np.zeros(T)
        self.v_val = np.round(self.raw_v_val * 1000) / 1000
        self.current_S_swap = S_swap.value if S_swap.value is not None else np.zeros(T)
        
        pure_revenue = revenue.value if revenue.value is not None else 0.0
        return pure_revenue, time.time() - t0

    def encrypt_state(self):
        t0 = time.time()
        enc = [self.pub_key.encrypt(float(-val)) for val in self.v_val]
        return enc, time.time() - t0

# =====================================================================
# Module 4: Centralized benchmark solver
# =====================================================================
def solve_centralized(N_BSMs, P_cap):
    print(f"  [Benchmark] Solving centralized MIP (N={N_BSMs})...")
    t0 = time.time()
    P_c = cp.Variable(T)
    # Keep the centralized benchmark as a true MIP baseline.
    delta_Q3 = cp.Variable(T, integer=True)
    S_swaps = [cp.Variable(T, integer=True) for _ in range(N_BSMs)]
    c_invs = [cp.Variable(T, integer=True) for _ in range(N_BSMs)]
    vs = [cp.Variable(T, integer=True) for _ in range(N_BSMs)]

    constraints = [P_c >= 0, P_c <= P_cap, delta_Q3 >= 0]
    constraints += [P_c * (5/60) * eta_c >= delta_Q3 * E_b * delta_SoC]
    constraints += [delta_Q3 == sum(vs)]

    total_revenue = 0
    for i in range(N_BSMs):
        constraints += [
            S_swaps[i] >= 0, S_swaps[i] <= D_t, 
            c_invs[i] >= 0, c_invs[i] <= N_capacity, c_invs[i][0] == 10, 
            vs[i] >= 0
        ]
        for t in range(T - 1):
            constraints += [vs[i][t] == c_invs[i][t+1] - c_invs[i][t] + S_swaps[i][t]]
        constraints += [vs[i][T-1] == S_swaps[i][T-1]]
        total_revenue += cp.sum(cp.multiply((theta_0_new + TOU_price), S_swaps[i]) * E_b * delta_SoC)

    cost_ch = cp.sum(cp.multiply(TOU_price, P_c * (5/60)))
    cost_deg = alpha * cp.sum(P_c * (5/60))

    objective = cp.Maximize(total_revenue - cost_ch - cost_deg)
    prob = cp.Problem(objective, constraints)
    solver_used, status = solve_with_fallback(
        prob,
        primary_solver=cp.GUROBI,
        fallback_solvers=[cp.SCIP, cp.CLARABEL],
        verbose=False,
    )
    print(f"  [Benchmark] Solver: {solver_used}, Status: {status}")
    
    return prob.value if prob.value else 0.0, time.time() - t0

# =====================================================================
# Module 5: Integrated distributed simulation engine
# =====================================================================
def run_simulation(
    N_BSMs,
    P_cap,
    rho=0.5,
    MAX_ITER=200,
    BURN_IN=40,
    dp_noise=0.0,
    stop_tol=1e-6,
):
    mode_str = "DP-Noise" if dp_noise > 0 else f"PriBSCS (rho={rho})"
    print(f"\n[Run] {mode_str} | BSMs: {N_BSMs}, transformer limit: {P_cap} kW")
    bcm = BCM_Subsystem(P_cap)
    bsms = [BSM_Subsystem(id=i, pub_key=bcm.pub_key) for i in range(N_BSMs)]
    global_residual = np.zeros(T)
    
    logs = []
    total_parallel_time_s = 0.0

    best_residual = float('inf')
    best_P_c_record = np.zeros(T)

    for it in range(MAX_ITER):
        # 1) Local optimization
        cost_bcm, t_opt_bcm = bcm.local_optimization(global_residual, rho)
        rev_bsms_res = [bsm.local_optimization(global_residual, bcm.dual_lambda, rho) for bsm in bsms]
        raw_profit = sum([res[0] for res in rev_bsms_res]) - cost_bcm 
        t_opt_bsms = [res[1] for res in rev_bsms_res]
        
        # 2) Encryption
        enc_bcm, t_enc_bcm = bcm.encrypt_state() 
        enc_bsms_res = [bsm.encrypt_state() for bsm in bsms]
        enc_bsms = [res[0] for res in enc_bsms_res]
        t_enc_bsms = [res[1] for res in enc_bsms_res]
        
        # 3) Encrypted aggregation
        t_agg_start = time.time()
        enc_residual = []
        for t in range(T):
            sum_t = enc_bcm[t]
            for b_enc in enc_bsms:
                sum_t = sum_t + b_enc[t]
            enc_residual.append(sum_t)
        t_agg = time.time() - t_agg_start

        # 4) Decryption and dual update
        global_residual, t_dec_bcm = bcm.decrypt_and_update_dual(enc_residual, rho, dp_noise_scale=dp_noise)
        
        # Runtime statistics and logging
        iter_parallel_time = max(t_opt_bcm, max(t_opt_bsms)) + max(t_enc_bcm, max(t_enc_bsms)) + t_agg + t_dec_bcm
        iter_crypto_only_ms = (max(t_enc_bcm, max(t_enc_bsms)) + t_agg + t_dec_bcm) * 1000
        total_parallel_time_s += iter_parallel_time
        
        primal_norm = np.linalg.norm(global_residual)
        logs.append({
            "iter": it + 1, 
            "raw_profit": raw_profit, 
            "primal_norm": primal_norm, 
            "crypto_time_ms": iter_crypto_only_ms
        })

        # Track best residual after burn-in
        if it >= BURN_IN and primal_norm < best_residual:
            best_residual = primal_norm
            best_P_c_record = np.copy(bcm.current_P_c)

        if (it+1) % 50 == 0 or it == 0:
            print(f" Iter {it+1:03d} | Residual: {primal_norm:>6.1f} | Profit: {raw_profit:>7.1f} | Best residual: {best_residual:>6.1f}")

        # Paper-consistent stopping rule: decoded primal residual threshold.
        if primal_norm <= stop_tol:
            print(f" [Stop] ||r||={primal_norm:.3e} <= {stop_tol:.1e}, terminated at iteration {it+1}")
            break

    steady_profits = [log["raw_profit"] for log in logs[BURN_IN:]]
    if len(steady_profits) == 0:
        # If the algorithm converges before burn-in, fall back to full-history averaging.
        fallback_profits = [log["raw_profit"] for log in logs]
        expected_profits = np.cumsum(fallback_profits) / np.arange(1, len(fallback_profits) + 1)
    else:
        expected_profits = np.cumsum(steady_profits) / np.arange(1, len(steady_profits) + 1)

    for i, log in enumerate(logs):
        if len(steady_profits) == 0:
            log["expected_profit"] = expected_profits[i]
        else:
            log["expected_profit"] = expected_profits[i - BURN_IN] if i >= BURN_IN else ""
        
    return logs, expected_profits[-1], total_parallel_time_s, best_P_c_record

# =====================================================================
# Module 6: Batch execution and result export
# =====================================================================
if __name__ == "__main__":
    os.makedirs("data_results", exist_ok=True)
    
    # Feature switches
    RUN_DP = False
    RUN_LARGE_SCALE = False

    small_scale_rho = 20
    large_scale_rho = 0.5

    baseline_configs = [(1, 50.0), (2, 60.0), (4, 70.0)]
    # baseline_configs = []  # Use this to run large-scale cases only.

    summary_results_568 = []
    summary_results_631 = []


    print("==========================================================")
    print(" Stage 1: baseline performance and Section 6.3.1 comparison (N=1,2,4)")
    print("==========================================================")
    for N, P in baseline_configs:
        # 1) RBUS baseline
        prof_r, P_c_r = run_rbus(N, P)
        
        # 2) PriBSCS run
        logs, final_profit, parallel_time, P_c_p = run_simulation(N_BSMs=N, P_cap=P, rho=small_scale_rho, MAX_ITER=200)
        
        # 3) Centralized benchmark
        cent_profit, cent_time = solve_centralized(N_BSMs=N, P_cap=P)
        print(f"  [Benchmark] Profit: {cent_profit:.1f} CNY | Runtime: {cent_time:.2f}s\n")
        
        # Collect summary data for Fig. 7, Fig. 8, and Fig. 9
        trad_admm_time = parallel_time - sum([lg["crypto_time_ms"]/1000 for lg in logs])
        summary_results_568.append([N, P, final_profit, cent_profit, parallel_time, trad_admm_time, cent_time])
        
        # Collect summary data for Fig. 5 and Fig. 6
        summary_results_631.append([N, P, prof_r, final_profit])
        
        # Save timeseries data for Fig. 2, Fig. 3, and Fig. 4
        with open(f"data_results/Fig2_3_4_N{N}.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Iteration", "Raw_Profit", "Expected_Profit", "Primal_Residual", "Crypto_Time_ms"])
            for log in logs:
                writer.writerow([log["iter"], log["raw_profit"], log["expected_profit"], log["primal_norm"], log["crypto_time_ms"]])

        # Save N=4 trajectories for Fig. 6
        if N == 4:
            with open("data_results/Fig631_TimeSeries_N4.csv", "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["TimeSlot", "P_c_RBUS", "P_c_PriBSCS"])
                for t in range(T):
                    writer.writerow([t, P_c_r[t], P_c_p[t]])

    # Save aggregate summary for Fig. 5
    with open("data_results/Fig631_Profit_Summary.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["N_BSMs", "P_cap_kW", "Profit_RBUS", "Profit_PriBSCS"])
        for row in summary_results_631:
            writer.writerow(row)

    print("==========================================================")
    print(" Stage 2: differential privacy (DP) and large-scale scalability")
    print("==========================================================")
    if RUN_DP:
        logs_dp, _, _, _ = run_simulation(N_BSMs=1, P_cap=50.0, rho=small_scale_rho, MAX_ITER=100, dp_noise=1.5)
        with open(f"data_results/Fig7_DP_N1.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Iteration", "Primal_Residual_DP"])
            for log in logs_dp:
                writer.writerow([log["iter"], log["primal_norm"]])

    # Run large-scale scalability cases (N=10,20,40)
    if RUN_LARGE_SCALE:
        scale_configs = [(10, 200.0), (20, 400.0), (40, 800.0)]
        for N, P in scale_configs:
            # Large-scale setting uses rho=0.5 for stable residual behavior.
            _, final_profit, parallel_time, _ = run_simulation(N_BSMs=N, P_cap=P, rho=0.5, MAX_ITER=200)
            summary_results_568.append([N, P, final_profit, "", parallel_time, "", ""])

    # Smart write-back: load historical rows, merge new rows, then write.
    summary_file = "data_results/Fig5_6_8_Summary.csv"
    header = ["N_BSMs", "P_cap_kW", "PriBSCS_Profit", "Cent_Profit", "PriBSCS_Time", "Trad_ADMM_Time", "Cent_Time"]
    
    merged_data = {}
    
    # 1) Load existing rows when the summary file already exists.
    if os.path.exists(summary_file):
        with open(summary_file, "r", newline='') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) >= 7:  # Keep only valid rows.
                    try:
                        n_val = int(row[0])
                        merged_data[n_val] = row
                    except ValueError:
                        pass
                        
    # 2) Merge newly generated rows.
    for row in summary_results_568:
        n_val = int(row[0])
        merged_data[n_val] = row
        
    # 3) Write merged rows back, sorted by N.
    with open(summary_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for n_val in sorted(merged_data.keys()):
            writer.writerow(merged_data[n_val])
            
    print("\n[OK] Summary merge completed. Historical rows were preserved and new rows were updated.")
    print("Next step: run plot.py to generate all figures.")