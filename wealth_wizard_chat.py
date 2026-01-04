import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class WealthWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("WealthWizard 🪄💰")
        self.root.geometry("1000x700")
        self.root.configure(bg="#0d1117")  # Dark mode vibe

        # Title
        ttk.Label(root, text="WealthWizard", font=("Helvetica", 28, "bold"), 
                  foreground="#58a6ff", background="#0d1117").pack(pady=10)
        ttk.Label(root, text="Slide to see your future riches grow! 🚀", 
                  font=("Helvetica", 14), foreground="#8b949e", background="#0d1117").pack()

        # Input frame
        input_frame = ttk.Frame(root, padding=20)
        input_frame.pack(fill="x")

        # Weekly pay
        ttk.Label(input_frame, text="Weekly Pay ($):", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.pay_var = tk.DoubleVar(value=1000)
        pay_entry = ttk.Entry(input_frame, textvariable=self.pay_var, width=12, font=("Helvetica", 12))
        pay_entry.grid(row=0, column=1, sticky="w")
        pay_entry.bind("<KeyRelease>", lambda e: self.update())

        # Invest %
        ttk.Label(input_frame, text="Invest % of pay:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.invest_pct = tk.DoubleVar(value=20)
        self.invest_slider = ttk.Scale(input_frame, from_=0, to=50, orient="horizontal", 
                                       variable=self.invest_pct, length=300, command=self.update)
        self.invest_slider.grid(row=1, column=1, columnspan=2, sticky="w", pady=5)
        self.invest_label = ttk.Label(input_frame, text="20%", font=("Helvetica", 12, "bold"))
        self.invest_label.grid(row=1, column=3, padx=10, sticky="w")

        # Expected return %
        ttk.Label(input_frame, text="Expected annual return (%):", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.return_pct = tk.DoubleVar(value=8)
        self.return_slider = ttk.Scale(input_frame, from_=4, to=15, orient="horizontal", 
                                       variable=self.return_pct, length=300, command=self.update)
        self.return_slider.grid(row=2, column=1, columnspan=2, sticky="w", pady=5)
        self.return_label = ttk.Label(input_frame, text="8.0%", font=("Helvetica", 12, "bold"))
        self.return_label.grid(row=2, column=3, padx=10, sticky="w")

        # Results area
        self.result_text = tk.Text(root, height=10, width=60, font=("Helvetica", 11), bg="#161b22", fg="#c9d1d9")
        self.result_text.pack(pady=15, padx=20, fill="x")

        # Chart
        self.fig = Figure(figsize=(8, 4), dpi=100, facecolor="#0d1117")
        self.ax = self.fig.add_subplot(111, facecolor="#161b22")
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)

        # Initial update
        self.update()

    def update(self, event=None):
        try:
            weekly_pay = self.pay_var.get()
            invest_pct = self.invest_pct.get() / 100
            annual_return = self.return_pct.get() / 100

            # Update slider labels
            self.invest_label.config(text=f"{self.invest_pct.get():.0f}%")
            self.return_label.config(text=f"{self.return_pct.get():.1f}%")

            weekly_invest = weekly_pay * invest_pct
            weekly_fun = weekly_pay - weekly_invest

            # Projections (weekly compounding)
            years = [1, 5, 10]
            projections = {}
            for y in years:
                n = y * 52
                r_week = (1 + annual_return) ** (1/52) - 1
                if r_week == 0:
                    fv = weekly_invest * n
                else:
                    fv = weekly_invest * (( (1 + r_week)**n - 1 ) / r_week)
                projections[y] = fv

            # Results text
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "🔮 Your Wealth Spell 🔮\n\n")
            self.result_text.insert(tk.END, f"Weekly Pay:          ${weekly_pay:,.2f}\n")
            self.result_text.insert(tk.END, f"Investing:           ${weekly_invest:,.2f}  ({invest_pct*100:.0f}%)\n")
            self.result_text.insert(tk.END, f"Fun / Spend / Debt:  ${weekly_fun:,.2f}\n\n")
            self.result_text.insert(tk.END, "Future You Projections (at " + f"{annual_return*100:.1f}% avg return):\n")
            for y in years:
                msg = f"In {y} years → ${projections[y]:,.0f}  (≈ {projections[y]/weekly_pay:,.0f}x your weekly pay!)\n"
                self.result_text.insert(tk.END, msg)

            # Chart
            self.ax.clear()
            timeline = np.linspace(0, 10, 200)
            growth = []
            r_week = (1 + annual_return) ** (1/52) - 1
            for t in timeline:
                n = t * 52
                if r_week == 0:
                    fv = weekly_invest * n
                else:
                    fv = weekly_invest * (( (1 + r_week)**n - 1 ) / r_week)
                growth.append(fv)

            self.ax.plot(timeline, growth, color='#58a6ff', linewidth=3)
            self.ax.set_title("Your Growing Empire 📈", color='white', fontsize=14)
            self.ax.set_xlabel("Years", color='white')
            self.ax.set_ylabel("Wealth ($)", color='white')
            self.ax.tick_params(colors='white')
            self.ax.grid(True, alpha=0.3, color='gray')
            self.ax.set_facecolor("#161b22")
            self.fig.set_facecolor("#0d1117")

            # Markers
            for y in years:
                val = projections[y]
                self.ax.plot(y, val, 'o', color='#f78166')
                self.ax.annotate(f"${val:,.0f}", (y, val*1.05), color='#f78166', ha='center')

            self.canvas.draw()

        except:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "⚠️ Enter valid numbers!")

if __name__ == "__main__":
    root = tk.Tk()
    app = WealthWizard(root)
    root.mainloop()
