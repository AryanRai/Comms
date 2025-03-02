import asyncio
import subprocess
import os

#run stream handler
subprocess.Popen(["python", "sh/sh.py"])

# Change to custom directory after current path
current_path = os.getcwd()
os.chdir(os.path.join(current_path, "en"))

subprocess.Popen(["python", "en.py"])

print("Stream handler running")
print("Engine running")