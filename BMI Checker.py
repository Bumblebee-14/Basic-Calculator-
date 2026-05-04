import tkinter as tk
from tkinter import ttk
import math

# ── Palette (same sci-fi cyan theme as the calculator) ──────────────────────
BG        = "#0a0a0a"
PANEL     = "#0d0d0d"
BORDER    = "#1a2a28"
CYAN      = "#00e5cc"
CYAN_DIM  = "#008f80"
TEXT      = "#cceeec"
TEXT_DIM  = "#3a6a64"
RED       = "#ff4455"
ORANGE    = "#ff8c00"
YELLOW    = "#ffd700"
GREEN     = "#39ff14"
BLUE      = "#00aaff"

# ── BMI Categories ───────────────────────────────────────────────────────────
CATEGORIES = [
    (0,    18.5, "UNDERWEIGHT",      BLUE,   "⬇ Below healthy range. Consider consulting a nutritionist."),
    (18.5, 25.0, "NORMAL WEIGHT",    GREEN,  "✔ Healthy BMI range. Maintain your lifestyle!"),
    (25.0, 30.0, "OVERWEIGHT",       YELLOW, "⚠ Slightly above range. Light diet changes may help."),
    (30.0, 35.0, "OBESE  CLASS I",   ORANGE, "⚠ Moderate obesity. Consult a healthcare provider."),
    (35.0, 40.0, "OBESE  CLASS II",  RED,    "⚠ Severe obesity. Medical guidance recommended."),
    (40.0, 999,  "OBESE CLASS III",  RED,    "⚠ Very severe obesity. Please seek medical advice."),
]

def classify(bmi):
    for lo, hi, label, color, tip in CATEGORIES:
        if lo <= bmi < hi:
            return label, color, tip
    return CATEGORIES[-1][2], CATEGORIES[-1][3], CATEGORIES[-1][4]

def ideal_weight_range(height_m):
    lo = 18.5 * height_m ** 2
    hi = 24.9 * height_m ** 2
    return lo, hi

# ── Animated gauge canvas ─────────────────────────────────────────────────────
class BMIGauge(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, width=320, height=160,
                         bg=BG, bd=0, highlightthickness=0, **kwargs)
        self._bmi   = 0
        self._color = CYAN
        self._target = 0
        self._draw_static()

    def _draw_static(self):
        """Draw the arc background bands."""
        cx, cy, r = 160, 150, 120
        bands = [
            (180, 37,  BLUE),    # underweight
            (143, 37,  GREEN),   # normal
            (106, 37,  YELLOW),  # overweight
            (69,  19,  ORANGE),  # obese I
            (50,  19,  RED),     # obese II+
        ]
        for start, extent, col in bands:
            self.create_arc(cx-r, cy-r, cx+r, cy+r,
                            start=start, extent=extent,
                            style="arc", outline=col,
                            width=18)
        # tick labels
        labels = [("15", 180), ("18.5", 143), ("25", 106),
                  ("30", 69),  ("35", 50),    ("40+", 31)]
        for txt, angle in labels:
            rad = math.radians(angle)
            tx = cx + (r + 18) * math.cos(rad)
            ty = cy - (r + 18) * math.sin(rad)
            self.create_text(tx, ty, text=txt,
                             font=("Courier", 7), fill=TEXT_DIM)

    def set_bmi(self, bmi, color):
        self._target = min(bmi, 45)
        self._color  = color
        self._animate(self._bmi)

    def _animate(self, current):
        if abs(current - self._target) < 0.3:
            current = self._target
        else:
            current += (self._target - current) * 0.15

        self._bmi = current
        self._draw_needle(current)

        if abs(current - self._target) > 0.1:
            self.after(16, lambda: self._animate(current))

    def _draw_needle(self, bmi):
        self.delete("needle")
        cx, cy, r = 160, 150, 120
        # Map BMI 10–45 → 180°–0°
        angle_deg = 180 - ((bmi - 10) / 35) * 180
        angle_deg = max(0, min(180, angle_deg))
        rad = math.radians(angle_deg)

        nx = cx + (r - 10) * math.cos(rad)
        ny = cy - (r - 10) * math.sin(rad)

        # Glow shadow
        self.create_line(cx, cy, nx, ny, fill=self._color,
                         width=6, tags="needle")
        self.create_line(cx, cy, nx, ny, fill="white",
                         width=2, tags="needle")

        # Center dot
        self.create_oval(cx-8, cy-8, cx+8, cy+8,
                         fill=self._color, outline="", tags="needle")
        # BMI text
        self.create_text(cx, cy - 45, text=f"{bmi:.1f}",
                         font=("Courier", 22, "bold"),
                         fill=self._color, tags="needle")

