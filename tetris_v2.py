import tkinter as tk
import random

class Tetris:
    def __init__(self, root):
        self.root = root
        self.root.title("Tetris")
        self.W, self.H, self.C = 10, 20, 30
        self.colors = ["#f22", "#2a2", "#22f", "#df2", "#2f2", "#2df", "#f55", "#2af"]
        self.board = [[0]*self.W for _ in range(self.H)]
        self.score = self.level = self.lines = 0
        self.running = True
        self.over = False
        self.shape = None
        self.shape_x = self.shape_y = 0
        self.color_idx = random.randrange(len(self.colors))
        self.next_shape = self.make_shape()

        self.canvas = tk.Canvas(root, width=self.W*self.C, height=self.H*self.C, bg="#101010")
        self.canvas.pack()
        self.canvas.focus_set()

        self.shape = self.next_shape
        self.next_shape = self.make_shape()

        root.bind("<KeyPress-Left>", lambda e: self.move(-1))
        root.bind("<KeyPress-Right>", lambda e: self.move(1))
        root.bind("<KeyPress-Down>", lambda e: self.move(0, 1))
        root.bind("<KeyPress-Up>", lambda e: self.rotate())
        root.bind("<KeyPress-space>", lambda e: self.rotate())
        root.bind("<KeyPress-r>", lambda e: self.reset())

        self.loop()

    def make_shape(self):
        pool = [
            [[1,1,1,1]],
            [[1,1],[1,1]],
            [[1,1,1],[0,1,0]],
            [[0,1,1],[1,1,0]],
            [[1,1,0],[0,1,1]],
            [[1,1,1],[1,0,0]],
            [[1,1,1],[0,0,1]],
        ]
        s = random.choice(pool)
        return [[1 if c else 0 for c in row] for row in s]

    def rotate(self):
        if self.over: return
        s = self.shape
        n, m = len(s), len(s[0])
        rot = [[0]*n for _ in range(m)]
        for i in range(n):
            for j in range(m):
                rot[j][n-1-i] = s[i][j]
        if self.fits(rot, self.shape_x, self.shape_y):
            self.shape = rot
            self.draw()

    def move(self, dx, dy=0):
        if self.over: return
        if self.fits(self.shape, self.shape_x+dx, self.shape_y+dy):
            self.shape_x += dx
            self.shape_y += dy
            self.draw()

    def fits(self, s, x, y):
        for i in range(len(s)):
            for j in range(len(s[0])):
                if s[i][j]:
                    nx, ny = x+j, y+i
                    if nx < 0 or nx >= self.W or ny >= self.H: return False
                    if ny >= 0 and self.board[ny][nx]: return False
        return True

    def lock(self):
        for i in range(len(self.shape)):
            for j in range(len(self.shape[0])):
                if self.shape[i][j]:
                    ny, nx = self.shape_y+i, self.shape_x+j
                    if 0 <= ny < self.H and 0 <= nx < self.W:
                        self.board[ny][nx] = self.color_idx
        self.clear_lines()
        self.color_idx = random.randrange(len(self.colors))
        self.next_shape = self.make_shape()
        if not self.fits(self.next_shape, self.W//2-len(self.next_shape[0])//2, 0):
            self.over = True

    def clear_lines(self):
        kept = [row for row in self.board if any(row)]
        while len(kept) < self.H:
            kept.insert(0, [0]*self.W)
        self.board = kept
        lines = self.H - len(kept)
        if lines > 0:
            self.lines += lines
            self.level = self.lines // 10 + 1
            self.score += [0, 100, 300, 500, 800][lines] * self.level
            self.draw()

    def loop(self):
        if not self.over:
            self.drop()
        self.draw()
        if not self.over:
            self.root.after(220 - (self.level-1)*15, self.loop)

    def drop(self):
        if self.over: return
        if self.fits(self.shape, self.shape_x, self.shape_y+1):
            self.shape_y += 1
        else:
            self.lock()

    def reset(self):
        self.board = [[0]*self.W for _ in range(self.H)]
        self.score = self.level = self.lines = 0
        self.over = False
        self.color_idx = random.randrange(len(self.colors))
        self.shape = self.next_shape
        self.next_shape = self.make_shape()
        self.shape_x = self.W//2 - len(self.shape[0])//2
        self.shape_y = 0
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for y, row in enumerate(self.board):
            for x, v in enumerate(row):
                if v:
                    self.canvas.create_rectangle(x*self.C, y*self.C, (x+1)*self.C, (y+1)*self.C,
                                                 fill=self.colors[v], outline="#000")
        if self.shape and not self.over:
            for i in range(len(self.shape)):
                for j in range(len(self.shape[0])):
                    if self.shape[i][j]:
                        self.canvas.create_rectangle((self.shape_x+j)*self.C, (self.shape_y+i)*self.C,
                                                     (self.shape_x+j+1)*self.C, (self.shape_y+i+1)*self.C,
                                                     fill=self.colors[self.color_idx], outline="#000")
        self.canvas.create_text(self.W*self.C+8, 20, text="Score", fill="#aaa", font=("Arial", 10))
        self.canvas.create_text(self.W*self.C+8, 40, text=str(self.score), fill="#fff", font=("Arial", 16))
        self.canvas.create_text(self.W*self.C+8, 60, text="Level", fill="#aaa", font=("Arial", 10))
        self.canvas.create_text(self.W*self.C+8, 80, text=str(self.level), fill="#fff", font=("Arial", 16))

if __name__ == "__main__":
    root = tk.Tk()
    Tetris(root)
    root.mainloop()
