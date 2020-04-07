import os
import subprocess


def is_configured(interface):
    return interface.encode() in subprocess.check_output(['cat', '/proc/net/dev'])

def add_peer(interface, pubkey, allowed_ips, endpoint=None, keepalive='30'):
    cmd = f'wg set {interface} peer {pubkey}\
 allowed-ips {allowed_ips} persistent-keepalive {keepalive}'
    if endpoint:
        cmd = cmd + f' endpoint {endpoint}'
    os.system(cmd)

def add_interface(interface):
    os.system(f'ip link add {interface} type wireguard')

def remove_interface(interface):
    os.system(f'ip link del dev {interface}')

def set_interface_private_key(interface, pk_path):
    os.system(f'wg set {interface} private-key {pk_path}')

def set_interface_ip(interface, ip):
    os.system(f'ip addr add {ip} dev {interface}')

def set_interface_listen_port(interface, port):
    os.system(f'wg set {interface} listen-port {port}')

def interface_down(interface):
    os.system(f'ip link set {interface} down')

def interface_up(interface):
    # Set MTU 1420 and bring up interface
    os.system(f'ip link set {interface} up')

def genkey(path):
    # TODO set umask / fix perms?
    os.system(f'wg genkey > {path}')

def pubkey(path):
    with open(path, 'r') as pk_file:
        return subprocess.check_output(['wg', 'pubkey'], stdin=pk_file).decode().strip()

# TODO setup DNS
def configure_dns(interface, nameservers):
    '''See wg-quick's use of resolvconf
    https://manpages.debian.org/unstable/wireguard-tools/wg-quick.8.en.html
    '''
    pass

def init(interface, ip, pk_path):
    add_interface(interface)
    set_interface_private_key(interface, pk_path)
    set_interface_listen_port(interface, '18521')
    set_interface_ip(interface, ip)
    interface_up(interface)
