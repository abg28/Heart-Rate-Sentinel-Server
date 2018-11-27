# Heart-Rate-Sentinel-Server
Author: Alex Guevara (GitHub username/Duke netID: abg28)
Version: 1.0.0 
Release Date: 11/27/18

# Summary
This repository houses software for a Flask web server that supports storage and retrieval of cardiac patient data.  The server implements a RESTful API with the following endpoints:

* POST /api/new_patient --> initializes a patient's data
* POST /api/heart_rate --> adds a heart rate measurement
* POST /api/heart_rate/interval_average --> gets a patient's average heart rate over a specified interval
* GET /api/status/<patient_id> --> determines whether or not a patient is tachycardic
* GET /api/heart_rate/<patient_id> --> gets every previous heart rate measurement for a patient
* GET /api/heart_rate/average/<patient_id> --> gets a patient's average heart rate

The Flask server runs with the address http://vcm-7291.vm.duke.edu:5000 on port 5000 of a VM supplied by Duke University OIT's Virtual Computing Manager.  This project also uses a Mongo database hosted by mlab.  It is accessed in the code through the pymodm module, which allows for storage of the patient's data in a MongoModel child class, named "Patient".

The repository contains several files:

* sentinelMain.py --> Python file that contains all of the executable code, server endpoints, and functions
* testSentinelMain.py --> Python file that contains the unit tests for each function (except for the endpoints)
* app.log --> Text file to which the Flask server's built-in logger outputs important messages about the program during runtime (will be added to during each execution of sentinelMain.py)
* example.py --> Python file to demonstrate use of the server endpoints through the requests module (more info on this in the section below)
* mongoSetup.py --> Python file that houses the "Patient" class, which is used for exchanging patient data with the Mongo server
* .travis.yml --> Yaml file that specifies how Travis CI should run its integration tests
* requirements.txt --> Text file that lists the required packages to be installed in a user's virtual environment, should they fork and/or clone this repository
* LICENSE --> Text file housing this software's MIT license

# Instructions for Use
The Flask server is set to constantly run on the VM, such that a user need only type in the server's http address into a browser bar, along with the tag of the desired endpoint.  See the VM's server address in the section above.  For the POST methods, requests must be made.  This can be done through any desired method ("requests" package in Python, curl, etc.).  See the endpoints' documentation for details on how to format requests.

The file "example.py" in this repository shows several examples of the "request" package being used to input properly-formatted JSON's to the POST endpoints.  Note that this file sends requests to the local address "0.0.0.0:5000", such that the user would need to run the file "sentinelMain.py" on his/her local machine to set up their own instance of the Flask server.  This acts as a useful sandbox mode.  The user must set up a Python3.6 virtual environment and install the packages in this repository's "requirements.txt" in order to use this method.

# How it Works
The file "sentinelMain.py" has been run on the VM such that the Flask server has been initialized with its endpoints, and is constantly running on the remote VM address.  Each endpoint communicates with the Mongo database hosted on mlab.  When a new patient is initialized through the /api/new_patient endpoint, an instance of the "Patient" class is saved to the database with fields for the patient's ID number, attending physician's email address, and age.  Two lists for heart rate measurements and corresponding timestamps, respectively, are also initialized with the placeholder String literal "begin"; this was done so that Mongo would not raise a ValidationError due to empty lists.  Once a heart rate measurement is added for that patient through the /api/heart_rate endpoint, "begin" is replaced in both lists with the proper values related to the measurement.  A patient's tachycardic status is determined by the endpoint /api/status/<patient_id> according to his/her age (https://en.wikipedia.org/wiki/Tachycardia).  The remaining three endpoints are achieved through simple retrieval calls and minimal logic (averaging and list splicing).

# Limitations
Note that the current build omits any implementation of the SendGrid API.  While this was originally intended to be used to send warning emails to a patient's physician when he/she became tachycardic, there were difficulties integrating this functionality into the code.  This will be rectified in a future release.

# Travis Build Status Indicator (branch master)
[![Build Status](https://travis-ci.org/abg28/Heart-Rate-Sentinel-Server.svg?branch=master)](https://travis-ci.org/abg28/Heart-Rate-Sentinel-Server)