# ── Main App ──────────────────────────────────────────────────────────────────
class BMIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI PREDICTOR — Designed by Mihir Jaqtap")
        self.configure(bg=BG)
        self.resizable(False, False)

        self.unit_mode = tk.StringVar(value="metric")  # metric | imperial
        self._build()

    def _build(self):
        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(16, 0))
        tk.Label(hdr, text="BMI PREDICTOR", font=("Courier", 16, "bold"),
                 fg=CYAN, bg=BG).pack(side="left")
        tk.Label(hdr, text="body mass index analysis",
                 font=("Courier", 8), fg=TEXT_DIM, bg=BG).pack(side="left", padx=10)

        # ── Unit toggle ───────────────────────────────────────────────────────
        tog = tk.Frame(self, bg=BG)
        tog.pack(pady=(6, 0))
        for txt, val in [("METRIC (kg/cm)", "metric"), ("IMPERIAL (lb/in)", "imperial")]:
            tk.Radiobutton(tog, text=txt, variable=self.unit_mode, value=val,
                           font=("Courier", 9), fg=CYAN_DIM, bg=BG,
                           selectcolor=BG, activebackground=BG,
                           activeforeground=CYAN,
                           command=self._on_unit_change).pack(side="left", padx=10)

        # ── Input panel ───────────────────────────────────────────────────────
        inp = tk.Frame(self, bg=PANEL,
                       highlightbackground=BORDER, highlightthickness=1)
        inp.pack(padx=20, pady=10, fill="x")

        # Age
        self._row(inp, 0, "AGE", "years", "age_var", "25")
        # Gender
        gf = tk.Frame(inp, bg=PANEL)
        gf.grid(row=1, column=0, columnspan=3, sticky="ew", padx=16, pady=6)
        tk.Label(gf, text="GENDER", font=("Courier", 9), fg=TEXT_DIM,
                 bg=PANEL, width=10, anchor="w").pack(side="left")
        self.gender_var = tk.StringVar(value="Male")
        for g in ("Male", "Female", "Other"):
            tk.Radiobutton(gf, text=g, variable=self.gender_var, value=g,
                           font=("Courier", 9), fg=CYAN_DIM, bg=PANEL,
                           selectcolor=PANEL, activebackground=PANEL,
                           activeforeground=CYAN).pack(side="left", padx=8)

        # Height / Weight labels change with unit
        self.height_label_var = tk.StringVar(value="HEIGHT (cm)")
        self.weight_label_var = tk.StringVar(value="WEIGHT (kg)")

        self._row(inp, 2, None, None, "height_var", "170",
                  label_var=self.height_label_var)
        self._row(inp, 3, None, None, "weight_var", "70",
                  label_var=self.weight_label_var)

        # ── Calculate button ──────────────────────────────────────────────────
        btn = tk.Button(self, text="[ CALCULATE BMI ]",
                        font=("Courier", 13, "bold"),
                        fg="#000", bg=CYAN,
                        activebackground=CYAN_DIM, activeforeground="#000",
                        bd=0, padx=0, pady=10,
                        cursor="hand2",
                        command=self._calculate)
        btn.pack(fill="x", padx=20, pady=(0, 10))

        # ── Gauge ─────────────────────────────────────────────────────────────
        self.gauge = BMIGauge(self)
        self.gauge.pack(pady=(0, 4))

        # ── Result panel ──────────────────────────────────────────────────────
        res = tk.Frame(self, bg=PANEL,
                       highlightbackground=BORDER, highlightthickness=1)
        res.pack(padx=20, pady=(0, 6), fill="x")

        self.cat_var = tk.StringVar(value="— enter values and calculate —")
        self.tip_var = tk.StringVar(value="")
        self.ideal_var = tk.StringVar(value="")

        tk.Label(res, textvariable=self.cat_var,
                 font=("Courier", 14, "bold"), fg=CYAN,
                 bg=PANEL, pady=8).pack()
        tk.Label(res, textvariable=self.tip_var,
                 font=("Courier", 9), fg=TEXT, bg=PANEL,
                 wraplength=320, justify="center").pack(pady=(0, 4))
        tk.Label(res, textvariable=self.ideal_var,
                 font=("Courier", 9), fg=CYAN_DIM, bg=PANEL,
                 pady=4).pack()

        # ── BMI scale legend ──────────────────────────────────────────────────
        leg = tk.Frame(self, bg=BG)
        leg.pack(padx=20, pady=(0, 4), fill="x")
        legend_data = [
            ("<18.5", "Underweight", BLUE),
            ("18.5–25", "Normal", GREEN),
            ("25–30", "Overweight", YELLOW),
            ("30–35", "Obese I", ORANGE),
            ("35+", "Obese II+", RED),
        ]
        for i, (rng, lbl, col) in enumerate(legend_data):
            f = tk.Frame(leg, bg=BG)
            f.grid(row=0, column=i, padx=4)
            tk.Label(f, text="█", font=("Courier", 10),
                     fg=col, bg=BG).pack()
            tk.Label(f, text=rng, font=("Courier", 7),
                     fg=col, bg=BG).pack()
            tk.Label(f, text=lbl, font=("Courier", 7),
                     fg=TEXT_DIM, bg=BG).pack()
        for i in range(5):
            leg.columnconfigure(i, weight=1)

        # ── Footer ────────────────────────────────────────────────────────────
        tk.Label(self, text="Designed by Mihir Jaqtap",
                 font=("Courier", 8), fg=TEXT_DIM, bg=BG).pack(pady=(4, 10))

    def _row(self, parent, row, label_text, unit, var_name, default,
             label_var=None):
        setattr(self, var_name, tk.StringVar(value=default))
        entry_var = getattr(self, var_name)

        if label_var:
            lbl = tk.Label(parent, textvariable=label_var,
                           font=("Courier", 9), fg=TEXT_DIM,
                           bg=PANEL, width=14, anchor="w")
        else:
            lbl = tk.Label(parent, text=label_text,
                           font=("Courier", 9), fg=TEXT_DIM,
                           bg=PANEL, width=14, anchor="w")
        lbl.grid(row=row, column=0, padx=(16, 4), pady=8, sticky="w")

        ent = tk.Entry(parent, textvariable=entry_var,
                       font=("Courier", 13), fg=CYAN, bg="#111",
                       insertbackground=CYAN, bd=0,
                       highlightbackground=BORDER, highlightthickness=1,
                       width=10)
        ent.grid(row=row, column=1, padx=4, pady=8)

        if unit:
            tk.Label(parent, text=unit, font=("Courier", 9),
                     fg=TEXT_DIM, bg=PANEL).grid(row=row, column=2,
                                                  padx=(4, 16))

    def _on_unit_change(self):
        if self.unit_mode.get() == "metric":
            self.height_label_var.set("HEIGHT (cm)")
            self.weight_label_var.set("WEIGHT (kg)")
            self.height_var.set("170")
            self.weight_var.set("70")
        else:
            self.height_label_var.set("HEIGHT (in)")
            self.weight_label_var.set("WEIGHT (lb)")
            self.height_var.set("67")
            self.weight_var.set("154")

    def _calculate(self):
        try:
            age    = int(self.age_var.get())
            height = float(self.height_var.get())
            weight = float(self.weight_var.get())
        except ValueError:
            self.cat_var.set("⚠  Invalid input")
            self.tip_var.set("Please enter numeric values for age, height, and weight.")
            self.ideal_var.set("")
            return

        if age < 2 or age > 120:
            self.cat_var.set("⚠  Age out of range")
            self.tip_var.set("Please enter an age between 2 and 120.")
            return
        if height <= 0 or weight <= 0:
            self.cat_var.set("⚠  Invalid measurements")
            self.tip_var.set("Height and weight must be positive numbers.")
            return

        # Convert imperial → metric if needed
        if self.unit_mode.get() == "imperial":
            height_m = height * 0.0254
            weight_kg = weight * 0.453592
        else:
            height_m = height / 100
            weight_kg = weight

        bmi = weight_kg / (height_m ** 2)

        # Age adjustment note (BMI interpreted differently for children)
        age_note = ""
        if age < 18:
            age_note = "  [Note: BMI for children uses age/sex percentiles.]"

        label, color, tip = classify(bmi)

        ideal_lo, ideal_hi = ideal_weight_range(height_m)
        if self.unit_mode.get() == "imperial":
            ideal_lo_disp = ideal_lo / 0.453592
            ideal_hi_disp = ideal_hi / 0.453592
            unit = "lb"
        else:
            ideal_lo_disp = ideal_lo
            ideal_hi_disp = ideal_hi
            unit = "kg"

        self.cat_var.set(f"BMI {bmi:.1f}  ·  {label}")
        self.tip_var.set(tip + age_note)
        self.ideal_var.set(
            f"Ideal weight range: {ideal_lo_disp:.1f}–{ideal_hi_disp:.1f} {unit}"
        )
        self.cat_var.set(f"BMI {bmi:.1f}  ·  {label}")

        # Recolor category label
        for w in self.winfo_children():
            pass  # finding the label is easier via textvariable lookup

        # Update gauge
        self.gauge.set_bmi(bmi, color)

        # Flash the label color
        for widget in self.pack_slaves():
            if isinstance(widget, tk.Frame):
                for child in widget.pack_slaves() + widget.grid_slaves():
                    if isinstance(child, tk.Label) and \
                       child.cget("textvariable") == str(self.cat_var):
                        child.config(fg=color)

        # Force redraw category label color by recreating StringVar binding
        self._update_cat_color(color)

    def _update_cat_color(self, color):
        """Walk widget tree to recolor the category label."""
        def walk(widget):
            for child in widget.winfo_children():
                try:
                    if isinstance(child, tk.Label) and \
                            hasattr(child, '_var') and child._var == "cat":
                        child.config(fg=color)
                except Exception:
                    pass
                walk(child)

        # Simpler: re-pack a colored label overlay isn't practical in grid;
        # instead store ref at build time
        if hasattr(self, "_cat_label"):
            self._cat_label.config(fg=color)


