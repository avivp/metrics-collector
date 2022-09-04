
## website monitor
System which monitors website availability over the network and produces metrics.

### setup
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


### How to run using docker
from root folder run:
> docker build -f src/producer/Dockerfile -t <producer_img_name> .

> docker run -d -e SSL_CAFILE_PATH="path" -e SSL_CERTFILE_PATH="path" -e SSL_KEYFILE_PATH="path"
    -v /<path without file name>:/<path without file name> <producer_img_name>


> > for mac use -v /Users:/Users

> docker build -f src/consumer/Dockerfile -t <consumer_img_name> .

> docker run -d -e SSL_CAFILE_PATH="path" -e SSL_CERTFILE_PATH="path" -e SSL_KEYFILE_PATH="path"
    -e DB_USER="some_key_id" -e DB_PASSWORD="some_secret"
    -v /<path without file name>:/<path without file name> <consumer_img_name>


> > for mac use -v /Users:/Users


### How to run unit tests
(Requires pytest installation)
> pytest test


## Service description
I designed this code with separation of concerns and extensibility in mind:
1) The service can be extended to collect metrics on other resources rather than websites.
For now I used a resource type in METRICS table but designing for separated METRICS tables is also valid.
2) Additional metrics data can be added to storage (this will require DB schema change, if you ask me if we can  avoid this I would say that initially i would use a NOSQL unstructured storage)
3) I used wrappers on top of Kafka and Postgresql to support both mocking and the ability to change the underlying technology (i.e. rabbitMQ or MySql or even NOSQL)
4) database and queue creations are done during deployment stage (in reality, deployment of course should include migrations and rollback plan).
5) I added basic retry mechanism to handle transient network issues, code running in distributed system should account for network failures.

## table schema
METRICS table
1) ID primary key
2) RESOURCE_NAME - for simplicity keeps the resource name. however should consider a foreign key table of resource names
  to reduce size of duplicated strings. VARCHAR (255) is enough for now as full domain name is up to 253 chars.
3) RESOURCE_TYPE - a foreign key for type table.
4) RESPONSE_TIME - metrics for response time (I did not add the word "http" to it as different resource might have different meaning for timing)
5) STATUS_CODE - metrics for status code
6) CONTENT - resource content, for website it is some text from the page.
7) CREATED_TIME_UTC - time when metrics was created in UTC to have all events normalized to same timeline.


## Feature clarifications
1) How to handle invalid website URL? for now decided no metrics will be published.
Also, URL should be removed from list of websites, since it is invalid there is no point in retrying it every time.
2) are www.hbo.com, http://hbo.com, hbo.com/en_fi are all the same ? I decided to normalize them all to hbo.com
3) should we publish metrics in case of error in pinging the website (e.g. timeout)? network errors dont really indicate metrics about the website hence i skip those.

## Design thoughts:
1) Which storage should we use relational DB or NOSQL?  how much data is expected to be stored? as postgresql is not known for scaling.
Also is there data retention policy (in which we could clear some storage).
2) Scaling - scaling a service by using threads, and scaling the system by adding nodes. That means both for services and DB connections.
3) Consider the optimal way to handle duplicated msgs on kafka stream which in turn might create duplicated metrics.



## Future improvements:
In attempt to box my efforts and nail the spirit on this exercise, i.e. high level design of how such system would work, I did not drill down to every aspect of the code nor tried to make it perfect.
Here are some improvement which I would address in real production code:
1) environment setup - the idea was to create the database if doesnt exist and also the kafka topic. For some reason database creation fails due to exisitng transaction (although such does not exist) and kafkaclient could not properly connect. These 2 issues requires some investigation which i thought was redundant as the main idea for this work is clear.
2) To scale our service we should add threads for publishing and reading the metrics. Most VMs come with a few cores, no reason not to take advantage of it.
Note that KafkaProducer is thread safe (sharing a single producer instance across threads will generally be faster than having multiple instances.)
However, KafkaConsumer is not thread safe and different threads should instantiate their own client. Can simulate consumer threads by using the same group id for all consumers.
If we use threads for process messages in parallel note that DB should support parallel connections and scale accordingly.
3) Consider sending messages and reading messages in batches. This will reduce the amount of requests to kafka, will remove load and reduce cost.
Need to measure and decide what would be the optimal batch size.
4) if URL is invalid i would remove it from the list as there's no point of retrying
5) For this exercise I didnt use Flask/Fastapi as for now the service doesnt expose APIs.