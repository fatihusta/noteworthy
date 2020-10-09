# Noteworthy

Noteworthy is an experimental distributed networking toolkit. It is similar to existing personal networking products such as ZeroTier and TailScale but is 100% community powered, free and open source software. 

Noteworthy's development is sponsored by Decentralabs LLC, a Wyoming based telecommuniations research and development firm that specializes in the development free and open source telecommunications infrastucture.

# A Cost Gravity Accelerator
Noteworthy is an ambitious open source project that aims to lower the costs of designing, deploying, maintaning trusted distributed overlay networks and the applications that run on top of them. It is not enough for Noteworthy to be open source, technical complexity contributes substantially to the excessive cost of access.
Because of this, Noteworthy aims to be as simple and easy to use and understand as possible. We're activley seeking contributions from DevOps, SecOps and Infrastructure Engineers who have strong opinions about security, privacy and civil liberties.

# Getting started (Users)
Docker is the only requirement to get started with Noteworthy.

```
$ bash <(curl -s get.noteworthy.im)
```
The above script will pull the `decentralabs/noteworthy` Docker container and launch your default browser to a locally hosted on-boarding wizard.

# Getting started (Developers)

Docker is used for development and deployment of the Noteworthy reference implementations. For now, Docker is the only officially supported deployment environment but support is planned for vanilla linux containers and K3S as deployment targets.

Drop into a development container to check out the  `notectl` command-line utility:

- Make sure Docker is installed
- Clone and `cd` into this repo
- Run the following:

```
$ make shell
```







