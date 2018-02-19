# From mdillon/postgis

The `mdillon/postgis` image provides a Docker container running Postgres 9 with [PostGIS 2.3](http://postgis.net/) installed. This image is based on the official [`postgres`](https://registry.hub.docker.com/_/postgres/) image and provides variants for each version of Postgres 9 supported by the base image (9.2-9.6).

## Usage

In order to run a basic container capable of serving a PostGIS-enabled database, start a container as follows:

    docker build . -t postgres && docker run -e POSTGRES_PASSWORD=mysecretpassword postgres

For more detailed instructions about how to start and control your Postgres container, see the documentation for the `postgres` image [here](https://registry.hub.docker.com/_/postgres/).
