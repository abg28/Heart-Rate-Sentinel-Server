# IMPORTS
from flask import Flask, jsonify, request
import logging.handlers
import datetime
from mongoSetup import Patient
from pymodm import errors
from pymodm import connect

# FLASK SERVER SETUP
app = Flask(__name__)
formatter = logging.Formatter(
    "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
handler = logging.handlers.RotatingFileHandler(
        'app.log',
        maxBytes=1024 * 1024)
handler.setFormatter(formatter)
handler.setLevel("DEBUG")
app.logger.addHandler(handler)


# SERVER ENDPOINTS
@app.route("/api/new_patient", methods=["POST"])
def post_new_patient():
    """ Registers a new patient with the server, and allows for future heart
    rate measurements from the patient.  The JSON request received should be a
    dictionary with the following key-value pairs:
        "patient_id" : float representing patient's ID number
        "attending_email" : String representing attending physician's email
        "user_age" : float representing patient's age in years

    :return: A tuple of length 2.  The second entry is always the HTTP status
    code.  If no errors raised, the first entry is a patient data dictionary
    serialized as JSON, containing patient ID, attending physician's email,
    and patient's age.  Otherwise, it is an error message serialized as JSON.
    """
    patient_data = request.get_json()
    try:
        cleared_patient_data = check_patient_data(patient_data)
    except KeyError:
        return jsonify("Error 400: Patient data dictionary missing keys."), 400
    except ValueError:
        return jsonify("Error 400: Invalid entry in patient data dict."), 400
    except TypeError:
        return jsonify("Error 400: Attending email not of type String."), 400
    patient = Patient(cleared_patient_data["patient_id"],
                      attending_email=cleared_patient_data["attending_email"],
                      age=cleared_patient_data["user_age"],
                      heart_rates=[],
                      timestamps=[])
    patient.save()
    return jsonify(cleared_patient_data), 200


@app.route("/api/heart_rate", methods=["POST"])
def post_heart_rate():
    """ Posts a patient's heart rate to the server along with his/her ID.  The
    JSON request received should be a dictionary with the following key-value
    pairs:
        "patient_id" : float representing patient's ID number
        "heart_rate" : float representing current heart rate measurement

    :return: A tuple of length 2.  The second entry is always the HTTP status
    code.  If no errors raised, the first entry is a patient data dictionary
    serialized as JSON, containing patient ID, heart rate, and timestamp.
    Otherwise, it is an error message serialized as JSON.
    """
    heart_rate = request.get_json()
    try:
        cleared_heart_rate = check_heart_rate(heart_rate)
        cleared_heart_rate["timestamp"] = datetime.datetime.now()
    except KeyError:
        return jsonify("Error 400: Patient data dictionary missing keys."), 400
    except ValueError:
        return jsonify("Error 400: Invalid entry in patient data dict."), 400
    try:
        patient = Patient.objects.raw({"_id": cleared_heart_rate["patient_id"]
                                       }).first()
    except errors.DoesNotExist:
        return jsonify("Error 404: Patient with the requested ID does not "
                       "exist."), 404
    hrs = patient.heart_rates
    hrs.append(cleared_heart_rate["heart_rate"])
    patient.heart_rates = hrs
    tss = patient.timestamps
    tss.append(cleared_heart_rate["timestamp"])
    patient.timestamps = tss
    patient.save()
    return jsonify(cleared_heart_rate), 200


@app.route("/api/status/<patient_id>", methods=["GET"])
def get_status(patient_id):
    """ Returns whether the patient is currently tachycardic based on the
    previously available heart rate, as well as a timestamp of the most recent
    heart rate.

    :param patient_id: The patient's ID number
    :return: A tuple of length 2.  The second entry is always the HTTP status
    code.  If no errors raised, the first entry is a patient data dictionary
    serialized as JSON, containing a String detailing whether or not the
    patient's heart rate is tachycardic and a String representing a timestamp
    of the most recent measurement. Otherwise, it is an error message
    serialized as JSON.
    """
    try:
        patient = Patient.objects.raw({"_id": patient_id}).first()
    except errors.DoesNotExist:
        return jsonify("Error 404: Patient with the requested ID does not "
                       "exist."), 404
    try:
        hrs = patient.heart_rates
        newest_hr = hrs[len(hrs)-1]
        tss = patient.timestamps
        newest_timestamp = tss[len(tss)-1]
    except IndexError:
        return jsonify("Error 400: No heart rates have been entered yet."), 400
    age = patient.age
    status = is_tachycardic(newest_hr, age)
    return jsonify({"Tachycardia status": status,
                    "Timestamp": newest_timestamp}), 200


@app.route("/api/heart_rate/<patient_id>", methods=["GET"])
def get_heart_rates(patient_id):
    """ Returns all previous heart rate measurements for the patient.

    :param patient_id: The patient's ID number
    :return: A tuple of length 2.  The second entry is always the HTTP status
    code.  If no errors raised, the first entry is a list of heart rates
    serialized as JSON.  Otherwise, it is an error message serialized as JSON.
    """
    try:
        patient = Patient.objects.raw({"_id": patient_id}).first()
    except errors.DoesNotExist:
        return jsonify("Error 404: Patient with the requested ID does not "
                       "exist."), 404
    return jsonify(patient.heart_rates), 200


@app.route("/api/heart_rate/average/<patient_id>", methods=["GET"])
def get_heart_rate_avg(patient_id):
    """ Returns the average of all previous heart rate measurements for the
    patient.

    :param patient_id: The patient's ID number
    :return: A tuple of length 2.  The second entry is always the HTTP status
    code.  If no errors raised, the first entry is a float representing the
    average of the patient's past HR measurements, serialized as JSON.
    Otherwise, it is an error message serialized as JSON.
    """
    try:
        patient = Patient.objects.raw({"_id": patient_id}).first()
    except errors.DoesNotExist:
        return jsonify("Error 404: Patient with the requested ID does not "
                       "exist."), 404
    try:
        hrs = patient.heart_rates
        avg_hr = sum(hrs)/len(hrs)
    except ZeroDivisionError:
        return jsonify("Error 400: No heart rates have been entered yet."), 400
    return jsonify(avg_hr), 200


@app.route("/api/heart_rate/interval_average", methods=["POST"])
def get_heart_rate_interval_avg():
    """ Returns the average of all previous heart rate measurements for the
    patient from the inputted timestamp onwards.  The JSON request received
    should be a dictionary with the following key-value pairs:
        "patient_id" : float representing patient's ID number
        "heart_rate_average_since" : String representing timestamp

    :return: A tuple of length 2.  The second entry is always the HTTP status
    code.  If no errors raised, the first entry is a float representing the
    average of the patient's past HR measurements in the specified interval,
    serialized as JSON.  Otherwise, it is an error message serialized as JSON.
    """
    avg_request_dict = request.get_json()
    cleared = check_avg_request_dict(avg_request_dict)
    try:
        patient = Patient.objects.raw({"_id": cleared["patient_id"]}).first()
    except errors.DoesNotExist:
        return jsonify("Error 404: Patient with the requested ID does not "
                       "exist."), 404
    start_index = 0
    try:
        for index, ts in enumerate(patient.timestamps):
            if ts < cleared["heart_rate_average_since"]:
                start_index = index
                break
        hrs = patient.heart_rates[start_index:]
        avg_hr = sum(hrs)/len(hrs)
    except ZeroDivisionError:
        return jsonify("Error 400: No heart rates have been entered yet."), 400
    except IndexError:
        return jsonify("Error 400: No heart rates have been entered yet."), 400
    return jsonify(avg_hr), 200


# HELPER FUNCTIONS
def check_patient_data(patient_data):
    """ Checks to see that the input for the /api/new_patient endpoint is
    valid, i.e. a dictionary with the correct key-value pairs and types.

    :param patient_data: The inputted patient data
    :return: The input, if no exceptions are thrown
    """

    if "patient_id" not in patient_data or "attending_email" not in \
            patient_data or "user_age" not in patient_data:
        app.logger.error("A key is missing from the patient data dictionary.")
        raise KeyError

    if None in patient_data.values():
        app.logger.error("One of the fields is empty.")
        raise ValueError

    for value in patient_data.values():
        if type(value) == bool:
            app.logger.error("Boolean detected where it shouldn't be.")
            raise ValueError

    patient_id = float(patient_data["patient_id"])
    if type(patient_id) != float:
        app.logger.error("Patient ID not a number")
        raise ValueError

    if type(patient_data["attending_email"]) != str:
        app.logger.error("Attending email not a String")
        raise TypeError

    if "@" not in patient_data["attending_email"] or "." not in \
            patient_data["attending_email"]:
        app.logger.error("Email address missing a special character "
                         "('@' or '.')")
        raise ValueError

    patient_age = float(patient_data["user_age"])
    if type(patient_age) != float:
        app.logger.error("Patient age not a number")
        raise ValueError

    if patient_age < 0:
        app.logger.error("Patient age invalid")
        raise ValueError

    try:
        if len(patient_data) > 3:
            raise ValueError
    except ValueError:
        app.logger.warning("Too many keys in dictionary.  Check user input to "
                           "save space.")

    patient_data["patient_id"] = patient_id
    patient_data["user_age"] = patient_age
    return patient_data


def check_heart_rate(patient_data):
    """ Checks to see that the input for the /api/heart_rate endpoint is
    valid, i.e. a dictionary with the correct key-value pairs and types.

    :param patient_data: The inputted patient data
    :return: The input, if no exceptions are thrown
    """

    if "patient_id" not in patient_data or "heart_rate" not in \
            patient_data:
        app.logger.error("A key is missing from the patient data dictionary.")
        raise KeyError

    if None in patient_data.values():
        app.logger.error("One of the fields is empty.")
        raise ValueError

    for value in patient_data.values():
        if type(value) == bool:
            app.logger.error("Boolean detected where it shouldn't be.")
            raise ValueError

    patient_id = float(patient_data["patient_id"])
    if type(patient_id) != float:
        app.logger.error("Patient ID not a number")
        raise ValueError

    heart_rate = float(patient_data["heart_rate"])
    if type(heart_rate) != float:
        app.logger.error("Heart rate not a number")
        raise ValueError

    if heart_rate < 0:
        app.logger.error("Invalid heart rate")
        raise ValueError

    try:
        if len(patient_data) > 2:
            raise ValueError
    except ValueError:
        app.logger.warning("Too many keys in dictionary.  Check user input to "
                           "save space.")

    patient_data["patient_id"] = patient_id
    patient_data["heart_rate"] = heart_rate
    return patient_data


def check_avg_request_dict(patient_data):
    """ Checks to see that the input for the /api/heart_rate/interval_average
    endpoint is valid, i.e. a dictionary with the correct key-value pairs and
    types.

    :param patient_data: The inputted patient data
    :return: The input, if no exceptions are thrown
    """

    if "patient_id" not in patient_data or "heart_rate_average_since" not in \
            patient_data:
        app.logger.error("A key is missing from the patient data dictionary.")
        raise KeyError

    if None in patient_data.values():
        app.logger.error("One of the fields is empty.")
        raise ValueError

    for value in patient_data.values():
        if type(value) == bool:
            app.logger.error("Boolean detected where it shouldn't be.")
            raise ValueError

    patient_id = float(patient_data["patient_id"])
    if type(patient_id) != float:
        app.logger.error("Patient ID not a number")
        raise ValueError

    if type(patient_data["heart_rate_average_since"]) != str:
        app.logger.error("Timestamp not a String")
        raise TypeError

    if "-" not in patient_data["heart_rate_average_since"] or \
            ":" not in patient_data["heart_rate_average_since"] or \
            "." not in patient_data["heart_rate_average_since"]:
        app.logger.error("Timestamp not correctly formatted")
        raise ValueError

    try:
        if len(patient_data) > 2:
            raise ValueError
    except ValueError:
        app.logger.warning("Too many keys in dictionary.  Check user input to "
                           "save space.")

    patient_data["patient_id"] = patient_id
    return patient_data


def is_tachycardic(heart_rate, age):
    """ Checks to see if a patient's heart rate is tachycardic based on
    his/her age.

    :param heart_rate: Float representing the patient's heart rate
    :param age: Float representing the patient's age in years
    :return: Boolean representing tachycardia status of patient
    """
    if 1/365 <= age < 3/365:
        if heart_rate > 159:
            return True
        else:
            return False
    elif 3/365 <= age < 7/365:
        if heart_rate > 166:
            return True
        else:
            return False
    elif 7/365 <= age < 28/365:
        if heart_rate > 182:
            return True
        else:
            return False
    elif 28/365 <= age < 90/365:
        if heart_rate > 179:
            return True
        else:
            return False
    elif 90/365 <= age < 150/365:
        if heart_rate > 186:
            return True
        else:
            return False
    elif 150/365 <= age < 1:
        if heart_rate > 169:
            return True
        else:
            return False
    elif 1 <= age < 3:
        if heart_rate > 151:
            return True
        else:
            return False
    elif 3 <= age < 5:
        if heart_rate > 137:
            return True
        else:
            return False
    elif 5 <= age < 8:
        if heart_rate > 133:
            return True
        else:
            return False
    elif 8 <= age < 12:
        if heart_rate > 130:
            return True
        else:
            return False
    elif 12 <= age < 16:
        if heart_rate > 119:
            return True
        else:
            return False
    else:
        if heart_rate > 100:
            return True
        else:
            return False


# INSTRUCTIONS FOR CALLING DRIVER
if __name__ == "__main__":
    connect("mongodb://abg28:GODUKE10@ds225253.mlab.com:25253/bme590")
    app.run(host="0.0.0.0")

