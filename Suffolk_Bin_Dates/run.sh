#!/usr/bin/with-contenv bashio

#Move into app folder setup by Dockerfile
cd /home/app

echo "---- Setting up Python VENV ----"
#Setup a persistent python virtual enviroment
VIRTUAL_ENV=/data/venv
python3 -m venv $VIRTUAL_ENV
PATH="$VIRTUAL_ENV/bin:$PATH"


#Install requirements, if not already present in the persistent venv
pip3 install -r requirements.txt

echo "---- VENV setup done ----"

#Run the main py script
python3 main.py