from django.db import models

from readings import choices as readings_choices


class DateLocationMeasurementModel(models.Model):
    """
    Abstract base class for PressureNET measurements.
    """
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    user_id = models.CharField(max_length=255, db_index=True)
    latitude = models.FloatField(db_index=True)
    longitude = models.FloatField(db_index=True)
    altitude = models.FloatField(default=0.0)
    daterecorded = models.BigIntegerField(db_index=True)
    tzoffset = models.BigIntegerField()
    client_key = models.CharField(max_length=255)
    sharing = models.CharField(max_length=255, choices=readings_choices.SHARING_CHOICES)
    provider = models.CharField(max_length=255, default='')

    class Meta:
        abstract = True


class Reading(DateLocationMeasurementModel):
    """
    Barometer reading from pressureNET
    """
    reading = models.FloatField()
    reading_accuracy = models.FloatField()
    observation_type = models.CharField(max_length=255, default='')
    observation_unit = models.CharField(max_length=255, default='')
    location_accuracy = models.FloatField()
    is_charging = models.CharField(max_length=255, default='') 
    model_type  = models.CharField(max_length=255, default='')
    version_number = models.CharField(max_length=255, default='')
    package_name = models.CharField(max_length=255, default='')

    class Meta:
        verbose_name = 'reading'
        verbose_name_plural = 'readings'

    def __unicode__(self):
        return '%s: %s' % (self.user_id, self.reading)


class Condition(DateLocationMeasurementModel):
    """
    Condition reading from pressureNET
    """
    accuracy = models.FloatField()
    general_condition = models.CharField(max_length=255)
    windy = models.CharField(max_length=255)
    fog_thickness = models.CharField(max_length=255)
    cloud_type = models.CharField(max_length=255)
    precipitation_type = models.CharField(max_length=255)
    precipitation_amount = models.FloatField()
    precipitation_unit = models.CharField(max_length=255)
    thunderstorm_intensity = models.CharField(max_length=255)
    user_comment = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'condition'
        verbose_name_plural = 'conditions'

    def __unicode__(self):
        return '%s: %s' % (self.user_id, self.general_condition)


class ConditionFilter(models.Model):
    """
    pressureNET user filter for conditions
    """
    user_id = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'condition filter'
        verbose_name_plural = 'condition filters'

    def __unicode__(self):
        return self.user_id


class ReadingSync(models.Model):
    """
    Reading synchronization from Tomcat Server
    """
    date = models.DateTimeField(auto_now_add=True)
    readings = models.IntegerField()
    processing_time = models.FloatField()

    class Meta:
        verbose_name = 'reading sync'
        verbose_name_plural = 'reading syncs'

    def __unicode__(self):
        return '%s: %s' % (self.date, self.readings)
