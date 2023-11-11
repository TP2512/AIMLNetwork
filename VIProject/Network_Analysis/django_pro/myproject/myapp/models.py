from django.db import models


class Circle(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name
