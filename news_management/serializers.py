from rest_framework import serializers

from .models import News


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = "__all__"

    def create(self, validated_data):
        instance = super(NewsSerializer, self).create(validated_data)
        instance.save()
        return instance
