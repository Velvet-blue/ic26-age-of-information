from time import time
from src.config import np, plt, sp, minimize_scalar
from joblib import Parallel, delayed
import os

PAR_STEP = .02
PLOT_INTERVAL = 0.1

P_DOMAIN = np.arange(PAR_STEP, 1.0, PAR_STEP)
A_DOMAIN = np.arange(PAR_STEP, 1.0 + PAR_STEP, PAR_STEP)
# PLOT_DOMAIN = np.arange(0.1,  1.1, .1)
PLOT_DOMAIN = np.array([0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0])
T_DOMAIN = np.arange(1, 11, 1)


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
        P, A = np.meshgrid(P_DOMAIN, A_DOMAIN)
        # !!!
        simulated_data = vec_func(arrival_prob=A, send_prob=P, time=time)

    elif method == "joblib":
        # método usando a lib "joblib"
        results = Parallel(n_jobs=-1)(
            delayed(metric_func)(arrival_prob=a, send_prob=p, time=time)
            for a in A_DOMAIN
            for p in P_DOMAIN
        )
        simulated_data = np.array(results).reshape(
            len(A_DOMAIN),
            len(P_DOMAIN)
            )

    else:
        raise ValueError("Método desconhecido. Use 'numpy' ou 'joblib'.")

    # salva no google drive, se for passado o nome
    if name != "":
            np.save(f'data/{name}.npy', simulated_data)
            print(f"Dados salvos em 'data/{name}.npy'.")

    return simulated_data


def simulate_metric_TSA(metric_func, time: int, name: str = ""):
    # método usando a função vetorizada da métrica
    vec_func = np.vectorize(metric_func)
    P, A, T = np.meshgrid(P_DOMAIN, A_DOMAIN, T_DOMAIN)
    # !!!
    simulated_data = vec_func(arrival_prob=A, send_prob=P, threshold=T, time=time)
    if name != "":
        np.save(f'data/{name}.npy', simulated_data)
        print(f"Dados salvos em 'data/{name}.npy'.")
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
        match metrics_data.ndim:
            case 2:
                def metric_func(arrival_prob: float, send_prob: float):
                    # encontra os índices mais próximos no domínio
                    a_idx = int(np.round(arrival_prob*(domain_size) - 1))
                    p_idx = int(np.round(send_prob*(domain_size) - 1))

                    return metrics_data[a_idx, p_idx]
        
            case 3:
                def metric_func(arrival_prob: float, send_prob: float, threshold: int):
                    # encontra os índices mais próximos no domínio
                    a_idx = int(np.round(arrival_prob*(domain_size) - 1))
                    p_idx = int(np.round(send_prob*(domain_size) - 1))

                    gamma_idx = threshold - 1
                    return metrics_data[a_idx, p_idx, gamma_idx]
            case _:
                raise ValueError("Array de métricas deve ser 2D ou 3D.")

        return np.vectorize(metric_func)
    
    else:

        raise ValueError(
            "metrics_data deve ser uma expressão simbólica ou um "
            "array numpy."
        )
    

def optimize_metric(metric_func, find_max=False):

    # lista_a = [i/1000 for i in range(2, 1001, 2)]
    opt_metric = {"p_opt":[], "metric_opt":[]}
    if find_max:
        metric_func_a = lambda p, a: -metric_func(a, p)  # inverte para maximizar
    else:
        metric_func_a = lambda p ,a: metric_func(a, p)  # exemplo fixando p=0.5

    for a_val in A_DOMAIN:
        # Busca o mínimo de p no intervalo [0, 1] para cada 'a'
        res = minimize_scalar(metric_func_a, args=(a_val,), bounds=(0, 1), method='bounded')
        opt_metric["p_opt"].append(res.x)
        opt_metric["metric_opt"].append(res.fun)
    if find_max:
        opt_metric["metric_opt"] = [-val for val in opt_metric["metric_opt"]]  # reverte os valores para o máximo
    return opt_metric


def optimize_metric_grid(metric_func, find_max=False):
    """
    Otimiza uma métrica buscando exaustivamente sobre P_DOMAIN e T_DOMAIN
    para cada valor em A_DOMAIN.
    """
    results = {
        "p_opt": [],
        "gamma_opt": [],
        "metric_opt": []
    }

    for a_val in A_DOMAIN:
        # Reinicia os recordes para o 'a' atual
        best_p = None
        best_gamma = None
        best_metric = float('-inf') if find_max else float('inf')

        # Testa todas as combinações (p, gamma)
        for gamma_val in T_DOMAIN:
            for p_val in P_DOMAIN:
                
                # Calcula a métrica para a trinca atual
                current_metric = metric_func(a_val, p_val, gamma_val)

                # Verifica se é o melhor valor encontrado até agora
                is_better = (current_metric > best_metric) if find_max else (current_metric < best_metric)
                
                if is_better:
                    best_metric = current_metric
                    best_p = p_val
                    best_gamma = gamma_val

        # Salva o cenário campeão para este 'a'
        results["p_opt"].append(best_p)
        results["gamma_opt"].append(best_gamma)
        results["metric_opt"].append(best_metric)

    return results

