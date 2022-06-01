from cmath import sin
import matplotlib.pyplot as plt
import numpy as np
from math import sin, pi
import os


def trasduttore(x, i_p=25 * 1.41):
    return 4 + 0.0327 * i_p * sin(2 * pi * 50 * x)


def condizionato(x):
    return 7.07 * sin(2 * pi * 50 * x)


x = np.arange(0, 0.1, 0.0001)

y = [condizionato(x_i) for x_i in x]

y_2 = [0 for x_i in x]

cond = plt.plot(x, y, label="V_o")
gnd = plt.plot(x, y_2, label="GND")
plt.legend(loc="lower right")
plt.savefig(os.path.join("documentazione", "corrente", "sign_adattato.png"))
