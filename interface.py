import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import threading
import subprocess
import webbrowser
from pathlib import Path
from logic import load_json_data, SystemInfo, Tweaker, WingetManager, UninstallManager, ChocolateyManager
import self_update

# --- ANA PENCERE ---
class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.app_exe_name = "Saydut Program Yöneticisi.exe"
        self.current_version = self_update.read_local_version(Path(os.getcwd()))
        self.title(f"Saydut Program Yöneticisi v{self.current_version}")
        self.geometry("1100x750")
        self.minsize(900, 650)
        
        # Grid Yapılandırması
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- SOL MENÜ (Sidebar) ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1) # Spacer

        # Logo / Başlık
        self.logo_label = ctk.CTkLabel(self.sidebar, text="SAYDUT\nYAZILIM", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))
        
        self.lbl_version = ctk.CTkLabel(self.sidebar, text=f"v{self.current_version} Stable", text_color="gray")
        self.lbl_version.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Menü Butonları
        self.btn_programs = self.create_sidebar_btn("🚀 Programlar", self.show_programs)
        self.btn_programs.grid(row=2, column=0, padx=20, pady=8)
        
        self.btn_choco = self.create_sidebar_btn("🍫 Chocolatey", self.show_choco)
        self.btn_choco.grid(row=3, column=0, padx=20, pady=8)

        self.btn_tweaks = self.create_sidebar_btn("🛠️ Tweakler", self.show_tweaks)
        self.btn_tweaks.grid(row=4, column=0, padx=20, pady=8)
        
        self.btn_updates = self.create_sidebar_btn("🔄 Uygulama Güncelle", self.show_updates)
        self.btn_updates.grid(row=5, column=0, padx=20, pady=8)
        
        self.btn_uninstall = self.create_sidebar_btn("🗑️ Kaldır", self.show_uninstall)
        self.btn_uninstall.grid(row=6, column=0, padx=20, pady=8)

        self.btn_system = self.create_sidebar_btn("💻 Sistem", self.show_system)
        self.btn_system.grid(row=7, column=0, padx=20, pady=8)
        
        self.btn_about = self.create_sidebar_btn("ℹ️ Hakkında", self.show_about)
        self.btn_about.grid(row=8, column=0, padx=20, pady=8, sticky="s")

        # Tema Seçici (Alt Kısım)
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar, text="Tema Modu:", anchor="w")
        self.appearance_mode_label.grid(row=9, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar, values=["Dark", "Light", "System"],
                                                               command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=10, column=0, padx=20, pady=(10, 20))

        # --- SAĞ TARAF (Ana İçerik) ---
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)
        
        # Sekmeleri Hazırla
        self.frames = {}
        for F in (ProgramsFrame, ChocolateyFrame, TweaksFrame, UpdatesFrame, UninstallFrame, SystemFrame, AboutFrame):
            frame = F(parent=self.main_area, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_programs() # Başlangıç sayfası
        # Program (self) update kontrolü (sessiz)
        self.after(1500, self._auto_check_launcher_update)


    def create_sidebar_btn(self, text, command):
        return ctk.CTkButton(self.sidebar, text=text, command=command, 
                             fg_color="transparent", text_color=("gray10", "#DCE4EE"), 
                             hover_color=("gray70", "gray30"), anchor="w", height=45, 
                             font=ctk.CTkFont(size=15, weight="bold"))

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    # Buton Fonksiyonları
    def show_programs(self): self.show_frame(ProgramsFrame)
    def show_choco(self): self.show_frame(ChocolateyFrame)
    def show_tweaks(self): self.show_frame(TweaksFrame)
    def show_updates(self): self.show_frame(UpdatesFrame)
    def show_uninstall(self): self.show_frame(UninstallFrame)
    def show_system(self): 
        self.show_frame(SystemFrame)
        self.frames[SystemFrame].refresh() 
    def show_about(self): self.show_frame(AboutFrame)

    
    # ---------------- SELF UPDATE (Programın kendisi) ----------------
    def _auto_check_self_update(self):
        # Sessiz kontrol: hata mesajı yok
        threading.Thread(target=self._self_update_worker, args=(False,), daemon=True).start()

    def _check_self_update_manual(self):
        threading.Thread(target=self._self_update_worker, args=(True,), daemon=True).start()

    def _self_update_worker(self, show_messages: bool):
        try:
            install_dir = Path(os.getcwd())
            current = self_update.read_local_version(install_dir)
            rel = self_update.fetch_latest_release()
            latest = self_update._normalize_version(rel.tag)

            if not self_update.is_newer(latest, current):
                if show_messages:
                    messagebox.showinfo("Güncelleme", "Program güncel.")
                return

            def open_dialog():
                dlg = None

                def on_later():
                    try:
                        dlg.destroy()
                    except Exception:
                        pass

                def on_update():
                    # download then run updater
                    dlg.btn_update.configure(state="disabled")
                    dlg.btn_later.configure(state="disabled")
                    dlg.status.configure(text="İndiriliyor...")

                    def progress(done, total):
                        if total > 0:
                            pct = int(done * 100 / total)
                            dlg.status.configure(text=f"İndiriliyor... %{pct}")
                        else:
                            dlg.status.configure(text="İndiriliyor...")

                    try:
                        zpath = self_update.TEMP_ROOT / rel.zip_name
                        self_update.download_file(rel.zip_url, zpath, progress_cb=progress)
                        dlg.status.configure(text="Kurulum başlatılıyor...")
                        # updater çağır ve uygulamayı kapat
                        self_update.run_updater(install_dir, zpath, self.app_exe_name)
                        self.after(200, self.destroy)
                    except Exception as e:
                        dlg.status.configure(text=f"Hata: {e}")
                        dlg.btn_later.configure(state="normal")

                dlg = SelfUpdateDialog(self, latest, rel.body, on_update, on_later)

            self.after(0, open_dialog)

        except Exception as e:
            if show_messages:
                messagebox.showerror("Güncelleme Hatası", str(e))
            # sessizde yut

    def _auto_check_launcher_update(self):
        threading.Thread(target=self._launcher_update_worker, daemon=True).start()

    def _launcher_update_worker(self):
        try:
            install_dir = Path(os.getcwd())
            current = self_update.read_local_version(install_dir)
            payload = self_update.fetch_programs_manifest()
            latest = self_update.read_program_version(payload, "program-yoneticisi")
            if latest and self_update.is_newer(latest, current):
                self.after(0, lambda: self._show_launcher_update_prompt(current, latest))
        except Exception:
            return

    def _show_launcher_update_prompt(self, current: str, latest: str):
        if messagebox.askyesno(
            "Güncelleme mevcut",
            f"Mevcut sürüm: {current}\nYeni sürüm: {latest}\n\nGüncellemeyi Saydut Launcher ile yapmak ister misin?",
        ):
            self.open_launcher_update()

    def open_launcher_update(self):
        launcher_hint_path = r"C:\Saydut\launcher_path.txt"
        launcher_candidates = [
            r"C:\Saydut\SaydutLauncher\SaydutLauncher.exe",
            r"C:\Saydut\Saydut Launcher\SaydutLauncher.exe",
            r"C:\Saydut\SaydutLauncher\Saydut Launcher.exe",
        ]

        launcher_path = None
        if os.path.exists(launcher_hint_path):
            try:
                with open(launcher_hint_path, "r", encoding="utf-8") as handle:
                    candidate = handle.read().strip()
                if candidate and os.path.exists(candidate):
                    launcher_path = candidate
            except OSError:
                launcher_path = None

        if not launcher_path:
            launcher_path = next((p for p in launcher_candidates if os.path.exists(p)), None)

        if launcher_path:
            try:
                if launcher_path.lower().endswith(".py"):
                    subprocess.Popen([sys.executable, launcher_path])
                else:
                    subprocess.Popen([launcher_path])
                return
            except Exception as exc:
                messagebox.showerror("Hata", f"Launcher acilamadi:\n{exc}")
                return

        messagebox.showinfo(
            "Launcher Gerekli",
            "Guncelleme icin Saydut Launcher gerekli.\nIndirip kurduktan sonra tekrar deneyin.",
        )
        webbrowser.open("https://www.saydut.com")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

# --- 1. PROGRAMLAR SAYFASI ---


# --- PROGRAM (SELF) UPDATE DIALOG ---
class SelfUpdateDialog(ctk.CTkToplevel):
    def __init__(self, master, latest_version: str, release_notes: str, on_update, on_later):
        super().__init__(master)
        self.title("Yeni sürüm bulundu")
        self.geometry("620x520")
        self.resizable(False, False)
        self.grab_set()

        wrap = ctk.CTkFrame(self, corner_radius=14)
        wrap.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(wrap, text="Yeni sürüm bulundu", font=("Arial", 22, "bold")).pack(anchor="w", padx=16, pady=(14, 0))
        ctk.CTkLabel(wrap, text=f"Yeni sürüm: v{latest_version}", text_color="gray").pack(anchor="w", padx=16, pady=(2, 10))

        ctk.CTkLabel(wrap, text="Yenilikler", font=("Arial", 14, "bold")).pack(anchor="w", padx=16, pady=(6, 6))
        notes = ctk.CTkTextbox(wrap, height=300, corner_radius=10)
        notes.pack(fill="both", expand=False, padx=16)
        notes.insert("1.0", release_notes.strip() or "(Not bulunamadı)")
        notes.configure(state="disabled")

        self.status = ctk.CTkLabel(wrap, text="", text_color="gray")
        self.status.pack(anchor="w", padx=16, pady=(10, 0))

        btnrow = ctk.CTkFrame(wrap, fg_color="transparent")
        btnrow.pack(fill="x", padx=16, pady=14)

        self.btn_update = ctk.CTkButton(btnrow, text="Güncelle", command=on_update, height=38)
        self.btn_update.pack(side="right")

        self.btn_later = ctk.CTkButton(btnrow, text="Sonra", command=on_later, height=38, fg_color="#2b2b2b")
        self.btn_later.pack(side="right", padx=(0, 10))


class ProgramsFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.winget = WingetManager()
        self.checkboxes = []
        self.all_selected = False  # Seçim durumu
        
        # Başlık
        head = ctk.CTkLabel(self, text="Popüler Programlar (Winget)", font=("Inter", 26, "bold"))
        head.pack(anchor="w", pady=(0,5))
        
        desc = ctk.CTkLabel(self, text="Winget (Microsoft Resmi Kaynağı) üzerinden güvenli, reklamsız ve hızlı kurulum.", text_color="gray")
        desc.pack(anchor="w", pady=(0,15))

        # Liste Alanı (Scroll)
        self.scroll = ctk.CTkScrollableFrame(self, label_text="Yazılım Kütüphanesi")
        self.scroll.pack(fill="both", expand=True, pady=(0, 20))
        
        # Verileri Yükle
        self.load_programs()

        # Alt Butonlar
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        
        self.btn_select_all = ctk.CTkButton(btn_frame, text="Tümünü Seç", command=self.toggle_select_all, 
                                            fg_color="#475569", hover_color="#334155", width=120)
        self.btn_select_all.pack(side="left")

        self.btn_install = ctk.CTkButton(btn_frame, text="Seçilenleri Kur", command=self.install_selected, 
                                         fg_color="#22c55e", hover_color="#15803d", height=45, width=200)
        self.btn_install.pack(side="right")
        
        self.log_lbl = ctk.CTkLabel(btn_frame, text="Hazır", text_color="gray")
        self.log_lbl.pack(side="right", padx=20)

    def load_programs(self):
        data = load_json_data("programs.json")
        if not data:
            data = [
                {"name": "Google Chrome", "id": "Google.Chrome", "description": "Hızlı web tarayıcısı."},
                {"name": "Discord", "id": "Discord.Discord", "description": "Sohbet uygulaması."},
                {"name": "WinRAR", "id": "RARLab.WinRAR", "description": "Arşiv yöneticisi."},
                {"name": "VLC", "id": "VideoLAN.VLC", "description": "Medya oynatıcı."},
                {"name": "Steam", "id": "Valve.Steam", "description": "Oyun platformu."},
                {"name": "Spotify", "id": "Spotify.Spotify", "description": "Müzik platformu."},
                {"name": "Zoom", "id": "Zoom.Zoom", "description": "Video konferans."},
                {"name": "Adobe Acrobat", "id": "Adobe.Acrobat.Reader.64-bit", "description": "PDF okuyucu."}
            ]

        row = 0
        col = 0
        for item in data:
            card = ctk.CTkFrame(self.scroll, fg_color=("gray90", "gray20"))
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.scroll.grid_columnconfigure(0, weight=1)
            self.scroll.grid_columnconfigure(1, weight=1)
            self.scroll.grid_columnconfigure(2, weight=1) # 3 Kolonlu yapı

            cb = ctk.CTkCheckBox(card, text=item['name'], font=("Inter", 14, "bold"))
            cb.id_val = item['id']
            cb.pack(anchor="w", padx=10, pady=(10, 5))
            self.checkboxes.append(cb)

            desc = ctk.CTkLabel(card, text=item.get('description', ''), text_color="gray", wraplength=200, justify="left")
            desc.pack(anchor="w", padx=35, pady=(0, 10))

            col += 1
            if col > 2: # 3 Kolon
                col = 0
                row += 1

    def toggle_select_all(self):
        # Durumu tersine çevir
        self.all_selected = not self.all_selected
        
        # Tüm kutuları yeni duruma göre güncelle
        for cb in self.checkboxes:
            if self.all_selected:
                cb.select()
            else:
                cb.deselect()
        
        # Buton metnini güncelle
        new_text = "Seçimi Kaldır" if self.all_selected else "Tümünü Seç"
        self.btn_select_all.configure(text=new_text)

    def update_log(self, text):
        self.log_lbl.configure(text=text)

    def install_selected(self):
        selected = [cb.id_val for cb in self.checkboxes if cb.get()]
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen en az bir program seçin.")
            return
        
        self.btn_install.configure(state="disabled", text="Kuruluyor...")
        
        def install_queue():
            total = len(selected)
            for i, app_id in enumerate(selected):
                self.update_log(f"[{i+1}/{total}] Kuruluyor: {app_id}...")
                
                # SESSİZ KURULUM YERİNE CMD PENCERESİ AÇ
                try:
                    # Yeni bir konsol penceresi açıp orada winget komutunu çalıştırıyoruz.
                    # /k komutu pencerenin açık kalmasını sağlar (debug için iyi), /c ise işlem bitince kapatır.
                    # Kullanıcı görsün diye '/c' (close after finish) veya sürecin tamamlandığını görmek isterse pause ekleyebiliriz.
                    # Burada standart olarak pencere açılsın, işlem bitince kapansın istiyoruz.
                    
                    cmd = f'winget install --id {app_id} -e --accept-package-agreements --accept-source-agreements'
                    
                    # subprocess.CREATE_NEW_CONSOLE bayrağı ile yeni pencere
                    subprocess.run(f'start /wait cmd /c "{cmd}"', shell=True)
                    
                except Exception as e:
                    print(f"Hata: {e}")
            
            self.update_log("Tüm işlemler tamamlandı.")
            self.btn_install.configure(state="normal", text="Seçilenleri Kur")
            
        threading.Thread(target=install_queue, daemon=True).start()

# --- 2. CHOCOLATEY SAYFASI ---
class ChocolateyFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.choco = ChocolateyManager()
        self.checkboxes = []
        self.installed = self.choco.is_installed()
        self.all_selected = False

        # Başlık
        head = ctk.CTkLabel(self, text="Chocolatey Paketleri", font=("Inter", 26, "bold"), text_color="#d2691e")
        head.pack(anchor="w", pady=(0,5))
        
        status_text = "Yüklü ✅" if self.installed else "Yüklü Değil ❌"
        status_color = "#10b981" if self.installed else "#ef4444"
        self.lbl_status = ctk.CTkLabel(self, text=f"Durum: {status_text}", text_color=status_color, font=("Inter", 14, "bold"))
        self.lbl_status.pack(anchor="w", pady=(0, 15))

        if not self.installed:
            self.btn_install_choco = ctk.CTkButton(self, text="Chocolatey'i Şimdi Yükle", command=self.install_core, fg_color="#d2691e", hover_color="#a0522d")
            self.btn_install_choco.pack(anchor="w", pady=(0, 20))

        # Liste
        self.scroll = ctk.CTkScrollableFrame(self, label_text="Choco Paketleri")
        self.scroll.pack(fill="both", expand=True, pady=(0, 20))
        
        self.load_packages()

        # Alt Butonlar
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x")

        self.btn_select_all = ctk.CTkButton(btn_frame, text="Tümünü Seç", command=self.toggle_select_all, width=120, fg_color="#475569")
        self.btn_select_all.pack(side="left")

        self.btn_run = ctk.CTkButton(btn_frame, text="Seçilenleri Kur", command=self.run_install, 
                                     fg_color="#d2691e", hover_color="#a0522d", height=45)
        self.btn_run.pack(side="right", fill="x", expand=True, padx=10)
        
        self.log_lbl = ctk.CTkLabel(self, text="", text_color="gray")
        self.log_lbl.pack()

        if not self.installed:
            self.btn_run.configure(state="disabled")
            self.btn_select_all.configure(state="disabled")

    def toggle_select_all(self):
        self.all_selected = not self.all_selected
        for cb in self.checkboxes:
            if self.all_selected: cb.select()
            else: cb.deselect()
        self.btn_select_all.configure(text="Seçimi Kaldır" if self.all_selected else "Tümünü Seç")

    def install_core(self):
        self.btn_install_choco.configure(state="disabled", text="Yükleniyor...")
        
        # CMD penceresi ile kurulum
        def run_install():
            try:
                # PowerShell komutunu yeni pencerede çalıştır
                cmd = "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
                subprocess.run(f'start /wait powershell -Command "{cmd}"', shell=True)
                self.update_log("Chocolatey kuruldu! Programı yeniden başlatın.")
            except Exception as e:
                self.update_log(f"Hata: {e}")

        threading.Thread(target=run_install, daemon=True).start()

    def update_log(self, msg):
        self.log_lbl.configure(text=msg)
        if "kuruldu" in msg:
            self.installed = True
            self.lbl_status.configure(text="Yüklü ✅ (Yeniden Başlatma Gerekebilir)", text_color="#10b981")
            self.btn_run.configure(state="normal")
            self.btn_select_all.configure(state="normal")
            self.btn_install_choco.pack_forget()

    def load_packages(self):
        data = load_json_data("chocolatey.json")
        if not data:
            data = [{"name": "NodeJS", "package": "nodejs"}, {"name": "Python", "package": "python"}, {"name": "Git", "package": "git"}]

        row = 0
        col = 0
        for item in data:
            cb = ctk.CTkCheckBox(self.scroll, text=item['name'], font=("Inter", 13))
            cb.pkg_name = item['package']
            cb.grid(row=row, column=col, padx=20, pady=10, sticky="w")
            
            if not self.installed: cb.configure(state="disabled")
            self.checkboxes.append(cb)
            
            col += 1
            if col > 3:
                col = 0
                row += 1

    def run_install(self):
        selected = [cb.pkg_name for cb in self.checkboxes if cb.get()]
        if not selected: return
        self.btn_run.configure(state="disabled")
        
        def install_thread():
            packages_str = " ".join(selected)
            try:
                # CMD Penceresi ile kurulum
                cmd = f"choco install {packages_str} -y"
                subprocess.run(f'start /wait cmd /c "{cmd} & pause"', shell=True)
                self.update_log("İşlem tamamlandı.")
            except Exception as e:
                self.update_log(f"Hata: {e}")
            self.btn_run.configure(state="normal")
        
        threading.Thread(target=install_thread, daemon=True).start()

# --- 3. TWEAKLER SAYFASI ---
class TweaksFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.tweaker = Tweaker()
        self.checkboxes = []
        self.all_selected = False

        head = ctk.CTkLabel(self, text="Sistem İyileştirmeleri (Tweaks)", font=("Inter", 26, "bold"))
        head.pack(anchor="w", pady=(0,10))
        
        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, pady=10)
        
        self.load_tweaks()
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)

        self.btn_select_all = ctk.CTkButton(btn_frame, text="Tümünü Seç", command=self.toggle_select_all, width=120, fg_color="#475569")
        self.btn_select_all.pack(side="left")

        self.btn_apply = ctk.CTkButton(btn_frame, text="Seçilenleri Uygula", fg_color="#ef4444", hover_color="#b91c1c", 
                                       command=self.apply_tweaks, height=45)
        self.btn_apply.pack(side="right", fill="x", expand=True, padx=10)
        
        self.status = ctk.CTkLabel(self, text="Hazır", text_color="gray")
        self.status.pack()

    def load_tweaks(self):
        data = load_json_data("tweaks.json")
        for item in data:
            row = ctk.CTkFrame(self.scroll, fg_color=("gray95", "gray25"))
            row.pack(fill="x", pady=5, padx=5)
            
            cb = ctk.CTkSwitch(row, text=item['name'], font=("Inter", 14, "bold"))
            cb.tweak_data = item
            cb.pack(side="left", padx=10, pady=10)
            
            desc = ctk.CTkLabel(row, text=item.get('description', ''), text_color="gray")
            desc.pack(side="right", padx=10)
            self.checkboxes.append(cb)

    def toggle_select_all(self):
        self.all_selected = not self.all_selected
        for cb in self.checkboxes:
            if self.all_selected: cb.select()
            else: cb.deselect()
        self.btn_select_all.configure(text="Seçimi Kaldır" if self.all_selected else "Tümünü Seç")

    def log(self, text):
        self.status.configure(text=text)

    def apply_tweaks(self):
        selected = [cb.tweak_data for cb in self.checkboxes if cb.get()]
        if not selected: return
        
        if not messagebox.askyesno("Dikkat", "Seçilen ayarlar sisteme uygulanacak.\nSistem Geri Yükleme noktası oluşturulması önerilir."):
            return

        self.btn_apply.configure(state="disabled")
        
        def run_thread():
            for tweak in selected:
                # Tweak işlemleri genellikle hızlıdır ve sessiz yapılır, ama cmd gerektirenler için
                # logic.py'de subprocess.run kısmını düzenlemek gerekir.
                # Şimdilik standart sessiz modda bırakıyoruz çünkü tweakler genelde registry ayarıdır.
                self.tweaker.apply_tweak(tweak, self.log)
            self.log("İşlemler tamamlandı.")
            self.btn_apply.configure(state="normal")
            
        threading.Thread(target=run_thread, daemon=True).start()

