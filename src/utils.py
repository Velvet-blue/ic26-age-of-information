from src.config import np, plt, sp
from joblib import Parallel, delayed
# import os

PROB_DOMAIN = np.arange(.02, 1, .02)
PLOT_DOMAIN = np.arange(.1,  1, .1)


# def simulate_metric_teste(metric_func, time: int, name: str = ""):
#     tamanho = len(PROB_DOMAIN)
#     simulation_data = np.empty((tamanho, tamanho))

#     for i, a in enumerate(PROB_DOMAIN):
#         for j, p in enumerate(PROB_DOMAIN):
#             simulation_data[i, j] = metric_func(
#                 arrival_prob=a, send_prob=p, time=time)

#     return simulation_data


def simulate_metric(metric_func, time: int, name: str = "", method="numpy"):
    """
    Simulate a given metric function over a grid of arrival and sending
    probabilities.

    :param metric_func: The metric function to simulate.
    :type metric_func: function
    :param prob_domain: domain array of probabilities to simulate over.
    :type prob_domain: list or np.ndarray
    :param time: run time for the simulation.
    :type time: int
    :param name: Name to save the data in Google Drive.
    :type name: str
    :param method: Method to use for simulation ('numpy' or 'joblib').
    :type method: str
    :return: Simulated data as a 2D numpy array.
    :rtype: np.ndarray
    """

    if method == "numpy":
        # método usando a função vetorizada da métrica
        vec_func = np.vectorize(metric_func)
        P, A = np.meshgrid(PROB_DOMAIN, PROB_DOMAIN)
        simulated_data = vec_func(arrival_prob=A, send_prob=P, time=time)

    elif method == "joblib":
        # método usando a lib "joblib"
        results = Parallel(n_jobs=-1)(
            delayed(metric_func)(arrival_prob=a, send_prob=p, time=time)
            for a in PROB_DOMAIN
            for p in PROB_DOMAIN
        )
        simulated_data = np.array(results).reshape(
            len(PROB_DOMAIN),
            len(PROB_DOMAIN)
            )

    else:
        raise ValueError("Método desconhecido. Use 'numpy' ou 'joblib'.")

    # salva no google drive, se for passado o nome
    # if name != "":
    #     if os.path.exists('/content/drive'):
    #         path = (
    #             f'/content/drive/MyDrive/IC - Age of '
    #             f'Information/Data/{name}.npy'
    #         )
    #         np.save(path, simulated_data)
    # else:
    #   print("Google Drive não montado. Dados não salvos.")

    return simulated_data


def make_metric_func(metrics_data):
    """
    Create a metric function that retrieves precomputed metric values from a
    2D array or evaluates a symbolic expression.

    :param metrics_data: 2D numpy array with precomputed metric values.
    :type metrics_data: np.ndarray
    :return: A function that takes arrival and sending probabilities and
            returns the corresponding metric value.
    :rtype: function
    """
    if isinstance(metrics_data, sp.Expr):
        # se for uma expressão simbólica, cria a função diretamente
        arrival_prob, send_prob = sp.symbols('a p')
        func = sp.lambdify([arrival_prob, send_prob], metrics_data, 'numpy')
        return np.vectorize(func)
    elif isinstance(metrics_data, np.ndarray):
        domain_size = len(metrics_data)  # usar PROB_DOMAIN evita conflitos

        def metric_func(arrival_prob: float, send_prob: float):
            # encontra os índices mais próximos no domínio
            a_idx = int(np.round(arrival_prob*(domain_size + 1) - 1))
            p_idx = int(np.round(send_prob*(domain_size + 1) - 1))
            return metrics_data[a_idx, p_idx]

        return np.vectorize(metric_func)
    else:
        raise ValueError(
            "metrics_data deve ser uma expressão simbólica ou um "
            "array numpy."
        )


def plot_metric(
        analytical_func,
        simulation_data_func,
        cmap: str,
        title: str,
        axis: str = "p",
        yrange = None
        ) -> None:
    plt.figure(figsize=(10, 6))
    color_map = plt.get_cmap(cmap)
    match axis:
        case "p":
            ctrl_param = "$a$"
            xlabel = "Probabilidade de acesso ($p$)"
            calc_math = lambda x: analytical_func(x, PROB_DOMAIN)
            calc_sim = lambda x: simulation_data_func(arrival_prob=x, send_prob=PROB_DOMAIN)
        case "a":
            ctrl_param = "$p$"
            xlabel = "Probabilidade de chegada ($a$)"
            calc_math = lambda x: analytical_func(PROB_DOMAIN, x)
            calc_sim = lambda x: simulation_data_func(arrival_prob=PROB_DOMAIN, send_prob=x)
        case _:
            raise ValueError("Eixo desconhecido. Use 'p' ou 'a'.")
    for i, plt_value in enumerate(PLOT_DOMAIN):
        math_plot = calc_math(plt_value)
        simulated_plot = calc_sim(plt_value)

        color = color_map(i / len(PLOT_DOMAIN))
        plt.plot(PROB_DOMAIN, math_plot,
                 label=f"{ctrl_param} = {plt_value:.2f}",
                 color=color, linestyle='-', lw=2)
        plt.plot(PROB_DOMAIN, simulated_plot, color=color,
                 linestyle='None', marker='o', markersize=2)
    plt.xlabel(xlabel)
    plt.ylabel("Métrica")
    if yrange is not None:
        plt.ylim(yrange)
    plt.title(title)
    plt.legend(title = f"Parâmetro {ctrl_param}", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.show()


def compare_metric_plot(
        analytical_expr: sp.Expr,
        simulation_data: np.ndarray,
        title: str,
        cmap: str = "viridis",
        axis: str = "p",
        yrange = None
        ) -> None:
    metric_func = make_metric_func(analytical_expr)
    simulated_metric = make_metric_func(simulation_data)
    plot_metric(
        analytical_func=metric_func,
        simulation_data_func=simulated_metric,
        cmap=cmap,
        title=title,
        axis=axis,
        yrange=yrange
    )
