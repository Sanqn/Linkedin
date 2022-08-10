from django.db import models


class LinkedinUsers(models.Model):
    first_name = models.CharField(max_length=254, blank=True, null=True)
    last_name = models.CharField(max_length=254, blank=True, null=True)
    company = models.CharField(max_length=254, blank=True, null=True)
    position = models.CharField(max_length=254, blank=True, null=True)
    url_linkedin = models.CharField(max_length=254, blank=True, null=True)
    email = models.CharField(max_length=254, blank=True, null=True)
    number_phone = models.CharField(max_length=254, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'linkedin_users'

    def __str__(self):
        return self.first_name

