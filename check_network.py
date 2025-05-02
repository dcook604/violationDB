#!/usr/bin/env python3
import socket
import subprocess
import sys

def check_dns(hostname):
    """Try to resolve a hostname to IP address"""
    print(f"Resolving {hostname}...")
    try:
        ip = socket.gethostbyname(hostname)
        print(f"✓ Successfully resolved {hostname} to {ip}")
        return ip
    except Exception as e:
        print(f"✗ Failed to resolve {hostname}: {e}")
        return None

def check_socket_connection(host, port, timeout=5):
    """Test direct socket connection to host:port"""
    print(f"Testing socket connection to {host}:{port}...")
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        print(f"✓ Socket connection to {host}:{port} successful")
        return True
    except Exception as e:
        print(f"✗ Socket connection to {host}:{port} failed: {e}")
        return False

def run_ping(host, count=3):
    """Run system ping command"""
    print(f"Pinging {host} ({count} times)...")
    try:
        output = subprocess.check_output(
            ["ping", "-c", str(count), host], 
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        print(f"✓ Ping successful: {host}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Ping failed: {host}: {e.output}")
        return False

def check_traceroute(host):
    """Run system traceroute command"""
    print(f"Running traceroute to {host}...")
    try:
        output = subprocess.check_output(
            ["traceroute", "-m", "15", host], 
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        print(f"Traceroute to {host}:")
        print(output)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Traceroute failed: {e.output}")
        return False
    except FileNotFoundError:
        print("✗ Traceroute command not found")
        return False

def check_telnet(host, port, timeout=5):
    """Test with telnet"""
    print(f"Testing telnet to {host}:{port}...")
    try:
        output = subprocess.check_output(
            ["timeout", str(timeout), "telnet", host, str(port)], 
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        print(f"Telnet output: {output}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Telnet failed: {e.output if hasattr(e, 'output') else str(e)}")
        return False
    except FileNotFoundError:
        print("✗ Telnet command not found")
        return False

def main():
    # List of hosts to test
    hosts = [
        ("mail.smtp2go.com", 2525),  # Your SMTP server
        ("smtp.gmail.com", 587),     # Common alternative
        ("8.8.8.8", 53),            # Google DNS
        ("1.1.1.1", 53)             # Cloudflare DNS
    ]
    
    print("=== NETWORK CONNECTIVITY TEST ===\n")
    
    print("System Python version:")
    print(sys.version)
    print("")
    
    # Test each host
    for host, port in hosts:
        print(f"\n=== Testing connectivity to {host}:{port} ===")
        
        # DNS resolution
        ip = check_dns(host)
        
        # If it's not an IP address already
        if not ip and not host[0].isdigit():
            print(f"Cannot proceed with further tests for {host} due to DNS resolution failure")
            continue
        
        # Ping test (to the original hostname)
        run_ping(host)
        
        # Direct socket connection
        check_socket_connection(host, port)
        
        # Try telnet
        check_telnet(host, port)
        
        print("")
    
    print("\n=== NETWORK CONNECTIVITY TEST COMPLETED ===")

if __name__ == "__main__":
    main() 