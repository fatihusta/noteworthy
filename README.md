Noteworthy is a loose collection of free software and open protocols with an acompanying toolchain for building decentralized public and private telecommunications infrastructure.

See OVERVIEW.md for a detailed overview of Noteworthy.

# Getting Started
Docker is the only requirement to get started with Noteworthy.

The `notectl` command-line utility is the primary interface for interacting with Noteworthy.
```
$ bash <(curl -s https://get.noteworthy.im)
```

The above script will pull the `decentralabs/noteworthy:taproot-beta` Docker container and start the interactive installation process. You will need to request an invite to the public Decentralabs Hub if you are not planning on deploying your own Hub as described below.


## Getting started (Developers)
Start by building the Taproot container:
```
make docker ROLE=taproot GIT_COMMIT=$(git rev-parse HEAD) RELEASE_TAG=dev
```

This will create the container `decentralabs/noteworthy:taproot-dev`

We recommend the use of a shell functions to wrap invocations of the `notectl` command-line utility living inside the container you built in the previous step.

Copy and paste the `notectl-dev` shell function wrapper:
```
notectl-dev() {
	docker run -e NOTEWORTHY_DOMAIN=$NOTEWORTHY_DOMAIN --rm -it -v "/var/run/docker.sock:/var/run/docker.sock" decentralabs/noteworthy:taproot-dev "$@";
}
```

### Interacting with multiple release stages
You can define multiple shell functions to manage interacting with the various release stages (prod, beta, dev etc) of Noteworthy.
The vanilla `notectl` is reserved for the current production release.

For example, to build a `beta` release Taproot container, pull the latest changes from the `master` branch and run the following:
```
make docker ROLE=taproot GIT_COMMIT=$(git rev-parse HEAD) RELEASE_TAG=beta
```
Then define the following Bash function wrapper:
```
notectl-beta() {
	docker run -e NOTEWORTHY_DOMAIN=$NOTEWORTHY_DOMAIN --rm -it -v "/var/run/docker.sock:/var/run/docker.sock" decentralabs/noteworthy:taproot-beta "$@";
}
```
You can then deploy and interact with networks/services using Noteworthy's `beta ` release:
```
$ notectl-beta install
```
## Deploy a Noteworthy Hub
You must build the Hub and Link containers before launching a hub.

Build Hub container:
```
make docker ROLE=hub GIT_COMMIT=$(git rev-parse HEAD) RELEASE_TAG=dev
```
Build Link container:
```
make docker ROLE=link RELEASE_TAG=dev
```

Define a Bash function wrapper for Hub container:
```
notectl-hub-dev() {
	docker run -e NOTEWORTHY_DOMAIN=$NOTEWORTHY_DOMAIN --rm -it -v "/var/run/docker.sock:/var/run/docker.sock" decentralabs/noteworthy:hub-dev "$@";
}
```

Launch the Hub container:
```
$ notectl-hub-dev launcher launch_hub hub.example.com
```
Replace `hub.example.com` in the above example with the FQDN of your hub.

# Noteworthy Team
Noteworthy's development is sponsored by Decentralabs LLC, a Wyoming based telecommuniations research and development firm that specializes in the development of open source telecommunications systems and next-generation digital infrastructure solutions.

Contributions to this project are welcomed and encouraged!

Contact us on Matrix - #noteworthy:tincan.community

"WireGuard" is a registered trademark of Jason A. Donenfeld.
