from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
	def __init__(self, *args, **kwargs):
		fields = kwargs.pop("fields", None)
		excludes = kwargs.pop("excludes", None)

		super().__init__(*args, **kwargs)

		if fields:
			allowed = set(fields)
			existing = set(self.fields)
			for field_name in existing - allowed:
				self.fields.pop(field_name)

		if excludes:
			for field_name in excludes:
				self.fields.pop(field_name)

	def to_representation(self, instance):
		data = super().to_representation(instance)

		if "created_date" in self.fields:
			data["created_date"] = instance.created_date.strftime("%d-%m-%Y %H:%M:%S")
		if "updated_date" in self.fields:
			data["updated_date"] = instance.updated_date.strftime("%d-%m-%Y %H:%M:%S")

		return data
