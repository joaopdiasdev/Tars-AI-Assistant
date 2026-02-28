import customtkinter as ctk
import threading
import time
from pynput import keyboard 
from tars_utils import gravar_audio, transcrever_audio, processar_interacao_completa, falar

# --- VISUAL CONFIGURATION ---
ctk.set_appearance_mode("dark")

class TarsEliteGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Settings
        self.title("TARS - Personal Assistant")
        self.geometry("1100x800")
        self.configure(fg_color="#050505") 

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#0D0D0D", border_width=1, border_color="#1A1A1A")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.lbl_logo = ctk.CTkLabel(self.sidebar, text="TARS", font=("Consolas", 48, "bold"), text_color="#1E90FF")
        self.lbl_logo.pack(pady=(60, 10))
        
        self.lbl_sub = ctk.CTkLabel(self.sidebar, text="PERSONAL ASSISTANT", font=("Consolas", 11), text_color="#444")
        self.lbl_sub.pack()

        # Status Indicator
        self.status_box = ctk.CTkFrame(self.sidebar, fg_color="#151515", corner_radius=12, border_width=1, border_color="#222")
        self.status_box.pack(padx=25, pady=50, fill="x")
        
        self.dot = ctk.CTkLabel(self.status_box, text="●", text_color="#32CD32", font=("Arial", 18))
        self.dot.pack(side="left", padx=(15, 5), pady=12)
        
        self.status_text = ctk.CTkLabel(self.status_box, text="READY", font=("Consolas", 14, "bold"), text_color="#E0E0E0")
        self.status_text.pack(side="left", pady=12)

        # Hotkey Info
        self.info_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.info_frame.pack(pady=20, padx=25, fill="x")
        self.lbl_info = ctk.CTkLabel(self.info_frame, text="HOTKEY: Ctrl + Space", font=("Consolas", 12), text_color="#1E90FF")
        self.lbl_info.pack()

        self.btn_clear = ctk.CTkButton(self.sidebar, text="CLEAR HISTORY", fg_color="transparent", 
                                       border_width=1, border_color="#333", text_color="#666",
                                       hover_color="#1A1A1A", font=("Consolas", 12), command=self.clear_chat)
        self.btn_clear.pack(side="bottom", pady=40, padx=25, fill="x")

        # --- MAIN AREA ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Chat Log (No word-breaking)
        self.log_area = ctk.CTkTextbox(self.main_frame, font=("Consolas", 18), 
                                       fg_color="#0A0A0A", border_width=1, border_color="#222",
                                       text_color="#F0F0F0", wrap="word")
        self.log_area.grid(row=0, column=0, sticky="nsew")
        self.log_area.configure(state="disabled") 
        
        # COLOR TAGS - PRESERVED
        self.log_area.tag_config("user_tag", foreground="#00CED1") # Cyan for YOU
        self.log_area.tag_config("tars_tag", foreground="#1E90FF") # Blue for TARS
        self.log_area.tag_config("content", foreground="#FFFFFF")  
        self.log_area.tag_config("sys", foreground="#444444")      

        # Action Button
        self.btn_speak = ctk.CTkButton(self.main_frame, text="LISTEN", font=("Consolas", 24, "bold"),
                                       height=80, fg_color="#1E90FF", text_color="#000",
                                       hover_color="#00BFFF", corner_radius=20, 
                                       border_width=2, border_color="#0055AA",
                                       command=self.start_thread)
        self.btn_speak.grid(row=1, column=0, pady=(30, 0), sticky="ew")

        self.iniciar_atalho_global()
        self.append_log("System", "TARS Online. Using Ctrl+Space shortcut.", "sys")

    def append_log(self, sender, message, mode="tars"):
        self.log_area.configure(state="normal")
        if mode == "user":
            self.log_area.insert("end", f"\nYOU: ", "user_tag")
            self.log_area.insert("end", f"{message}\n", "content")
        elif mode == "sys":
            self.log_area.insert("end", f"\nSYSTEM: {message}\n", "sys")
        else:
            self.log_area.insert("end", f"\nTARS: ", "tars_tag")
            self.log_area.insert("end", f"{message}\n", "content")
        self.log_area.see("end")
        self.log_area.configure(state="disabled")

    def clear_chat(self):
        self.log_area.configure(state="normal")
        self.log_area.delete("1.0", "end")
        self.log_area.configure(state="disabled")
        self.append_log("System", "History cleared.", "sys")

    def update_ui_status(self, text, color, btn_text=None):
        self.status_text.configure(text=text)
        self.dot.configure(text_color=color)
        if btn_text:
            self.btn_speak.configure(text=btn_text)

    def start_thread(self):
        if self.btn_speak.cget("state") == "disabled":
            return
        self.btn_speak.configure(state="disabled")
        threading.Thread(target=self.run_logic, daemon=True).start()

    def run_logic(self):
        try:
            # Step 1: Calibration & Listening
            self.update_ui_status("ACTIVE", "#FFFF00", "LISTENING...")
            audio = gravar_audio()
            
            # Step 2: Speech-to-Text
            self.update_ui_status("ANALYZING", "#FF4500", "ANALYZING...")
            query = transcrever_audio(audio)
            
            if query:
                self.append_log("YOU", query, "user")
                
                # Step 3: AI Processing
                self.update_ui_status("THINKING", "#1E90FF", "THINKING...")
                response = processar_interacao_completa(query)
                self.append_log("TARS", response, "tars")
                
                # Step 4: Voice Response
                self.update_ui_status("SPEAKING", "#8A2BE2", "SPEAKING...")
                falar(response)
            else:
                self.append_log("System", "No clear audio signal.", "sys")
        except Exception as e:
            self.append_log("System", f"Error: {e}", "sys")
        finally:
            self.update_ui_status("READY", "#32CD32", "LISTEN")
            self.btn_speak.configure(state="normal")

    def iniciar_atalho_global(self):
        def on_activate():
            self.after(0, self.deiconify)
            self.after(0, self.focus_force)
            self.after(0, self.start_thread)

        def listener_thread():
            with keyboard.GlobalHotKeys({'<ctrl>+<space>': on_activate}) as h:
                h.join()

        threading.Thread(target=listener_thread, daemon=True).start()

if __name__ == "__main__":
    app = TarsEliteGUI()
    app.mainloop()
