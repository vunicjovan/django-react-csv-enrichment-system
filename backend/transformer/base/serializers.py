from rest_framework import serializers


class MemoryUsageSerializer(serializers.Serializer):
    total = serializers.CharField()
    available = serializers.CharField()
    used_percent = serializers.CharField()


class DiskUsageSerializer(serializers.Serializer):
    total = serializers.CharField()
    free = serializers.CharField()
    used_percent = serializers.CharField()


class SystemInfoSerializer(serializers.Serializer):
    os = serializers.CharField()
    python_version = serializers.CharField()
    cpu_count = serializers.IntegerField()
    memory = MemoryUsageSerializer()
    disk = DiskUsageSerializer()


class DatabaseInfoSerializer(serializers.Serializer):
    status = serializers.CharField()
    tables = serializers.ListField(child=serializers.CharField())
    engine = serializers.CharField()


class CeleryInfoSerializer(serializers.Serializer):
    status = serializers.CharField()
    registered_tasks = serializers.ListField(child=serializers.CharField())


class HealthCheckSerializer(serializers.Serializer):
    system = SystemInfoSerializer()
    database = DatabaseInfoSerializer()
    celery = CeleryInfoSerializer()
