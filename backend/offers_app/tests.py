import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import Profile, User
from offers_app.api.serializers import OfferSerializer
from offers_app.models import Offer, OfferDetail


def image_file(name='test.png'):
    buffer = BytesIO()
    Image.new('RGB', (1, 1)).save(buffer, format='PNG')
    return SimpleUploadedFile(
        name,
        buffer.getvalue(),
        content_type='image/png',
    )


class OfferApiTests(APITestCase):
    def setUp(self):
        self.business = self.create_user('business', User.BUSINESS)
        self.other_business = self.create_user('otherbusiness', User.BUSINESS)
        self.customer = self.create_user('customer', User.CUSTOMER)
        self.offer = self.create_offer(self.business, 'Logo Design', 20, 2)

    def create_user(self, username, user_type):
        user = User.objects.create_user(
            username=username,
            password='Testpass123!',
            type=user_type,
        )
        Profile.objects.create(user=user)
        return user

    def detail_data(self, prefix='Package'):
        return [
            {
                'title': f'{prefix} Basic',
                'revisions': 1,
                'delivery_time_in_days': 2,
                'price': '20.00',
                'features': ['One concept'],
                'offer_type': OfferDetail.BASIC,
            },
            {
                'title': f'{prefix} Standard',
                'revisions': 2,
                'delivery_time_in_days': 4,
                'price': '40.00',
                'features': ['Two concepts'],
                'offer_type': OfferDetail.STANDARD,
            },
            {
                'title': f'{prefix} Premium',
                'revisions': -1,
                'delivery_time_in_days': 6,
                'price': '60.00',
                'features': ['Three concepts'],
                'offer_type': OfferDetail.PREMIUM,
            },
        ]

    def create_offer(self, creator, title, price, delivery):
        offer = Offer.objects.create(
            creator=creator,
            title=title,
            description=f'{title} description',
        )
        for index, offer_type in enumerate(
            [OfferDetail.BASIC, OfferDetail.STANDARD, OfferDetail.PREMIUM]
        ):
            OfferDetail.objects.create(
                offer=offer,
                title=f'{title} {offer_type}',
                revisions=index + 1,
                delivery_time_in_days=delivery + index,
                price=price + (index * 10),
                features=['Feature'],
                offer_type=offer_type,
            )
        return offer

    def test_business_can_create_offer(self):
        self.client.force_authenticate(user=self.business)
        data = {
            'title': 'Web Design',
            'description': 'Responsive website',
            'details': self.detail_data('Web'),
        }
        response = self.client.post('/api/offers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], self.business.id)
        self.assertEqual(len(response.data['details']), 3)

    def test_customer_cannot_create_offer(self):
        self.client.force_authenticate(user=self.customer)
        data = {'title': 'Blocked', 'details': self.detail_data()}
        response = self.client.post('/api/offers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_offer_requires_three_unique_package_types(self):
        self.client.force_authenticate(user=self.business)
        data = {'title': 'Invalid', 'details': self.detail_data()[:2]}
        response = self.client.post('/api/offers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_offer_rejects_non_list_features(self):
        self.client.force_authenticate(user=self.business)
        details = self.detail_data()
        details[0]['features'] = 'not-a-list'
        response = self.client.post(
            '/api/offers/',
            {'title': 'Invalid', 'details': details},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_offer_list_is_public_and_paginated(self):
        response = self.client.get('/api/offers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['user'], self.business.id)

    def test_offer_list_supports_search_and_filters(self):
        self.create_offer(self.other_business, 'Video Editing', 80, 8)
        search = self.client.get('/api/offers/?search=Logo')
        creator = self.client.get(
            f'/api/offers/?creator_id={self.business.id}'
        )
        delivery = self.client.get('/api/offers/?max_delivery_time=3')
        self.assertEqual(search.data['count'], 1)
        self.assertEqual(creator.data['count'], 1)
        self.assertEqual(delivery.data['count'], 1)

    def test_offer_list_orders_by_min_price(self):
        expensive = self.create_offer(
            self.other_business, 'Video Editing', 80, 8
        )
        response = self.client.get('/api/offers/?ordering=min_price')
        ids = [item['id'] for item in response.data['results']]
        self.assertEqual(ids, [self.offer.id, expensive.id])

    def test_owner_can_update_offer_and_details(self):
        self.client.force_authenticate(user=self.business)
        data = {'title': 'Updated Logo', 'details': self.detail_data('Updated')}
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/', data, format='json'
        )
        self.offer.refresh_from_db()
        basic = self.offer.details.get(offer_type=OfferDetail.BASIC)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.offer.title, 'Updated Logo')
        self.assertEqual(basic.title, 'Updated Basic')

    def test_owner_can_upload_offer_image(self):
        self.client.force_authenticate(user=self.business)
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.patch(
                    f'/api/offers/{self.offer.id}/',
                    {'image': image_file('offer.png')},
                    format='multipart',
                )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('/media/offer_images/', response.data['image'])

    def test_non_owner_cannot_update_offer(self):
        self.client.force_authenticate(user=self.other_business)
        response = self.client.patch(
            f'/api/offers/{self.offer.id}/',
            {'title': 'No access'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_offer(self):
        self.client.force_authenticate(user=self.business)
        response = self.client.delete(f'/api/offers/{self.offer.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(id=self.offer.id).exists())

    def test_put_is_not_allowed_for_offers(self):
        self.client.force_authenticate(user=self.business)
        response = self.client.put(
            f'/api/offers/{self.offer.id}/',
            {'title': 'Blocked'},
            format='json',
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_offer_detail_is_public(self):
        detail = self.offer.details.first()
        response = self.client.get(f'/api/offerdetails/{detail.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], detail.id)

    def test_serializer_calculates_minimum_values_without_annotations(self):
        plain_offer = Offer.objects.get(id=self.offer.id)
        data = OfferSerializer(plain_offer).data
        self.assertEqual(data['min_price'], 20)
        self.assertEqual(data['min_delivery_time'], 2)

    def test_model_string_values(self):
        detail = self.offer.details.first()
        self.assertEqual(str(self.offer), 'Logo Design')
        self.assertEqual(str(detail), detail.title)
