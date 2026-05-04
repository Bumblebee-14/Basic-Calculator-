import tkinter as tk
from tkinter import font
import math

# ── Colors matching your sci-fi design ──────────────────────────────────────
BG        = "#0a0a0a"
DISPLAY_BG= "#0d0d0d"
BORDER    = "#1a1a1a"
CYAN      = "#00e5cc"
CYAN_DIM  = "#008f80"
BTN_BG    = "#0f0f0f"
BTN_HOV   = "#1a2a28"
BTN_ACT   = "#00e5cc"
BTN_ACT_FG= "#000000"
TEXT_DIM  = "#007a6e"

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CALC — Designed by Mihir Jaqtap")
        self.configure(bg=BG)
        self.resizable(False, False)

        self.expression  = ""
        self.sci_mode    = tk.BooleanVar(value=False)
        self.history     = []
        self.just_evaluated = False

        self._build_ui()
        self._render_buttons()

    # ── UI Structure ─────────────────────────────────────────────────────────
    def _build_ui(self):
        # Top bar
        top = tk.Frame(self, bg=BG, pady=6)
        top.pack(fill="x", padx=10)

        tk.Label(top, text="CALC", font=("Courier", 11, "bold"),
                 fg=CYAN_DIM, bg=BG).pack(side="left")

        self.mode_btn = tk.Button(
            top, text="[ SCI MODE ]", font=("Courier", 9),
            fg=CYAN_DIM, bg=BG, bd=0, activebackground=BG,
            activeforeground=CYAN, cursor="hand2",
            command=self._toggle_mode
        )
        self.mode_btn.pack(side="right")

        # History display
        self.history_var = tk.StringVar(value="")
        hist_frame = tk.Frame(self, bg=DISPLAY_BG,
                              highlightbackground=BORDER,
                              highlightthickness=1)
        hist_frame.pack(fill="x", padx=10, pady=(0, 2))
        tk.Label(hist_frame, textvariable=self.history_var,
                 font=("Courier", 9), fg=TEXT_DIM, bg=DISPLAY_BG,
                 anchor="e", padx=10, pady=4).pack(fill="x")

        # Main display
        disp_frame = tk.Frame(self, bg=DISPLAY_BG,
                              highlightbackground=CYAN_DIM,
                              highlightthickness=1)
        disp_frame.pack(fill="x", padx=10, pady=(0, 8))

        self.display_var = tk.StringVar(value="0")
        tk.Label(disp_frame, textvariable=self.display_var,
                 font=("Courier", 30, "bold"), fg=CYAN,
                 bg=DISPLAY_BG, anchor="e", padx=14, pady=14
                 ).pack(fill="x")

        # Button container
        self.btn_frame = tk.Frame(self, bg=BG)
        self.btn_frame.pack(padx=10, pady=(0, 10))

        # Footer
        tk.Label(self, text="Designed by Mihir Jaqtap",
                 font=("Courier", 8), fg=TEXT_DIM, bg=BG
                 ).pack(pady=(0, 8))

    # ── Button Layouts ────────────────────────────────────────────────────────
    def _render_buttons(self):
        for w in self.btn_frame.winfo_children():
            w.destroy()

        if self.sci_mode.get():
            self._build_sci_layout()
            self.mode_btn.config(text="[ BASIC MODE ]")
        else:
            self._build_basic_layout()
            self.mode_btn.config(text="[ SCI MODE ]")

    def _build_basic_layout(self):
        rows = [
            [("C", "clear"), ("±", "negate"), ("%", "%"), ("÷", "/")],
            [("7", "7"),     ("8", "8"),      ("9", "9"), ("×", "*")],
            [("4", "4"),     ("5", "5"),      ("6", "6"), ("−", "-")],
            [("1", "1"),     ("2", "2"),      ("3", "3"), ("+", "+")],
            [("0", "0"),     (".", "."),       ("=", "=")],
        ]
        self._place_rows(rows, col_span={("0","0"): 2})

    def _build_sci_layout(self):
        rows = [
            [("C","clear"), ("±","negate"),  ("%","%"),     ("÷","/")],
            [("7","7"),     ("8","8"),        ("9","9"),     ("×","*")],
            [("4","4"),     ("5","5"),        ("6","6"),     ("−","-")],
            [("1","1"),     ("2","2"),        ("3","3"),     ("+","+")],
            [("0","0"),     (".","." ),       ("=","=")],
            [("sin(","sin("),("cos(","cos("),("tan(","tan(")],
            [("(",  "("),   (")",")" ),       ("π","π"),     ("√","sqrt(")],
            [("x²","x²"),   ("xʸ","**"),      ("log(","log("),("ln(","ln(")],
            [("1/x","1/x"), ("|x|","abs("),   ("e","e"),     ("!","!")],
        ]
        self._place_rows(rows, col_span={("0","0"): 2})

    def _place_rows(self, rows, col_span=None):
        col_span = col_span or {}
        for r, row in enumerate(rows):
            col = 0
            for label, cmd in row:
                span = 2 if (label, cmd) in col_span else 1
                btn = self._make_btn(label, cmd)
                btn.grid(in_=self.btn_frame, row=r, column=col,
                         columnspan=span, sticky="nsew",
                         padx=2, pady=2)
                col += span
        # Make cols/rows expand evenly
        cols = 4
        for c in range(cols):
            self.btn_frame.columnconfigure(c, weight=1, minsize=72)
        for r in range(len(rows)):
            self.btn_frame.rowconfigure(r, weight=1, minsize=62)

    # ── Button Factory ────────────────────────────────────────────────────────
    def _make_btn(self, label, cmd):
        is_op  = cmd in ("=",)
        is_clr = cmd in ("clear",)

        fg_color = BTN_ACT_FG if is_op else (
                   "#ff4455" if is_clr else CYAN)
        bg_color = CYAN if is_op else (
                   "#1a0a0a" if is_clr else BTN_BG)

        btn = tk.Button(
            self.btn_frame,
            text=label,
            font=("Courier", 14, "bold" if is_op else "normal"),
            fg=fg_color, bg=bg_color,
            activebackground=BTN_HOV,
            activeforeground=CYAN,
            bd=0, padx=0, pady=0,
            relief="flat", cursor="hand2",
            highlightbackground=BORDER,
            highlightthickness=1,
            command=lambda c=cmd: self._handle(c)
        )
        # Hover effects
        btn.bind("<Enter>", lambda e, b=btn, oc=bg_color: (
            b.config(bg=BTN_HOV) if oc not in (CYAN,) else None))
        btn.bind("<Leave>", lambda e, b=btn, oc=bg_color: b.config(bg=oc))
        return btn

    # ── Logic ─────────────────────────────────────────────────────────────────
    def _toggle_mode(self):
        self.sci_mode.set(not self.sci_mode.get())
        self._render_buttons()

    def _handle(self, cmd):
        cur = self.expression

        if cmd == "clear":
            self.expression = ""
            self.display_var.set("0")
            self.history_var.set("")
            self.just_evaluated = False
            return

        if cmd == "=":
            self._evaluate()
            return

        if cmd == "negate":
            try:
                val = float(eval(cur)) if cur else 0
                val = -val
                self.expression = str(int(val) if val == int(val) else val)
                self.display_var.set(self.expression)
            except Exception:
                pass
            return

        if cmd == "%":
            try:
                val = float(eval(cur)) if cur else 0
                val /= 100
                self.expression = str(int(val) if val == int(val) else val)
                self.display_var.set(self.expression)
            except Exception:
                pass
            return

        if cmd == "x²":
            self.expression += "**2"
            self._evaluate()
            return

        if cmd == "1/x":
            try:
                val = float(eval(cur)) if cur else 0
                result = 1 / val
                self.expression = str(int(result) if result == int(result) else result)
                self.display_var.set(self.expression)
            except ZeroDivisionError:
                self.display_var.set("Error")
                self.expression = ""
            return

        if cmd == "!":
            try:
                val = int(float(eval(cur))) if cur else 0
                result = math.factorial(val)
                self.history_var.set(f"{val}! =")
                self.expression = str(result)
                self.display_var.set(self.expression)
                self.just_evaluated = True
            except Exception:
                self.display_var.set("Error")
                self.expression = ""
            return

        if cmd == "abs(":
            self.expression += "abs("
            self.display_var.set(self.expression or "0")
            return

        # If just evaluated and user types a digit/function, start fresh
        if self.just_evaluated and cmd not in ("+", "-", "*", "/", "**"):
            self.expression = ""
            self.just_evaluated = False

        # Map special symbols to Python
        special = {
            "π": "math.pi",
            "e": "math.e",
            "sqrt(": "math.sqrt(",
            "sin(": "math.sin(math.radians(",
            "cos(": "math.cos(math.radians(",
            "tan(": "math.tan(math.radians(",
            "log(": "math.log10(",
            "ln(": "math.log(",
        }

        self.expression += special.get(cmd, cmd)

        # Display friendlier version
        disp = (self.expression
                .replace("math.pi", "π")
                .replace("math.e", "e")
                .replace("math.sqrt(", "√(")
                .replace("math.sin(math.radians(", "sin(")
                .replace("math.cos(math.radians(", "cos(")
                .replace("math.tan(math.radians(", "tan(")
                .replace("math.log10(", "log(")
                .replace("math.log(", "ln(")
                .replace("**", "^"))
        self.display_var.set(disp or "0")

    def _evaluate(self):
        expr = self.expression
        if not expr:
            return
        # Close unclosed trig parens (sin/cos/tan need double close)
        opens = expr.count("(")
        closes = expr.count(")")
        expr += ")" * (opens - closes)

        try:
            result = eval(expr, {"__builtins__": {}}, {"math": math, "abs": abs})
            result = round(result, 10)
            if isinstance(result, float) and result.is_integer():
                result = int(result)

            disp_expr = (self.expression
                         .replace("math.pi", "π")
                         .replace("math.e", "e")
                         .replace("**", "^"))
            self.history_var.set(f"{disp_expr} =")
            self.expression = str(result)
            self.display_var.set(str(result))
            self.just_evaluated = True
        except ZeroDivisionError:
            self.display_var.set("÷ 0 Error")
            self.expression = ""
        except Exception:
            self.display_var.set("Syntax Error")
            self.expression = ""

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
