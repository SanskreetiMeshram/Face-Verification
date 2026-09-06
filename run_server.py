"""
FaceChain Verify — Universal Single-Server Launcher
Runs the complete application (Frontend UI + FastAPI Backend + SQLite DB + Blockchain Engine) on a single port.
Works on Windows, Android (via Termux/LAN), Linux, and macOS.
"""
import os
import sys
import socket
import webbrowser
import uvicorn

def get_lan_ip():
    """Retrieve local network IP for mobile/Android sharing."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def main():
    lan_ip = get_lan_ip()
    port = 8000

    print("=" * 65)
    print("      🚀 FACECHAIN VERIFY — APPLICATION SERVER LAUNCHED")
    print("=" * 65)
    print(f"\n  [✓] Local Machine URL:      http://localhost:{port}")
    print(f"  [✓] Mobile / Android URL:   http://{lan_ip}:{port}")
    print(f"  [✓] Backend API Docs:       http://localhost:{port}/docs")
    print(f"  [✓] SQLite Database:        Initialized (backend/app/facechain.db)")
    print(f"  [✓] Progressive Web App:    Active (Installable on Android/iOS/PC)")
    print("\n" + "-" * 65)
    print(f"  📲 TO OPEN ON YOUR ANDROID PHONE / FRIEND'S LAPTOP:")
    print(f"     1. Connect your phone to the same Wi-Fi network.")
    print(f"     2. Open Chrome/Browser on your phone and go to:")
    print(f"        👉  http://{lan_ip}:{port}")
    print(f"     3. Tap 'Install App' or 'Add to Home Screen' to use it as an app!")
    print("-" * 65 + "\n")

    # Ensure backend directory is in sys.path
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    # Open browser automatically on desktop
    try:
        webbrowser.open(f"http://localhost:{port}")
    except Exception:
        pass

    # Start FastAPI server
    from app.main import app
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    main()
