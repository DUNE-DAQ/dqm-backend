# DQM Backend
Backend of the Data Quality Monitoring. Web based display and analysis tools
for Data Quality Assessment

# Web display installation
## Prerequisites
### Docker
A docker container running redis is needed, for that install docker and then run
```
docker pull redis:4
docker run -p 6379:6379 -d redis
```
### Python version
The web display has only been tested on recent python versions so it is recommended to 
set up a DUNEDAQ working area with a recent nightly and run the web server from there.

## Installation
Temporarily, copy the `Web` repository from a working location in np04 since it contains one of the 

To install for the first time run:
```
./make_env
./prepare_dqm
```

When using the `prepare_dqm` script, it is possible to change the port by changing by changing the last line to:
```
./manage.py runserver --nostatic 0.0.0.0:PORT
```
## Running
After it has been installed for the first time it's not necessary to run those scripts again.
One should remember to set up the workarea if the web display has been installed from one. There will
There are two parts running, the first one is the script that receives the data from kafka, saves it and is used to trigger the updates in the web display. Run:
```
python dqm/manage.py shell < scripts/consumer.python
```
and leave the terminal open (for example using a tmux session). The second part is the web display itself. Run:
```
python dqm/manage.py runserver 0.0.0.0:PORT
```
where PORT can be changed. The address can be ommitted and by default it will run on `127.0.0.1:8050`
