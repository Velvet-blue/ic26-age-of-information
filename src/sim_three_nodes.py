from src.config import np, njit


@njit
def AAoI_PAoI_het_sim(arrival_prob, send_prob, time, threshold=0):

    # rolagem de todos os dados
    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    arrivals_C = np.random.random(time) < arrival_prob
    sends_A = np.random.random(time) < 1 - send_prob #send_prob_array[0]
    sends_B = np.random.random(time) < send_prob #send_prob_array[1]
    sends_C = np.random.random(time) < 0 #send_prob_array[2]

    # Do ponto de vista do destino, a idade inicial é 0 (ou o tempo atual)
    successes = 0
    AAoI = 0
    PAoI = 0

    # Variáveis dos transmissores
    Age_A = 0
    Age_B = 0
    Age_C = 0
    t_arrival_A = 0
    t_arrival_B = 0
    t_arrival_C = 0
    A_have = False
    B_have = False
    C_have = False

    for t in range(time):

        # 1. Lógica de Transmissão

        A_tries = A_have and sends_A[t] and Age_A >= threshold
        B_tries = B_have and sends_B[t] and Age_B >= threshold
        C_tries = C_have and sends_C[t] and Age_C >= threshold

        # 2. Updates

        # Sucesso de A
        if A_tries and not (B_tries or C_tries):
            PAoI += Age_A - 1
            Age_A = (t - t_arrival_A) + 1
            successes += 1
            A_have = False

        # Sucesso de B
        if B_tries and not (A_tries or C_tries):
            Age_B = (t - t_arrival_B) + 1
            B_have = False

        # Sucesso de C
        if C_tries and not (A_tries or B_tries):
            Age_C = (t - t_arrival_C) + 1
            C_have = False

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
        AAoI = None
        PAoI = None
    return (AAoI, PAoI)


@njit
def AAoI_PAoI_hom_sim(arrival_prob, send_prob, time, threshold=0):

    # rolagem de todos os dados
    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    arrivals_C = np.random.random(time) < arrival_prob
    sends_A = np.random.random(time) < send_prob
    sends_B = np.random.random(time) < send_prob
    sends_C = np.random.random(time) < send_prob

    # Do ponto de vista do destino, a idade inicial é 0 (ou o tempo atual)
    successes = 0
    AAoI = 0
    PAoI = 0

    # Variáveis dos transmissores
    Age_A = 0
    Age_B = 0
    Age_C = 0
    t_arrival_A = 0
    t_arrival_B = 0
    t_arrival_C = 0
    A_have = False  # trocar por arrivals[0] em todos os arquivos
    B_have = False  # trocar por arrivals[0] em todos os arquivos
    C_have = False  # trocar por arrivals[0] em todos os arquivos

    for t in range(time):

        # 1. Lógica de Transmissão

        A_tries = A_have and sends_A[t] and Age_A > threshold
        B_tries = B_have and sends_B[t] and Age_B > threshold
        C_tries = C_have and sends_C[t] and Age_C > threshold

        # 2. Updates

        # Sucesso de A
        if A_tries and not (B_tries or C_tries):
            PAoI += Age_A - 1
            Age_A = (t - t_arrival_A)
            successes += 1
            A_have = False

        # Sucesso de B
        if B_tries and not (A_tries or C_tries):
            Age_B = (t - t_arrival_B)
            B_have = False

        # Sucesso de C
        if C_tries and not (A_tries or B_tries):
            Age_C = (t - t_arrival_C)
            C_have = False

        # 3. Arrivals and Ages

        if arrivals_A[t]:
            t_arrival_A = t
            A_have = True
        if arrivals_B[t]:
            t_arrival_B = t
            B_have = True
        if arrivals_C[t]:
            t_arrival_C = t
            C_have = True

        AAoI += Age_A
        Age_A += 1
        Age_B += 1
        Age_C += 1

    if successes > 0:
        AAoI = AAoI / time
        PAoI = PAoI / successes
    else:
        AAoI = None
        PAoI = None
    return (AAoI, PAoI)



