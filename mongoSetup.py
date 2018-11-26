from pymodm import MongoModel, fields, base


class Patient(MongoModel):
    ID = fields.FloatField(primary_key=True)
    attending_email = fields.CharField()
    age = fields.FloatField()
    heart_rates = fields.ListField(field=base.fields.
                                   MongoBaseField(blank=True))
    timestamps = fields.ListField(field=base.fields.
                                  MongoBaseField(blank=True))
