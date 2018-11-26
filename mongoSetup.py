from pymodm import connect
from pymodm import MongoModel, fields

connect("mongodb://abg28:GODUKE10@ds225253.mlab.com:25253/bme590")


class Patient(MongoModel):
    ID = fields.FloatField(primary_key=True)
    attending_email = fields.CharField()
    age = fields.FloatField()
    heart_rates = fields.ListField()
    timestamps = fields.ListField()
