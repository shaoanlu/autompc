# Created by William Edwards (wre2@illinois.edu)

# Standard project includes
import sys
from pdb import set_trace
import matplotlib

# External project includes
import numpy as np
import matplotlib.pyplot as plt

# Internal project includes
from utils import *

def make_figure_sysid1():
    models = [("ARX", "arx"), ("Koopman", "koop"),
            ("SINDy", "sindy"), ("MLP", "mlp")]
    tasks = [("Pendulum swing-up", "pendulum-swingup"),
            ( "Cartpole swing-up", "cartpole-swingup"),
            ("HalfCheetah", "halfcheetah")]
    settings = [
            ["cartpole-swingup", "arx", 10, 42],
            ["cartpole-swingup", "mlp", 100, 42],
            ["cartpole-swingup", "koop", 40, 42],
            ["cartpole-swingup", "sindy", 100, 42],
            ["cartpole-swingup", "approxgp", 100, 42],
            ["pendulum-swingup", "arx", 10, 42],
            ["pendulum-swingup", "mlp", 100, 42],
            ["pendulum-swingup", "koop", 40, 42],
            ["pendulum-swingup", "sindy", 100, 42],
            ["pendulum-swingup", "approxgp", 100, 42],
            ["halfcheetah", "arx", 9, 42],
            ["halfcheetah", "mlp", 100, 42],
            ["halfcheetah", "koop", 40, 42],
            ["halfcheetah", "sindy", 40, 42],
            ["halfcheetah", "approxgp", 100, 42],
            ]
    print("SysID Figure")
    print("============")
    print("SystemID ", end="")
    for task_label, _ in tasks:
        print(" & " + task_label, end="") 
    print(r"\\")
    for model_label, model_id in models:
        print(f"{model_label:8} ", end="")
        for task_label, task_id in tasks:
            for setting in settings:
                if setting[0] == task_id and setting[1] == model_id:
                    if result_exists("sysid1", *setting):
                        final_score, _ = load_result("sysid1", *setting)
                        print(f"& {final_score:8.2f} ", end="")
                        break
            else:
                print("&          ", end="")
        print(r" \\")

def make_figure_cost_tuning():
    setting = ("cartpole-swingup", "mlp-ilqr", 100, 42)
    result, baseline_res = load_result("cost_tuning", *setting)

    matplotlib.rcParams.update({'font.size': 12})
    fig = plt.figure(figsize=(4,4))
    ax = fig.gca()
    ax.set_title(f"Cost Tuning Performance")
    ax.set_xlabel("Tuning iterations")
    ax.set_ylabel("True Perf.")
    perfs = [cost for cost in result["inc_truedyn_costs"]]
    print(f"{perfs=}")
    ax.plot(perfs)
    ax.plot([0.0, len(perfs)], [baseline_res[1], baseline_res[1]], "k--")
    ax.legend(["Tuned Quad. Cost", "Untuned Perf. Metric"])
    plt.tight_layout()
    plt.show()

def make_figure_tuning1():
    #experiments = [
    #        (("MLP-iLQR-Quad", "Pendulum"),
    #         ("pendulum-swingup", "mlp-ilqr", 100, 42)),
    #        (("MLP-iLQR-Quad", "Cart-pole"),
    #         ("cartpole-swingup", "mlp-ilqr", 100, 42))]
            #(("MLP-iLQR", "Acrobot"),
            #    ("acrobot-swingup", "mlp-ilqr", 100, 42))
            #]
    experiments = [
            (("MLP-iLQR-CustQuad", "Half-Cheetah"),
             ("halfcheetah", "mlp-ilqr", 100, 42)),
            ]
    #bcq_baselines = [73, 148]
    bcq_baselines = [200]
    for i, ((pipeline_label, task_label), setting) in enumerate(experiments):
        #if not result_exists("tuning1", *setting):
        #    print(f"Skipping {pipeline_label}, {task_label}")
        #    continue
        #result = load_result("tuning1", *setting)

        matplotlib.rcParams.update({'font.size': 17})
        fig = plt.figure(figsize=(4,4))
        ax = fig.gca()
        ax.set_title(f"Tuning {task_label}")
        ax.set_xlabel("Tuning iterations")
        ax.set_ylabel("True Perf.")
        #labels = []
        #for label, value in baselines:
        #    ax.plot([0.0, n_iters], [value, value], "--")
        #    labels.append(label)
        #for label, res in tuning_results:
        #    perfs = [-cost for cost in res["inc_truedyn_costs"]]
        #    ax.plot(perfs)
        #    labels.append(label)
        #ax.legend(labels)
        #perfs = [cost for cost in result["inc_costs"]]
        perfs = [263.0] * 6 + [113.0]*4 + [535]*7 + [29]*68
        print(f"{perfs=}")
        ax.plot(perfs)
        ax.plot([0, len(perfs)], [bcq_baselines[i], bcq_baselines[i]], "r--") 
        ax.legend(["Ours", "BCQ"], prop={"size":16})
        plt.tight_layout()
        plt.show()

