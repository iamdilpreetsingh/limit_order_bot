#!/bin/bash

# Launcher script for running multiple limit order instances
# Each instance runs in the background with output logged to separate files

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONFIG_DIR="$SCRIPT_DIR/configs"
LOG_DIR="$SCRIPT_DIR/logs"
PID_DIR="$SCRIPT_DIR/pids"

# Create directories if they don't exist
mkdir -p "$LOG_DIR"
mkdir -p "$PID_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Limit Order Multi-Instance Launcher"
echo "=========================================="
echo ""

# Function to start a single instance
start_instance() {
    local config_file=$1
    local config_name=$(basename "$config_file" .py)
    local log_file="$LOG_DIR/${config_name}.log"
    local pid_file="$PID_DIR/${config_name}.pid"
    
    # Check if already running
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠  Instance $config_name already running (PID: $pid)${NC}"
            return 1
        else
            # PID file exists but process is dead, clean it up
            rm "$pid_file"
        fi
    fi
    
    # Start the instance
    echo -e "${GREEN}✓${NC}  Starting instance: $config_name"
    python3 "$SCRIPT_DIR/limit_order_multi.py" "$config_file" > "$log_file" 2>&1 &
    local pid=$!
    
    # Save PID
    echo $pid > "$pid_file"
    
    echo "   PID: $pid"
    echo "   Log: $log_file"
    echo ""
    
    return 0
}

# Function to stop a single instance
stop_instance() {
    local config_name=$1
    local pid_file="$PID_DIR/${config_name}.pid"
    
    if [ ! -f "$pid_file" ]; then
        echo -e "${YELLOW}⚠  Instance $config_name not running${NC}"
        return 1
    fi
    
    local pid=$(cat "$pid_file")
    
    if ps -p $pid > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}  Stopping instance: $config_name (PID: $pid)"
        kill $pid
        rm "$pid_file"
        return 0
    else
        echo -e "${YELLOW}⚠  Instance $config_name not running (stale PID file)${NC}"
        rm "$pid_file"
        return 1
    fi
}

# Function to show status of all instances
show_status() {
    echo "=========================================="
    echo "  Instance Status"
    echo "=========================================="
    echo ""
    
    local running_count=0
    local stopped_count=0
    
    for pid_file in "$PID_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            local config_name=$(basename "$pid_file" .pid)
            local pid=$(cat "$pid_file")
            
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "${GREEN}✓ RUNNING${NC}  $config_name (PID: $pid)"
                running_count=$((running_count + 1))
            else
                echo -e "${RED}✗ STOPPED${NC}  $config_name (stale PID)"
                rm "$pid_file"
                stopped_count=$((stopped_count + 1))
            fi
        fi
    done
    
    if [ $running_count -eq 0 ] && [ $stopped_count -eq 0 ]; then
        echo "No instances found"
    fi
    
    echo ""
    echo "Summary: $running_count running, $stopped_count stopped"
}

# Function to tail logs of all instances
tail_logs() {
    echo "=========================================="
    echo "  Tailing all logs (Ctrl+C to stop)"
    echo "=========================================="
    echo ""
    
    tail -f "$LOG_DIR"/*.log 2>/dev/null
}

# Main script logic
case "${1:-start}" in
    start)
        echo "Starting all configured instances..."
        echo ""
        
        # Find all config files
        config_count=0
        for config_file in "$CONFIG_DIR"/config_*.py; do
            if [ -f "$config_file" ]; then
                start_instance "$config_file"
                config_count=$((config_count + 1))
            fi
        done
        
        if [ $config_count -eq 0 ]; then
            echo -e "${RED}✗${NC}  No config files found in $CONFIG_DIR"
            echo "   Create config files named config_1.py, config_2.py, etc."
            exit 1
        fi
        
        echo "=========================================="
        echo "Started $config_count instances"
        echo ""
        echo "Commands:"
        echo "  ./launcher.sh status  - Check status"
        echo "  ./launcher.sh logs    - View logs"
        echo "  ./launcher.sh stop    - Stop all"
        ;;
        
    stop)
        echo "Stopping all instances..."
        echo ""
        
        for pid_file in "$PID_DIR"/*.pid; do
            if [ -f "$pid_file" ]; then
                config_name=$(basename "$pid_file" .pid)
                stop_instance "$config_name"
            fi
        done
        
        echo ""
        echo "All instances stopped"
        ;;
        
    restart)
        echo "Restarting all instances..."
        echo ""
        $0 stop
        sleep 2
        $0 start
        ;;
        
    status)
        show_status
        ;;
        
    logs)
        tail_logs
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start all configured instances"
        echo "  stop    - Stop all running instances"
        echo "  restart - Restart all instances"
        echo "  status  - Show status of all instances"
        echo "  logs    - Tail all log files"
        exit 1
        ;;
esac

