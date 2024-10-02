import re

from rest_framework import serializers

from base.serializers import BaseSerializer
from users.models import User, Administrator, Manager, Specialist, Student
from utils import validations


class UserSerializer(BaseSerializer):
	# Cho Manager
	certificate = serializers.CharField(max_length=255, write_only=True, required=False)
	# Cho Specialist
	degree = serializers.CharField(max_length=255, write_only=True, required=False)
	# Cho Student
	student_id = serializers.CharField(max_length=10, write_only=True, required=False)
	university = serializers.CharField(max_length=255, write_only=True, required=False)
	faculty = serializers.CharField(max_length=255, write_only=True, required=False)
	major = serializers.CharField(max_length=255, write_only=True, required=False)
	academic_year = serializers.IntegerField(write_only=True, required=False)

	user_instance = serializers.SerializerMethodField(read_only=True)

	class Meta:
		model = User
		fields = [
			"id", "role", "email", "password", "identification", "full_name", "avatar",
			"dob", "gender", "address", "phone", "date_joined", "last_login", "user_instance",
			"certificate", "degree", "student_id", "university", "faculty", "major", "academic_year",
		]
		extra_kwargs = {
			"gender": {"read_only": True},
			"address": {"read_only": True},
			"phone": {"read_only": True},
			"code": {"read_only": True},
			"date_joined": {"read_only": True},
			"last_login": {"read_only": True},
			"password": {"write_only": True},
		}

	def to_representation(self, user):
		data = super().to_representation(user)
		avatar = data.get("avatar")
		dob = data.get("dob")
		date_joined = data.get("date_joined")

		if "avatar" in self.fields and avatar:
			data["avatar"] = user.avatar.url
		if "dob" in self.fields and dob:
			data["dob"] = user.dob.strftime("%d-%m-%Y")
		if "date_joined" in self.fields and date_joined:
			data["date_joined"] = user.date_joined.strftime("%d-%m-%Y %H:%M:%S")

		return data

	def create(self, validated_data):
		other_field = {
			"certificate": validated_data.pop("certificate", None),
			"degree": validated_data.pop("degree", None),
			"student_id": validated_data.pop("student_id", None),
			"university": validated_data.pop("university", None),
			"faculty": validated_data.pop("faculty", None),
			"major": validated_data.pop("major", None),
			"academic_year": validated_data.pop("academic_year", None),
		}

		user = User.objects.create_user(email=validated_data.pop("email"), password=validated_data.pop("password"), **validated_data)
		self.create_user_instance(user, **other_field)

		return user

	def get_user_instance(self, user):
		serializer_class, instance_name = validations.check_user_role(user)
		user_instance = getattr(user, instance_name, None)

		return serializer_class(user_instance).data

	def validate_role(self, role):
		if role is None or role != User.Role.STUDENT:
			raise serializers.ValidationError({"message": "Vai trò không hợp lệ."})

		return role

	def validate_email(self, email):
		if email is None or not re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email.strip()):
			raise serializers.ValidationError({"message": "Email không đúng định dạng."})

		return email

	def validate_password(self, password):
		if password is None or not re.fullmatch(r"^.{8,}$", password.strip()):
			raise serializers.ValidationError({"message": "Mật khẩu phải chứa ít nhất 8 ký tự."})

		return password

	def validate_identification(self, identification):
		if identification is None or not re.fullmatch(r"^[0-9]{12}$", identification.strip()):
			raise serializers.ValidationError({"message": "Số CCCD không hợp lệ."})

		return identification

	def validate_student_id(self, student_id):
		if student_id is not None and not re.fullmatch(r"^[0-9]{10}$", student_id.strip()):
			raise serializers.ValidationError({"message": "Mã số sinh viên không hợp lệ."})

		# if Student.objects.filter(student_id=student_id).exists():
		# 	raise serializers.ValidationError({"message": "Mã số sinh viên đã tồn tại."})

		return student_id

	def validate(self, data):
		role = data.get("role")
		other_field = {
			"certificate": data.get("certificate", None),
			"degree": data.get("degree", None),
			"student_id": data.get("student_id", None),
			"university": data.get("university", None),
			"faculty": data.get("faculty", None),
			"major": data.get("major", None),
			"academic_year": data.get("academic_year", None),
		}

		certificate = other_field.pop("certificate")
		if role == User.Role.MANAGER and not certificate:
			raise serializers.ValidationError({"message": "Vui lòng nhập chứng chỉ."})

		degree = other_field.pop("degree")
		if role == User.Role.SPECIALIST and not degree:
			raise serializers.ValidationError({"message": "Vui lòng nhập bằng cấp."})

		if role == User.Role.STUDENT and not all(other_field.values()):
			raise serializers.ValidationError({"message": "Vui lòng nhập đầy đủ thông tin."})

		return data

	def create_user_instance(self, user, **other_field):
		if user.role == User.Role.STUDENT:
			student_id = other_field.get("student_id", None)
			university = other_field.get("university", None)
			faculty = other_field.get("faculty", None)
			major = other_field.get("major", None)
			academic_year = other_field.get("academic_year", None)

			Student.objects.create(
				user=user,
				student_id=student_id,
				university=university,
				faculty=faculty,
				major=major,
				academic_year=academic_year
			)