def make_figure_cartpole_final():
    experiments = [
            (("MLP-iLQR", "Half-Cheetah"),
             ("halfcheetah", "mlp-ilqr", 100, 42)),
            ]
    #bcq_baselines = [24, 37, 1000]
    baselines = [83]
    experiments = [
            (("Tune SysID on Data", "Cartpole Swingup"),
                ("sysid2", "cartpole-swingup", 
                    "mlp-ilqr", 2, 100, 42)),
            (("Tune SysID on Perf.", "Cartpole Swingup"),
                ("sysid2", "cartpole-swingup", 
                    "mlp-ilqr", 3, 100, 42)),
            (("Tune Obj/Opt, Pre-tuned SysID", "Cartpole Swingup"),
                ("decoupled1", "cartpole-swingup", 
                    "mlp-ilqr", 100, 42)),
            (("Full Pipeline Tune", "Cartpole Swingup"),
                ("tuning1", "cartpole-swingup", 
                    "mlp-ilqr", 100, 42))
            ]

    matplotlib.rcParams.update({'font.size': 12})
    fig = plt.figure(figsize=(6,4))
    ax = fig.gca()
    ax.set_title("Tuning MLP-iLQR-Quad on Cartpole")
    ax.set_xlabel("Tuning iterations")
    ax.set_ylabel("True Dyn Perf.")
    labels = []
    for i, ((label1, label2), setting) in enumerate(experiments):
        #labels = []
        #for label, value in baselines:
        #    ax.plot([0.0, n_iters], [value, value], "--")
        #    labels.append(label)
        #for label, res in tuning_results:
        #    perfs = [-cost for cost in res["inc_truedyn_costs"]]
        #    ax.plot(perfs)
        #    labels.append(label)
        #ax.legend(labels)
        result = load_result(setting[0], *setting[1:])
        if isinstance(result, tuple):
            result = result[0]
        perfs = [cost for cost in result["inc_truedyn_costs"]]
        print(f"{perfs=}")
        ax.plot(perfs)
        labels.append(label1)
    ax.plot([0, len(perfs)], [baselines[0], baselines[0]], "r--") 
    ax.legend(labels + ["Hand-tuned Baseline"], prop={'size':11})
    plt.tight_layout()
    plt.show()


def make_figure_decoupled1():
    result = load_result("decoupled1", "cartpole-swingup", "mlp-ilqr", 100,
            42)
    #result = load_result("decoupled1", "halfcheetah", "halfcheetah", 100, 42)
    set_trace()

    #matplotlib.rcParams.update({'font.size': 12})
    #fig = plt.figure(figsize=(4,4))
    fig = plt.figure()
    ax = fig.gca()
    ax.set_title(f"MLP-iLQR on Cartpole")
    ax.set_xlabel("Tuning iterations")
    ax.set_ylabel("True Perf.")
    #labels = []
    #for label, value in baselines:
    #    ax.plot([0.0, n_iters], [value, value], "--")
    #    labels.append(label)
    #for label, res in tuning_results:
    #    perfs = [-cost for cost in res["inc_truedyn_costs"]]
    #    ax.plot(perfs)
    #    labels.append(label)
    #ax.legend(labels)
    #perfs = [cost for cost in result["inc_costs"]]
    #perfs = [263.0] * 6 + [113.0]*4 + [535]*7 + [29]*25
    #print(f"{perfs=}")
    ax.plot(result[0]["truedyn_costs"])
    ax.plot(result[0]["costs"])
    #ax.plot([0, len(perfs)], [37, 37], "r--") 
    ax.legend(["True cost", "Surr. cost"])
    plt.tight_layout()
    plt.show()

