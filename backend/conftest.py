import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import factory

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """用户工厂"""
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = 'testpass123'

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class(*args, **kwargs)
        obj.set_password(kwargs.pop('password', 'testpass123'))
        obj.save()
        return obj


class CategoryFactory(factory.django.DjangoModelFactory):
    """分类工厂"""
    from apps.products.models import Category

    class Meta:
        model = Category

    name = factory.Faker('word')
    slug = factory.Faker('slug')
    description = factory.Faker('text')


class ProductFactory(factory.django.DjangoModelFactory):
    """产品工厂"""
    from apps.products.models import Product

    class Meta:
        model = Product

    name = factory.Faker('word')
    slug = factory.Faker('slug')
    description = factory.Faker('text')
    price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    sku = factory.Faker('uuid4')
    stock = 100
    category = factory.SubFactory(CategoryFactory)
    seller = factory.SubFactory(UserFactory)
    store = factory.LazyAttribute(lambda o: None)  # 稍后设置


@pytest.fixture
def api_client():
    """API 客户端"""
    return APIClient()


@pytest.fixture
def authenticated_user():
    """认证用户"""
    return UserFactory()


@pytest.fixture
def authenticated_client(authenticated_user):
    """已认证的 API 客户端"""
    client = APIClient()
    client.force_authenticate(user=authenticated_user)
    return client


@pytest.fixture
def sample_category():
    """示例分类"""
    return CategoryFactory()


@pytest.fixture
def sample_product(sample_category, authenticated_user):
    """示例产品"""
    product = ProductFactory(category=sample_category, seller=authenticated_user)
    return product


@pytest.mark.django_db
class TestBase:
    """测试基类"""
    pass
