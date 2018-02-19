# mdillon/postgis

https://travis-ci.org/appropriate/docker-postgis)

The `mdillon/postgis` image provides a Docker container running Postgres 9 with [PostGIS 2.3](http://postgis.net/) installed. This image is based on the official [`postgres`](https://registry.hub.docker.com/_/postgres/) image and provides variants for each version of Postgres 9 supported by the base image (9.2-9.6).

This image ensures that the default database created by the parent `postgres` image will have the following extensions installed:

* `postgis`
* `postgis_topology`
* `fuzzystrmatch`
* `postgis_tiger_geocoder`

Unless `-e POSTGRES_DB` is passed to the container at startup time, this database will be named after the admin user (either `postgres` or the user specified with `-e POSTGRES_USER`). If you would prefer to use the older template database mechanism for enabling PostGIS, the image also provides a PostGIS-enabled template database called `template_postgis`.

## Usage

In order to run a basic container capable of serving a PostGIS-enabled database, start a container as follows:

    docker build . -t postgis && docker run -e POSTGRES_PASSWORD=mysecretpassword postgis

For more detailed instructions about how to start and control your Postgres container, see the documentation for the `postgres` image [here](https://registry.hub.docker.com/_/postgres/).

Once you have started a database container, you can then connect to the database as follows:

    docker run -it --link some-postgis:postgres --rm postgres \
        sh -c 'exec psql -h "$POSTGRES_PORT_5432_TCP_ADDR" -p "$POSTGRES_PORT_5432_TCP_PORT" -U postgres'

See [the PostGIS documentation](http://postgis.net/docs/postgis_installation.html#create_new_db_extensions) for more details on your options for creating and using a spatially-enabled database.

## Known Issues / Errors

When You encouter errors due to PostGIS update `OperationalError: could not access file "$libdir/postgis-X.X`, run:

`docker exec some-postgis update-postgis.sh`

It will update to Your newest PostGIS. Update is idempotent, so it won't hurt when You run it more than once, You will get notification like:


## Insert images paths in PostGreSQL

docker exec -it postgis /bin/bash && cd /scripts/ && python add_products_to_postgis.py -f /images/Images/


python delete_geotiff_from_database.py -s 2017-01-01T01:02:03 -e 2017-02-02T02:03:04