# Patch build to save cat_label ref
_orig_build = BMIApp._build

def _patched_build(self):
    _orig_build(self)

BMIApp._build = _patched_build


class BMIAppFixed(BMIApp):
    """Subclass that stores the category label ref for color updates."""
    def _build(self):
        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(16, 0))
        tk.Label(hdr, text="BMI PREDICTOR", font=("Courier", 16, "bold"),
                 fg=CYAN, bg=BG).pack(side="left")
        tk.Label(hdr, text="body mass index analysis",
                 font=("Courier", 8), fg=TEXT_DIM, bg=BG).pack(side="left", padx=10)

        tog = tk.Frame(self, bg=BG)
        tog.pack(pady=(6, 0))
        for txt, val in [("METRIC (kg/cm)", "metric"), ("IMPERIAL (lb/in)", "imperial")]:
            tk.Radiobutton(tog, text=txt, variable=self.unit_mode, value=val,
                           font=("Courier", 9), fg=CYAN_DIM, bg=BG,
                           selectcolor=BG, activebackground=BG,
                           activeforeground=CYAN,
                           command=self._on_unit_change).pack(side="left", padx=10)

        inp = tk.Frame(self, bg=PANEL,
                       highlightbackground=BORDER, highlightthickness=1)
        inp.pack(padx=20, pady=10, fill="x")
        self._row(inp, 0, "AGE", "years", "age_var", "25")
        gf = tk.Frame(inp, bg=PANEL)
        gf.grid(row=1, column=0, columnspan=3, sticky="ew", padx=16, pady=6)
        tk.Label(gf, text="GENDER", font=("Courier", 9), fg=TEXT_DIM,
                 bg=PANEL, width=10, anchor="w").pack(side="left")
        self.gender_var = tk.StringVar(value="Male")
        for g in ("Male", "Female", "Other"):
            tk.Radiobutton(gf, text=g, variable=self.gender_var, value=g,
                           font=("Courier", 9), fg=CYAN_DIM, bg=PANEL,
                           selectcolor=PANEL, activebackground=PANEL,
                           activeforeground=CYAN).pack(side="left", padx=8)
        self.height_label_var = tk.StringVar(value="HEIGHT (cm)")
        self.weight_label_var = tk.StringVar(value="WEIGHT (kg)")
        self._row(inp, 2, None, None, "height_var", "170",
                  label_var=self.height_label_var)
        self._row(inp, 3, None, None, "weight_var", "70",
                  label_var=self.weight_label_var)

        btn = tk.Button(self, text="[ CALCULATE BMI ]",
                        font=("Courier", 13, "bold"),
                        fg="#000", bg=CYAN,
                        activebackground=CYAN_DIM, activeforeground="#000",
                        bd=0, padx=0, pady=10,
                        cursor="hand2",
                        command=self._calculate)
        btn.pack(fill="x", padx=20, pady=(0, 10))

        self.gauge = BMIGauge(self)
        self.gauge.pack(pady=(0, 4))

        res = tk.Frame(self, bg=PANEL,
                       highlightbackground=BORDER, highlightthickness=1)
        res.pack(padx=20, pady=(0, 6), fill="x")
        self.cat_var   = tk.StringVar(value="— enter values and calculate —")
        self.tip_var   = tk.StringVar(value="")
        self.ideal_var = tk.StringVar(value="")

        self._cat_label = tk.Label(res, textvariable=self.cat_var,
                                   font=("Courier", 14, "bold"), fg=CYAN,
                                   bg=PANEL, pady=8)
        self._cat_label.pack()
        tk.Label(res, textvariable=self.tip_var,
                 font=("Courier", 9), fg=TEXT, bg=PANEL,
                 wraplength=340, justify="center").pack(pady=(0, 4))
        tk.Label(res, textvariable=self.ideal_var,
                 font=("Courier", 9), fg=CYAN_DIM, bg=PANEL,
                 pady=4).pack()

        leg = tk.Frame(self, bg=BG)
        leg.pack(padx=20, pady=(0, 4), fill="x")
        legend_data = [
            ("<18.5", "Under", BLUE),
            ("18.5–25", "Normal", GREEN),
            ("25–30", "Over", YELLOW),
            ("30–35", "Obese I", ORANGE),
            ("35+", "Obese II+", RED),
        ]
        for i, (rng, lbl, col) in enumerate(legend_data):
            f = tk.Frame(leg, bg=BG)
            f.grid(row=0, column=i, padx=4)
            tk.Label(f, text="█", font=("Courier", 10), fg=col, bg=BG).pack()
            tk.Label(f, text=rng, font=("Courier", 7), fg=col, bg=BG).pack()
            tk.Label(f, text=lbl, font=("Courier", 7), fg=TEXT_DIM, bg=BG).pack()
        for i in range(5):
            leg.columnconfigure(i, weight=1)

        tk.Label(self, text="Designed by Mihir Jaqtap",
                 font=("Courier", 8), fg=TEXT_DIM, bg=BG).pack(pady=(4, 10))


if __name__ == "__main__":
    app = BMIAppFixed()
    app.mainloop()