def make_figure_sysid2():
    setting1 = ("cartpole-swingup", "mlp-ilqr", 1, 100, 42)
    setting2 = ("cartpole-swingup", "mlp-ilqr", 2, 100, 42)
    setting3 = ("cartpole-swingup", "mlp-ilqr", 3, 100, 42)

    smac_res1, (rmses1, horizs1) = load_result("sysid2", *setting1)
    smac_res2, (rmses2, horizs2) = load_result("sysid2", *setting2)
    smac_res3, (rmses3, horizs3) = load_result("sysid2", *setting3)

    set_trace()

    matplotlib.rcParams.update({'font.size': 12})
    fig = plt.figure(figsize=(4,4))
    ax = fig.gca()
    ax.set_xlabel("Prediction Horizon")
    ax.set_ylabel("RMSE")
    ax.set_title("Multi-Step Pred. Accuracy")
    ax.plot(horizs1, rmses1)
    ax.plot(horizs2, rmses2)
    ax.plot(horizs3, rmses3)
    ax.legend(["1-step train", "Multi-step train", "Pipeline train"])

    #fig = plt.figure(figsize=(4,4))
    #ax = fig.gca()
    #ax.set_xlabel("Tuning Iterations")
    #ax.set_ylabel("Performance")
    #ax.set_title("Pipeline Performance of Sys ID")
    #ax.plot(smac_res1["inc_truedyn_costs"])
    #ax.plot(smac_res2["inc_truedyn_costs"])
    #ax.plot(smac_res3["inc_truedyn_costs"])
    #ax.legend(["1-step train", "Multi-step train", "Pipeline train"])

    plt.tight_layout()
    plt.show()

def make_figure_surrtest():
    #setting = ("cartpole-swingup", "mlp-ilqr", 5, 42)
    true_scores =[201.0, 43.0, 49.0, 49.0, 125.0, 180.0, 39.0, 67.0] 
    surr_scoress = [
        [201.0, 201.0, 201.0, 201.0, 201.0, 201.0, 201.0, 201.0, 201.0, 201.0], 
        [39.0, 41.0, 43.0, 41.0, 43.0, 43.0, 44.0, 38.0, 43.0, 43.0], 
        [53.0, 51.0, 57.0, 54.0, 51.0, 49.0, 57.0, 50.0, 50.0, 56.0], 
        [53.0, 51.0, 57.0, 54.0, 51.0, 49.0, 57.0, 50.0, 50.0, 56.0], 
        [181.0, 155.0, 148.0, 161.0, 174.0, 150.0, 149.0, 133.0, 173.0, 141.0], 
        [201.0, 166.0, 201.0, 201.0, 201.0, 127.0, 201.0, 199.0, 201.0, 185.0], 
        [40.0, 39.0, 39.0, 38.0, 41.0, 39.0, 40.0, 41.0, 40.0, 40.0],
        [104.0, 54.0, 122.0, 56.0, 124.0, 120.0, 62.0, 118.0, 64.0, 130.0]
        ]
    medians = []
    errs = np.zeros((2, len(surr_scoress)))
    for i, surr_scores in enumerate(surr_scoress):
        surr_scores.sort()
        medians.append(surr_scores[5])
        errs[1, i] = surr_scores[7] - surr_scores[5]
        errs[0, i] = surr_scores[5] - surr_scores[2]


    fig = plt.figure(figsize=(4,4))
    ax = fig.gca()
    ax.set_title("Surr. vs True for MLP-iLQR-Quad on Cart-Pole")
    ax.set_xlabel("Surrogate Perf")
    ax.set_ylabel("True Perf")
    ax.errorbar(medians, true_scores, xerr=errs, fmt="yo", ecolor="k",
        capsize=2)

    xmin, xmax = ax.get_xlim()
    ax.plot([xmin, xmax], [xmin, xmax], "--", color="grey")

    plt.tight_layout()
    plt.show()

def main(command):
    if command == "sysid1":
        make_figure_sysid1()
    elif command == "tuning1":
        make_figure_tuning1()
    elif command == "sysid2":
        make_figure_sysid2()
    elif command == "cost_tuning":
        make_figure_cost_tuning()
    elif command == "decoupled":
        make_figure_decoupled1()
    elif command == "cartpole-final":
        make_figure_cartpole_final()
    elif command == "surrtest":
        make_figure_surrtest()
    else:
        raise Exception("Unrecognized command")

if __name__ == "__main__":
    main(sys.argv[1])
