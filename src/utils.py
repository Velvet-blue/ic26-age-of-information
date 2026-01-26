from src.config import np, njit, plt, sp
from joblib import Parallel, delayed
import os

PROB_DOMAIN = np.linspace(.02, .98, 49)
PLOT_DOMAIN = np.arange(0.1, 1.0, 0.1)

def simulate_metric(metric_func, time:int, name:str="", method="numpy"):
    """
    Simulate a given metric function over a grid of arrival and sending probabilities.
    
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
        A, P = np.meshgrid(PROB_DOMAIN, PROB_DOMAIN)
        simulated_data = vec_func(P, A, time)

    elif method == "joblib":
        # método usando a lib "joblib"
        results = Parallel(n_jobs=-1)(
            delayed(metric_func)(arrival_prob=a, send_prob=p, time=time)
            for a in PROB_DOMAIN
            for p in PROB_DOMAIN
        )
        simulated_data = np.array(results).reshape(len(PROB_DOMAIN), len(PROB_DOMAIN))

    else:
        raise ValueError("Método desconhecido. Use 'numpy' ou 'joblib'.")

    # salva no google drive, se for passado o nome
    # if name != "":
    #     if os.path.exists('/content/drive'):
    #         np.save(f'/content/drive/MyDrive/IC - Age of Information/Data/{name}.npy', simulated_data)
    # else:
    #   print("Google Drive não montado. Dados não salvos.")

    return simulated_data

def make_metric_func(metrics_data):
    """
    Create a metric function that retrieves precomputed metric values from a 2D array or evaluates a symbolic expression.
    
    :param metrics_data: 2D numpy array with precomputed metric values.
    :type metrics_data: np.ndarray
    :return: A function that takes arrival and sending probabilities and returns the corresponding metric value.
    :rtype: function
    """
    if isinstance(metrics_data, sp.Expr):
        # se for uma expressão simbólica, cria a função diretamente
        arrival_prob, send_prob = sp.symbols('a p')
        func = sp.lambdify([arrival_prob, send_prob], metrics_data, 'numpy')
        return np.vectorize(func)
    elif isinstance(metrics_data, np.ndarray):
        domain_size = len(metrics_data) - 1 # não usar PROB_DOMAIN para evitar conflitos
        
        def metric_func(arrival_prob:float, send_prob:float):
            # encontra os índices mais próximos no domínio
            a_idx = int(np.round(arrival_prob*domain_size))
            p_idx = int(np.round(send_prob*domain_size))
            return metrics_data[a_idx, p_idx]

        return np.vectorize(metric_func)
    else:
        raise ValueError("metrics_data deve ser uma expressão simbólica ou um array numpy.")


def plot_metric(
        math_metric,
        simulated_metric,
        cmap:str,
        title:str,
        axis:str = "p"
        ) -> None:
    plt.figure(figsize=(10, 6))
    color_map = plt.get_cmap(cmap)
    for i, plt_value in enumerate(PLOT_DOMAIN):
        if axis == "p":
            ctrl_param = "a"
            xlabel = "Probabilidade de acesso (p)"
            math_plot = math_metric(plt_value, PROB_DOMAIN)
            simulated_plot = simulated_metric(arrival_prob=plt_value, send_prob=PROB_DOMAIN)
        elif axis == "a":
            ctrl_param = "p"
            xlabel = "Probabilidade de chegada (a)"
            math_plot = math_metric(arrival_prob=PROB_DOMAIN, send_prob=plt_value)
            simulated_plot = simulated_metric(arrival_prob=PROB_DOMAIN, send_prob=plt_value)
        else:
            raise ValueError("Eixo desconhecido. Use 'p' ou 'a'.")

        color = color_map(i / len(PLOT_DOMAIN))
        plt.plot(PROB_DOMAIN, math_plot, label=f"{ctrl_param} = {plt_value:.2f}", color=color, linestyle='-', lw=2)
        plt.plot(PROB_DOMAIN, simulated_plot, color=color, linestyle='None', marker='o', markersize=2)
    plt.xlabel(xlabel)
    plt.ylabel("Métrica")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()


def compare_metric_plot(
        analytical_expr:sp.Expr,
        simulated_data:np.ndarray,
        title:str,
        cmap:str="viridis",
        axis:str="p"
        ) -> None:
    metric_func = make_metric_func(analytical_expr)
    simulated_metric = make_metric_func(simulated_data)
    plot_metric(
        math_metric=metric_func,
        simulated_metric=simulated_metric,
        cmap=cmap,
        title=title,
        axis=axis
    )