# --- 4. GÜNCELLEME SAYFASI ---
class UpdatesFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.wm = WingetManager()
        self.update_checkboxes = []  # Checkbox referansları
        self.found_updates = []
        self.all_selected = False

        head = ctk.CTkLabel(self, text="Yazılım Güncellemeleri", font=("Inter", 26, "bold"))
        head.pack(anchor="w", pady=10)
        
        desc = ctk.CTkLabel(self, text="Yüklü programları tarar ve güncellenecekleri listeler.", text_color="gray")
        desc.pack(anchor="w")

        # Buton Paneli (Üst)
        top_btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_btn_frame.pack(anchor="w", pady=10, fill="x")

        self.btn_scan = ctk.CTkButton(top_btn_frame, text="Taramayı Başlat", command=self.scan_updates, height=40)
        self.btn_scan.pack(side="left", padx=(0, 10))

        # Yükleme Göstergesi
        self.loading_label = ctk.CTkLabel(top_btn_frame, text="", text_color="#3b82f6")
        self.loading_label.pack(side="left")
        
        self.list_area = ctk.CTkScrollableFrame(self, label_text="Bulunan Güncellemeler")
        self.list_area.pack(fill="both", expand=True, pady=10)
        
        # Alt Butonlar
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=5)

        self.btn_select_all = ctk.CTkButton(bottom_frame, text="Tümünü Seç", command=self.toggle_select_all, width=120, fg_color="#475569")
        self.btn_select_all.pack(side="left")

        self.btn_update_selected = ctk.CTkButton(bottom_frame, text="Seçilenleri Güncelle", command=self.run_updates, 
                                                 fg_color="#22c55e", hover_color="#15803d", height=45, state="disabled")
        self.btn_update_selected.pack(side="right")

    def toggle_select_all(self):
        self.all_selected = not self.all_selected
        for cb in self.update_checkboxes:
            if self.all_selected: cb.select()
            else: cb.deselect()
        self.btn_select_all.configure(text="Seçimi Kaldır" if self.all_selected else "Tümünü Seç")

    def scan_updates(self):
        self.btn_scan.configure(state="disabled")
        self.loading_label.configure(text="Taranıyor... Lütfen bekleyin.")
        self.btn_update_selected.configure(state="disabled")
        
        # Listeyi Temizle
        for widget in self.list_area.winfo_children():
            widget.destroy()
        self.update_checkboxes.clear()
        self.found_updates.clear()

        # Thread ile tarama başlat (Donmayı önler)
        self.wm.check_updates(self.on_scan_finished)
        
    def on_scan_finished(self, updates):
        self.btn_scan.configure(state="normal")
        self.loading_label.configure(text="")
        
        if not updates:
            ctk.CTkLabel(self.list_area, text="Sisteminiz güncel! Güncelleme bulunamadı.", text_color="gray").pack(pady=20)
            return
            
        # Güncellemeleri Listele
        for line in updates:
            # Satırın tam verisini sakla
            full_line = line.strip()
            
            # --- GELİŞMİŞ ID TESPİTİ ---
            # Winget çıktısı: "Ad  ID  Sürüm  Mevcut  Kaynak"
            # Genellikle Sürüm (Version) sütunu sayılar ve noktalar içerir (örn: 112.0.5615.49)
            # ID ise sürümden önceki sütundur.
            
            parts = full_line.split()
            app_id = None
            
            # Sürüm numarasını bulmaya çalış (İçinde nokta olan ve rakamla başlayan ilk öğe)
            version_index = -1
            for i, part in enumerate(parts):
                # Basit versiyon kontrolü: Rakamla başlar, nokta içerir, en az 3 karakterdir
                if i > 0 and len(part) > 3 and part[0].isdigit() and '.' in part:
                    version_index = i
                    break
            
            if version_index > 0:
                # Sürüm bulunduysa, bir önceki öğe ID'dir.
                app_id = parts[version_index - 1]
            else:
                # Bulunamazsa varsayılan olarak sondan 3. öğeyi (Name, ID, Version, Avail, Source) almayı dene
                # veya satır çok kısaysa güvenli bir tahmin yap
                if len(parts) >= 2:
                    # Genellikle ID, içinde nokta olan bir stringdir (Google.Chrome gibi)
                    possible_ids = [p for p in parts if '.' in p and not p[0].isdigit()]
                    if possible_ids:
                        app_id = possible_ids[0] # En olası aday
                    else:
                        app_id = parts[-2] # Fallback
                else:
                    app_id = full_line # Çok kötü durum, satırı komple ver

            # Görsel satır oluştur
            row = ctk.CTkFrame(self.list_area, fg_color=("gray90", "gray25"))
            row.pack(fill="x", pady=2, padx=5)
            
            # Checkbox'a tespit edilen ID'yi ata
            cb = ctk.CTkCheckBox(row, text=full_line, font=("Consolas", 12))
            cb.app_id = app_id 
            
            cb.pack(side="left", padx=10, pady=5)
            cb.select() # Varsayılan olarak seçili
            self.update_checkboxes.append(cb)

        self.btn_update_selected.configure(state="normal")

    def run_updates(self):
        selected_updates = []
        for cb in self.update_checkboxes:
            if cb.get():
                selected_updates.append(cb.app_id)

        if not selected_updates:
            messagebox.showwarning("Uyarı", "Lütfen güncellenecek programları seçin.")
            return

        if messagebox.askyesno("Onay", f"{len(selected_updates)} program güncellenecek. Bu işlem zaman alabilir.\nDevam edilsin mi?"):
            self.btn_update_selected.configure(state="disabled", text="Güncelleniyor...")
            
            # Thread içinde güncelle
            def update_thread():
                total = len(selected_updates)
                for i, app_id in enumerate(selected_updates):
                    # UI'da ilerlemeyi göster
                    self.loading_label.configure(text=f"Güncelleniyor ({i+1}/{total}): {app_id}...")
                    
                    try:
                        # --- CMD EKRANI AÇILARAK GÜNCELLEME ---
                        # subprocess.run yerine os.system veya start komutu ile yeni pencere açıyoruz.
                        # winget upgrade komutu interaktiftir, kullanıcıya göstermek en iyisidir.
                        
                        cmd = f"winget upgrade --id {app_id} --accept-source-agreements --accept-package-agreements"
                        # start /wait cmd /c "komut & pause" -> İşlem bitince pencere kapanmaz (pause sayesinde), kullanıcı sonucu görür.
                        # pause istemezseniz kaldrabilirsiniz.
                        
                        subprocess.run(f'start /wait cmd /c "{cmd} & echo. & echo İşlem Tamamlandı... & timeout /t 3"', shell=True)
                        
                    except Exception as e:
                        print(f"Update Error for {app_id}: {e}")
                
                self.loading_label.configure(text="Tüm güncellemeler tamamlandı.")
                self.btn_update_selected.configure(state="normal", text="Seçilenleri Güncelle")

            threading.Thread(target=update_thread, daemon=True).start()

