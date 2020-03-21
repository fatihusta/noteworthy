#!/bin/sh

# Only run the first time we start
FILE=/opt/noteworthy/.wg-easy
if [ ! -f "$FILE" ]; then
    # Generate SSH host keys
    ssh-keygen -A

    if [ -n "$HUB" ]
    then
        echo -e 'y\n' | ssh-keygen -f /opt/noteworthy/noteworthy-wireguard/hub/id_rsa -t rsa -N ''
    fi

    # Optionally enable password login?
    # Set UsePAM yes so we can login with
    # a locked account without setting a password
    sed -i s/^#UsePAM.no/"UsePAM yes"/ /etc/ssh/sshd_config

    # Create the wg-easy user
    adduser -s /usr/bin/wg-easy-hub.py -D wg-easy
    echo "Setting password to: " $HUB_PASSWORD
    echo -e "$HUB_PASSWORD\n$HUB_PASSWORD" |passwd wg-easy
    touch /home/wg-easy/.hushlogin

    # sudo for netlink perms
    # because we want hub.py to init networking on first invocation from remote peer
    # may not be worth added complexity / risk
    echo "wg-easy ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers.d/wg-easy

    touch /opt/decentralabs/.wg-easy

    echo "wg-easy: first_run -- Freedom's Greetings from the Big Easy!"
fi

echo "Decentralabs 2020. All rights reverse engineered."
/usr/sbin/sshd

mkdir /home/wg-easy/.ssh
cp /opt/noteworthy/noteworthy-wireguard/hub/id_rsa /home/wg-easy/.ssh/
cp /opt/noteworthy/noteworthy-wireguard/hub/id_rsa.pub /home/wg-easy/.ssh/authorized_keys

chown -R wg-easy:wg-easy /home/wg-easy/.ssh

# Where the magic happens
if [ -z "$HUB" ]
then
    wg-easy.sh|wg-easy-set.py
fi

tail -f /dev/null
#sleep 300