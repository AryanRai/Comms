# HyperThreader.py
import asyncio
import subprocess
import os
import psutil
import time
from tkinter import Tk, Button, Label, Frame, Text, Scrollbar, messagebox
from threading import Thread
import tracemalloc
import logging
import gc
import pystray
from PIL import Image
import io
import shutil
import queue
import socket

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class ProcessManager:
    def __init__(self):
        self.processes = {}
        self.root = Tk()
        self.root.title("Comms HyperThreader")
        self.root.geometry("800x600")
        
        tracemalloc.start()
        self.setup_ui()
        self.performance_history = {}
        self.tray_icon = None
        self.setup_tray()
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        
        self.output_queue = queue.Queue()

    def setup_ui(self):
        control_frame = Frame(self.root)
        control_frame.pack(pady=10, fill="x")
        
        sh_frame = Frame(control_frame)
        sh_frame.pack(pady=5)
        Label(sh_frame, text="Stream Handler").pack()
        Button(sh_frame, text="Start SH", command=self.start_sh).pack(side="left")
        Button(sh_frame, text="Stop SH", command=self.stop_sh).pack(side="left")
        Button(sh_frame, text="Debug SH", command=self.debug_sh).pack(side="left")
        self.sh_status = Label(sh_frame, text="Not Running")
        self.sh_status.pack()
        
        en_frame = Frame(control_frame)
        en_frame.pack(pady=5)
        Label(en_frame, text="Engine").pack()
        Button(en_frame, text="Start EN", command=self.start_en).pack(side="left")
        Button(en_frame, text="Stop EN", command=self.stop_en).pack(side="left")
        Button(en_frame, text="Debug EN", command=self.debug_en).pack(side="left")
        self.en_status = Label(en_frame, text="Not Running")
        self.en_status.pack()
        
        ui_frame = Frame(control_frame)
        ui_frame.pack(pady=5)
        Label(ui_frame, text="Aries UI").pack()
        Button(ui_frame, text="Start UI", command=self.start_ui).pack(side="left")
        Button(ui_frame, text="Stop UI", command=self.stop_ui).pack(side="left")
        Button(ui_frame, text="Build UI", command=self.build_ui).pack(side="left")  # New Build UI button
        self.ui_status = Label(ui_frame, text="Not Running")
        self.ui_status.pack()
        
        Button(control_frame, text="Minimize to Tray", command=self.minimize_to_tray).pack(pady=5)
        
        display_frame = Frame(self.root)
        display_frame.pack(pady=10, fill="both", expand=True)
        
        perf_frame = Frame(display_frame)
        perf_frame.pack(side="left", fill="both", expand=True)
        Label(perf_frame, text="Performance Metrics").pack()
        self.perf_text = Text(perf_frame, height=20, width=40)
        perf_scrollbar = Scrollbar(perf_frame, command=self.perf_text.yview)
        self.perf_text.configure(yscrollcommand=perf_scrollbar.set)
        self.perf_text.pack(side="left", fill="both", expand=True)
        perf_scrollbar.pack(side="right", fill="y")
        
        output_frame = Frame(display_frame)
        output_frame.pack(side="right", fill="both", expand=True)
        Label(output_frame, text="Terminal Output").pack()
        self.output_text = Text(output_frame, height=20, width=40)
        output_scrollbar = Scrollbar(output_frame, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=output_scrollbar.set)
        self.output_text.pack(side="left", fill="both", expand=True)
        output_scrollbar.pack(side="right", fill="y")

    def setup_tray(self):
        image = Image.new('RGB', (64, 64), (255, 0, 0))
        icon = pystray.Icon(
            "ProcessManager",
            image,
            menu=pystray.Menu(
                pystray.MenuItem("Restore", self.restore_from_tray),
                pystray.MenuItem("Quit", self.on_closing)
            )
        )
        self.tray_icon = icon

    def minimize_to_tray(self):
        self.root.withdraw()
        Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_from_tray(self):
        self.tray_icon.stop()
        self.root.deiconify()

    def get_detailed_metrics(self, process, name):
        try:
            p = psutil.Process(process.pid)
            with p.oneshot():
                memory_info = p.memory_full_info()
                metrics = {
                    'pid': p.pid,
                    'cpu_percent': p.cpu_percent(interval=0.1),
                    'memory_rss': memory_info.rss / 1024 / 1024,
                }
                self.performance_history.setdefault(name, []).append(metrics)
                if len(self.performance_history[name]) > 100:
                    self.performance_history[name].pop(0)
                return metrics
        except:
            return None

    def format_metrics(self, name, metrics):
        return f"{name}: ..."  # Placeholder

    def read_output(self, pipe, name):
        while True:
            line = pipe.readline()
            if not line:
                break
            self.output_queue.put(f"{name}: {line.strip()}")

    def update_output(self):
        while not self.output_queue.empty():
            line = self.output_queue.get()
            self.output_text.insert("end", line + "\n")
            self.output_text.see("end")
        self.root.after(100, self.update_output)

    def start_process(self, name, command, cwd=None):
        if name not in self.processes or self.processes[name].poll() is not None:
            try:
                if command[0] == "npm":
                    npm_path = shutil.which("npm")
                    if not npm_path:
                        raise FileNotFoundError("npm not found in PATH. Please install Node.js.")
                    command[0] = npm_path
                
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                self.processes[name] = process
                
                Thread(target=self.read_output, args=(process.stdout, name), daemon=True).start()
                Thread(target=self.read_output, args=(process.stderr, name), daemon=True).start()
                
                logging.info(f"Started {name}")
                return True
            except FileNotFoundError as e:
                messagebox.showerror("Error", f"Failed to start {name}: {str(e)}")
                logging.error(f"Failed to start {name}: {str(e)}")
                return False
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error starting {name}: {str(e)}")
                logging.error(f"Unexpected error starting {name}: {str(e)}")
                return False
        return False

    def kill_process_tree(self, pid):
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                child.kill()
            parent.kill()
        except psutil.NoSuchProcess:
            pass
        except Exception as e:
            logging.error(f"Error killing process tree for PID {pid}: {str(e)}")

    def cleanup_process(self, name, force=False):
        if name in self.processes:
            process = self.processes[name]
            try:
                if process.poll() is None:
                    if force:
                        self.kill_process_tree(process.pid)
                    else:
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill()
                
                if process.stdout:
                    process.stdout.close()
                if process.stderr:
                    process.stderr.close()
                process.stdin = None
                
                del self.processes[name]
                if name in self.performance_history:
                    del self.performance_history[name]
                
                gc.collect()
                logging.info(f"Cleaned up resources for {name}")
                return True
            except Exception as e:
                logging.error(f"Error cleaning up {name}: {str(e)}")
                return False
        return False

    def stop_process(self, name, force=False):
        return self.cleanup_process(name, force=force)

    def send_debug_signal(self, host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall("debug".encode())
            logging.info(f"Sent debug signal to {host}:{port}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch debug: {str(e)}")

    def debug_sh(self):
        if "sh" in self.processes and self.processes["sh"].poll() is None:
            self.send_debug_signal("localhost", 5001)
        else:
            messagebox.showwarning("Warning", "Stream Handler is not running")

    def debug_en(self):
        if "en" in self.processes and self.processes["en"].poll() is None:
            self.send_debug_signal("localhost", 5002)
        else:
            messagebox.showwarning("Warning", "Engine is not running")

    def start_sh(self):
        if self.start_process("sh", ["python", "sh/sh.py"]):
            self.sh_status.config(text="Running")

    def stop_sh(self):
        if self.stop_process("sh"):
            self.sh_status.config(text="Not Running")

    def start_en(self):
        current_path = os.getcwd()
        en_path = os.path.join(current_path, "en")
        if self.start_process("en", ["python", "en.py"], cwd=en_path):
            self.en_status.config(text="Running")

    def stop_en(self):
        if self.stop_process("en"):
            self.en_status.config(text="Not Running")

    def start_ui(self):
        current_path = os.getcwd()
        ui_path = os.path.join(current_path, "ui", "ariesUI")
        if not os.path.exists(ui_path):
            messagebox.showerror("Error", f"UI directory not found: {ui_path}")
            return
        if self.start_process("ui", ["npm", "run", "start"], cwd=ui_path):
            self.ui_status.config(text="Running")

    def stop_ui(self):
        if self.stop_process("ui", force=True):
            self.ui_status.config(text="Not Running")

    def build_ui(self):
        current_path = os.getcwd()
        ui_path = os.path.join(current_path, "ui", "ariesUI")
        if not os.path.exists(ui_path):
            messagebox.showerror("Error", f"UI directory not found: {ui_path}")
            return
        # Use a different name for build process to avoid conflict with "ui" (start/stop)
        if self.start_process("ui_build", ["npm", "run", "build"], cwd=ui_path):
            self.ui_status.config(text="Building...")
            # Monitor the build process and reset status when done
            def check_build():
                process = self.processes.get("ui_build")
                if process and process.poll() is not None:  # Process has finished
                    self.cleanup_process("ui_build", force=True)
                    self.ui_status.config(text="Not Running")
                else:
                    self.root.after(1000, check_build)
            self.root.after(1000, check_build)

    async def monitor_performance(self):
        while True:
            self.perf_text.delete(1.0, "end")
            for name, process in list(self.processes.items()):
                metrics = self.get_detailed_metrics(process, name)
                self.perf_text.insert("end", self.format_metrics(name, metrics))
                self.perf_text.insert("end", "-" * 50 + "\n")
            await asyncio.sleep(1)

    def run_monitor(self):
        asyncio.run(self.monitor_performance())

    def on_closing(self):
        for name in list(self.processes.keys()):
            self.cleanup_process(name, force=True)
        if self.tray_icon:
            self.tray_icon.stop()
        tracemalloc.stop()
        self.root.destroy()

    def start(self):
        monitor_thread = Thread(target=self.run_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        self.update_output()
        
        self.root.mainloop()

    def __del__(self):
        for name in list(self.processes.keys()):
            self.cleanup_process(name, force=True)
        if self.tray_icon:
            self.tray_icon.stop()
        tracemalloc.stop()

if __name__ == "__main__":
    manager = ProcessManager()
    manager.start()