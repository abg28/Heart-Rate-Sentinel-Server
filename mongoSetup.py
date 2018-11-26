from pymodm import MongoModel, fields


class Patient(MongoModel):
    ID = fields.IntegerField(primary_key=True)
    attending_email = fields.CharField()
    age = fields.FloatField()
    heart_rates = fields.ListField()
    timestamps = fields.ListField()