@njit
def AAoI_PAoI_til_sim(arrival_prob, send_prob, time, threshold=0):

    # rolagem de todos os dados
    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    arrivals_C = np.random.random(time) < arrival_prob
    sends_A = np.random.random(time) < send_prob
    sends_B = np.random.random(time) < send_prob
    sends_C = np.random.random(time) < send_prob

    # Do ponto de vista do destino, a idade inicial é 0 (ou o tempo atual)
    successes = 0
    AAoI = 0
    PAoI = 0

    # Variáveis dos transmissores
    Age_A = 0
    Age_B = 0
    Age_C = 0
    tau_A = 0
    tau_B = 0
    tau_C = 0
    Age_til_A = 0
    Age_til_B = 0
    Age_til_C = 0

    t_arrival_A = 0
    t_arrival_B = 0
    t_arrival_C = 0
    A_have = False  # trocar por arrivals[0] em todos os arquivos
    B_have = False  # trocar por arrivals[0] em todos os arquivos
    C_have = False  # trocar por arrivals[0] em todos os arquivos

    for t in range(time):

        
        
        Age_til_A = Age_A - tau_A
        Age_til_B = Age_B - tau_B
        Age_til_C = Age_C - tau_C

        # 1. Lógica de Transmissão

        A_tries = A_have and sends_A[t] and Age_til_A > threshold
        B_tries = B_have and sends_B[t] and Age_til_B > threshold
        C_tries = C_have and sends_C[t] and Age_til_C > threshold

        # 2. Updates

        # Sucesso de A
        if A_tries and not (B_tries or C_tries):
            PAoI += Age_A - 1
            Age_A = tau_A + 1
            successes += 1
            A_have = False

        # Sucesso de B
        if B_tries and not (A_tries or C_tries):
            Age_B = tau_B + 1
            B_have = False

        # Sucesso de C
        if C_tries and not (A_tries or B_tries):
            Age_C = tau_C + 1
            C_have = False

        # 3. Arrivals and Ages

        if arrivals_A[t]:
            t_arrival_A = t
            A_have = True
        if arrivals_B[t]:
            t_arrival_B = t
            B_have = True
        if arrivals_C[t]:
            t_arrival_C = t
            C_have = True

        tau_A = t - t_arrival_A
        tau_B = t - t_arrival_B
        tau_C = t - t_arrival_C

        AAoI += Age_A
        Age_A += 1
        Age_B += 1
        Age_C += 1

    if successes > 0:
        AAoI = AAoI / time
        PAoI = PAoI / successes
    else:
        AAoI = None
        PAoI = None
    return (AAoI, PAoI)



@njit
def AAoI_PAoI_plinio_sim(arrival_prob, send_prob, time, threshold=0):

    # rolagem de todos os dados
    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    arrivals_C = np.random.random(time) < arrival_prob
    sends_A = np.random.random(time) < send_prob
    sends_B = np.random.random(time) < send_prob
    sends_C = np.random.random(time) < send_prob

    # Do ponto de vista do destino, a idade inicial é 0 (ou o tempo atual)
    successes = 0
    AAoI = 0
    PAoI = 0

    # Variáveis dos transmissores
    Age_A = 0
    Age_B = 0
    Age_C = 0
    t_arrival_A = 0
    t_arrival_B = 0
    t_arrival_C = 0
    A_have = False  # trocar por arrivals[0] em todos os arquivos
    B_have = False  # trocar por arrivals[0] em todos os arquivos
    C_have = False  # trocar por arrivals[0] em todos os arquivos

    for t in range(time):

        # 1. Lógica de Transmissão

        A_tries = A_have and (Age_A == threshold +1 or (sends_A[t] and Age_A > threshold+1))
        B_tries = B_have and (Age_B == threshold +1 or (sends_B[t] and Age_B > threshold+1))
        C_tries = C_have and (Age_C == threshold +1 or (sends_C[t] and Age_C > threshold+1))

        # 2. Updates

        # Sucesso de A
        if A_tries and not (B_tries or C_tries):
            PAoI += Age_A - 1
            Age_A = (t - t_arrival_A)
            successes += 1
            A_have = False

        # Sucesso de B
        if B_tries and not (A_tries or C_tries):
            Age_B = (t - t_arrival_B)
            B_have = False

        # Sucesso de C
        if C_tries and not (A_tries or B_tries):
            Age_C = (t - t_arrival_C)
            C_have = False

        # 3. Arrivals and Ages

        if arrivals_A[t]:
            t_arrival_A = t
            A_have = True
        if arrivals_B[t]:
            t_arrival_B = t
            B_have = True
        if arrivals_C[t]:
            t_arrival_C = t
            C_have = True

        AAoI += Age_A
        Age_A += 1
        Age_B += 1
        Age_C += 1

    if successes > 0:
        AAoI = AAoI / time
        PAoI = PAoI / successes
    else:
        AAoI = None
        PAoI = None
    return (AAoI, PAoI)



