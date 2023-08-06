
## Build

```bash
sudo docker build -t="dsgrid/chrome" chrome # chrome is reference to this directory
```
## Usage
```bash
sudo dsgrid status
# Note Hub IP and add it to the environment variable for run command
sudo docker run -d -e GRID_IP=<IP> dsgrid/chrome /home/chrome/run.sh
```

## Problems

* Experiencing timeouts
* Older version of `selenium-server-standalone` jar
* Older version of `chromedriver`
*


## Credit

* Container Scripts - https://github.com/web-animations/web-animations-js/blob/master/.travis-setup.sh
