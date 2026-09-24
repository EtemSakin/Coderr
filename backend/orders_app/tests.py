from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import Profile, User
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order


class OrderApiTests(APITestCase):
    def setUp(self):
        self.customer = self.create_user('customer', User.CUSTOMER)
        self.business = self.create_user('business', User.BUSINESS)
        self.other_business = self.create_user('otherbusiness', User.BUSINESS)
        self.detail = self.create_detail(self.business)

    def create_user(self, username, user_type):
        user = User.objects.create_user(
            username=username,
            password='Testpass123!',
            type=user_type,
        )
        Profile.objects.create(user=user)
        return user

    def create_offer(self, business):
        return Offer.objects.create(
            creator=business,
            title='Logo Design',
            description='Professional logo',
        )

    def create_detail(self, business):
        offer = self.create_offer(business)
        return OfferDetail.objects.create(
            offer=offer,
            title='Basic Logo',
            revisions=2,
            delivery_time_in_days=3,
            price='25.00',
            features=['Logo file'],
            offer_type=OfferDetail.BASIC,
        )

    def create_order(self, status_value=Order.IN_PROGRESS):
        return Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            offer_detail=self.detail,
            title=self.detail.title,
            revisions=self.detail.revisions,
            delivery_time_in_days=self.detail.delivery_time_in_days,
            price=self.detail.price,
            features=list(self.detail.features),
            offer_type=self.detail.offer_type,
            status=status_value,
        )

    def test_customer_can_create_order_from_offer_detail(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(
            '/api/orders/',
            {'offer_detail_id': self.detail.id},
            format='json',
        )
        order = Order.objects.get()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(order.business_user, self.business)
        self.assertEqual(order.offer_type, OfferDetail.BASIC)
        self.assertEqual(order.status, Order.IN_PROGRESS)

    def test_business_cannot_create_order(self):
        self.client.force_authenticate(user=self.business)
        response = self.client.post(
            '/api/orders/',
            {'offer_detail_id': self.detail.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_requires_offer_detail(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/api/orders/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_status_cannot_be_set_during_order_creation(self):
        self.client.force_authenticate(user=self.customer)
        data = {
            'offer_detail_id': self.detail.id,
            'status': Order.COMPLETED,
        }
        response = self.client.post('/api/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_list_requires_authentication(self):
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def create_unrelated_order(self):
        other_customer = self.create_user('othercustomer', User.CUSTOMER)
        return Order.objects.create(
            customer_user=other_customer,
            business_user=self.other_business,
            offer_detail=None,
            title='Other Order',
            revisions=1,
            delivery_time_in_days=1,
            price='10.00',
            features=[],
        )

    def test_order_list_only_contains_related_orders(self):
        order = self.create_order()
        self.create_unrelated_order()
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/orders/')
        detail = self.client.get(f'/api/orders/{order.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item['id'] for item in response.data], [order.id])
        self.assertEqual(detail.status_code, status.HTTP_200_OK)

    def test_business_can_update_own_order_status(self):
        order = self.create_order()
        self.client.force_authenticate(user=self.business)
        response = self.client.patch(
            f'/api/orders/{order.id}/',
            {'status': Order.COMPLETED},
            format='json',
        )
        order.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(order.status, Order.COMPLETED)

    def test_customer_cannot_update_order_status(self):
        order = self.create_order()
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(
            f'/api/orders/{order.id}/',
            {'status': Order.COMPLETED},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_offer_detail_cannot_be_changed_after_creation(self):
        order = self.create_order()
        other_detail = self.create_detail(self.business)
        self.client.force_authenticate(user=self.business)
        response = self.client.patch(
            f'/api/orders/{order.id}/',
            {'offer_detail_id': other_detail.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_can_delete_order(self):
        order = self.create_order()
        admin = self.create_user('admin', User.CUSTOMER)
        admin.is_staff = True
        admin.save(update_fields=['is_staff'])
        self.client.force_authenticate(user=admin)
        response = self.client.delete(f'/api/orders/{order.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=order.id).exists())

    def test_order_count_endpoints_are_public(self):
        self.create_order()
        self.create_order(Order.COMPLETED)
        progress = self.client.get(f'/api/order-count/{self.business.id}/')
        completed = self.client.get(
            f'/api/completed-order-count/{self.business.id}/'
        )
        self.assertEqual(progress.data['order_count'], 1)
        self.assertEqual(completed.data['completed_order_count'], 1)
