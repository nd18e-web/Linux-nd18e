#!/usr/bin/env python3
# ND18E Konfiguracja - wykrywa sprzet i sprawdza sterowniki przy pierwszym uruchomieniu.
import tkinter as tk
from tkinter import ttk
import subprocess, os, sys

BG, FG, RED, PANEL = "#120708", "#f3e9e9", "#e11d2e", "#1a0b0e"
MARK = os.path.expanduser("~/.config/nd18e-setup-done")
if "--first-run" in sys.argv and os.path.exists(MARK):
    sys.exit(0)


def sh(c):
    try:
        return subprocess.run(c, shell=True, capture_output=True, text=True, timeout=8).stdout.strip()
    except Exception:
        return ""


class Setup(tk.Tk):
    def __init__(s):
        super().__init__()
        s.title("ND18E Konfiguracja systemu")
        s.geometry("600x500")
        s.configure(bg=BG)
        tk.Label(s, text="N", bg=BG, fg=RED, font=("sans", 54, "bold")).pack(pady=(14, 0))
        tk.Label(s, text="Konfiguracja systemu", bg=BG, fg=FG, font=("sans", 15, "bold")).pack()
        s.st = tk.Label(s, text="Wykrywanie sprzetu...", bg=BG, fg="#a89a9a")
        s.st.pack(pady=6)
        s.bar = ttk.Progressbar(s, length=420, mode="determinate")
        s.bar.pack()
        s.box = tk.Frame(s, bg=PANEL, highlightthickness=1, highlightbackground="#4a1a20")
        s.v = 0
        s.after(60, s.tick)

    def tick(s):
        s.v += 5
        s.bar["value"] = s.v
        if s.v < 100:
            s.after(45, s.tick)
        else:
            s.show()

    def row(s, k, v, ok=None):
        f = tk.Frame(s.box, bg=PANEL)
        f.pack(fill="x", padx=10, pady=4)
        tk.Label(f, text=k, bg=PANEL, fg="#a89a9a", width=14, anchor="w").pack(side="left")
        tk.Label(f, text=v, bg=PANEL, fg=FG if ok is None else ("#4ade80" if ok else "#ff6b5e"),
                 anchor="w", justify="left", wraplength=400).pack(side="left", fill="x")

    def show(s):
        s.bar.pack_forget()
        s.st.config(text="Sprzet wykryty")
        s.box.pack(fill="x", padx=18, pady=8)
        cpu = sh("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2").replace("(R)", "").replace("(TM)", "")
        gpu = sh("lspci | grep -Ei 'vga|3d|display' | head -1 | cut -d: -f3-")
        use = sh("lspci -k | grep -EiA4 'vga|3d' | grep -i 'in use' | head -1 | cut -d: -f2")
        mem = sh("awk '/MemTotal/{printf \"%.1f GB\", $2/1048576}' /proc/meminfo")
        s.row("Procesor", cpu or "?")
        s.row("Karta graficzna", gpu or "?")
        s.row("Pamiec RAM", mem or "?")
        s.row("Sterownik grafiki", use or "brak")
        if "nvidia" in gpu.lower():
            ok = "nvidia" in use.lower()
            s.row("NVIDIA", "Sterownik NVIDIA dziala - pelna wydajnosc w grach" if ok else
                  "Uzywany sterownik otwarty (nouveau). Wylacz Secure Boot w BIOS i uruchom system ponownie.", ok)
        s.row("Mikrokod CPU", "zaladowany" if sh("grep -m1 microcode /proc/cpuinfo") else "brak", bool(sh("grep -m1 microcode /proc/cpuinfo")))
        s.row("Internet", "polaczony" if sh("ping -c1 -W2 1.1.1.1 | grep '1 received'") else "brak - polacz sie z Wi-Fi (ikona przy zegarze)",
              bool(sh("ping -c1 -W2 1.1.1.1 | grep '1 received'")))
        bf = tk.Frame(s, bg=BG)
        bf.pack(pady=10)
        for t, c in (("Test dzwieku", lambda: subprocess.Popen(["paplay", "/usr/share/sounds/nd18e/startup.wav"])),
                     ("Ustawienia dzwieku", lambda: subprocess.Popen(["pavucontrol-qt"])),
                     ("Otworz Sklep", lambda: subprocess.Popen(["nd18e-store"]))):
            tk.Button(bf, text=t, command=c, bg="#2a1014", fg=FG, relief="flat", padx=12, pady=6).pack(side="left", padx=4)
        tk.Button(s, text="Gotowe", command=s.done, bg=RED, fg="white", relief="flat", padx=30, pady=8).pack(pady=6)

    def done(s):
        os.makedirs(os.path.dirname(MARK), exist_ok=True)
        open(MARK, "w").close()
        s.destroy()


Setup().mainloop()
