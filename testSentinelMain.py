import pytest


def test_check_patient_data():
    """ Tests the function "check_patient_data" from sentinelMain.py

    :return: Passes if inputs to check_patient_data validated properly, fails
    o.w.
    """
    from sentinelMain import check_patient_data

    # No errors
    case1 = {"patient_id": 3,
             "attending_email": "abg28@duke.edu",
             "user_age": 10
             }
    assert(check_patient_data(case1)["patient_id"] ==
           pytest.approx(case1["patient_id"]))
    assert(check_patient_data(case1)["attending_email"] ==
           case1["attending_email"])
    assert(check_patient_data(case1)["user_age"] ==
           pytest.approx(case1["user_age"]))

    # Key missing
    case2 = {"attending_email": "abg28@duke.edu",
             "user_age": 10
             }
    with pytest.raises(KeyError):
        check_patient_data(case2)

    # Strings parseable as floats
    case3 = {"patient_id": "3",
             "attending_email": "abg28@duke.edu",
             "user_age": "4",
             }
    assert(check_patient_data(case3)["patient_id"] ==
           pytest.approx(case3["patient_id"]))
    assert(check_patient_data(case3)["attending_email"] ==
           case3["attending_email"])
    assert(check_patient_data(case3)["user_age"] ==
           pytest.approx(case3["user_age"]))

    # Non-float entries
    case4 = {"patient_id": True,
             "attending_email": "abg28@duke.edu",
             "user_age": "asdfg",
             }
    with pytest.raises(ValueError):
        check_patient_data(case4)

    # Empty entries
    case5 = {"patient_id": None,
             "attending_email": None,
             "user_age": None,
             }
    with pytest.raises(ValueError):
        check_patient_data(case5)

    # Non-String type
    case6 = {"patient_id": 3,
             "attending_email": 24,
             "user_age": 10,
             }
    with pytest.raises(TypeError):
        check_patient_data(case6)

    # Invalid email
    case7 = {"patient_id": 3,
             "attending_email": "alexdukeedu",
             "user_age": 10,
             }
    with pytest.raises(ValueError):
        check_patient_data(case7)

    # Negative age
    case8 = {"patient_id": 3,
             "attending_email": "abg28@duke.edu",
             "user_age": -999,
             }
    with pytest.raises(ValueError):
        check_patient_data(case8)


def test_check_heart_rate():
    """ Tests the function "check_heart_rate" from sentinelMain.py

    :return: Passes if inputs to check_heart_rate validated properly, fails
    o.w.
    """
    from sentinelMain import check_heart_rate

    # No errors
    case1 = {"patient_id": 3,
             "heart_rate": 150.8,
             }
    assert(check_heart_rate(case1)["patient_id"] ==
           pytest.approx(case1["patient_id"]))
    assert(check_heart_rate(case1)["heart_rate"] ==
           pytest.approx(case1["heart_rate"]))

    # Key missing
    case2 = {"patient_id": 4
             }
    with pytest.raises(KeyError):
        check_heart_rate(case2)

    # Strings parseable as floats
    case3 = {"patient_id": "3",
             "heart_rate": "150.8",
             }
    assert(check_heart_rate(case3)["patient_id"] ==
           pytest.approx(case3["patient_id"]))
    assert(check_heart_rate(case3)["heart_rate"] ==
           pytest.approx(case3["heart_rate"]))

    # Non-float entries
    case4 = {"patient_id": True,
             "heart_rate": "asdfg",
             }
    with pytest.raises(ValueError):
        check_heart_rate(case4)

    # Empty entries
    case5 = {"patient_id": None,
             "heart_rate": None,
             }
    with pytest.raises(ValueError):
        check_heart_rate(case5)

    # Negative heart rate
    case6 = {"patient_id": 3,
             "heart_rate": -999,
             }
    with pytest.raises(ValueError):
        check_heart_rate(case6)


def test_check_avg_request_dict():
    """ Tests the function "check_avg_request_dict" from sentinelMain.py

    :return: Passes if inputs to check_avg_request_dict are validated
    properly, fails o.w.
    """
    from sentinelMain import check_avg_request_dict

    # No errors
    case1 = {"patient_id": 3,
             "heart_rate_average_since": "2018-03-09 11:00:36.372339"
             }
    assert(check_avg_request_dict(case1)["patient_id"] ==
           pytest.approx(case1["patient_id"]))
    assert(check_avg_request_dict(case1)["heart_rate_average_since"] ==
           case1["heart_rate_average_since"])

    # Key missing
    case2 = {"patient_id": 3
             }
    with pytest.raises(KeyError):
        check_avg_request_dict(case2)

    # Strings parseable as floats
    case3 = {"patient_id": "3",
             "heart_rate_average_since": "2018-03-09 11:00:36.372339"
             }
    assert(check_avg_request_dict(case3)["patient_id"] ==
           pytest.approx(case3["patient_id"]))
    assert(check_avg_request_dict(case3)["heart_rate_average_since"] ==
           case3["heart_rate_average_since"])

    # Non-float entries
    case4 = {"patient_id": True,
             "heart_rate_average_since": "2018-03-09 11:00:36.372339"
             }
    with pytest.raises(ValueError):
        check_avg_request_dict(case4)

    # Empty entries
    case5 = {"patient_id": None,
             "heart_rate_average_since": None
             }
    with pytest.raises(ValueError):
        check_avg_request_dict(case5)

    # Non-String type
    case6 = {"patient_id": 3,
             "heart_rate_average_since": 1234567
             }
    with pytest.raises(TypeError):
        check_avg_request_dict(case6)

    # Invalid timestamp
    case7 = {"patient_id": 3,
             "heart_rate_average_since": "20180309 110036372339"
             }
    with pytest.raises(ValueError):
        check_avg_request_dict(case7)


@pytest.mark.parametrize("heart_rate,age,expected", [
    (150, 1 / 365, False),
    (150, 3 / 365, False),
    (150, 7 / 365, False),
    (150, 28 / 365, False),
    (150, 90 / 365, False),
    (150, 150 / 365, False),
    (150, 1, False),
    (150, 3, True),
    (150, 5, True),
    (150, 8, True),
    (150, 12, True),
    (150, 100, True),
])
def test_is_tachycardic(heart_rate, age, expected):
    """ Tests the function "is_tachycardic" from sentinelMain.py

    :param heart_rate: Inputted heart rate (float)
    :param age: Inputted patient age (float)
    :param expected: Expected output (True or False)
    :return: Passes if heart rates correctly classified as tachycardic, fails
    o.w.
    """
    from sentinelMain import is_tachycardic
    assert is_tachycardic(heart_rate, age) == expected
