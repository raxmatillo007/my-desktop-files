import importlib.util, sys, random, time
# Import parent module lazily without launching GUI
spec = importlib.util.spec_from_file_location("tetrismod", "/c/Users/Microsoft N/Desktop/tetris.py")
# The module immediately runs mainloop() -> we prepend a guard by exec'ing only the class defs.
src = open("/c/Users/Microsoft N/Desktop/tetris.py").read()
# extract up to the GUI launch, then exec class definitions only
head = src.split("root = tk.Tk()")[0]
ns = {}
exec(head, ns)
T = ns["Tetris"]

g = T.__new__(T)
g.root = type("R", (), {"title": lambda s: None, "bind": lambda s, a, b: None,
                       "after": lambda s, ms, fn: None, "delete": lambda s, *a, **k: None})()
g.canvas = type("C", (), {"create_rectangle": lambda s, *a, **k: None,
                          "delete": lambda s, *a, **k: None})()
g.W, g.H, g.C = 10, 20, 30
g.colors = ["#f22", "#2a2", "#22f", "#df2", "#2f2", "#2df", "#f55", "#2af"]
g.board = [[0]*g.W for _ in range(g.H)]
g.score = g.level = g.lines = 0
g.running = True
g.over = False
g.shape = g.next_shape = None
g.shape_x = g.shape_y = 0
g.color_idx = 0
g.shape = g.next_shape
g.shape_x = g.W//2 - len(g.shape[0])//2
g.shape_y = 0

# tests
def rect(s, x, y, w, h):  # label coords inline
    return s
fails = 0
for _ in range(500):
    g.shape = g.next_shape
    g.next_shape = g.make_shape()
    g.shape_x = g.W//2 - len(g.shape[0])//2
    g.shape_y = 0
    # try random moves
    for _ in range(30):
        dx = random.choice([-1, 0, 1])
        g.move(dx)
        g.rotate()
    g.drop()
    if not g.fits(g.shape, g.shape_x, g.shape_y):  # landed
        g.lock()
    if g.over:
        g.reset()
# verify board dims after lock
if g.board and len(g.board) == g.H and all(len(r) == g.W for r in g.board):
    print("LOGIC OK: board reset dims correct after 500 random-play iterations")
else:
    print("LOGIC FAIL:", len(g.board) if g.board else None)
    fails += 1
print("score state:", g.score, "lines:", g.lines, "level:", g.level)
