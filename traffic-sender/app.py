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
# The K8s service name for Consul, injected by the deployment YAML
CONSUL_HOST = os.getenv("CONSUL_HOST", None)
CONSUL_PORT = int(os.getenv("CONSUL_PORT", 8500))
CONSUL_TPS_KEY = "config/tps"
DEFAULT_TPS = 1.0 # Default TPS if Consul fails

def get_tps_from_consul():
    """
    Fetches the TPS configuration from Consul.
    Returns DEFAULT_TPS if Consul is unavailable.
    """
    if not CONSUL_HOST:
        print(f"Consul host not set. Using default TPS: {DEFAULT_TPS}")
        return DEFAULT_TPS
        
    try:
        # Note: consul-server.consul.svc.cluster.local is the FQDN
        # We just use the host 'consul-server' since it's in the same namespace
        # or the injected env var 'consul-server.consul.svc.cluster.local'
        c = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)
        index, data = c.kv.get(CONSUL_TPS_KEY)
        if data:
            tps = float(data['Value'])
            print(f"Successfully fetched TPS from Consul: {tps}")
            return tps
        else:
            print(f"No TPS key found in Consul ({CONSUL_TPS_KEY}). Using default: {DEFAULT_TPS}")
            return DEFAULT_TPS
    except Exception as e:
        print(f"Error connecting to Consul at {CONSUL_HOST}: {e}. Using default TPS: {DEFAULT_TPS}")
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
    print(f"Consul Host: {CONSUL_HOST}")
    
    current_tps = get_tps_from_consul()
    last_consul_check = time.time()
    
    # Set the Prometheus gauge
    TPS_GAUGE.set(current_tps)

    while True:
        # Check Consul for updates every 60 seconds (as you requested)
        if CONSUL_HOST and (time.time() - last_consul_check > 60):
            print("Checking Consul for TPS update...")
            current_tps = get_tps_from_consul()
            TPS_GAUGE.set(current_tps) # Update the metric
            last_consul_check = time.time()

        # Calculate sleep time based on TPS
        if current_tps <= 0:
            current_tps = 1.0 # Safety check to avoid ZeroDivisionError
            
        sleep_time = 1.0 / current_tps
        
        problem = generate_problem()
        
        try:
            response = requests.post(WORKER_URL, json={"equation": problem})
            
            if response.status_code == 200:
                # --- FIX for AttributeError ---
                # Check if the response is a dictionary before trying .get()
                response_data = response.json()
                if isinstance(response_data, dict):
                    answer = response_data.get('answer', 'N/A')
                    print(f"Sent: {problem}, Got: {answer}")
                else:
                    print(f"Sent: {problem}, Got unexpected response: {response_data}")
                # --- End of FIX ---
            else:
                print(f"Sent: {problem}, Got Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError as e:
            print(f"Failed to connect to worker: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        
        time.sleep(sleep_time)

if __name__ == "__main__":
    run_sender()
