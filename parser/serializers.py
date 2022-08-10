from rest_framework import serializers

from .models import LinkedinUsers


class CheckMyUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = LinkedinUsers
        fields = '__all__'
