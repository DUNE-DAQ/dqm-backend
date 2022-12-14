# OCI Container

The Containerfile here should be workable for building the application container.

For example:

```shell
buildah build -f Containerfile -t dunedaq/pocket-dqmdjango:XXXXXXXXX
buildah push dunedaq/pocket-dqmdjango:XXXXXXXXX oci:/tmp/oci_layout
buildah push dunedaq/pocket-dqmdjango:XXXXXXXXX docker-archive:/tmp/docker.tar
```
