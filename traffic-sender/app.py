import os
import random
import time
import requests
import consul
from prometheus_client import start_http_server, Gauge

# --- Prometheus Metrics ---
# Create a Gauge metric to track Transactions Per Second
TPS_GAUGE = Gauge('traffic_sender_tps', 'Current Transactions Per Second')

try:
    # Start an HTTP server for Prometheus to scrape on port 8001, bound to all interfaces
    start_http_server(8001, '0.0.0.0')
    print("Prometheus metrics server started on port 8001.")
except Exception as e:
    # Add a log in case it fails (e.g., port already in use)
    print(f"Error starting Prometheus server: {e}")


# --- Configuration ---
# Get config from environment variables
WORKER_URL = os.getenv("WORKER_URL", "http://worker-svc:8525/calculate")
CONSUL_HOST = os.getenv("CONSUL_HOST", None) # Set to None to disable by default
CONSUL_PORT = int(os.getenv("CONSUL_PORT", 8500))
CONSUL_TPS_KEY = "config/tps"
DEFAULT_TPS = 2.0 # Default TPS if Consul fails

def get_tps_from_consul():
    """
    Fetches the TPS configuration from Consul.
    Returns DEFAULT_TPS if Consul is unavailable.
    """
    if not CONSUL_HOST:
        print(f"Consul host not set. Using default TPS: {DEFAULT_TPS}")
        return DEFAULT_TPS
        
    try:
        c = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)
        index, data = c.kv.get(CONSUL_TPS_KEY)
        if data:
            tps = float(data['Value'])
            print(f"Successfully fetched TPS from Consul: {tps}")
            return tps
        else:
            print(f"No TPS key found in Consul. Using default: {DEFAULT_TPS}")
            return DEFAULT_TPS
    except Exception as e:
        print(f"Error connecting to Consul: {e}. Using default TPS: {DEFAULT_TPS}")
        return DEFAULT_TPS

def generate_problem():
    """Generates a simple, random math problem."""
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    op_choice = random.choice(['+', '-', '*', '/'])
    
    # Avoid division by zero
    if op_choice == '/' and b == 0:
        b = 1
        
    return f"{a} {op_choice} {b}"

def run_sender():
    """
    Main loop for the traffic sender.
    Sends requests to the worker based on the TPS config.
    """
    print("Traffic Sender started.")
    print(f"Worker URL: {WORKER_URL}")
    
    # --- We will uncomment this when we install Consul ---
    # current_tps = get_tps_from_consul()
    # last_consul_check = time.time()
    
    # --- Hardcoded value for now ---
    current_tps = 2.0
    print(f"Starting with hardcoded TPS: {current_tps}")
    
    # Set the Prometheus gauge
    TPS_GAUGE.set(current_tps)

    while True:
        # --- We will uncomment this when we install Consul ---
        # Check Consul for updates every 2 minutes
        # if CONSUL_HOST and (time.time() - last_consul_check > 120):
        #     print("Checking Consul for TPS update...")
        #     current_tps = get_tps_from_consul()
        #     TPS_GAUGE.set(current_tps) # Update the metric
        #     last_consul_check = time.time()

        # Calculate sleep time based on TPS
        sleep_time = 1.0 / current_tps
        
        problem = generate_problem()
        
        try:
            response = requests.post(WORKER_URL, json={"equation": problem})
            if response.status_code == 200:
                print(f"Sent: {problem}, Got: {response.json().get('answer')}")
            else:
                print(f"Sent: {problem}, Got Error: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            print(f"Failed to connect to worker: {e}")
        
        time.sleep(sleep_time)

if __name__ == "__main__":
    run_sender()


