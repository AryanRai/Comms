# Enhanced HyperThreader v2 with Tool Message Support
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
import sys
from datetime import datetime
from typing import Dict, Any, Optional, Callable

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from tool_message_handlers import (
    get_execution_manager, register_tool_executor, 
    start_tool_handlers, stop_tool_handlers
)
from message_validation import create_tool_call, create_tool_result, validate_message
from message_registry import get_registry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class ToolMessageRouter:
    """Handles routing and processing of tool execution messages"""
    
    def __init__(self):
        self.message_handlers: Dict[str, Callable] = {}
        self.execution_manager = get_execution_manager()
        self.registry = get_registry()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Register message handlers for tool execution"""
        self.message_handlers['tool_call'] = self.handle_tool_call
        self.message_handlers['tool_result'] = self.handle_tool_result
        
    async def route_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Route incoming messages to appropriate handlers"""
        try:
            message_type = message.get('type')
            if message_type in self.message_handlers:
                return await self.message_handlers[message_type](message)
            else:
                logging.warning(f"No handler for message type: {message_type}")
                return None
        except Exception as e:
            logging.error(f"Error routing message: {e}")
            return self.create_error_response(message, str(e))
    
    async def handle_tool_call(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution requests"""
        try:
            # Validate message format
            if not validate_message(message, 'tool_call'):
                return self.create_error_response(message, "Invalid tool_call message format")
            
            tool_name = message.get('tool_name')
            parameters = message.get('parameters', {})
            execution_id = message.get('execution_id')
            context = message.get('context', {})
            
            logging.info(f"Executing tool: {tool_name} with ID: {execution_id}")
            
            # Execute tool through execution manager
            result = await self.execution_manager.execute_tool(
                tool_name=tool_name,
                parameters=parameters,
                execution_id=execution_id,
                context=context
            )
            
            # Create tool_result message
            return create_tool_result(
                execution_id=execution_id,
                tool_name=tool_name,
                status=result.get('status', 'success'),
                result=result.get('result'),
                error=result.get('error')
            )
            
        except Exception as e:
            logging.error(f"Error handling tool_call: {e}")
            return create_tool_result(
                execution_id=message.get('execution_id', 'unknown'),
                tool_name=message.get('tool_name', 'unknown'),
                status='error',
                result=None,
                error=str(e)
            )
    
    async def handle_tool_result(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle tool execution results"""
        try:
            # Validate message format
            if not validate_message(message, 'tool_result'):
                logging.error("Invalid tool_result message format")
                return None
            
            execution_id = message.get('execution_id')
            tool_name = message.get('tool_name')
            status = message.get('status')
            
            logging.info(f"Received tool result for {tool_name} (ID: {execution_id}): {status}")
            
            # Process result through execution manager
            await self.execution_manager.handle_tool_result(message)
            
            return None  # tool_result messages don't need responses
            
        except Exception as e:
            logging.error(f"Error handling tool_result: {e}")
            return None
    
    def create_error_response(self, original_message: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Create error response for failed tool execution"""
        return create_tool_result(
            execution_id=original_message.get('execution_id', 'unknown'),
            tool_name=original_message.get('tool_name', 'unknown'),
            status='error',
            result=None,
            error=error
        )

class EnhancedProcessManager:
    def __init__(self):
        self.processes = {}
        self.root = Tk()
        self.root.title("Enhanced Comms HyperThreader v2")
        self.tool_router = ToolMessageRouter()
        self.message_queue = asyncio.Queue()
        self.running = False
           
     
        # Initialize UI components
        self.setup_ui()
        
        # Start tool handlers
        start_tool_handlers()
        
        # Start message processing loop
        self.start_message_processing()
    
    def setup_ui(self):
        """Setup the enhanced UI with tool execution monitoring"""
        # Main frame
        main_frame = Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Process management section
        process_frame = Frame(main_frame)
        process_frame.pack(fill=tk.X, pady=(0, 10))
        
        Label(process_frame, text="Process Management", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        # Process buttons
        button_frame = Frame(process_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        Button(button_frame, text="Start Stream Handler", 
               command=self.start_stream_handler).pack(side=tk.LEFT, padx=(0, 5))
        Button(button_frame, text="Stop All", 
               command=self.stop_all_processes).pack(side=tk.LEFT, padx=5)
        Button(button_frame, text="Refresh Status", 
               command=self.refresh_status).pack(side=tk.LEFT, padx=5)
        
        # Tool execution section
        tool_frame = Frame(main_frame)
        tool_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        Label(tool_frame, text="Tool Execution Monitor", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        # Tool execution log
        log_frame = Frame(tool_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.tool_log = Text(log_frame, height=15, wrap=tk.WORD)
        tool_scrollbar = Scrollbar(log_frame, orient=tk.VERTICAL, command=self.tool_log.yview)
        self.tool_log.configure(yscrollcommand=tool_scrollbar.set)
        
        self.tool_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tool_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status section
        status_frame = Frame(main_frame)
        status_frame.pack(fill=tk.X)
        
        self.status_label = Label(status_frame, text="Status: Initializing...", 
                                 font=("Arial", 10))
        self.status_label.pack(anchor=tk.W)
        
        # Tool statistics
        self.stats_label = Label(status_frame, text="Tool Executions: 0 | Active: 0 | Errors: 0", 
                                font=("Arial", 10))
        self.stats_label.pack(anchor=tk.W)
        
        # Initialize statistics
        self.tool_stats = {
            'total_executions': 0,
            'active_executions': 0,
            'error_count': 0
        }
        
        self.log_tool_message("Tool execution monitoring initialized")
    
    def start_message_processing(self):
        """Start the async message processing loop"""
        self.running = True
        
        # Start the async event loop in a separate thread
        def run_async_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.message_processing_loop())
        
        self.async_thread = Thread(target=run_async_loop, daemon=True)
        self.async_thread.start()
    
    async def message_processing_loop(self):
        """Main message processing loop"""
        while self.running:
            try:
                # Process messages from queue
                if not self.message_queue.empty():
                    message = await self.message_queue.get()
                    await self.process_message(message)
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logging.error(f"Error in message processing loop: {e}")
                await asyncio.sleep(1)  # Longer delay on error
    
    async def process_message(self, message: Dict[str, Any]):
        """Process incoming messages through the tool router"""
        try:
            self.log_tool_message(f"Processing message: {message.get('type', 'unknown')}")
            
            # Update statistics
            if message.get('type') == 'tool_call':
                self.tool_stats['total_executions'] += 1
                self.tool_stats['active_executions'] += 1
                self.update_stats_display()
            
            # Route message through tool router
            response = await self.tool_router.route_message(message)
            
            # Handle response if any
            if response:
                await self.handle_response(response)
            
            # Update statistics for completion
            if message.get('type') == 'tool_call':
                self.tool_stats['active_executions'] -= 1
                if response and response.get('status') == 'error':
                    self.tool_stats['error_count'] += 1
                self.update_stats_display()
                
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            self.log_tool_message(f"Error processing message: {e}")
            
            # Update error statistics
            self.tool_stats['error_count'] += 1
            if message.get('type') == 'tool_call':
                self.tool_stats['active_executions'] -= 1
            self.update_stats_display()
    
    async def handle_response(self, response: Dict[str, Any]):
        """Handle responses from tool execution"""
        try:
            response_type = response.get('type')
            if response_type == 'tool_result':
                execution_id = response.get('execution_id')
                tool_name = response.get('tool_name')
                status = response.get('status')
                
                self.log_tool_message(f"Tool {tool_name} ({execution_id}): {status}")
                
                # Log error details if present
                if status == 'error' and response.get('error'):
                    self.log_tool_message(f"Error details: {response.get('error')}")
                
                # Here you would typically send the response back through the stream handler
                # For now, we'll just log it
                logging.info(f"Tool execution completed: {tool_name} -> {status}")
                
        except Exception as e:
            logging.error(f"Error handling response: {e}")
    
    def log_tool_message(self, message: str):
        """Log message to the tool execution monitor"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Update UI in main thread
        self.root.after(0, lambda: self._update_tool_log(log_entry))
    
    def _update_tool_log(self, log_entry: str):
        """Update tool log in main thread"""
        self.tool_log.insert(tk.END, log_entry)
        self.tool_log.see(tk.END)
        
        # Keep log size manageable
        if int(self.tool_log.index('end-1c').split('.')[0]) > 1000:
            self.tool_log.delete('1.0', '100.0')
    
    def update_stats_display(self):
        """Update the statistics display"""
        stats_text = (f"Tool Executions: {self.tool_stats['total_executions']} | "
                     f"Active: {self.tool_stats['active_executions']} | "
                     f"Errors: {self.tool_stats['error_count']}")
        
        self.root.after(0, lambda: self.stats_label.config(text=stats_text))
    
    async def queue_message(self, message: Dict[str, Any]):
        """Queue a message for processing"""
        await self.message_queue.put(message)
    
    def start_stream_handler(self):
        """Start the stream handler process"""
        try:
            if "stream_handler" not in self.processes:
                # Start stream handler (enhanced mode with tool support by default)
                cmd = [sys.executable, "sh/stream_handlerv2.4.py"]
                process = subprocess.Popen(cmd, cwd=os.path.dirname(__file__))
                self.processes["stream_handler"] = process
                
                self.log_tool_message("Stream handler started with tool support")
                self.status_label.config(text="Status: Stream handler running")
            else:
                messagebox.showinfo("Info", "Stream handler already running")
                
        except Exception as e:
            error_msg = f"Failed to start stream handler: {e}"
            self.log_tool_message(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def stop_all_processes(self):
        """Stop all managed processes"""
        try:
            # Stop tool handlers
            stop_tool_handlers()
            
            # Stop managed processes
            for name, process in self.processes.items():
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    self.log_tool_message(f"Stopped {name}")
            
            self.processes.clear()
            self.running = False
            
            self.log_tool_message("All processes stopped")
            self.status_label.config(text="Status: All processes stopped")
            
        except Exception as e:
            error_msg = f"Error stopping processes: {e}"
            self.log_tool_message(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def refresh_status(self):
        """Refresh the status of all processes"""
        try:
            active_processes = []
            dead_processes = []
            
            for name, process in list(self.processes.items()):
                if process.poll() is None:
                    active_processes.append(name)
                else:
                    dead_processes.append(name)
                    del self.processes[name]
            
            status_text = f"Status: {len(active_processes)} processes running"
            if dead_processes:
                status_text += f" ({len(dead_processes)} stopped)"
            
            self.status_label.config(text=status_text)
            self.log_tool_message(f"Status refresh: {len(active_processes)} active, {len(dead_processes)} stopped")
            
        except Exception as e:
            error_msg = f"Error refreshing status: {e}"
            self.log_tool_message(error_msg)
    
    def run(self):
        """Run the enhanced process manager"""
        try:
            self.log_tool_message("Enhanced HyperThreader v2 started")
            self.status_label.config(text="Status: Ready")
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log_tool_message("Shutting down...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources on shutdown"""
        try:
            self.running = False
            self.stop_all_processes()
            logging.info("Enhanced HyperThreader v2 shutdown complete")
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

def main():
    """Main entry point"""
    try:
        # Enable memory tracing for debugging
        tracemalloc.start()
        
        # Create and run the enhanced process manager
        manager = EnhancedProcessManager()
        manager.run()
        
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        messagebox.showerror("Fatal Error", f"Application failed to start: {e}")
    finally:
        # Stop memory tracing
        tracemalloc.stop()

if __name__ == "__main__":
    main()