# Noteworthy

Noteworthy is a free and open source collaborative tooling ecosystem that combines existing best-in-class open source collaboration tools with an innovative Matrix sub-protocol distrubuted overlay networking framework that enables collaborative self-hosting of personal and organizational online services.

Noteworthy is comprised of a collection of Matrix powered meta-protocols for establishing secure and private distributed overlay networks. In some aspects, it is similar to existing personal networking products such as ZeroTier or TailScale but is 100% community powered, non-commercial free and open source software.

Noteworthy makes it easy to deploy publically accessible online services behind a distributed network of transparent TLS reverse-proxies (think ngrok but decentralized). Noteworthy accomplishes this with a distributed Hub and Spoke topology. A distributed network of transparent reverse TLS proxies enables Noteworthy to ship a federation capable Matrix home server that can be deployed to hosts behind firewalls / NAT or that are otherwise not accessible to the public internet. In Noteworthy parlance we call these deployments "Taproots" and the distributed network of transparent proxies that serve them "Hubs". A Taproot is a dedicated host that functions as a Noteworthy end-user's primary home server. A Hub is a publically accessible host running the Noteworthy Hub software described below. Taproot's must be invited in order to receieve inbound connectivity via a Noteworthy Hub.


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

