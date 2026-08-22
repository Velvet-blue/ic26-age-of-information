from src.config import np, njit
from src.simulations import gen_events


@njit
def AAoI_PAoI_sim(arrival_prob, send_prob, time, threshold=1):

    # rolagem de todos os dados
    (arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
        a=arrival_prob, p=send_prob, time=time)

    # Do ponto de vista do destino, a idade inicial é 0 (ou o tempo atual)
    successes = 0
    AAoI = 0
    PAoI = 0

    # Variáveis dos transmissores
    Age_A = 0
    Age_B = 0
    t_arrival_A = 0
    t_arrival_B = 0
    A_have = False
    B_have = False

    for t in range(time):

        # 1. Lógica de Transmissão

        A_tries = A_have and sends_A[t] and Age_A >= threshold
        B_tries = B_have and sends_B[t] and Age_B >= threshold

        # 2. Updates

        # Sucesso de A
        if A_tries and not B_tries:
            PAoI += Age_A
            Age_A = (t - t_arrival_A)
            successes += 1
            A_have = False

        # Sucesso de B
        if B_tries and not A_tries:
            Age_B = (t - t_arrival_B)
            B_have = False

        # 3. Arrivals and Ages

        if arrivals_A[t]:
            t_arrival_A = t
            A_have = True
        if arrivals_B[t]:
            t_arrival_B = t
            B_have = True

        AAoI += Age_A
        Age_A += 1
        Age_B += 1

    if successes > 0:
        AAoI = AAoI / time
        PAoI = PAoI / successes
    else:
        AAoI = np.nan
        PAoI = np.nan
    return (AAoI, PAoI)


@njit
def evolution_AoI_sim(arrival_prob, send_prob, threshold, time=100):
    ev_aoi_A = np.empty(time)
    ev_aoi_B = np.empty(time)
    arrivals_succes_pack = np.empty(time)
    updates = np.empty(time)

    # rolagem de todos os dados
    (arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
        a=arrival_prob, p=send_prob, time=time)

    # Do ponto de vista do destino, a idade inicial é 0 (ou o tempo atual)
    current_aoi_A = 0
    current_aoi_B = 0
    successes = 0
    PAoI = 0
    AAoI = 0

    # Variáveis dos transmissores
    tA_arrival = 0
    tB_arrival = 0
    A_have = False
    B_have = False

    for t in range(time):

        ev_aoi_A[t] = current_aoi_A
        ev_aoi_B[t] = current_aoi_B
      
        # 1. A idade no destino sempre aumenta em 1 a cada time step
        current_aoi_A += 1
        current_aoi_B += 1

        # 2. Lógica de Transmissão (acontece no slot)
        A_tries = A_have and sends_A[t] and current_aoi_A >= threshold # não é >= pois já estamos no tempo t+1, depois do update
        B_tries = B_have and sends_B[t] and current_aoi_B >= threshold

        # Sucesso de A
        if A_tries and not B_tries:
            PAoI += current_aoi_A
            current_aoi_A = (t - tA_arrival)
            arrivals_succes_pack[successes] = tA_arrival
            updates[successes] = t
            successes += 1
            A_have = False

        # Sucesso de B
        if B_tries and not A_tries:
            current_aoi_B = (t - tB_arrival)
            B_have = False

        # 3. Lógica de Chegada (com substituição). Desde o tempo 0, pode ter pacotes.
        # aqui, ficou mais fácil deixar as chegadas neste ponto
        if arrivals_A[t]:
            tA_arrival = t
            A_have = True

        if arrivals_B[t]:
            tB_arrival = t
            B_have = True

        AAoI += current_aoi_A

        # 4. Armazena o estado do AoI no final do processo

    return ev_aoi_A, ev_aoi_B, arrivals_succes_pack[:successes], updates, PAoI/successes, AAoI/time, successes