@njit
def AAoI_PAoI_limit(arrival_prob, send_prob, time, threshold=0):

    # rolagem de todos os dados
    arrivals_A = np.random.random(time) < arrival_prob
    arrivals_B = np.random.random(time) < arrival_prob
    arrivals_C = np.random.random(time) < arrival_prob

    # Do ponto de vista do destino, a idade inicial é 0 (ou o tempo atual)
    successes = 0
    AAoI = 0.0
    PAoI = 0.0

    # Variáveis dos transmissores
    Age_A = 0
    Age_B = 0
    Age_C = 0
    t_arrival_A = 0
    t_arrival_B = 0
    t_arrival_C = 0
    A_have = False  # trocar por arrivals[0] em todos os arquivos
    B_have = False  # trocar por arrivals[0] em todos os arquivos
    C_have = False  # trocar por arrivals[0] em todos os arquivos

    for t in range(time):

        # 4. Armazena o estado do AoI no final do processo
        AAoI += Age_A
        
        # 1. A idade no destino sempre aumenta em 1 a cada time step
        Age_A += 1

        # 2. Lógica de Transmissão (acontece no slot)
        A_tries = False
        B_tries = False
        C_tries = False

        maior_idade = -1
        if A_have and Age_A > maior_idade:
            maior_idade = Age_A
        if B_have and Age_B > maior_idade:
            maior_idade = Age_B
        if C_have and Age_C > maior_idade:
            maior_idade = Age_C


        if maior_idade != -1:
            # Conta e identifica quem empata na maior idade
            # Usa índices numéricos (0 = A, 1 = B, 2 = C) em vez de strings
            candidatos_idx = np.empty(3, dtype=np.int32)
            qtd = 0

            if A_have and Age_A == maior_idade:
                candidatos_idx[qtd] = 0
                qtd += 1
            if B_have and Age_B == maior_idade:
                candidatos_idx[qtd] = 1
                qtd += 1
            if C_have and Age_C == maior_idade:
                candidatos_idx[qtd] = 2
                qtd += 1

            # Sorteia 1 participante entre os empatados
            escolhido_idx = candidatos_idx[np.random.randint(0, qtd)]

            A_tries = (escolhido_idx == 0)
            B_tries = (escolhido_idx == 1)
            C_tries = (escolhido_idx == 2)

        # Sucesso de A
        if A_tries and not (B_tries or C_tries):
            PAoI += Age_A - 1
            Age_A = (t - t_arrival_A)
            successes += 1
            A_have = False

        # Sucesso de B
        if B_tries and not (A_tries or C_tries):
            Age_B = (t - t_arrival_B)
            B_have = False

        # Sucesso de C
        if C_tries and not (A_tries or B_tries):
            Age_C = (t - t_arrival_C)
            C_have = False

        # 3. Lógica de Chegada (com substituição). Desde o tempo 0, pode ter pacotes.
        # aqui, ficou mais fácil deixar as chegadas neste ponto
        if arrivals_A[t]:
            t_arrival_A = t
            A_have = True

        if arrivals_B[t]:
            t_arrival_B = t
            B_have = True

        if arrivals_C[t]:
            t_arrival_C = t
            C_have = True

    if successes > 0:
        AAoI = AAoI / time
        PAoI = PAoI / successes
    else:
        AAoI = None
        PAoI = None
    return (AAoI, PAoI)