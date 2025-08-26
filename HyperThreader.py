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

    def force_remove_directory(self, path):
        """Force remove directory with Windows file permission handling"""
        def handle_remove_readonly(func, path, exc):
            """Handle readonly files and directories"""
            if os.path.exists(path):
                # Make the file writable and try again
                os.chmod(path, 0o777)
                func(path)
        
        if not os.path.exists(path):
            return
        
        try:
            # First try normal removal
            shutil.rmtree(path)
            logging.info(f"Successfully removed directory: {path}")
        except (OSError, PermissionError) as e:
            logging.warning(f"Normal removal failed: {e}. Trying force removal...")
            try:
                # Try with error handler for readonly files
                shutil.rmtree(path, onerror=handle_remove_readonly)
                logging.info(f"Successfully removed directory with force: {path}")
            except (OSError, PermissionError) as e2:
                logging.warning(f"Force removal failed: {e2}. Trying Windows-specific removal...")
                try:
                    # Windows-specific: use cmd to remove
                    subprocess.run(f'rmdir /s /q "{path}"', shell=True, check=True)
                    logging.info(f"Successfully removed directory with rmdir: {path}")
                except subprocess.CalledProcessError:
                    # Kill processes that might be locking files
                    logging.warning("Trying to kill processes that might be locking files...")
                    self.kill_build_processes()
                    time.sleep(2)
                    
                    # Try one more time after killing processes
                    try:
                        subprocess.run(f'rmdir /s /q "{path}"', shell=True, check=True)
                        logging.info(f"Successfully removed directory after killing processes: {path}")
                    except subprocess.CalledProcessError:
                        # Last resort: rename and try again later
                        import uuid
                        temp_name = f"{path}_to_delete_{uuid.uuid4().hex[:8]}"
                        try:
                            os.rename(path, temp_name)
                            logging.warning(f"Renamed directory to {temp_name} for later cleanup")
                        except OSError:
                            logging.error(f"Could not remove directory {path}. Manual cleanup required.")
                            # Don't raise - just continue with build
    
    def kill_build_processes(self):
        """Kill processes that might be locking build files"""
        try:
            # Kill Visual Studio processes
            subprocess.run("taskkill /f /im devenv.exe", shell=True, capture_output=True)
            subprocess.run("taskkill /f /im MSBuild.exe", shell=True, capture_output=True)
            subprocess.run("taskkill /f /im cmake.exe", shell=True, capture_output=True)
            subprocess.run("taskkill /f /im git.exe", shell=True, capture_output=True)
            logging.info("Killed potential file-locking processes")
        except Exception as e:
            logging.warning(f"Could not kill processes: {e}")

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
        Button(button_frame, text="Web Only", command=self.start_ui_web_only).pack(side="left", padx=2)
        Button(button_frame, text="Stop UI", command=self.stop_ui).pack(side="left", padx=2)
        Button(button_frame, text="Install Deps", command=self.install_ui_dependencies).pack(side="left", padx=2)
        Button(button_frame, text="Build UI", command=self.build_ui).pack(side="left", padx=2)
        self.ui_status = Label(ui_frame, text="Not Running")
        self.ui_status.pack()
        
        # StarSim controls
        starsim_frame = Frame(control_frame)
        starsim_frame.pack(pady=5)
        Label(starsim_frame, text="StarSim Physics Engine").pack()
        button_frame = Frame(starsim_frame)
        button_frame.pack()
        Button(button_frame, text="Start StarSim", command=self.start_starsim).pack(side="left", padx=2)
        Button(button_frame, text="Stop StarSim", command=self.stop_starsim).pack(side="left", padx=2)
        Button(button_frame, text="Build StarSim", command=self.build_starsim).pack(side="left", padx=2)
        Button(button_frame, text="Manual Build", command=self.manual_build_starsim).pack(side="left", padx=2)
        Button(button_frame, text="Run Demo", command=self.run_starsim_demo).pack(side="left", padx=2)
        self.starsim_status = Label(starsim_frame, text="Not Running")
        self.starsim_status.pack()
        
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
                
                # Check if process started successfully
                time.sleep(0.5)  # Give it a moment to start
                if process.poll() is not None:
                    # Process already exited, check return code
                    if process.returncode != 0:
                        stderr_output = process.stderr.read()
                        logging.error(f"Process {name} failed to start: {stderr_output}")
                        return False
                
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
        """Start AriesUI in development mode with enhanced error handling"""
        if not os.path.exists("ui/ariesUI"):
            messagebox.showerror("Error", "AriesUI directory not found at ui/ariesUI")
            return
        
        # Check if npm is installed
        if not shutil.which("npm"):
            messagebox.showerror("Error", "npm not found. Please install Node.js and npm.")
            return
        
        # Check if dependencies are installed
        if not os.path.exists("ui/ariesUI/node_modules"):
            messagebox.showwarning("Warning", "Dependencies not installed. Installing npm packages...")
            self.install_ui_dependencies()
            return
        
        # Clean up any existing processes first
        self.cleanup_ui_processes()
        
        # Wait a moment for cleanup
        time.sleep(1)
        
        # Start electron-dev directly (like your manual execution)
        success = self.start_ui_electron_dev()
        
        if not success:
            # Fallback to web-only mode if electron-dev fails
            messagebox.showwarning("Warning", "Electron-dev failed. Starting web-only mode...")
            self.start_ui_web_only()
    
    def start_ui_electron_dev(self):
        """Start AriesUI with electron-dev (matches your manual execution)"""
        try:
            # Use shell=True and let Windows handle the npm command resolution
            # This matches exactly how PowerShell executes npm
            process = subprocess.Popen(
                "npm run electron-dev",
                cwd="ui/ariesUI",
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0,
                shell=True
            )
            
            self.processes["ui"] = process
            
            # Check if process started successfully
            time.sleep(2)
            if process.poll() is None:
                self.ui_status.config(text="Running (Electron-dev)")
                logging.info("Started AriesUI with electron-dev")
                messagebox.showinfo("AriesUI Started", 
                                  "AriesUI is starting with electron-dev.\\n\\n"
                                  "Check the new console window for output.\\n\\n"
                                  "The app should open automatically when ready.")
                return True
            else:
                # Process already exited
                logging.error(f"electron-dev process exited immediately with code {process.returncode}")
                return False
                
        except Exception as e:
            logging.error(f"Failed to start electron-dev: {e}")
            return False
    
    def install_ui_dependencies(self):
        """Install AriesUI dependencies"""
        if not os.path.exists("ui/ariesUI"):
            messagebox.showerror("Error", "AriesUI directory not found at ui/ariesUI")
            return
        
        def install_deps():
            try:
                # Install dependencies
                subprocess.run(["npm", "install"], cwd="ui/ariesUI", check=True)
                messagebox.showinfo("Success", "Dependencies installed successfully. You can now start the UI.")
                logging.info("AriesUI dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to install dependencies: {str(e)}")
                logging.error(f"Failed to install AriesUI dependencies: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {str(e)}")
                logging.error(f"Unexpected error installing dependencies: {str(e)}")
        
        # Run in separate thread to not block UI
        Thread(target=install_deps, daemon=True).start()
    
    def start_ui_web_only(self):
        """Start AriesUI in web-only mode (without Electron)"""
        success = self.start_process(
            "ui_web",
            ["npm", "run", "dev"],
            cwd="ui/ariesUI"
        )
        
        if success:
            self.ui_status.config(text="Running (Web)")
            logging.info("Started AriesUI in web-only mode")
            
            # Open browser after a delay
            def open_browser():
                time.sleep(3)
                import webbrowser
                webbrowser.open("http://localhost:3000")
            
            Thread(target=open_browser, daemon=True).start()
            
            messagebox.showinfo("AriesUI Started", 
                              "AriesUI is starting in web mode.\n\n"
                              "It will open in your browser at:\n"
                              "http://localhost:3000\n\n"
                              "Please wait a moment for the server to start.")
        else:
            messagebox.showerror("Error", "Failed to start AriesUI in web mode")
            logging.error("Failed to start AriesUI in web mode")
    
    def start_electron_client(self):
        """Start Electron client separately (connects to existing web server)"""
        try:
            # Check if web server is running
            import requests
            try:
                response = requests.get("http://localhost:3000", timeout=2)
                if response.status_code != 200:
                    messagebox.showerror("Error", "Web server is not running on port 3000")
                    return
            except requests.RequestException:
                messagebox.showerror("Error", "Web server is not responding on port 3000")
                return
            
            # Start Electron client
            success = self.start_process(
                "electron_client",
                ["npm", "run", "electron"],
                cwd="ui/ariesUI"
            )
            
            if success:
                logging.info("Started Electron client")
                messagebox.showinfo("Electron Started", "Electron desktop app is starting...")
            else:
                messagebox.showerror("Error", "Failed to start Electron client")
                
        except ImportError:
            messagebox.showwarning("Warning", "requests library not available. Starting Electron without web server check...")
            
            # Try to start Electron anyway
            success = self.start_process(
                "electron_client",
                ["npm", "run", "electron"],
                cwd="ui/ariesUI"
            )
            
            if success:
                logging.info("Started Electron client (without web server check)")
            else:
                messagebox.showerror("Error", "Failed to start Electron client")
    
    def cleanup_ui_processes(self):
        """Clean up any running UI processes and temp files"""
        try:
            # Stop any existing UI processes
            for proc_name in ["ui", "ui_web", "electron_client"]:
                if proc_name in self.processes:
                    self.stop_process(proc_name)
            
            # Kill any Node.js processes that might be holding the port
            try:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    if proc.info['name'] in ['node.exe', 'node'] and proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        if 'next dev' in cmdline or 'electron' in cmdline:
                            logging.info(f"Killing hanging Node.js process: {proc.info['pid']}")
                            proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logging.warning(f"Could not kill process: {e}")
            
            # Clean up .next directory if it exists and is causing issues
            next_dir = "ui/ariesUI/.next"
            if os.path.exists(next_dir):
                try:
                    shutil.rmtree(next_dir)
                    logging.info("Cleaned up .next directory")
                except (OSError, PermissionError) as e:
                    logging.warning(f"Could not clean .next directory: {e}")
            
            # Wait for processes to fully terminate
            time.sleep(2)
            
        except Exception as e:
            logging.error(f"Error during UI cleanup: {e}")
    
    def check_ui_status(self):
        """Check AriesUI status and dependencies"""
        status_info = []
        
        # Check if directory exists
        if os.path.exists("ui/ariesUI"):
            status_info.append("✅ AriesUI directory found")
        else:
            status_info.append("❌ AriesUI directory not found")
            
        # Check if npm is available
        if shutil.which("npm"):
            status_info.append("✅ npm is available")
        else:
            status_info.append("❌ npm not found")
            
        # Check if dependencies are installed
        if os.path.exists("ui/ariesUI/node_modules"):
            status_info.append("✅ Dependencies installed")
        else:
            status_info.append("❌ Dependencies not installed")
            
        # Check if electron is available
        if os.path.exists("ui/ariesUI/node_modules/electron"):
            status_info.append("✅ Electron available")
        else:
            status_info.append("❌ Electron not installed")
            
        # Check running processes
        ui_running = "ui" in self.processes and self.processes["ui"].poll() is None
        web_running = "ui_web" in self.processes and self.processes["ui_web"].poll() is None
        
        if ui_running:
            status_info.append("✅ UI process running (Electron)")
        elif web_running:
            status_info.append("✅ UI process running (Web)")
        else:
            status_info.append("❌ No UI process running")
            
        messagebox.showinfo("UI Status", "\n".join(status_info))

    def stop_ui(self):
        """Stop AriesUI with full cleanup"""
        stopped = False
        
        # Stop all UI-related processes
        ui_processes = ["ui", "ui_web", "electron_client"]
        for proc_name in ui_processes:
            if self.stop_process(proc_name, force=True):
                stopped = True
        
        # Perform cleanup
        self.cleanup_ui_processes()
        
        if stopped:
            self.ui_status.config(text="Not Running")
            logging.info("Stopped AriesUI and cleaned up processes")
        else:
            logging.warning("No AriesUI process found to stop")

    def build_ui(self):
        """Build AriesUI for production"""
        if not os.path.exists("ui/ariesUI"):
            messagebox.showerror("Error", "AriesUI directory not found at ui/ariesUI")
            return
        
        # Check if npm is installed
        if not shutil.which("npm"):
            messagebox.showerror("Error", "npm not found. Please install Node.js and npm.")
            return
        
        def check_build():
            try:
                # Run npm install first
                subprocess.run(["npm", "install"], cwd="ui/ariesUI", check=True)
                
                # Build the UI
                subprocess.run(["npm", "run", "build-electron"], cwd="ui/ariesUI", check=True)
                
                messagebox.showinfo("Success", "AriesUI built successfully. Check the dist folder.")
                logging.info("AriesUI build completed successfully")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Build failed: {str(e)}")
                logging.error(f"AriesUI build failed: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error during build: {str(e)}")
                logging.error(f"Unexpected error during AriesUI build: {str(e)}")
        
        # Run build in a separate thread to not block the UI
        Thread(target=check_build, daemon=True).start()

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
    
    def start_starsim(self):
        """Start StarSim physics engine - Simple approach"""
        if not os.path.exists("int/StarSim"):
            messagebox.showerror("Error", "StarSim directory not found at int/StarSim")
            return
        
        # Simple approach: just open a command prompt and run the demo
        try:
            # Create a simple run script
            run_script = """@echo off
echo ===============================================
echo StarSim Integration Demo
echo ===============================================
echo.
echo Starting StarSim-Comms integration demo...
echo.
echo Current directory: %CD%
echo.
cd int\\StarSim
echo Changed to StarSim directory: %CD%
echo.
echo Running integration demo...
python run_integration_demo.py
echo.
echo Demo finished. Press any key to close...
pause
"""
            
            with open("run_starsim_demo.bat", 'w') as f:
                f.write(run_script)
            
            # Run the demo script in a new console using start command
            os.system("start cmd /c run_starsim_demo.bat")
            
            self.starsim_status.config(text="Running")
            logging.info("Started StarSim integration demo")
            
            messagebox.showinfo("StarSim Started", 
                              "StarSim integration demo started in new console window.\n\n"
                              "The demo will start all components automatically.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start StarSim demo: {str(e)}")
            logging.error(f"StarSim demo failed: {str(e)}")
    
    def stop_starsim(self):
        """Stop StarSim physics engine"""
        if self.stop_process("starsim"):
            self.starsim_status.config(text="Not Running")
            logging.info("Stopped StarSim physics engine")
    
    def build_starsim(self):
        """Build StarSim - Simple direct approach"""
        if not os.path.exists("int/StarSim"):
            messagebox.showerror("Error", "StarSim directory not found at int/StarSim")
            return
        
        # Simple approach: just open a command prompt in the right directory
        try:
            # Create a simple build script
            build_script = """@echo off
echo ===============================================
echo StarSim Build Script
echo ===============================================
echo.
echo This will build ParsecCore for StarSim integration
echo.
echo Current directory: %CD%
echo.
echo Step 1: Navigate to ParsecCore directory
cd int\\StarSim\\ParsecCore
echo.
echo Step 2: Create build directory
if exist build rmdir /s /q build
mkdir build
cd build
echo.
echo Step 3: Configure with CMake
cmake .. -G "Visual Studio 17 2022"
if errorlevel 1 (
    echo.
    echo CMake configuration failed!
    echo Make sure you have Visual Studio 2022 and CMake installed
    pause
    exit /b 1
)
echo.
echo Step 4: Build the project
cmake --build .
if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)
echo.
echo ===============================================
echo BUILD SUCCESSFUL!
echo ===============================================
echo.
echo StarSim ParsecCore has been built successfully
echo You can now use HyperThreader to start StarSim
echo.
pause
"""
            
            with open("build_starsim_simple.bat", 'w') as f:
                f.write(build_script)
            
            # Run the build script in a new console using start command
            os.system("start cmd /c build_starsim_simple.bat")
            
            messagebox.showinfo("StarSim Build", 
                              "StarSim build script started in new console window.\n\n"
                              "Follow the prompts to build ParsecCore.\n\n"
                              "This approach is simpler and more reliable.")
            
            logging.info("Started StarSim build script")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start build script: {str(e)}")
            logging.error(f"Build script failed: {str(e)}")
    
    def manual_build_starsim(self):
        """Open command prompt for manual StarSim build"""
        build_dir = "int/StarSim/ParsecCore/build"
        
        # Create build directory if it doesn't exist
        if not os.path.exists(build_dir):
            os.makedirs(build_dir, exist_ok=True)
        
        # Create batch file for manual build
        batch_content = f"""@echo off
echo Manual ParsecCore Build
echo ======================
cd /d "{os.path.abspath(build_dir)}"
echo.
echo Current directory: %CD%
echo.
echo Step 1: Run CMake configuration
echo cmake .. -G "Visual Studio 17 2022"
echo.
echo Step 2: Build the project
echo cmake --build .
echo.
echo Step 3: Run tests (optional)
echo ctest
echo.
echo Press any key to start CMake configuration...
pause
cmake .. -G "Visual Studio 17 2022"
if errorlevel 1 (
    echo CMake configuration failed!
    pause
    exit /b 1
)
echo.
echo CMake configuration completed. Press any key to build...
pause
cmake --build .
if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)
echo.
echo Build completed successfully!
echo.
echo You can now run tests with: ctest
echo.
pause
"""
        
        batch_file = "manual_build_starsim.bat"
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        
        # Open command prompt with the batch file
        subprocess.Popen(f'cmd /c "{batch_file}"', shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        messagebox.showinfo("Manual Build", 
                          "Manual build console opened.\n\n"
                          "Follow the prompts to build ParsecCore step by step.\n\n"
                          "This allows you to see progress and troubleshoot any issues.")
        
        logging.info("Opened manual build console")
    
    def run_starsim_demo(self):
        """Run StarSim integration demo - Simple approach"""
        if not os.path.exists("int/StarSim"):
            messagebox.showerror("Error", "StarSim directory not found at int/StarSim")
            return
        
        # Just use the same simple approach as start_starsim
        self.start_starsim()

if __name__ == "__main__":
    manager = ProcessManager()
    manager.start()