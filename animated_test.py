import matplotlib.pyplot as plt
import numpy as np
import time
from src.simulations import evolution_AoI_sim

plt.ion() # Liga o modo interativo
fig, ax = plt.subplots()
line, = ax.plot([], [], 'b-')

xdata, ydata = [], []

try:
    y_i = 0
    for t in range(100000):
        # --- O seu código que calcula y entra aqui ---
        # Exemplo: y é uma função do tempo com um pouco de ruído
        # y = np.sin(0.2 * t) + np.random.normal(0, 0.00)
        y = y_i + np.random.normal(1, t**2)
        y_i = -(y - y_i)*1000 + y_i*0.99

        # ---------------------------------------------

        # Adiciona o novo ponto ao histórico
        xdata.append(t)
        ydata.append(y)

        # Atualiza os dados da linha existente (mais rápido que plotar de novo)
        line.set_data(xdata, ydata)

        # Reajusta os limites dos eixos para "seguir" os novos pontos
        ax.relim()
        ax.autoscale_view()

        # Renderiza a atualização e controla a velocidade
        plt.pause(0.01)
        fig.canvas.draw_idle()
        fig.canvas.flush_events()

except KeyboardInterrupt:
    print("Gráfico interrompido pelo usuário.")

# Mantém a janela aberta após o término do loop
plt.ioff()
plt.show()