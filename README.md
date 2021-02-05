# Overview
This repository contains the proof-of-concept implementation that preceded the upcoming Noteworthy Architecture and Noteworthy Meta-Protocols.

The Noteworthy Architecture makes it easy to self-host services on-prem by transparently proxying encrypted traffic through a publically accessible host. Nginx serves as the reverse proxy and WireGuard is utilized for secure tunneling between on-prem systems and the publically accessible host. TLS is terminated on-prem. The reference implementation in this repository is considered experimental and is not recommended for production use cases. The secure tunnel capabilities provided are similar to ngrok, PageKite, Inlets or Argo Tunnels. There is also support for a one-click deployment of a federation capable Matrix homeserver. 

# Getting Started
Docker is the only requirement to get started with Noteworthy.

## Hub (Host with public IP)
Start by building the hub container on any publically accessible host:
```
$ make docker RELEASE_TAG=beta ROLE=hub GIT_COMMIT=$(git rev-parse HEAD)
```

Define a Bash function wrapper for Hub container:
```
notectl-hub() {
	docker run --rm -it -v "/var/run/docker.sock:/var/run/docker.sock" decentralabs/noteworthy:hub-beta "$@";
}
```
Launch the Hub container on the publically accessible host.
Replace `hub.example.com` in the above example with the FQDN of your hub.
```
$ notectl-hub launcher launch_hub hub.example.com
```

Generate an invite to the hub:
```
$ notectl-hub invite <some-identifier>
```

## Taproot (on-prem system)
Building the taproot container on your on-prem host:
```
$ make docker RELEASE_TAG=beta ROLE=taproot GIT_COMMIT=$(git rev-parse HEAD)
```
Copy and paste the `notectl` shell function wrapper:
```
notectl() {
	docker run --rm -it -v "/var/run/docker.sock:/var/run/docker.sock" decentralabs/noteworthy:taproot-beta "$@";
}
```

Launch a Matrix Server(Synapse) and make it publically accessible.
Make sure `matrix.example.com` DNS points to the same IP as `hub.example.com` before running this command.
```
notectl install matrix --server-name matrix.example.com
notectl link --container-id <matrix-container-id> --fqdn matrix.example.com --hub-fqdn hub.example.com --port 8008 https
```

You will be prompted to enter the invite code you generated on the hub with the `notectl invite` command above.

The link command above can be used to make any container available to the public internet by passing the container id and specifying the fqdn, hub-fqdn and internal port as show above.

## Getting started for Contributors
Start by building the development container:
```
make shell
$ notectl --help
```
You can now modify code in this repo on your host system to experiment with making changes to the Noteworthy PoC without needing to rebuild the container for every change.

# Noteworthy Team
Noteworthy's PoC development was sponsored by Decentralabs LLC, a Wyoming based telecommunications research and development firm that specialized in the development of open source telecommunications systems and next-generation digital infrastructure solutions.

Contact us on Matrix - #noteworthy:tincan.community

"WireGuard" is a registered trademark of Jason A. Donenfeld.