# --- 5. KALDIRMA (UNINSTALL) SAYFASI ---
class UninstallFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.manager = UninstallManager()
        self.radio_var = tk.StringVar(value="")
        
        head = ctk.CTkLabel(self, text="Program Kaldırma Aracı", font=("Inter", 26, "bold"), text_color="#ef4444")
        head.pack(anchor="w", pady=(0,5))
        
        # Arama ve Yenileme
        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.pack(fill="x", pady=10)
        
        self.search_entry = ctk.CTkEntry(ctrl_frame, placeholder_text="Program ara...", width=300)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.filter_list)
        
        self.btn_refresh = ctk.CTkButton(ctrl_frame, text="Yenile", command=self.refresh_list, width=100, fg_color="#475569")
        self.btn_refresh.pack(side="left")

        # Liste
        self.scroll = ctk.CTkScrollableFrame(self, label_text="Yüklü Programlar")
        self.scroll.pack(fill="both", expand=True, pady=10)
        
        # Butonlar
        self.btn_uninstall = ctk.CTkButton(self, text="Seçili Programı Kaldır", command=self.uninstall_selected, 
                                           fg_color="#ef4444", hover_color="#b91c1c", height=45)
        self.btn_uninstall.pack(fill="x", pady=5)
        
        self.status = ctk.CTkLabel(self, text="", text_color="gray")
        self.status.pack()
        
        self.all_programs = []
        self.refresh_list()

    def refresh_list(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()
        
        self.status.configure(text="Liste yükleniyor...")
        self.update()
        
        self.all_programs = self.manager.get_installed_programs()
        self.populate_list(self.all_programs)
        self.status.configure(text=f"{len(self.all_programs)} program bulundu.")

    def populate_list(self, programs):
        for widget in self.scroll.winfo_children():
            widget.destroy()
            
        for prog in programs:
            rb = ctk.CTkRadioButton(self.scroll, text=prog, variable=self.radio_var, value=prog)
            rb.pack(anchor="w", pady=2, padx=10)

    def filter_list(self, event=None):
        query = self.search_entry.get().lower()
        filtered = [p for p in self.all_programs if query in p.lower()]
        self.populate_list(filtered)

    def uninstall_selected(self):
        prog = self.radio_var.get()
        if not prog:
            messagebox.showwarning("Seçim Yok", "Lütfen kaldırılacak bir program seçin.")
            return
        
        if messagebox.askyesno("Onay", f"'{prog}' programını kaldırmak istediğinize emin misiniz?"):
            self.btn_uninstall.configure(state="disabled")
            
            # CMD ile Kaldırma
            def run_uninstall():
                try:
                    cmd = f'winget uninstall --name "{prog}"'
                    subprocess.run(f'start /wait cmd /c "{cmd} & pause"', shell=True)
                    self.update_status("İşlem tamamlandı.")
                except Exception as e:
                    self.update_status(f"Hata: {e}")
            
            threading.Thread(target=run_uninstall, daemon=True).start()

    def update_status(self, msg):
        self.status.configure(text=msg)
        self.btn_uninstall.configure(state="normal")
        if "tamamlandı" in msg:
            self.refresh_list()

# --- 6. SİSTEM BİLGİSİ SAYFASI ---
class SystemFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.sys = SystemInfo()
        
        head = ctk.CTkLabel(self, text="Sistem Raporu", font=("Inter", 26, "bold"))
        head.pack(anchor="w", pady=10)
        
        self.textbox = ctk.CTkTextbox(self, font=("Consolas", 14), corner_radius=10)
        self.textbox.pack(fill="both", expand=True, pady=10)
        
        self.btn_refresh = ctk.CTkButton(self, text="Bilgileri Yenile", command=self.refresh, height=40)
        self.btn_refresh.pack(fill="x")

    def refresh(self):
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", "Veriler toplanıyor...\n")
        self.after(100, self._get_data)
        
    def _get_data(self):
        report = self.sys.get_report()
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", report)

# --- 7. HAKKINDA SAYFASI ---
class AboutFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        
        container = ctk.CTkFrame(self, fg_color=("gray90", "gray20"), corner_radius=20)
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(container, text="Saydut Program Yöneticisi", font=("Inter", 30, "bold")).pack(padx=50, pady=(40, 10))
        ctk.CTkLabel(container, text=f"v{controller.current_version} Pro Edition", font=("Inter", 16)).pack(pady=5)
        ctk.CTkButton(container, text="Program Güncellemesini Kontrol Et", command=controller._check_self_update_manual, height=36).pack(pady=(18, 0))

        
        desc = ("Bu araç, sistem yönetimini kolaylaştırmak, programları güncellemek,\n"
                "gereksiz dosyaları temizlemek ve Windows ayarlarını optimize etmek\n"
                "için tasarlanmıştır.\n\n"
                "Geliştirici: Kemal Saydut\n"
                "Lisans: MIT Open Source")
        
        ctk.CTkLabel(container, text=desc, font=("Inter", 14), text_color="gray").pack(padx=50, pady=30)
        
        ctk.CTkButton(container, text="GitHub Sayfası", height=40).pack(pady=(0, 40))
