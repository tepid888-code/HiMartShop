from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.users.models import User, UserProfile, Address, Wishlist


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'address_type', 'street_address', 'city', 'state',
                  'postal_code', 'country', 'phone', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['total_purchases', 'total_spent']
        read_only_fields = ['total_purchases', 'total_spent']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'phone', 'is_seller', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserDetailSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'phone', 'gender', 'date_of_birth', 'profile_image', 'bio',
                  'is_seller', 'is_verified', 'profile', 'addresses', 'created_at']
        read_only_fields = ['id', 'is_verified', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name',
                  'phone', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(
                {'password': '密码不匹配。'}
            )

        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(
                {'username': '用户名已存在。'}
            )

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {'email': '邮箱已注册。'}
            )

        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User.objects.create_user(**validated_data, password=password)
        UserProfile.objects.create(user=user)
        Wishlist.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError(
                '必须提供用户名和密码。'
            )

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError(
                '用户名或密码错误。'
            )

        data['user'] = user
        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'gender',
                  'date_of_birth', 'profile_image', 'bio']
