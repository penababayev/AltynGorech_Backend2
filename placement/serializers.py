# placement/serializers.py
from rest_framework import serializers
from .models import PlacementQuestion, PlacementChoice

class PlacementChoiceOut(serializers.ModelSerializer):
    class Meta:
        model = PlacementChoice
        fields = ("id","text")  # is_correct asla gönderme!

class PlacementQuestionOut(serializers.ModelSerializer):
    choices = PlacementChoiceOut(many=True, read_only=True)
    class Meta:
        model = PlacementQuestion
        fields = ("id","text","skill","audio_url","choices")
