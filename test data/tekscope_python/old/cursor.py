import numpy as np
# https://matplotlib.org/3.1.3/gallery/misc/cursor_demo_sgskip.html
class Cursor(object):
    def __init__(self, ax):
        self.ax = ax
        self.lx = ax.axhline(color='k')  # the horiz line
        self.ly = ax.axvline(color='k')  # the vert line

        # text location in axes coords
        self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)

    def mouse_move(self, event):
        if not event.inaxes:
            return

        x, y = event.xdata, event.ydata
        # update the line positions
        self.lx.set_ydata(y)
        self.ly.set_xdata(x)

        self.txt.set_text('x=%1.2f, y=%1.2f' % (x, y))
        self.ax.figure.canvas.draw()

class SnaptoCursor(object):
    def __init__(self, ax, x, y):
        self.ax = ax
        self.ly = ax.axvline(color='k', alpha=0.2)  # the vert line
        self.marker, = ax.plot([0],[0], marker="o", color="crimson", zorder=3) 
        self.x = x
        self.y = y
        self.txt = ax.text(0.7, 0.9, '')

    def mouse_move(self, event):
        if not event.inaxes: return
        x, y = event.xdata, event.ydata
        indx = np.searchsorted(self.x, [x])[0]
        x = self.x[indx]
        y = self.y[indx]
        self.ly.set_xdata(x)
        self.marker.set_data([x],[y])
        self.txt.set_text('x=%1.8f, y=%1.8f' % (x, y))
        self.txt.set_position((x,y))
        self.ax.figure.canvas.draw_idle()

# t = np.arange(0.0, 1.0, 0.01)
# s = np.sin(2 * 2 * np.pi * t)

# fig, ax = plt.subplots()
# ax.plot(t, s, 'o')
# cursor = Cursor(ax)
# fig.canvas.mpl_connect('motion_notify_event', cursor.mouse_move)

# fig, ax = plt.subplots()
# ax.plot(t, s, 'o')
# snap_cursor = SnaptoCursor(ax, t, s)
# fig.canvas.mpl_connect('motion_notify_event', snap_cursor.mouse_move)

# plt.show()        