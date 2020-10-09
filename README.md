# Noteworthy

Noteworthy is an experimental distributed networking toolkit. It is similar to existing personal networking products such as ZeroTier and TailScale but is 100% community powered, free and open source software. 

Noteworthy's development is sponsored by Decentralabs LLC, a Wyoming based telecommuniations research and development firm that specializes in the development free and open source telecommunications infrastucture to enable a safe, free web.

# A Cost Gravity Accelerator
Noteworthy is an ambitious open source project that aims to lower the costs of designing, deploying, maintaning small-to-medium scale distributed overlay networks and the applications that run on top of them. It is not enough for Noteworthy to be open source. Technical complexity contributes substantially to an excessive cost of access.

Noteworthy tries to be as easy to use and understand as possible by being opinionated about defaults and things like deployment and orchestration. We're activley seeking contributions from DevOps, SecOps and Infrastructure engineers who also have strong opinions about security, privacy and the protection of digital freedoms.

# Getting started (Users)
Docker is the only requirement to get started with Noteworthy.

```
$ bash <(curl -s get.noteworthy.im)
```
The above script will pull the `decentralabs/noteworthy` Docker container and launch your default browser to a locally hosted on-boarding wizard.

# Getting started (Developers)

Docker is used for development and deployment of the Noteworthy reference implementations. For now, Docker is the only officially supported deployment environment but support is planned for vanilla linux containers and containerd K3S

Drop into a development container to play around with the `notectl` command-line utility

- Make sure Docker is installed
- Clone and `cd` into this repo
- Run the following:

```
$ make shell
```