class UserUpdateSerializer(serializers.Serializer):
	old_password = serializers.CharField(write_only=True, required=False)
	new_password = serializers.CharField(write_only=True, required=False)
	email = serializers.EmailField(required=False)
	avatar = serializers.ImageField(required=False)
	full_name = serializers.CharField(max_length=255, required=False)
	dob = serializers.DateField(required=False)
	gender = serializers.CharField(max_length=1, required=False)
	address = serializers.CharField(max_length=255, required=False)
	phone = serializers.CharField(max_length=15, required=False)
	# Cho Manager
	certificate = serializers.CharField(max_length=255, required=False)
	# Cho Specialist
	degree = serializers.CharField(max_length=255, required=False)
	# Cho Student
	student_id = serializers.CharField(max_length=10, required=False)
	university = serializers.CharField(max_length=255, required=False)
	faculty = serializers.CharField(max_length=255, required=False)
	major = serializers.CharField(max_length=255, required=False)
	academic_year = serializers.IntegerField(required=False)

	def update(self, user, validated_data):
		other_field = {
			"certificate": validated_data.pop("certificate", None),
			"degree": validated_data.pop("degree", None),
			"student_id": validated_data.pop("student_id", None),
			"university": validated_data.pop("university", None),
			"faculty": validated_data.pop("faculty", None),
			"major": validated_data.pop("major", None),
			"academic_year": validated_data.pop("academic_year", None),
		}

		if "old_password" in validated_data and "new_password" in validated_data:
			user.set_password(validated_data.pop("new_password"))
		if "avatar" in validated_data:
			user.avatar = validated_data.pop("avatar")
		for attr, value in validated_data.items():
			setattr(user, attr, value)
		user.save()

		self.update_user_instance(user, **other_field)

		return user

	def validate_email(self, email):
		if not re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email.strip()):
			raise serializers.ValidationError({"message": "Email không đúng định dạng."})

		return email

	def validate_new_password(self, new_password):
		if not re.fullmatch(r"^.{8,}$", new_password.strip()):
			raise serializers.ValidationError({"message": "Mật khẩu phải chứa ít nhất 8 ký tự."})

		return new_password

	def validate_identification(self, identification):
		if not re.fullmatch(r"^[0-9]{12}$", identification.strip()):
			raise serializers.ValidationError({"message": "Số CCCD không hợp lệ."})

		return identification

	def validate_student_id(self, student_id):
		if student_id is not None and not re.fullmatch(r"^[0-9]{10}$", student_id.strip()):
			raise serializers.ValidationError({"message": "Mã số sinh viên không hợp lệ."})

		return student_id

	def update_user_instance(self, user, **other_field):
		instance_name = validations.check_user_role(user)[1]
		user_instance = getattr(user, instance_name, None)

		if user.role == User.Role.MANAGER:
			certificate = other_field.get("certificate", None)

			user_instance.certificate = certificate if certificate else user_instance.certificate
		elif user.role == User.Role.SPECIALIST:
			degree = other_field.get("degree", None)

			user_instance.degree = degree if degree else user_instance.degree
		elif user.role == User.Role.STUDENT:
			student_id = other_field.get("student_id", None)
			university = other_field.get("university", None)
			faculty = other_field.get("faculty", None)
			major = other_field.get("major", None)
			academic_year = other_field.get("academic_year", None)

			user_instance.student_id = student_id if student_id else user_instance.student_id
			user_instance.university = university if university else user_instance.university
			user_instance.faculty = faculty if faculty else user_instance.faculty
			user_instance.major = major if major else user_instance.major
			user_instance.academic_year = academic_year if academic_year else user_instance.academic_year

		user_instance.save()


class BaseInstanceSerializer(BaseSerializer):
	class Meta:
		exclude = ["user", "is_active", "created_date", "updated_date"]


class AdministratorSerializer(BaseSerializer):
	class Meta:
		model = Administrator
		exclude = BaseInstanceSerializer.Meta.exclude


class ManagerSerializer(BaseSerializer):
	class Meta:
		model = Manager
		exclude = BaseInstanceSerializer.Meta.exclude


class SpecialistSerializer(BaseSerializer):
	class Meta:
		model = Specialist
		exclude = BaseInstanceSerializer.Meta.exclude


class StudentSerializer(BaseSerializer):
	class Meta:
		model = Student
		exclude = BaseInstanceSerializer.Meta.exclude
