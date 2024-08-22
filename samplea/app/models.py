from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100)
    sub = models.CharField(max_length=1000)
    about=models.FileField(upload_to='image/',null=True, blank=True)
    

class Appointment(models.Model):
    date = models.DateField()
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='image/',null=True, blank=True)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE,  null=True, blank=True)
    slot_1 = models.BinaryField(default=False)
    slot_2 = models.BinaryField(default=False)
    slot_3 = models.BinaryField(default=False)
    slot_4 = models.BinaryField(default=False)
    slot_5 = models.BinaryField(default=False)
    Approval = models.BinaryField(default=False)
    Status = models.BinaryField(default=False)


class Patient(models.Model):
    age = models.IntegerField()
    phonenumber=models.CharField(max_length=10)
    address = models.TextField()
    images=models.ImageField(upload_to='image/',null=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    stat = models.BinaryField(default=False)


    
class Doctor(models.Model):
    age=models.IntegerField(null=True)
    phonenumber=models.CharField(max_length=10)
    address=models.CharField(max_length=20)    
    images=models.ImageField(upload_to='image/',null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE,null=True, blank=True, related_name='doctors')
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    binary_data = models.BinaryField(default=False)
    date_of_join = models.DateField(null=True)

    
