#!/usr/bin/env python3
# ND18E Menedzer zadan - jak w Windowsie: procesy, CPU, pamiec, "Zakoncz zadanie".
import tkinter as tk
from tkinter import ttk
import psutil

BG, FG, RED, PANEL = "#120708", "#f3e9e9", "#e11d2e", "#1a0b0e"


class App(tk.Tk):
    def __init__(s):
        super().__init__()
        s.title("ND18E Menedzer zadan")
        s.geometry("640x460")
        s.configure(bg=BG)
        s.hist = [0] * 60
        st = ttk.Style(s)
        st.theme_use("clam")
        st.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=FG, rowheight=22, borderwidth=0)
        st.configure("Treeview.Heading", background="#2a1014", foreground=FG, relief="flat")
        st.map("Treeview", background=[("selected", RED)])
        st.configure("TNotebook", background=BG, borderwidth=0)
        st.configure("TNotebook.Tab", background="#2a1014", foreground=FG, padding=(16, 6))
        st.map("TNotebook.Tab", background=[("selected", RED)])
        nb = ttk.Notebook(s)
        nb.pack(fill="both", expand=True)

        # --- Procesy ---
        pf = tk.Frame(nb, bg=BG)
        nb.add(pf, text="Procesy")
        s.hdr = tk.Label(pf, bg=BG, fg=FG, anchor="w", font=("sans", 11, "bold"))
        s.hdr.pack(fill="x", padx=8, pady=6)
        cols = ("name", "pid", "cpu", "mem")
        s.tv = ttk.Treeview(pf, columns=cols, show="headings", selectmode="browse")
        for c, t, w in (("name", "Nazwa", 280), ("pid", "PID", 70), ("cpu", "CPU %", 80), ("mem", "Pamiec MB", 100)):
            s.tv.heading(c, text=t)
            s.tv.column(c, width=w, anchor="w" if c == "name" else "e")
        s.tv.pack(fill="both", expand=True, padx=8)
        tk.Button(pf, text="Zakoncz zadanie", bg=RED, fg="white", relief="flat", padx=14, pady=6,
                  command=s.kill).pack(anchor="e", padx=8, pady=8)

        # --- Wydajnosc ---
        pe = tk.Frame(nb, bg=BG)
        nb.add(pe, text="Wydajnosc")
        s.info = tk.Label(pe, bg=BG, fg=FG, justify="left", font=("sans", 12))
        s.info.pack(anchor="w", padx=12, pady=12)
        s.cv = tk.Canvas(pe, bg=PANEL, height=170, highlightthickness=1, highlightbackground="#4a1a20")
        s.cv.pack(fill="x", padx=12)
        tk.Label(pe, text="Uzycie procesora (ostatnie 60 s)", bg=BG, fg="#a89a9a").pack(anchor="w", padx=12)

        psutil.cpu_percent()
        for p in psutil.process_iter():
            try:
                p.cpu_percent()
            except Exception:
                pass
        s.after(1000, s.refresh)

    def kill(s):
        sel = s.tv.selection()
        if not sel:
            return
        try:
            psutil.Process(int(s.tv.item(sel[0])["values"][1])).terminate()
        except Exception:
            pass

    def refresh(s):
        rows = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info", "cmdline"]):
            i = p.info
            if not i.get("cmdline"):
                continue  # watki jadra systemu nie sa pokazywane (jak w Windowsie)
            try:
                rows.append((i["name"] or "?", i["pid"], i["cpu_percent"] or 0.0, i["memory_info"].rss / 1048576))
            except Exception:
                pass
        rows.sort(key=lambda r: (-r[2], -r[3]))
        keep = s.tv.selection()
        sel_pid = s.tv.item(keep[0])["values"][1] if keep else None
        s.tv.delete(*s.tv.get_children())
        for r in rows:
            iid = s.tv.insert("", "end", values=(r[0], r[1], "%.1f" % r[2], "%.0f" % r[3]))
            if sel_pid is not None and r[1] == sel_pid:
                s.tv.selection_set(iid)
        cpu = psutil.cpu_percent()
        vm = psutil.virtual_memory()
        s.hdr.config(text="Procesy: %d     CPU: %.0f%%     Pamiec: %.0f%%" % (len(rows), cpu, vm.percent))
        s.info.config(text="Procesor: %.0f%%\nPamiec: %.0f / %.0f MB (%.0f%%)\nLiczba procesow: %d" % (
            cpu, vm.used / 1048576, vm.total / 1048576, vm.percent, len(rows)))
        s.hist = s.hist[1:] + [cpu]
        s.cv.delete("all")
        w, h = s.cv.winfo_width(), s.cv.winfo_height()
        pts = []
        for k, v in enumerate(s.hist):
            pts += [k * w / 59, h - v * h / 100]
        s.cv.create_line(*pts, fill=RED, width=2)
        s.after(1500, s.refresh)


App().mainloop()
