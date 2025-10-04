"""
Backend startup script for Enhanced Dashboard
"""
import subprocess
import sys
import os
import time

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting Enhanced Dashboard Backend...")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    print(f"📁 Working directory: {os.getcwd()}")
    print("🔧 Starting FastAPI server...")
    print("🌐 Server will be available at: http://localhost:5001")
    print("📚 API documentation: http://localhost:5001/docs")
    print("=" * 50)
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "127.0.0.1", 
            "--port", "5001"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("\n💡 Make sure you have all dependencies installed:")
        print("   pip install fastapi uvicorn python-multipart")

if __name__ == "__main__":
    start_backend()