@njit
def evolution_AoI_til_sim(arrival_prob, send_prob, threshold, time=100):
    ev_aoi_A = np.empty(time)
    ev_aoi_B = np.empty(time)
    ev_tau_A = np.empty(time)
    arrivals_succes_pack = np.empty(time)

    # rolagem de todos os dados
    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    sends_A = np.random.random(time) < send_prob
    sends_B = np.random.random(time) < send_prob

    # Do ponto de vista do destino, a idade inicial é 0 (ou o tempo atual)
    current_aoi_A = 0
    tau_A = 0
    current_aoi_B = 0
    tau_B = 0
    successes = 0
    PAoI = 0
    AAoI = 0

    # Variáveis dos transmissores
    tA_arrival = 0
    tB_arrival = 0
    A_have = False
    B_have = False

    for t in range(time):
      
        AAoI += current_aoi_A
      
        # 1. A idade no destino sempre aumenta em 1 a cada time step
        current_aoi_A += 1
        current_aoi_B += 1
        tau_A = t - tA_arrival
        tau_B = t - tB_arrival

        # 2. Lógica de Transmissão (acontece no slot)
        A_tries = A_have and sends_A[t] and current_aoi_A - tau_A > threshold
        B_tries = B_have and sends_B[t] and current_aoi_B - tau_B > threshold

        # Sucesso de A
        if A_tries and not B_tries:
            PAoI += current_aoi_A
            current_aoi_A = tau_A
            arrivals_succes_pack[successes] = tA_arrival
            successes += 1
            A_have = False

        # Sucesso de B
        if B_tries and not A_tries:
            current_aoi_B = tau_B
            B_have = False

        # 3. Lógica de Chegada (com substituição). Desde o tempo 0, pode ter pacotes.
        # aqui, ficou mais fácil deixar as chegadas neste ponto
        if arrivals_A[t]:
            tA_arrival = t
            A_have = True

        if arrivals_B[t]:
            tB_arrival = t
            B_have = True

        # 4. Armazena o estado do AoI no final do processo
        ev_aoi_A[t] = current_aoi_A
        ev_aoi_B[t] = current_aoi_B
        ev_tau_A[t] = tau_A

    return ev_aoi_A, ev_aoi_B, ev_tau_A, arrivals_succes_pack[:successes], PAoI/successes, AAoI/time, successes


@njit
def evolution_AoI_plinio_sim(arrival_prob, send_prob, threshold, time=100):
    ev_aoi_A = np.empty(time)
    ev_aoi_B = np.empty(time)
    arrivals_succes_pack = np.empty(time)

    # rolagem de todos os dados
    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    sends_A = np.random.random(time) < send_prob
    sends_B = np.random.random(time) < send_prob

    arrivals_times = np.arange(time)[arrivals_A]

    # Do ponto de vista do destino, a idade inicial é 0 (ou o tempo atual)
    current_aoi_A = 0
    current_aoi_B = 0
    successes = 0
    PAoI = 0
    AAoI = 0

    # Variáveis dos transmissores
    tA_arrival = 0
    tB_arrival = 0
    A_have = False
    B_have = False

    for t in range(time):
      
        AAoI += current_aoi_A
      
        # 1. A idade no destino sempre aumenta em 1 a cada time step
        current_aoi_A += 1
        current_aoi_B += 1

        # 2. Lógica de Transmissão (acontece no slot)
        A_tries = current_aoi_A == threshold + 1 or (A_have and sends_A[t] and current_aoi_A > threshold+1) # não é >= pois já estamos no tempo t+1, depois do update
        B_tries = current_aoi_B == threshold + 1 or (B_have and sends_B[t] and current_aoi_B > threshold+1)

        # Sucesso de A
        if A_tries and not B_tries:
            PAoI += current_aoi_A
            current_aoi_A = (t - tA_arrival)
            arrivals_succes_pack[successes] = tA_arrival
            successes += 1
            A_have = False

        # Sucesso de B
        if B_tries and not A_tries:
            current_aoi_B = (t - tB_arrival)
            B_have = False

        # 3. Lógica de Chegada (com substituição). Desde o tempo 0, pode ter pacotes.
        # aqui, ficou mais fácil deixar as chegadas neste ponto
        if arrivals_A[t]:
            tA_arrival = t
            A_have = True

        if arrivals_B[t]:
            tB_arrival = t
            B_have = True

        # 4. Armazena o estado do AoI no final do processo
        ev_aoi_A[t] = current_aoi_A
        ev_aoi_B[t] = current_aoi_B

    return ev_aoi_A, ev_aoi_B, arrivals_succes_pack[:successes], PAoI/successes, AAoI/time, successes, arrivals_times


