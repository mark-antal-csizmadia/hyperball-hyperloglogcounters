import numpy as np
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import os
import sys
import time
from hyperball import HyperBall


def read_data(from_file_name, dataset):
    """ Reads data. """
    if dataset == "email":
        df_edges = pd.read_csv(from_file_name, sep=" ", header=None, skiprows=0, names=["src", "dst"])
        vertices_np = \
            np.unique(np.hstack([df_edges["src"].unique(), df_edges["dst"].unique()]))
        df_vertices = pd.DataFrame(data={"id": vertices_np})
    else:
        df_edges = pd.read_csv(from_file_name, sep="\t", header=None, skiprows=4, names=["src", "dst"])
        vertices_np = \
            np.unique(np.hstack([df_edges["src"].unique(), df_edges["dst"].unique()]))
        df_vertices = pd.DataFrame(data={"id": vertices_np})

    return df_edges, df_vertices


def plot_graph(g, path_save=None):
    """Plots graph."""
    plt.figure(figsize=(12, 12))
    nx.draw(g)

    if path_save is not None:
        plt.savefig(path_save)

    plt.show()


if __name__ == '__main__':
    script_start_time = time.time()
    # Set hash seed and restart interpreter.
    # This will be done only once if the env var is clear.
    if not os.environ.get('PYTHONHASHSEED'):
        os.environ['PYTHONHASHSEED'] = '678'
        os.execv(sys.executable, ['python3'] + sys.argv)

    try:
        dataset, b = str(sys.argv[1]), int(sys.argv[2])
        if not dataset in ["email", "wiki"]:
            raise ValueError

    except Exception:
        raise SystemExit(f"Usage: {sys.argv[0]} <dataset> <b>\n"
                         f"dataset is one of email or wiki, and b is the number of bits in HyperLogLogCounters")

    # read data
    if dataset == "email":
        from_file_name = Path("data/email-Eu-core.txt")
        graph_save_path = Path("assets/g_email.png")
        csv_save_path = Path("assets/email.csv")
    else:
        from_file_name = Path("data/wiki-Vote.txt")
        graph_save_path = Path("assets/g_wiki.png")
        csv_save_path = Path("assets/wiki.csv")

    print(f"reading {from_file_name}")
    df_edges, df_vertices = read_data(from_file_name=from_file_name, dataset=dataset)

    # create graph
    g = nx.from_pandas_edgelist(
        df=df_edges,
        source="src",
        target="dst",
        edge_attr=None,
        create_using=nx.DiGraph,
        edge_key=None
    )

    print(f"created graph with {len(g.nodes)} nodes and {len(g.edges)} edges")

    # start_time = time.time()
    # print(f"plotting graph...")
    # plot_graph(g, path_save=graph_save_path)
    # print(f"graph plotting execution time: {time.time() - start_time:.4f} seconds")

    start_time = time.time()
    hash_to = 64
    harmonic_centrality_hb = HyperBall(b=b, hash_to=hash_to, g=g.reverse())()
    print(f"HyperBall execution time: {time.time() - start_time:.4f} seconds")

    start_time = time.time()
    print("fitting NetworkX.harmonic_centrality() ...")
    harmonic_centrality_true = nx.harmonic_centrality(g)
    print(f"NetworkX execution time: {time.time() - start_time:.4f} seconds")

    # sort by node ids in ascending order
    harmonic_centrality_hb_sorted = {k: harmonic_centrality_hb[k] for k in sorted(harmonic_centrality_hb)}
    harmonic_centrality_true_sorted = {k: harmonic_centrality_true[k] for k in sorted(harmonic_centrality_true)}

    # make df, compute approximation error, and save resutls as csv
    # error is: https://en.wikipedia.org/wiki/Approximation_error
    df_hb = pd.DataFrame(harmonic_centrality_hb_sorted.items(), columns=['id', 'hb'])
    df_true = pd.DataFrame(harmonic_centrality_true_sorted.items(), columns=['id', 'true'])
    df_hb.drop("id", axis=1, inplace=True)
    df = pd.concat([df_true, df_hb], axis=1)

    df["err[%]"] = 100 * abs((df["hb"] - df["true"]) / (df["true"] + 10e-9))

    print(f"HyperBall converged with an approximation error of {df['err[%]'].mean():.4f}%")

    df.to_csv(csv_save_path, float_format='%.4f')
    print(f"saved results to: {csv_save_path}")

    print(f"script execution time: {time.time() - script_start_time:.4f} seconds\ndone!")