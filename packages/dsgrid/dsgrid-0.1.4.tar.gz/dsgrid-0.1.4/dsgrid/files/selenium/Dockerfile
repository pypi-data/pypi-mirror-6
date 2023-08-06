FROM ubuntu:13.10

RUN apt-get update
RUN apt-get install -y software-properties-common python
RUN add-apt-repository ppa:webupd8team/java
RUN apt-get update
RUN echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections
RUN echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections
RUN apt-get install oracle-java7-installer -y
RUN wget https://selenium.googlecode.com/files/selenium-server-standalone-2.39.0.jar
CMD ["java", "-jar", "selenium-server-standalone-2.39.0.jar", "-role", "hub"]
