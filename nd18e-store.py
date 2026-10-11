#!/usr/bin/env python3
# ND18E Sklep - instalowanie i usuwanie aplikacji jednym klikniem (Flathub).
import tkinter as tk
from tkinter import ttk
import subprocess, threading, queue

BG, FG, RED, PANEL = "#120708", "#f3e9e9", "#e11d2e", "#1a0b0e"
APPS = [("Firefox", "org.mozilla.firefox", "Przegladarka"), ("Chromium", "org.chromium.Chromium", "Przegladarka"),
        ("Steam", "com.valvesoftware.Steam", "Gry"), ("Lutris", "net.lutris.Lutris", "Gry z Windowsa"),
        ("Discord", "com.discordapp.Discord", "Czat"), ("OBS Studio", "com.obsproject.Studio", "Nagrywanie i stream"),
        ("VLC", "org.videolan.VLC", "Filmy i muzyka"), ("Spotify", "com.spotify.Client", "Muzyka"),
        ("GIMP", "org.gimp.GIMP", "Grafika"), ("Blender", "org.blender.Blender", "Grafika 3D"),
        ("Audacity", "org.audacityteam.Audacity", "Edycja dzwieku"), ("LibreOffice", "org.libreoffice.LibreOffice", "Biuro")]


class Store(tk.Tk):
    def __init__(s):
        super().__init__()
        s.title("ND18E Sklep")
        s.geometry("640x540")
        s.configure(bg=BG)
        s.q, s.busy, s.inst = queue.Queue(), False, set()
        st = ttk.Style(s)
        st.theme_use("clam")
        st.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=FG, rowheight=30, borderwidth=0)
        st.configure("Treeview.Heading", background="#2a1014", foreground=FG)
        st.map("Treeview", background=[("selected", RED)])
        tk.Label(s, text="Sklep z aplikacjami", bg=BG, fg=RED, font=("sans", 16, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        s.sv = tk.StringVar()
        s.sv.trace_add("write", lambda *a: s.fill())
        tk.Entry(s, textvariable=s.sv, bg=PANEL, fg=FG, insertbackground=FG, relief="flat").pack(fill="x", padx=12, pady=6, ipady=6)
        s.tv = ttk.Treeview(s, columns=("n", "d", "s"), show="headings", selectmode="browse", height=10)
        for c, t, w in (("n", "Aplikacja", 190), ("d", "Opis", 260), ("s", "Stan", 130)):
            s.tv.heading(c, text=t)
            s.tv.column(c, width=w)
        s.tv.pack(fill="both", expand=True, padx=12)
        bf = tk.Frame(s, bg=BG)
        bf.pack(fill="x", padx=12, pady=8)
        s.bi = tk.Button(bf, text="Zainstaluj", bg=RED, fg="white", relief="flat", padx=16, pady=6, command=lambda: s.act("install"))
        s.bu = tk.Button(bf, text="Odinstaluj", bg="#2a1014", fg=FG, relief="flat", padx=16, pady=6, command=lambda: s.act("uninstall"))
        s.bi.pack(side="left")
        s.bu.pack(side="left", padx=8)
        s.lg = tk.Text(s, height=7, bg="#050203", fg="#7dff9a", relief="flat", font=("monospace", 9))
        s.lg.pack(fill="x", padx=12, pady=(0, 12))
        s.fill()
        s.run(["flatpak", "list", "--app", "--columns=application"], quiet=True)
        s.after(150, s.poll)

    def fill(s):
        f = s.sv.get().lower()
        s.tv.delete(*s.tv.get_children())
        for n, i, d in APPS:
            if f in n.lower() or f in d.lower():
                s.tv.insert("", "end", iid=i, values=(n, d, "Zainstalowana" if i in s.inst else ""))

    def act(s, what):
        sel = s.tv.selection()
        if not sel or s.busy:
            return
        cmd = ["sudo", "flatpak", what, "-y", "--noninteractive"] + (["flathub"] if what == "install" else []) + [sel[0]]
        s.lg.insert("end", "> " + " ".join(cmd) + "\n")
        s.run(cmd)

    def run(s, cmd, quiet=False):
        s.busy = True
        s.bi.config(state="disabled")

        def w():
            out = []
            try:
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in p.stdout:
                    out.append(line.strip())
                    if not quiet:
                        s.q.put(("log", line))
                p.wait()
                s.q.put(("done", p.returncode, out, quiet))
            except Exception as e:
                s.q.put(("log", str(e) + "\n"))
                s.q.put(("done", 1, [], quiet))
        threading.Thread(target=w, daemon=True).start()

    def poll(s):
        while not s.q.empty():
            m = s.q.get()
            if m[0] == "log":
                s.lg.insert("end", m[1])
                s.lg.see("end")
            else:
                s.busy = False
                s.bi.config(state="normal")
                if m[3]:
                    s.inst = set(m[2])
                    s.fill()
                else:
                    if m[1] == 0:
                        subprocess.Popen(["paplay", "/usr/share/sounds/nd18e/done.wav"])
                    s.run(["flatpak", "list", "--app", "--columns=application"], quiet=True)
        s.after(150, s.poll)


Store().mainloop()
