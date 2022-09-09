
## website monitor
System which monitors website availability over the network and produces metrics.
website metrics are stored in kafka by a producer service and read and store to Postgresql DB by consumer service.

### Setup
> make sure your postgresql service has a table called ANALYTICS

> make sure your kafka service has topic called 'test'

> update src/common/configuration.ini file with the host and port for your Kafka and Postgresql services.

set up environment variables for secretive data
> export DB_USER=usr

> export DB_PASSWORD=pwd

> export SSL_CAFILE_PATH=path

> export SSL_CERTFILE_PATH=path

> export SSL_KEYFILE_PATH=path


setup environment is only required once (but can be executed many times)
This will install packages and setup the database:
> run from root folder:  bash initial_setup.sh 


### How to run using python
python assuming python3

> python src/producer/main.py

> python src/consumer/main.py


### How to run using docker compose
In root directory create a ".env" file with the following env vars and secrative values:
> DB_USER=

> DB_PASSWORD=

> SSL_CAFILE_PATH=

> SSL_CERTFILE_PATH=

> SSL_KEYFILE_PATH=

> LOCAL_PATH=

> APP_PATH=

LOCAL_PATH and APP_PATH are for mounting host working directory to the app's so the container knows where to look for ssl files. In macOS you can use LOCAL_PATH=/Users and APP_PATH=/Users


To start docker compose:
> docker-compose up -d

To stop docker compose
> docker-compose down


### How to run using docker
from root folder run:
> docker build -f src/producer/Dockerfile -t <producer_img_name> .

> docker run -d -e SSL_CAFILE_PATH="path" -e SSL_CERTFILE_PATH="path" -e SSL_KEYFILE_PATH="path"
    -v /host-directory:/app-directory <producer_img_name>


> docker build -f src/consumer/Dockerfile -t <consumer_img_name> .

> docker run -d -e SSL_CAFILE_PATH="path" -e SSL_CERTFILE_PATH="path" -e SSL_KEYFILE_PATH="path"
    -e DB_USER="some_key_id" -e DB_PASSWORD="some_secret"
    -v /host-directory:/app-directory <consumer_img_name>


Mounting host working directory to the app's to indicate the physical location of ssl files:
> > for macOS use -v /Users:/Users


### How to run unit tests
(Requires pytest installation)
> pytest test