@njit
def AAoI_PAoI_til_sim(arrival_prob, send_prob, time, threshold=1):

    # rolagem de todos os dados
    (arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
        a=arrival_prob, p=send_prob, time=time)

    # Do ponto de vista do destino, a idade inicial é 0 (ou o tempo atual)
    successes = 0
    AAoI = 0
    PAoI = 0

    # Variáveis dos transmissores
    Age_A = 0
    Age_B = 0
    tau_A = 0
    tau_B = 0
    Age_til_A = 0
    Age_til_B = 0

    t_arrival_A = 0
    t_arrival_B = 0
    A_have = False
    B_have = False

    for t in range(time):

        tau_A = t - t_arrival_A
        tau_B = t - t_arrival_B
        
        Age_til_A = Age_A - tau_A
        Age_til_B = Age_B - tau_B

        # 1. Lógica de Transmissão

        A_tries = A_have and sends_A[t] and Age_til_A >= threshold
        B_tries = B_have and sends_B[t] and Age_til_B >= threshold

        # 2. Updates

        # Sucesso de A
        if A_tries and not B_tries:
            PAoI += Age_A - 1
            Age_A = tau_A + 1
            successes += 1
            A_have = False

        # Sucesso de B
        if B_tries and not A_tries:
            Age_B = tau_B + 1
            B_have = False

        # 3. Arrivals and Ages

        if arrivals_A[t]:
            t_arrival_A = t
            A_have = True
        if arrivals_B[t]:
            t_arrival_B = t
            B_have = True

        AAoI += Age_A
        Age_A += 1
        Age_B += 1
        

    if successes > 0:
        AAoI = AAoI / time
        PAoI = PAoI / successes
    else:
        AAoI = np.nan
        PAoI = np.nan
    return (AAoI, PAoI)



@njit
def AAoI_PAoI_plinio_sim(arrival_prob, send_prob, time, threshold=1):

    # rolagem de todos os dados
    (arrivals_A, arrivals_B, sends_A, sends_B) = gen_events(
        a=arrival_prob, p=send_prob, time=time)

    # Do ponto de vista do destino, a idade inicial é 0 (ou o tempo atual)
    successes = 0
    AAoI = 0
    PAoI = 0

    # Variáveis dos transmissores
    Age_A = 0
    Age_B = 0
    t_arrival_A = 0
    t_arrival_B = 0
    A_have = False
    B_have = False

    for t in range(time):

        # 1. Lógica de Transmissão

        A_tries = A_have and (Age_A == threshold or (sends_A[t] and Age_A > threshold)) # se Age == threshold, acessa o canal
        B_tries = B_have and (Age_B == threshold or (sends_B[t] and Age_B > threshold))

        # 2. Updates

        # Sucesso de A
        if A_tries and not B_tries:
            PAoI += Age_A
            Age_A = (t - t_arrival_A)
            successes += 1
            A_have = False

        # Sucesso de B
        if B_tries and not A_tries:
            Age_B = (t - t_arrival_B)
            B_have = False

        # 3. Arrivals and Ages

        if arrivals_A[t]:
            t_arrival_A = t
            A_have = True
        if arrivals_B[t]:
            t_arrival_B = t
            B_have = True

        AAoI += Age_A
        Age_A += 1
        Age_B += 1

    if successes > 0:
        AAoI = AAoI / time
        PAoI = PAoI / successes
    else:
        AAoI = np.nan
        PAoI = np.nan
    return (AAoI, PAoI)