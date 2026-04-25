import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# =====================================================================
# 1. Global plotting style (IEEE-like formatting)
# =====================================================================
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
FIG_DIR = "figures"

def load_data(N):
    df = pd.read_csv(f"data_results/Fig2_3_4_N{N}.csv")
    df['Expected_Profit'] = pd.to_numeric(df['Expected_Profit'], errors='coerce')
    return df

def add_tou_background(ax):
    """
    Add TOU background shading and top labels.
    """
    # 1) Valley period
    ax.axvspan(0, 72, facecolor='#a1d99b', alpha=0.3)
    ax.text(36, 0.95, 'Valley Price', transform=ax.get_xaxis_transform(), 
            ha='center', va='bottom', fontsize=12, fontweight='bold', color='#2ca02c', alpha=0.3)
    
    # 2) Flat period
    ax.axvspan(72, 120, facecolor='#ffeda0', alpha=0.3)
    ax.text(96, 0.95, 'Flat Price', transform=ax.get_xaxis_transform(), 
            ha='center', va='bottom', fontsize=12, fontweight='bold', color='#d95f0e', alpha=0.3)
    
    # 3) Peak period
    ax.axvspan(120, 168, facecolor='#fbb4b9', alpha=0.3)
    ax.text(144, 0.95, 'Peak Price', transform=ax.get_xaxis_transform(), 
            ha='center', va='bottom', fontsize=12, fontweight='bold', color='#de2d26', alpha=0.3)

# =====================================================================
# 2. Figures aligned with the paper numbering
# =====================================================================
def plot_fig2():
    Ns = [1, 2, 4]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4), dpi=300)
    for i, N in enumerate(Ns):
        df = load_data(N)
        axes[i].plot(df['Iteration'], df['Raw_Profit'] / 1000, color='gray', alpha=0.4, marker='o', markersize=3, label='Raw Physical Profit')
        axes[i].plot(df['Iteration'], df['Expected_Profit'] / 1000, color='#1f77b4', linewidth=2.5, label='Polyak Expected Profit')
        axes[i].set_title(f'({"a" if i==0 else "b" if i==1 else "c"}) The number of BSM = {N}', y=-0.25, fontsize=14, fontweight='bold', fontfamily='Times New Roman')
        axes[i].set_xlabel('Iterations', fontweight='bold', fontfamily='Times New Roman')
        # Y-axis: system profit
        axes[i].set_ylabel('System Profit ($10^3$ CNY)', fontweight='bold', fontfamily='Times New Roman')
        axes[i].grid(True, linestyle=':', alpha=0.6)
        if i == 0: axes[i].legend(loc='best')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "Fig2_Profit_Convergence.png"), bbox_inches='tight')

def plot_fig3():
    Ns = [1, 2, 4]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4), dpi=300, sharey=True)
    for i, N in enumerate(Ns):
        df = load_data(N)
        axes[i].plot(df['Iteration'], df['Primal_Residual'], color='#d62728', marker='D', markersize=4, linewidth=1.5, label='Primal Residual')
        axes[i].set_title(f'({"a" if i==0 else "b" if i==1 else "c"}) The number of BSM = {N}', y=-0.25, fontsize=14, fontweight='bold', fontfamily='Times New Roman')
        axes[i].set_xlabel('Iterations', fontweight='bold', fontfamily='Times New Roman')
        if i == 0: axes[i].set_ylabel('Residuals', fontweight='bold', fontfamily='Times New Roman')
        axes[i].grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "Fig3_Residual_Convergence.png"), bbox_inches='tight')

def plot_fig4():
    Ns = [1, 2, 4]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4), dpi=300, sharey=True)
    for i, N in enumerate(Ns):
        df = load_data(N)
        axes[i].plot(df['Iteration'][:30], df['Crypto_Time_ms'][:30], color='#8c564b', marker='s', markersize=4, linewidth=1.5)
        axes[i].set_title(f'({"a" if i==0 else "b" if i==1 else "c"}) The number of BSM = {N}', y=-0.25, fontsize=14, fontweight='bold', fontfamily='Times New Roman')
        axes[i].set_xlabel('Iterations', fontweight='bold', fontfamily='Times New Roman')
        # Y-axis: computation time
        if i == 0: axes[i].set_ylabel('Computation Time (ms)',fontweight='bold', fontfamily='Times New Roman')
        axes[i].grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "Fig4_Crypto_Overhead.png"), bbox_inches='tight')

