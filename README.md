# Noteworthy

Noteworthy is an experimental distributed networking protocol and collaborative tooling ecosytem that aims to bring distrubuted overlay networks and self-hosted online services into the mainstream. Noteworthy is comprised of a collection Matrix based sub-protocols and meta-protocols for establishing trustful distributed overlay networks. It is similar in some aspects to existing personal networking products such as ZeroTier or TailScale but is 100% community powered, free and open source software.

Noteworthy makes it easy to deploy publically accessible web services behind a distributed network of blind TLS reverse-proxies (think ngrok) therefore making it possible to run a federation capable Matrix home server on a host that is not directly accessible to the public internet. Noteworthy accomplishes this with a Hub and Spoke topology. In Noteworthy parlance we call spokes "Taproots" which represent the end-user's primary home server.

Because Noteworthy builds on the Matrix decentralized messaging protocol, it aims to be the fastest and easiest way to deploy a federation capable Matrix home server.

# Getting Started
Docker is the only requirement to get started with Noteworthy.

The `notectl` command-line utility is the primary interface for interacting with Noteworthy.
```
$ bash <(curl -s get.noteworthy.im)
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
$ notectl-hub-dev launcher launch_hub
```

# Noteworthy Team
Noteworthy's development is sponsored by Decentralabs LLC, a Wyoming based telecommuniations research and development firm that specializes in the development of open source telecommunications systems and next-generation digital infrastructure solutions.

Contributions to this project are welcomed and encouraged!

Contact us on Matrix - #noteworthy:tincan.community

