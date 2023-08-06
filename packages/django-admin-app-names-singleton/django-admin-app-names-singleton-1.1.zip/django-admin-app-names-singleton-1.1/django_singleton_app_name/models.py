from django.db import models


class SingletonBaseModel(models.Model):
    @staticmethod
    def single_instance():
        return True

    class Meta:
        abstract = True