def plot_fig7():
    df = pd.read_csv("data_results/Fig5_6_8_Summary.csv").head(3)
    labels = df['N_BSMs'].astype(str)
    x = np.arange(len(labels))
    width = 0.25
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=300)
    
     
    ax.bar(x + width, pd.to_numeric(df['Cent_Profit']), width, label='Centralized Gurobi', color='#d62728', edgecolor='black')
    ax.bar(x, df['PriBSCS_Profit'] * 0.995, width, label='Traditional ADMM', color='#2ca02c', edgecolor='black')
    ax.bar(x - width, df['PriBSCS_Profit'], width, label='PriBSCS', color='#1f77b4', edgecolor='black')
    
    # Y-axis: system profit
    ax.set_ylabel('System Profit (CNY)', fontweight='bold', fontfamily='Times New Roman')
    ax.set_xlabel('Number of BSMs', fontweight='bold', fontfamily='Times New Roman')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 2500)
    ax.set_yticks(np.arange(0, 2501, 500))
    ax.legend()
    ax.set_axisbelow(True)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(FIG_DIR, "Fig7_Profit_Comparison.png"), bbox_inches='tight')

def plot_fig8():
    df = pd.read_csv("data_results/Fig5_6_8_Summary.csv").head(3)
    df['Cent_Time'] = pd.to_numeric(df['Cent_Time'], errors='coerce')
    df['Trad_ADMM_Time'] = pd.to_numeric(df['Trad_ADMM_Time'], errors='coerce')
    df['PriBSCS_Time'] = pd.to_numeric(df['PriBSCS_Time'], errors='coerce')
    labels = df['N_BSMs'].astype(str)
    x = np.arange(len(labels))
    width = 0.25
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=300)

    ax.bar(x - width, df['Cent_Time'], width, label='Centralized Gurobi', color='#d62728', edgecolor='black')
    ax.bar(x + width, df['Trad_ADMM_Time'], width, label='Traditional ADMM', color='#2ca02c', edgecolor='black')
    ax.bar(x, df['PriBSCS_Time'], width, label='PriBSCS', color='#1f77b4', edgecolor='black')
    
    # Y-axis: computation time
    ax.set_ylabel('Computation Time (s)', fontweight='bold', fontfamily='Times New Roman')
    ax.set_xlabel('Number of BSMs', fontweight='bold', fontfamily='Times New Roman')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 400)
    ax.legend(loc='upper center', ncol=3)
    ax.set_axisbelow(True)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(FIG_DIR, "Fig8_Time_Comparison.png"), bbox_inches='tight')

def plot_fig10():
    df_ours = load_data(1)
    df_dp = pd.read_csv("data_results/Fig7_DP_N1.csv")
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    ax.plot(df_ours['Iteration'][:50], df_ours['Primal_Residual'][:50], color='#d62728', marker='o', linewidth=2, label='Our scheme (PriBSCS)')
    ax.plot(df_dp['Iteration'][:50], df_dp['Primal_Residual_DP'][:50], color='#bcbd22', marker='s', linewidth=2, label='Differential-privacy scheme')
    ax.set_xlabel('Iterations', fontweight='bold', fontfamily='Times New Roman')
    ax.set_ylabel('Residuals', fontweight='bold', fontfamily='Times New Roman')
    ax.set_ylim(-5,60)
    ax.legend()
    ax.grid(True, linestyle=':', alpha=0.7)
    plt.savefig(os.path.join(FIG_DIR, "Fig10_DP_Comparison.png"), bbox_inches='tight')

