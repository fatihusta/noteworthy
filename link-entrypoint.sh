#!/bin/sh

echo $LINK_WG_KEY > /wg0.key

if [ "$NOTEWORTHY_ENV" = "dev" ]; then
    mkdir -p /dev/net
    mknod /dev/net/tun c 10 200
    wireguard-go wg0
else
    echo "Using native wireguard support."
    ip link add wg0 type wireguard
fi

wg set wg0 private-key /wg0.key
wg set wg0 listen-port 18521
ip addr add 10.0.0.1/24 dev wg0
ip link set wg0 up

#iptables forward port 80, 443 to 10.0.0.2:80/443
iptables -A FORWARD -i eth0 -o wg0 -p tcp --syn --dport 80 -m conntrack --ctstate NEW -j ACCEPT
iptables -A FORWARD -i eth0 -o wg0 -p tcp --syn --dport 443 -m conntrack --ctstate NEW -j ACCEPT

iptables -A FORWARD -i eth0 -o wg0 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -i wg0 -o eth0 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

iptables -P FORWARD DROP

iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j DNAT --to-destination 10.0.0.2
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 443 -j DNAT --to-destination 10.0.0.2

iptables -t nat -A POSTROUTING -o wg0 -p tcp --dport 80 -j SNAT --to-source 10.0.0.2
iptables -t nat -A POSTROUTING -o wg0 -p tcp --dport 443 -j SNAT --to-source 10.0.0.2

# vpn app udp proxies
socat UDP4-RECVFROM:18522,fork UDP4-SENDTO:10.0.0.2:18522,sp=18524,reuseaddr &
socat UDP4-RECVFROM:18523,fork UDP4-SENDTO:10.0.0.2:18522,sp=18525,reuseaddr