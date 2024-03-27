from django.db import models


class User(models.Model):
    Roles = (
    (1, "Employee"),
    (2, "Manager"),
  )
     
    username = models.CharField(max_length=50, unique=True)
    password = models.TextField()
    roles = models.IntegerField(choices=Roles, default=1)
    email=models.EmailField()

    def __str__(self):
        return self.name
class Task(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        primary_key=True,
    )
    username = models.CharField(max_length=50,unique=True)
    task = models.CharField(max_length=100)