# Noteworthy

Noteworthy is an experimental distributed networking toolkit. It is similar to existing personal networking products such as ZeroTier and TailScale but is 100% community powered, free and open source software. 

Noteworthy's development is sponsored by Decentralabs LLC, a Wyoming based telecommuniations research and development firm that specializes in the development of open source telecommunications systems and next-generation digital infrastructure solutions.

## Cost Gravity Accelerator
Noteworthy is an ambitious open source project that aims to lower the costs of designing, deploying, maintaning trusted distributed overlay networks and the applications that run on top of them. It is not enough for Noteworthy to be open source, technical complexity contributes substantially to the excessive cost of access.
Because of this, Noteworthy aims to be as simple and easy to use and understand as possible. We're activley seeking contributions from DevOps, SecOps and Infrastructure Engineers who have strong opinions about security, privacy and civil liberties.

## Getting started (Users)
Docker is the only requirement to get started with Noteworthy.

```
$ bash <(curl -s get.noteworthy.im)
```
The above script will pull the `decentralabs/noteworthy:taproot-beta` Docker container and start the interactive installation process. You will need to request an invite to the public Decentralabs Hub if you are not planning on deploying your own Hub [as described here](https://noteworthy.tech/hub)

## Getting started (Developers)

Docker is used for development and deployment of the Noteworthy reference implementations. For now, Docker is the only officially supported deployment environment.

Drop into a development container to check out the  `notectl` command-line utility:

- Make sure Docker is installed
- Clone and `cd` into this repo
- Run the following:

```
$ make shell
```

## Build a Taproot Docker container:
```
make docker ROLE=taproot GIT_COMMIT=$(git rev-parse HEAD) RELEASE_TAG=dev
```

This will create the container `decentralabs/noteworthy:taproot-dev`

## Installation

At this time the `notectl` command-line utility is the primary interface for Noteworthy.

The best way to interact with `notectl` is by building a release container as described in the section above, then create then following Bash function in your `~/.bashrc`:
```
notectl-dev() {
	docker run -e NOTEWORTHY_DOMAIN=$NOTEWORTHY_DOMAIN --rm -it -v "/var/run/docker.sock:/var/run/docker.sock" decentralabs/noteworthy:taproot-dev "$@";
}
```

We recommend creating multiple Bash functions to manage interacting with the various release stages (prod, beta, dev etc) of Noteworthy.
The vanilla `notectl` is reserved for the current production release.

For example, build a `beta` release Taproot container:
```
make docker ROLE=taproot GIT_COMMIT=$(git rev-parse HEAD) RELEASE_TAG=beta
```
Then define the following Bash function wrapper:
```
notectl-beta() {
	docker run -e NOTEWORTHY_DOMAIN=$NOTEWORTHY_DOMAIN --rm -it -v "/var/run/docker.sock:/var/run/docker.sock" decentralabs/noteworthy:taproot-beta "$@";
}
```
You can then deploy and interact with networks/services using the `beta ` release with:
```
$ notectl-beta install
```


