from rest_framework import serializers

from base.serializers import BaseSerializer
from interacts.models import Like
from rental.models import Room, Bed, Post, RentalContact, BillRentalContact, ViolateNotice, ElectricityAndWaterBills
from users import serializers as user_serializers


class RoomSerializer(BaseSerializer):
    beds = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["id", "name", "image", "number_of_bed", "type", "room_for", "created_date", "updated_date", "beds"]

    def to_representation(self, room):
        data = super().to_representation(room)
        image = data.get("image")

        if "image" in self.fields and image:
            data["image"] = room.image.url

        return data

    def update(self, room, validated_data):
        validated_data["number_of_bed"] = None

        for key, value in validated_data.items():
            setattr(room, key, value)
        room.save()

        return room

    def get_beds(self, room):
        beds = room.beds.all()

        return BedSerializer(beds, many=True).data


class PostSerializer(BaseSerializer):
    total_likes = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "name", "image", "description", "created_date", "updated_date", "total_likes", "room"]

    def to_representation(self, post):
        data = super().to_representation(post)
        image = data.get("image")

        if self.context.get('action') == 'list':
            data.pop('room', None)
        else:
            if "room" in self.fields and post.room:
                data["room"] = RoomSerializer(post.room).data
                if hasattr(post.room, 'bed'):
                    data["bed"] = BedSerializer(post.room.bed).data

        if "image" in self.fields and image:
            data["image"] = post.image.url

        return data

    def update(self, post, validated_data):
        for key, value in validated_data.items():
            setattr(post, key, value)
        post.save()

        return post

    def get_total_likes(self, post):
        return post.likes.filter(is_active=True).count()


class AuthenticatedPostSerializer(PostSerializer):
    liked = serializers.SerializerMethodField()

    class Meta:
        model = PostSerializer.Meta.model
        fields = PostSerializer.Meta.fields + ["liked"]

    def get_liked(self, post):
        request = self.context.get("request")

        try:
            like = Like.objects.get(user=request.user, post=post)
        except Like.DoesNotExist:
            return False

        return like.is_active


class BedSerializer(BaseSerializer):
    class Meta:
        model = Bed
        fields = ["id", "name", "price", "image", "description", "status", "created_date", "updated_date", "room"]
        extra_kwargs = {"room": {"write_only": True}}

    def to_representation(self, bed):
        data = super().to_representation(bed)
        image = data.get("image")

        if "image" in self.fields and image:
            data["image"] = bed.image.url

        return data

    def update(self, bed, validated_data):
        validated_data["price"] = None

        for key, value in validated_data.items():
            setattr(bed, key, value)
        bed.save()

        return bed

    def validate(self, data):
        room = data.get('room')
        if room:
            existing_beds_count = room.beds.count()
            number_of_beds = room.number_of_bed

            if existing_beds_count >= number_of_beds:
                raise serializers.ValidationError({"message": f"{room.name} đã đủ {number_of_beds} giường."})

        return data


class RentalContactSerializer(BaseSerializer):
    class Meta:
        model = RentalContact
        fields = ["id", "rental_number", "time_rental", "status", "created_date", "updated_date", "bed", "student",
                  "room"]

    def to_representation(self, rental_contact):
        data = super().to_representation(rental_contact)

        if "bed" in self.fields and rental_contact.bed:
            data["bed"] = BedSerializer(rental_contact.bed).data

        if "student" in self.fields and rental_contact.student:
            data["student"] = user_serializers.StudentSerializer(rental_contact.student).data

        if "room" in self.fields and rental_contact.room:
            room_data = RoomSerializer(rental_contact.room).data
            room_data.pop('beds', None)
            data["room"] = room_data

        return data


class BillRentalContactSerializer(BaseSerializer):
    class Meta:
        model = BillRentalContact
        fields = ["id", "bill_number", "total", "status", "created_date", "updated_date", "student", "specialist",
                  "rental_contact"]

    def to_representation(self, bill_rental_contact):
        data = super().to_representation(bill_rental_contact)
        student = data.get("student")
        specialist = data.get("specialist")
        rental_contact = data.get("rental_contact")

        if "student" in self.fields and student:
            data["student"] = user_serializers.StudentSerializer(bill_rental_contact.student).data
        if "specialist" in self.fields and specialist:
            data["specialist"] = user_serializers.UserSerializer(bill_rental_contact.specialist.user).data
        if "rental_contact" in self.fields and rental_contact:
            data["rental_contact"] = RentalContactSerializer(bill_rental_contact.rental_contact).data

        return data


class ViolateNoticeSerializer(BaseSerializer):
    class Meta:
        model = ViolateNotice
        fields = ["id", "violate_number", "description", "created_date", "updated_date", "manager", "room"]

    def to_representation(self, violate_notice):
        data = super().to_representation(violate_notice)
        manager = data.get("manager")
        room = data.get("room")

        if "manager" in self.fields and manager:
            data["manager"] = user_serializers.UserSerializer(violate_notice.manager.user).data
        if "room" in self.fields and room:
            data["room"] = RoomSerializer(violate_notice.room, excludes=["beds"]).data

        return data


class ElectricityAndWaterBillsSerializer(BaseSerializer):
    class Meta:
        model = ElectricityAndWaterBills
        fields = ["id", "total_cubic_meters_water", "total_electricity", "total_amount", "status", "created_date",
                  "updated_date", "manager", "room"]

    def to_representation(self, electricity_and_water_bills):
        data = super().to_representation(electricity_and_water_bills)
        manager = data.get("manager")
        room = data.get("room")

        if "manager" in self.fields and manager:
            data["manager"] = user_serializers.UserSerializer(electricity_and_water_bills.manager.user).data
        if "room" in self.fields and room:
            data["room"] = RoomSerializer(electricity_and_water_bills.room, excludes=["beds"]).data

        return data
