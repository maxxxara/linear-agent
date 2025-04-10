import os
import subprocess
import sys

if __name__ == "__main__":
    if os.path.exists("src/app.py"):
        subprocess.run([
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            "src/app.py",
            "--server.enableXsrfProtection=false",
            "--server.enableCORS=false",
            "--server.enableWebsocketCompression=false",
            "--global.developmentMode=false"
        ])
    else:
        print("❌ Error: run this script from the project root directory!")