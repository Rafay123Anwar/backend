# from rest_framework import serializers
# from .models import Job, Category
# from accounts.serializers import UserSerializer

# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['id', 'name']

# class JobSerializer(serializers.ModelSerializer):
#     client = UserSerializer(read_only=True)
#     category_name = serializers.CharField(source='category.name', read_only=True)
#     total_proposals = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Job
#         fields = [
#             'id', 'title', 'description', 'client', 'category', 'category_name',
#             'skills_required', 'budget', 'job_type', 'status', 'created_at',
#             'updated_at', 'total_proposals'
#         ]
#         read_only_fields = ['client', 'status', 'created_at', 'updated_at']
    
#     def get_total_proposals(self, obj):
#         return obj.proposals.count()
    
#     def create(self, validated_data):
#         validated_data['client'] = self.context['request'].user
#         return super().create(validated_data)
from rest_framework import serializers
from .models import Category, Job

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class JobSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    client = serializers.SerializerMethodField()
    total_proposals = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'client', 'category', 'category_name',
            'skills_required', 'budget', 'job_type', 'status', 'created_at',
            'updated_at', 'total_proposals'
        ]
    
    def get_client(self, obj):
        from accounts.serializers import UserSerializer
        return UserSerializer(obj.client).data
    
    def get_total_proposals(self, obj):
        return obj.proposals.count()

    def create(self, validated_data):
        validated_data['client'] = self.context['request'].user
        return super().create(validated_data)