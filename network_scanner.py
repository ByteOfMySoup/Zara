from scapy.all import arping
import socket

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
IP_parts = IPAddr.split(".")
end = IP_parts[len(IP_parts) - 1]
range = f"{IPAddr.replace(end, '1')}/24"
print(range)
arping(range)