FROM ubuntu:13.10

RUN apt-get update
RUN echo "deb http://security.ubuntu.com/ubuntu precise-security main" >> /etc/apt/sources.list
RUN apt-get install -y software-properties-common python unzip libnss3 libgconf-2-4
RUN add-apt-repository ppa:webupd8team/java
RUN apt-get update
RUN echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections
RUN echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections
RUN apt-get install oracle-java7-installer -y
RUN wget https://selenium.googlecode.com/files/selenium-server-standalone-2.39.0.jar
#RUN wget https://chromedriver.storage.googleapis.com/2.8/chromedriver_linux64.zip
#RUN unzip chromedriver_linux64.zip && rm chromedriver_linux64.zip && mv chromedriver /usr/bin && chmod 755 /usr/bin/chromedriver
RUN wget https://chromedriver.googlecode.com/files/chromedriver_linux64_2.3.zip
RUN unzip chromedriver_linux64_2.3.zip && rm chromedriver_linux64_2.3.zip && mv chromedriver /usr/bin && chmod 755 /usr/bin/chromedriver
RUN apt-get install xvfb dbus-x11 -y
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg --install google-chrome-stable_current_amd64.deb || apt-get -f install -y
RUN rm -f /opt/google/chrome/chrome-sandbox
RUN wget https://googledrive.com/host/0B5VlNZ_Rvdw6NTJoZDBSVy1ZdkE -O /opt/google/chrome/chrome-sandbox
RUN chown root:root /opt/google/chrome/chrome-sandbox && chmod 4755 /opt/google/chrome/chrome-sandbox && md5sum /opt/google/chrome/chrome-sandbox
RUN useradd chrome -m -s /bin/bash && mv /selenium-server-standalone-2.39.0.jar /home/chrome && chown chrome:chrome /home/chrome/selenium-server-standalone-2.39.0.jar
RUN mkdir /.pki && chown chrome:chrome /.pki && mkdir /.local && chown chrome:chrome /.local
#USER chrome
WORKDIR /home/chrome
ADD run.sh /home/chrome/run.sh
RUN chmod 755 /home/chrome/run.sh
CMD ["/bin/bash", "/home/chrome/run.sh"]
