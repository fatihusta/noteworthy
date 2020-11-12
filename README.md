# Noteworthy

Noteworthy is free and open source software that combines existing best-in-class open source collaboration tools with a Matrix powered meta-protocol in order to enable the collaborative self-hosting of personal online services.

Noteworthy makes it easy for non-technical users to establish Wireguard powered distributed overlay networks. In some respects, Noteworthy is similar to existing commercially available personal networking products such as ZeroTier and TailScale, but is much more ambitious and will always be 100% community powered, non-commercial free and open source software. Noteworthy aims to become the catalyst and toolbelt of a non-commercial user owned web.

With Noteworthy a non-technical user can deploy publically accessible online services behind a distributed network of transparent TLS reverse-proxies (think ngrok but decentralized). This is made possible with a distributed hub and spoke topology that is coordinated via the decentralized Matrix protocol. A distributed network of transparent reverse proxies enables federation capable Matrix home servers to be deployed to hosts behind firewalls, carrier-grade NATs or hosts otherwise not accessible to the public internet. In Noteworthy parlance we call the end-user deployments "roots" and the distributed network of transparent proxies tha service them "hubs". A root is a dedicated host that functions as a Noteworthy user's primary server. The goal is to enable users to operate both roots and hubs collaboratively with individuals they already know and trust IRL (in real life).

Noteworthy aims to provide the following apps and services as a 1-click plug-and-play solution:

- Instant Messaging/Voice/Video  - Powered by Matrix (Element/Synapse) (done)
- Social - Chupacabra, a Matrix powered content sharing and discussion client (coming soon, in-progress)
- Email/Calendar/Contacts - Powered by Mail-in-a-Box (coming soon, in-progress)
- Voice and Video Conferencing - Jitsi (coming soon)
- Publishing - Ghost CMS (coming soon)


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
