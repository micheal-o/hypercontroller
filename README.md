Hypercontroller is used for running multiple instances of pox to manage different
segments of the same network, which is not originally supported by openflow or pox.
Now instead of using the openflow standard of running using one controller to manage
our entire network, we

Note:
    - Support for hypercontroller has been added to openflow.discovery code without breaking existing
      functionalities, and it can still work normally if it is run without hypercontroller.

    - Apache Kafka is a distributed stream processing system. It is used for data streaming/messaging
      among the controllers.

Network:
    Apache Kafka server <------------------> Pox controller 1
                        <------------------> Pox controller 2
                        <------------------> Pox controller 3
                                                :
                        <------------------> Pox controller N
Mininet setup:
    - In mininet, all controllers can run on the mininet VM using different ports.
    - Install required libraries using 'pip install kafka-python' on mininet VM

Apache Kafka setup:
    - You can run kafka on the host machine or on mininet VM or on another VM. Whatever you
      choose, should be connected to the controllers (i.e Mininet VM). Ping to test connection.
    - Follow the link below to install Kafka on ubuntu machine:
    https://www.digitalocean.com/community/tutorials/how-to-install-apache-kafka-on-ubuntu-14-04
    - If running Kafka on a separate machine, ensure Kafka is listening on a reachable ip address not
      localhost.
