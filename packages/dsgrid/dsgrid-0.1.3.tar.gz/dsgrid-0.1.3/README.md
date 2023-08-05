# Docker Selenium Grid

CLI program for building and managing a Selenium Grid with Docker containers. Each browser node runs a single instance of the browser. I find this 
helpful when running Selenium tests in parallel.

[View the Demo](http://asciinema.org/a/5879) Installation and Usage on Ubuntu Raring with Vagrant

## Requirements

* Docker
* Python
* pip

## Installation

This installation will build the following Docker containers: Selenium Hub, PhantomJS, Chrome, and Firefox. Note: If you
want to customize the Dockerfiles, do so in `/usr/local/dsgrid/files` before running the install.

```bash
pip install dsgrid
dsgrid install
```

## Usage

Once installed you can start and manage a Selenium Grid. Example:

```
# Start the Hub
dsgrid start
# Add Nodes 
dsgrid nodes add firefox
dsgrid nodes add phantomjs
# Restart Nodes by Browser
dsgrid nodes restart firefox
# Restart All Nodes
dsgrid nodes restart
# Check Status
dsgrid status
# Shutdown
dsgrid shutdown
```

View the Grid console on: http://localhost:49044/grid/console

## Hacking

Feel free to hack the Dockerfiles and scripts under `files/`. Pull requests are welcomed.

## Author Note

I put this together over a weekend. I am not very strong in Python but wanted to build a CLI app which can be easily
installed on Docker hosts.

The tests are incomplete. What you see are my TDD leftovers.

## Special Thanks

* Yassine Jaffoo (Yas)

## Having Problems? Need Help?

**Author Email:** brady[at]vitrano.me or get my Gmail from the setup.py


