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
import json
import tkinter as tk

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
        button_frame = Frame(sh_frame)
        button_frame.pack()
        Button(button_frame, text="Start SH", command=self.start_sh).pack(side="left", padx=2)
        Button(button_frame, text="Stop SH", command=self.stop_sh).pack(side="left", padx=2)
        Button(button_frame, text="Debug SH", command=self.debug_sh).pack(side="left", padx=2)
        Button(button_frame, text="Configure SH", command=self.configure_sh).pack(side="left", padx=2)
        self.sh_status = Label(sh_frame, text="Not Running")
        self.sh_status.pack()
        
        en_frame = Frame(control_frame)
        en_frame.pack(pady=5)
        Label(en_frame, text="Engine").pack()
        button_frame = Frame(en_frame)
        button_frame.pack()
        Button(button_frame, text="Start EN", command=self.start_en).pack(side="left", padx=2)
        Button(button_frame, text="Stop EN", command=self.stop_en).pack(side="left", padx=2)
        Button(button_frame, text="Debug EN", command=self.debug_en).pack(side="left", padx=2)
        Button(button_frame, text="Configure EN", command=self.configure_en).pack(side="left", padx=2)
        self.en_status = Label(en_frame, text="Not Running")
        self.en_status.pack()
        
        ui_frame = Frame(control_frame)
        ui_frame.pack(pady=5)
        Label(ui_frame, text="Aries UI").pack()
        button_frame = Frame(ui_frame)
        button_frame.pack()
        Button(button_frame, text="Start UI", command=self.start_ui).pack(side="left", padx=2)
        Button(button_frame, text="Stop UI", command=self.stop_ui).pack(side="left", padx=2)
        Button(button_frame, text="Build UI", command=self.build_ui).pack(side="left", padx=2)
        self.ui_status = Label(ui_frame, text="Not Running")
        self.ui_status.pack()
        
        # Add control buttons for terminal output
        terminal_control_frame = Frame(control_frame)
        terminal_control_frame.pack(pady=5)
        Label(terminal_control_frame, text="Terminal Controls").pack()
        button_frame = Frame(terminal_control_frame)
        button_frame.pack()
        self.terminal_paused = False
        Button(button_frame, text="Clear Terminal", command=self.clear_terminal).pack(side="left", padx=2)
        self.pause_button = Button(button_frame, text="Pause Terminal", command=self.toggle_terminal_pause)
        self.pause_button.pack(side="left", padx=2)
        
        # Add Update Rates Configuration button
        Button(button_frame, text="Configure Update Rates", command=self.configure_update_rates).pack(side="left", padx=2)
        
        # System controls at the bottom
        system_frame = Frame(control_frame)
        system_frame.pack(pady=5)
        Label(system_frame, text="System Controls").pack()
        button_frame = Frame(system_frame)
        button_frame.pack()
        Button(button_frame, text="Minimize to Tray", command=self.minimize_to_tray).pack(side="left", padx=2)
        Button(button_frame, text="Safely Quit", command=self.safely_quit).pack(side="left", padx=2)
        
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
        if not metrics:
            return f"{name}: No metrics available\n"
            
        result = f"=== {name} ===\n"
        result += f"PID: {metrics['pid']}\n"
        result += f"CPU: {metrics['cpu_percent']:.1f}%\n"
        result += f"Memory: {metrics['memory_rss']:.1f} MB\n"
        
        # Add visual bar for CPU usage
        cpu_bar = "█" * int(metrics['cpu_percent'] / 5)  # Each block represents 5%
        result += f"CPU Usage: [{cpu_bar:<20}] {metrics['cpu_percent']:.1f}%\n"
        
        # Add visual bar for memory usage (assuming 1GB scale)
        mem_percent = min(100, (metrics['memory_rss'] / 1024) * 100)  # Scale to 1GB max
        mem_bar = "█" * int(mem_percent / 5)  # Each block represents 5%
        result += f"Memory Usage: [{mem_bar:<20}] {metrics['memory_rss']:.1f}MB\n"
        
        result += "-" * 40 + "\n"
        return result

    def read_output(self, pipe, name):
        while True:
            line = pipe.readline()
            if not line:
                break
            self.output_queue.put(f"{name}: {line.strip()}")

    def update_output(self):
        if not self.terminal_paused:
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
            await asyncio.sleep(0.1)

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
    

    # New safely_quit method:
    def safely_quit(self):
        """Gracefully stop all processes and close the application."""
        logging.info("Initiating safe quit...")
        
        process_names = ["sh", "en", "ui"]
        
        for name in process_names:
            if name in self.processes and self.processes[name].poll() is None:
                logging.info(f"Stopping {name}...")
                if not self.stop_process(name):
                    logging.error(f"Failed to stop {name}")
                    messagebox.showerror("Error", f"Failed to stop {name}")
                    return
        
        for name in process_names:
            if name in self.processes and self.processes[name].poll() is None:
                try:
                    self.processes[name].wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logging.warning(f"Process {name} did not terminate in time. Forcing stop.")
                    self.cleanup_process(name, force=True)
        
        self.on_closing()

    def clear_terminal(self):
        self.output_text.delete(1.0, "end")
        
    def toggle_terminal_pause(self):
        self.terminal_paused = not self.terminal_paused
        self.pause_button.config(text="Resume Terminal" if self.terminal_paused else "Pause Terminal")
        
    def configure_sh(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("localhost", 5001))
                s.sendall("config".encode())
                s.close()  # Explicitly close the socket
            logging.info("Sent config signal to Stream Handler")
        except ConnectionRefusedError:
            messagebox.showerror("Error", "Stream Handler is not running")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open SH config: {str(e)}")
            
    def configure_en(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("localhost", 5002))
                s.sendall("config".encode())
            logging.info("Sent config signal to Engine")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open EN config: {str(e)}")

    def configure_update_rates(self):
        config_root = tk.Toplevel(self.root)
        config_root.title("Update Rates Configuration")
        config_root.geometry("500x800")

        # Add scrollable frame
        canvas = tk.Canvas(config_root)
        scrollbar = tk.Scrollbar(config_root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Get current configuration from Engine
        current_config = {}
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("localhost", 5002))
                s.sendall("get_config".encode())
                response = s.recv(4096).decode()
                current_config = json.loads(response)
        except Exception as e:
            messagebox.showwarning("Warning", "Could not fetch current configuration. Is Engine running?")
            current_config = {
                "engine_rate": 0.1,
                "negotiator_rate": 0.1,
                "debug_level": 0,
                "module_rates": {},
                "module_configs": {}
            }

        # System Update Rates
        tk.Label(scrollable_frame, text="HyperThreader Display Update Rates", font=("TkDefaultFont", 12, "bold")).pack(pady=10)
        
        # Performance Monitor Rate
        tk.Label(scrollable_frame, text="Performance Monitor Rate (ms):").pack(pady=5)
        perf_rate = tk.Entry(scrollable_frame)
        perf_rate.insert(0, "100")  # HyperThreader's internal rate
        perf_rate.pack()

        # Terminal Output Rate
        tk.Label(scrollable_frame, text="Terminal Output Rate (ms):").pack(pady=5)
        term_rate = tk.Entry(scrollable_frame)
        term_rate.insert(0, "100")  # HyperThreader's internal rate
        term_rate.pack()

        # Engine Configuration
        tk.Label(scrollable_frame, text="Engine Configuration", font=("TkDefaultFont", 12, "bold")).pack(pady=10)
        
        # Debug Level
        tk.Label(scrollable_frame, text="Debug Level (0-2):").pack(pady=5)
        debug_level = tk.Entry(scrollable_frame)
        debug_level.insert(0, str(current_config.get("debug_level", 0)))
        debug_level.pack()
        
        # Engine Update Rate
        tk.Label(scrollable_frame, text="Engine Update Rate (ms):").pack(pady=5)
        engine_rate = tk.Entry(scrollable_frame)
        engine_rate.insert(0, str(current_config.get("engine_rate", 0.1) * 1000))
        engine_rate.pack()

        # Negotiator Rate
        tk.Label(scrollable_frame, text="Negotiator Update Rate (ms):").pack(pady=5)
        negotiator_rate = tk.Entry(scrollable_frame)
        negotiator_rate.insert(0, str(current_config.get("negotiator_rate", 0.1) * 1000))
        negotiator_rate.pack()

        # Dynamic Modules Configuration
        tk.Label(scrollable_frame, text="Dynamic Modules Configuration", font=("TkDefaultFont", 12, "bold")).pack(pady=10)

        module_rates = {}
        module_configs = {}
        
        def update_module_rates():
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(("localhost", 5002))
                    s.sendall("get_modules".encode())
                    response = s.recv(4096).decode()
                    modules = json.loads(response)
                    
                    for module_id in modules:
                        if module_id not in module_rates:
                            # Module frame
                            module_frame = tk.Frame(scrollable_frame)
                            module_frame.pack(pady=10, fill="x", padx=10)
                            
                            tk.Label(module_frame, text=f"{module_id} Configuration", font=("TkDefaultFont", 10, "bold")).pack()
                            
                            # Update Rate
                            rate_frame = tk.Frame(module_frame)
                            rate_frame.pack(fill="x")
                            tk.Label(rate_frame, text="Update Rate (ms):").pack(side="left")
                            rate_entry = tk.Entry(rate_frame, width=10)
                            current_rate = current_config.get("module_rates", {}).get(module_id, 0.1)
                            rate_entry.insert(0, str(current_rate * 1000))
                            rate_entry.pack(side="left", padx=5)
                            module_rates[module_id] = rate_entry
                            
                            # Additional module configs
                            if module_id in current_config.get("module_configs", {}):
                                config_entries = {}
                                for key, value in current_config["module_configs"][module_id].items():
                                    if isinstance(value, (int, float, str, bool)):
                                        config_frame = tk.Frame(module_frame)
                                        config_frame.pack(fill="x")
                                        tk.Label(config_frame, text=f"{key}:").pack(side="left")
                                        entry = tk.Entry(config_frame, width=20)
                                        entry.insert(0, str(value))
                                        entry.pack(side="left", padx=5)
                                        config_entries[key] = entry
                                module_configs[module_id] = config_entries
            except Exception as e:
                messagebox.showwarning("Warning", "Could not fetch module list. Is Engine running?")

        update_module_rates()

        def apply_config():
            try:
                # Validate all inputs are positive numbers
                rates = {
                    "perf_monitor_rate": float(perf_rate.get()) / 1000,
                    "terminal_rate": float(term_rate.get()),
                    "engine_rate": float(engine_rate.get()) / 1000,
                    "negotiator_rate": float(negotiator_rate.get()) / 1000,
                    "debug_level": int(debug_level.get())
                }
                
                # Validate debug level
                if not (0 <= rates["debug_level"] <= 2):
                    raise ValueError("Debug level must be between 0 and 2")
                
                # Validate rates
                for name, value in rates.items():
                    if value <= 0:
                        raise ValueError(f"{name} must be positive")

                # Apply system rates
                self.perf_monitor_rate = rates["perf_monitor_rate"]
                self.terminal_rate = rates["terminal_rate"]

                # Collect module rates and configs
                module_rate_values = {}
                module_config_values = {}
                
                for module_id, entry in module_rates.items():
                    rate = float(entry.get()) / 1000
                    if rate <= 0:
                        raise ValueError(f"Module {module_id} rate must be positive")
                    module_rate_values[module_id] = rate
                    
                    if module_id in module_configs:
                        config_dict = {}
                        for key, entry in module_configs[module_id].items():
                            value = entry.get()
                            # Try to convert to appropriate type
                            try:
                                if value.lower() in ('true', 'false'):
                                    value = value.lower() == 'true'
                                elif '.' in value:
                                    value = float(value)
                                else:
                                    value = int(value)
                            except:
                                pass  # Keep as string if conversion fails
                            config_dict[key] = value
                        module_config_values[module_id] = config_dict

                # Send configuration to Engine
                engine_config = {
                    "engine_rate": rates["engine_rate"],
                    "negotiator_rate": rates["negotiator_rate"],
                    "debug_level": rates["debug_level"],
                    "module_rates": module_rate_values,
                    "module_configs": module_config_values
                }
                
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(("localhost", 5002))
                    s.sendall(f"update_rates:{json.dumps(engine_config)}".encode())
                    response = s.recv(1024).decode()
                    if response != "success":
                        raise Exception(response)

                messagebox.showinfo("Success", "Update rates configured successfully")
                config_root.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to apply configuration: {str(e)}")

        # Add Apply button
        tk.Button(scrollable_frame, text="Apply Configuration", command=apply_config).pack(pady=20)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

if __name__ == "__main__":
    manager = ProcessManager()
    manager.start()