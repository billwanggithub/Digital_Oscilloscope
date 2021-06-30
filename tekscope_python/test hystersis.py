
import numpy as np
import matplotlib.pyplot as plt

def hyst(x, th_lo, th_hi, initial = False):
    """
    x : Numpy Array
        Series to apply hysteresis to.
    th_lo : float or int
        Below this threshold the value of hyst will be False (0).
    th_hi : float or int
        Above this threshold the value of hyst will be True (1).
    """        

    if th_lo > th_hi: # If thresholds are reversed, x must be reversed as well
        x = x[::-1]
        th_lo, th_hi = th_hi, th_lo
        rev = True
    else:
        rev = False

    hi = x >= th_hi
    lo_or_hi = (x <= th_lo) | hi

    ind = np.nonzero(lo_or_hi)[0]  # Index for everyone below or above
    if not ind.size:  # prevent index error if ind is empty
        x_hyst = np.zeros_like(x, dtype=bool) | initial
    else:
        cnt = np.cumsum(lo_or_hi)  # from 0 to len(x)
        x_hyst = np.where(cnt, hi[ind[cnt-1]], initial)

    if rev:
        x_hyst = x_hyst[::-1]

    return x_hyst

x = np.linspace(0,20, 1000)
y = np.sin(x)
h1 = hyst(y, -0.2, 0.2)
h2 = hyst(y, +0.5, -0.5)
plt.plot(x, y, x, -0.2 + h1*0.4, x, -0.5 + h2)
plt.legend(('input', 'output, classic, hyst(y, -0.2, +0.2)', 
            'output, reversed, hyst(y, +0.5, -0.5)'))
plt.title('Thresholding with hysteresis')
plt.show()