def plot_metric(
        analytical_func,
        simulation_data_func,
        cmap: str,
        title: str,
        axis: str = "p",
        yrange = None,
        find_max = False
        ) -> None:
    opt_metric = optimize_metric(analytical_func, find_max=find_max)
    plt.figure(figsize=(10, 6))
    color_map = plt.get_cmap(cmap)

    match axis:
        case "p":
            prob_domain = P_DOMAIN
            plot_domain = PLOT_DOMAIN
            ctrl_param = "$a$"
            xlabel = "access probability ($p$)"
            calc_math = lambda x: analytical_func(x, prob_domain)
            calc_sim = lambda x: simulation_data_func(arrival_prob=x, send_prob=prob_domain)
        case "a":
            prob_domain = A_DOMAIN
            plot_domain = PLOT_DOMAIN[PLOT_DOMAIN != 1.0]  # evita o 1.0 exato para $p$
            ctrl_param = "$p$"
            xlabel = "Probabilidade de chegada ($a$)"
            calc_math = lambda x: analytical_func(prob_domain, x)
            calc_sim = lambda x: simulation_data_func(arrival_prob=prob_domain, send_prob=x)
        case _:
            raise ValueError("Eixo desconhecido. Use 'p' ou 'a'.")
    for i, plt_value in enumerate(plot_domain):
        math_plot = calc_math(plt_value)
        simulated_plot = calc_sim(plt_value)

        color = color_map(i / len(plot_domain))
        plt.plot(prob_domain, math_plot,
                 label=f"{ctrl_param} = {plt_value:.2f}",
                 color=color, linestyle='-', lw=2)
        plt.plot(prob_domain, simulated_plot, color=color,
                 linestyle='None', marker='o', markersize=2)
        
    # otimização da métrica
    plt.plot(opt_metric["p_opt"], opt_metric["metric_opt"], label='optimization',
             color='red', linestyle='--', lw=1)
    plt.xlabel(xlabel, fontsize=20)
    plt.ylabel("Metric", fontsize=20)
    if yrange is not None:
        plt.ylim(yrange)
    plt.xlim(0, 1)
    plt.title(title, fontsize=30)
    plt.legend(fontsize=20, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.show()


def compare_metric_plot(
        analytical_expr: sp.Expr,
        simulation_data: np.ndarray,
        title: str,
        cmap: str = "viridis",
        axis: str = "p",
        yrange = None,
        find_max = False
        ) -> None:
    metric_func = make_metric_func(analytical_expr)
    simulated_metric = make_metric_func(simulation_data)
    plot_metric(
        analytical_func=metric_func,
        simulation_data_func=simulated_metric,
        cmap=cmap,
        title=title,
        axis=axis,
        yrange=yrange,
        find_max=find_max
    )


if __name__ == "__main__":
    import simulations as sim
    a, p = sp.symbols('a p') # arrival and access probabilities symbols

    P = sp.Matrix([
        [(1-a)**2,    a*(1-a),          a*(1-a),          a**2              ],
        [p*(1-a)**2,  (1-a)*(1-p+p*a),  p*a*(1-a),        a*(1-p+p*a)       ],
        [p*(1-a)**2,  p*a*(1-a),        (1-a)*(1-p+p*a),  a*(1-p+p*a)       ],
        [0,           p*(1-a)*(1-p),    p*(1-p)*(1-a),    p**2 + (1-p)*(1-p+2*p*a) ]
    ])

    pi00s, pi01s, pi10s, pi11s = sp.symbols('pi00 pi01 pi10 pi11')
    pi = sp.Matrix([pi00s, pi01s, pi10s, pi11s])

    # equações: pi = pi P  e soma(pi)=1
    eqs = list((pi.T * P - pi.T)[0,:])
    eqs[-1] = pi00s + pi01s + pi10s + pi11s - 1
    sol = sp.solve(eqs, [pi00s, pi01s, pi10s, pi11s], dict=True)
    sol = sol[0]  # dicionário com pi00,pi01,pi10,pi11
    pi00, pi01, pi10, pi11 = [sol[pi00s], sol[pi01s], sol[pi10s], sol[pi11s]]
    throughput_expr = sp.simplify(pi01*p + pi10*p + 2*pi11*p*(1-p))
    throughput_data = simulate_metric(sim.throughput, time=20000, method="numpy")
    compare_metric_plot(
        analytical_expr=throughput_expr,
        simulation_data=throughput_data,
        title="Throughput",
        cmap="viridis",
        axis="p"
    )