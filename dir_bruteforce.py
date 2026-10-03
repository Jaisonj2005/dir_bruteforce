import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import threading
import time

# Global flag to stop the scan gracefully
is_scanning = False

def load_wordlist():
    filepath = filedialog.askopenfilename(title="Select Wordlist (.txt)", filetypes=[("Text Files", "*.txt")])
    if filepath:
        entry_wordlist.delete(0, tk.END)
        entry_wordlist.insert(0, filepath)

def start_scan():
    global is_scanning
    target_url = entry_target.get().strip()
    wordlist_path = entry_wordlist.get().strip()
    
    if not target_url.startswith("http"):
        target_url = "http://" + target_url
        
    if not target_url:
        messagebox.showerror("Input Error", "Please enter a target URL.")
        return

    is_scanning = True
    btn_start.config(state=tk.DISABLED)
    btn_stop.config(state=tk.NORMAL)
    text_log.config(state=tk.NORMAL)
    text_log.delete(1.0, tk.END)
    text_log.insert(tk.END, f"[*] Initializing Directory Brute-Forcer target: {target_url}\n")
    text_log.insert(tk.END, "-" * 55 + "\n")
    text_log.config(state=tk.DISABLED)
    lbl_status.config(text="Scanning...", fg="#e67e22")
    
    threading.Thread(target=execute_scan, args=(target_url, wordlist_path), daemon=True).start()

def execute_scan(base_url, wordlist_path):
    global is_scanning
    
    # Use a small default list if no file is provided
    directories = ["admin", "login", "dashboard", "uploads", "api", "backup", "test", "dev", ".git", "robots.txt", "config"]
    
    if wordlist_path:
        try:
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                directories = [line.strip() for line in f if line.strip()]
        except Exception as e:
            insert_log(f"[!] Error reading wordlist: {e}")
            reset_ui()
            return

    # Ensure URL ends with a slash
    if not base_url.endswith('/'):
        base_url += '/'

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) SOC-Toolkit-Scan'}
    found_count = 0

    for directory in directories:
        if not is_scanning:
            insert_log("\n[!] Scan aborted by user.")
            break
            
        target = base_url + directory
        try:
            # We don't need the body, just the headers to check status, so stream=True is faster
            response = requests.get(target, headers=headers, timeout=3, allow_redirects=False)
            status = response.status_code
            
            # Filter out 404s (Not Found). Keep 200 (OK), 301/302 (Redirects), 401/403 (Forbidden/Auth)
            if status != 404:
                found_count += 1
                color_tag = "success" if status == 200 else "warning"
                msg = f"[+] {status} - /{directory:<15} --> {target}\n"
                insert_log(msg, tag=color_tag)
                
            # Update GUI progress
            lbl_status.after(0, lambda d=directory: lbl_status.config(text=f"Testing: /{d}"))
            
        except requests.exceptions.RequestException:
            # Ignore timeouts and connection errors on individual guesses to keep the scan moving
            pass
            
        time.sleep(0.05) # Tiny delay to prevent crashing local routers or dev servers

    insert_log("-" * 55 + f"\n[*] Scan Complete. Found {found_count} interesting directories.\n")
    root.after(0, reset_ui)

def insert_log(message, tag=None):
    text_log.config(state=tk.NORMAL)
    text_log.insert(tk.END, message, tag)
    text_log.see(tk.END)
    text_log.config(state=tk.DISABLED)

def stop_scan():
    global is_scanning
    is_scanning = False
    lbl_status.config(text="Stopping...", fg="#c0392b")

def reset_ui():
    btn_start.config(state=tk.NORMAL)
    btn_stop.config(state=tk.DISABLED)
    lbl_status.config(text="Ready", fg="#7f8c8d")

# --- Tkinter GUI Layout ---
root = tk.Tk()
root.title("SOC Toolkit - Web Directory Brute-Forcer")
root.geometry("650x500")
root.resizable(False, False)

frame = ttk.Frame(root, padding="15")
frame.pack(fill=tk.BOTH, expand=True)

lbl_title = tk.Label(frame, text="Web Directory Enumerator", font=("Helvetica", 13, "bold"))
lbl_title.pack(anchor="w", pady=(0, 15))

# Target Configuration
config_frame = tk.Frame(frame)
config_frame.pack(fill=tk.X, pady=(0, 15))

tk.Label(config_frame, text="Target URL:", font=("Helvetica", 9, "bold")).grid(row=0, column=0, sticky="w", pady=5)
entry_target = ttk.Entry(config_frame, width=40, font=("Consolas", 10))
entry_target.grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky="w")
entry_target.insert(0, "http://127.0.0.1")

tk.Label(config_frame, text="Wordlist:", font=("Helvetica", 9, "bold")).grid(row=1, column=0, sticky="w", pady=5)
entry_wordlist = ttk.Entry(config_frame, width=28, font=("Consolas", 9))
entry_wordlist.grid(row=1, column=1, padx=(10, 5), pady=5, sticky="w")

btn_browse = tk.Button(config_frame, text="Browse...", command=load_wordlist, font=("Helvetica", 8))
btn_browse.grid(row=1, column=2, sticky="w")
tk.Label(config_frame, text="(Leave blank for default quick-list)", font=("Helvetica", 8, "italic"), fg="#7f8c8d").grid(row=2, column=1, sticky="w", padx=10)

# Controls
control_frame = tk.Frame(frame)
control_frame.pack(fill=tk.X, pady=(10, 10))

btn_start = tk.Button(control_frame, text="Start Scan", command=start_scan, bg="#2980b9", fg="white", font=("Helvetica", 9, "bold"), width=15)
btn_start.pack(side=tk.LEFT, padx=(0, 10))

btn_stop = tk.Button(control_frame, text="Stop", command=stop_scan, bg="#c0392b", fg="white", font=("Helvetica", 9, "bold"), width=10, state=tk.DISABLED)
btn_stop.pack(side=tk.LEFT)

lbl_status = tk.Label(control_frame, text="Ready", font=("Consolas", 9), fg="#e67e22")
lbl_status.pack(side=tk.RIGHT, padx=(0, 5))

# Output Console
text_frame = tk.Frame(frame)
text_frame.pack(fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_log = tk.Text(text_frame, font=("Consolas", 10), bg="#1e1e1e", fg="#ecf0f1", yscrollcommand=scrollbar.set)
text_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
text_log.tag_config("success", foreground="#2ecc71") # Green for 200 OK
text_log.tag_config("warning", foreground="#f1c40f") # Yellow for 301/403
text_log.config(state=tk.DISABLED)

scrollbar.config(command=text_log.yview)

root.mainloop()