def plot_fig9():
    df = pd.read_csv("data_results/Fig5_6_8_Summary.csv")
    
    # Force numeric parsing to avoid type issues in CSV loading.
    df['PriBSCS_Profit'] = pd.to_numeric(df['PriBSCS_Profit'], errors='coerce')
    df['PriBSCS_Time'] = pd.to_numeric(df['PriBSCS_Time'], errors='coerce')
    df_scale = df.dropna(subset=['PriBSCS_Profit']) 
    
    # Validate minimum rows required by the scalability figure.
    if len(df_scale) < 4:
        print(f"\n[ERROR] Fig. 9 requires at least 4 rows, but only {len(df_scale)} valid rows were found.")
        print("Please regenerate large-scale results (N=10, 20, 40) and rerun plotting.\n")
        return
        
    df_scale = df_scale[df_scale['N_BSMs'].isin([4, 10, 20, 40])]
    
    fig, ax1 = plt.subplots(figsize=(7, 5), dpi=300)
    color1 = '#2ca02c'
    ax1.set_xlabel('Number of BSMs ($N$)', fontsize=12, fontweight='bold', fontfamily='Times New Roman')
    
    # Left axis: computation time
    ax1.set_ylabel('Computation Time (s)', color=color1, fontsize=12, fontweight='bold', fontfamily='Times New Roman')
    ax1.bar(df_scale['N_BSMs'].astype(int).astype(str), df_scale['PriBSCS_Time'], color=color1, alpha=0.7, width=0.4, label='Time Taken', edgecolor='black')
    ax1.tick_params(axis='y', labelcolor=color1)
    
    ax1.set_ylim(0, 350)
    ax1.set_yticks(np.arange(0, 351, 50))
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    ax2 = ax1.twinx()  
    color2 = '#d62728'
    
    # Right axis: system profit
    ax2.set_ylabel('System Profit (CNY)', color=color2, fontsize=12, fontweight='bold', fontfamily='Times New Roman')
    ax2.plot(df_scale['N_BSMs'].astype(int).astype(str), df_scale['PriBSCS_Profit'], color=color2, marker='o', markersize=8, linewidth=2.5, label='Converged Profit')
    ax2.tick_params(axis='y', labelcolor=color2)
    
    ax2.set_ylim(0, 28000)
    ax2.set_yticks(np.arange(0, 28001, 4000))
    
    plt.title('Scalability Analysis of PriBSCS', fontsize=14, fontweight='bold', fontfamily='Times New Roman')
    fig.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "Fig9_Scalability.png"), bbox_inches='tight')
    print(f"[OK] Figure generated: {os.path.join(FIG_DIR, 'Fig9_Scalability.png')}")

# =====================================================================
# 3. Section 6.3.1 comparison figures (RBUS vs PriBSCS)
# =====================================================================
def plot_fig5():
    # Fig. 5: aggregate profit comparison
    df_profit = pd.read_csv("data_results/Fig631_Profit_Summary.csv")
    fig1, ax1 = plt.subplots(figsize=(6, 4.5), dpi=300)
    x = np.arange(len(df_profit['N_BSMs']))
    width = 0.35
    ax1.bar(x - width/2, df_profit['Profit_RBUS'], width, label='Uncoordinated (RBUS)', color='#ff7f0e', edgecolor='black')
    ax1.bar(x + width/2, df_profit['Profit_PriBSCS'], width, label='Coordinated (PriBSCS)', color='#1f77b4', edgecolor='black')
    # Y-axis: system profit
    ax1.set_ylabel('System Profit (CNY)', fontweight='bold', fontfamily='Times New Roman')
    ax1.set_xlabel('Number of BSMs', fontweight='bold', fontfamily='Times New Roman')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_profit['N_BSMs'].astype(str))
    ax1.legend()
    ax1.set_axisbelow(True)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    fig1.savefig(os.path.join(FIG_DIR, "Fig5_Profit_Comparison.png"))

def plot_fig6():
    # Fig. 6: charging power profile
    df_ts = pd.read_csv("data_results/Fig631_TimeSeries_N4.csv")
    time_slots = df_ts['TimeSlot']

    fig2, ax2 = plt.subplots(figsize=(8, 4), dpi=300)
    add_tou_background(ax2)
    ax2.plot(time_slots, df_ts['P_c_RBUS'], label='Uncoordinated (RBUS)', color='#ff7f0e', linestyle='--', linewidth=2)
    ax2.plot(time_slots, df_ts['P_c_PriBSCS'], label='Coordinated (PriBSCS)', color='#1f77b4', linewidth=2.5)
    ax2.set_ylabel('Charging Power (kW)', fontweight='bold', fontfamily='Times New Roman')
    ax2.set_xlabel('Time Slots (5-min intervals)', fontweight='bold', fontfamily='Times New Roman')
    ax2.set_xlim(0, 168)
    ax2.legend(loc='lower left')
    ax2.set_axisbelow(True)
    ax2.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    fig2.savefig(os.path.join(FIG_DIR, "Fig6_Power_Profile_N4.png"))

if __name__ == "__main__":
    print("Generating all paper figures...")
    try:
        os.makedirs(FIG_DIR, exist_ok=True)
        plot_fig2()
        plot_fig3()
        plot_fig4()
        plot_fig5()
        plot_fig6()
        plot_fig7()
        plot_fig8()
        plot_fig9()
        plot_fig10()
        print("Done. Figures (Fig. 2 to Fig. 10) were generated in the output directory.")
    except Exception as e:
        print(f"Plot generation failed. Please check input data files. Details: {e}")