#!/usr/bin/env python3
"""
Python launcher for multi-instance limit order script
Alternative to launcher.sh for cross-platform compatibility
"""
import os
import sys
import subprocess
import signal
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_DIR = SCRIPT_DIR / "configs"
LOG_DIR = SCRIPT_DIR / "logs"
PID_DIR = SCRIPT_DIR / "pids"

# Create directories
LOG_DIR.mkdir(exist_ok=True)
PID_DIR.mkdir(exist_ok=True)

# Colors
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'


def is_running(pid):
    """Check if process is running"""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def start_instance(config_file):
    """Start a single instance"""
    config_name = config_file.stem
    log_file = LOG_DIR / f"{config_name}.log"
    pid_file = PID_DIR / f"{config_name}.pid"
    
    # Check if already running
    if pid_file.exists():
        pid = int(pid_file.read_text().strip())
        if is_running(pid):
            print(f"{YELLOW}⚠  Instance {config_name} already running (PID: {pid}){NC}")
            return False
        else:
            # Stale PID file
            pid_file.unlink()
    
    # Start the instance
    print(f"{GREEN}✓{NC}  Starting instance: {config_name}")
    
    with open(log_file, 'w') as log:
        process = subprocess.Popen(
            [sys.executable, str(SCRIPT_DIR / "limit_order_multi.py"), str(config_file)],
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True  # Detach from parent
        )
    
    # Save PID
    pid_file.write_text(str(process.pid))
    
    print(f"   PID: {process.pid}")
    print(f"   Log: {log_file}")
    print()
    
    return True


def stop_instance(config_name):
    """Stop a single instance"""
    pid_file = PID_DIR / f"{config_name}.pid"
    
    if not pid_file.exists():
        print(f"{YELLOW}⚠  Instance {config_name} not running{NC}")
        return False
    
    pid = int(pid_file.read_text().strip())
    
    if is_running(pid):
        print(f"{GREEN}✓{NC}  Stopping instance: {config_name} (PID: {pid})")
        try:
            os.kill(pid, signal.SIGTERM)
            pid_file.unlink()
            return True
        except Exception as e:
            print(f"{RED}✗{NC}  Failed to stop: {e}")
            return False
    else:
        print(f"{YELLOW}⚠  Instance {config_name} not running (stale PID file){NC}")
        pid_file.unlink()
        return False


def show_status():
    """Show status of all instances"""
    print("=" * 60)
    print("  Instance Status")
    print("=" * 60)
    print()
    
    running_count = 0
    stopped_count = 0
    
    for pid_file in sorted(PID_DIR.glob("*.pid")):
        config_name = pid_file.stem
        pid = int(pid_file.read_text().strip())
        
        if is_running(pid):
            print(f"{GREEN}✓ RUNNING{NC}  {config_name} (PID: {pid})")
            running_count += 1
        else:
            print(f"{RED}✗ STOPPED{NC}  {config_name} (stale PID)")
            pid_file.unlink()
            stopped_count += 1
    
    if running_count == 0 and stopped_count == 0:
        print("No instances found")
    
    print()
    print(f"Summary: {running_count} running, {stopped_count} stopped")


def tail_logs():
    """Tail all log files"""
    print("=" * 60)
    print("  Tailing all logs (Ctrl+C to stop)")
    print("=" * 60)
    print()
    
    log_files = list(LOG_DIR.glob("*.log"))
    if not log_files:
        print("No log files found")
        return
    
    # Use tail -f on Unix-like systems
    if os.name != 'nt':
        try:
            subprocess.run(['tail', '-f'] + [str(f) for f in log_files])
        except KeyboardInterrupt:
            print("\nStopped tailing logs")
    else:
        print("Log tailing not implemented for Windows. View logs manually:")
        for log_file in log_files:
            print(f"  {log_file}")


def start_all():
    """Start all configured instances"""
    print("=" * 60)
    print("  Limit Order Multi-Instance Launcher")
    print("=" * 60)
    print()
    print("Starting all configured instances...")
    print()
    
    config_files = sorted(CONFIG_DIR.glob("config_*.py"))
    
    if not config_files:
        print(f"{RED}✗{NC}  No config files found in {CONFIG_DIR}")
        print("   Create config files named config_1.py, config_2.py, etc.")
        return
    
    started = 0
    for config_file in config_files:
        if start_instance(config_file):
            started += 1
    
    print("=" * 60)
    print(f"Started {started}/{len(config_files)} instances")
    print()
    print("Commands:")
    print("  python launcher.py status  - Check status")
    print("  python launcher.py logs    - View logs")
    print("  python launcher.py stop    - Stop all")


def stop_all():
    """Stop all running instances"""
    print("Stopping all instances...")
    print()
    
    stopped = 0
    for pid_file in sorted(PID_DIR.glob("*.pid")):
        config_name = pid_file.stem
        if stop_instance(config_name):
            stopped += 1
    
    print()
    print(f"Stopped {stopped} instances")


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "start"
    
    if command == "start":
        start_all()
    elif command == "stop":
        stop_all()
    elif command == "restart":
        print("Restarting all instances...")
        print()
        stop_all()
        time.sleep(2)
        start_all()
    elif command == "status":
        show_status()
    elif command == "logs":
        tail_logs()
    else:
        print("Usage: python launcher.py {start|stop|restart|status|logs}")
        print()
        print("Commands:")
        print("  start   - Start all configured instances")
        print("  stop    - Stop all running instances")
        print("  restart - Restart all instances")
        print("  status  - Show status of all instances")
        print("  logs    - Tail all log files")
        sys.exit(1)


if __name__ == "__main__":
    main()

