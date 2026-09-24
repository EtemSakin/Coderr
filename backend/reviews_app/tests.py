from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import Profile, User
from offers_app.models import Offer
from reviews_app.models import Review


class ReviewApiTests(APITestCase):
    def setUp(self):
        self.customer = self.create_user('customer', User.CUSTOMER)
        self.other_customer = self.create_user('othercustomer', User.CUSTOMER)
        self.business = self.create_user('business', User.BUSINESS)
        self.other_business = self.create_user('otherbusiness', User.BUSINESS)

    def create_user(self, username, user_type):
        user = User.objects.create_user(
            username=username,
            password='Testpass123!',
            type=user_type,
        )
        Profile.objects.create(user=user)
        return user

    def create_review(self, reviewer=None, business=None, rating=4):
        return Review.objects.create(
            reviewer=reviewer or self.customer,
            business_user=business or self.business,
            rating=rating,
            description='Great service',
        )

    def test_review_list_is_public(self):
        self.create_review()
        response = self.client.get('/api/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_customer_can_create_review(self):
        self.client.force_authenticate(user=self.customer)
        data = {
            'business_user': self.business.id,
            'rating': 5,
            'description': 'Excellent',
        }
        response = self.client.post('/api/reviews/', data, format='json')
        review = Review.objects.get()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(review.reviewer, self.customer)

    def test_business_cannot_create_review(self):
        self.client.force_authenticate(user=self.business)
        data = {
            'business_user': self.other_business.id,
            'rating': 5,
            'description': 'Blocked',
        }
        response = self.client.post('/api/reviews/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_user_cannot_create_review(self):
        data = {
            'business_user': self.business.id,
            'rating': 5,
            'description': 'Blocked',
        }
        response = self.client.post('/api/reviews/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_duplicate_review_is_rejected(self):
        self.create_review()
        self.client.force_authenticate(user=self.customer)
        data = {
            'business_user': self.business.id,
            'rating': 3,
            'description': 'Again',
        }
        response = self.client.post('/api/reviews/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rating_outside_range_is_rejected(self):
        self.client.force_authenticate(user=self.customer)
        data = {
            'business_user': self.business.id,
            'rating': 6,
            'description': 'Invalid',
        }
        response = self.client.post('/api/reviews/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reviewer_can_update_review(self):
        review = self.create_review()
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(
            f'/api/reviews/{review.id}/',
            {'rating': 5},
            format='json',
        )
        review.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(review.rating, 5)

    def test_business_user_cannot_be_changed(self):
        review = self.create_review()
        self.client.force_authenticate(user=self.customer)
        response = self.client.patch(
            f'/api/reviews/{review.id}/',
            {'business_user': self.other_business.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_other_customer_cannot_edit_review(self):
        review = self.create_review()
        self.client.force_authenticate(user=self.other_customer)
        response = self.client.patch(
            f'/api/reviews/{review.id}/',
            {'rating': 2},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reviewer_can_delete_review(self):
        review = self.create_review()
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(f'/api/reviews/{review.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    def review_ids(self, query):
        response = self.client.get(query)
        return [item['id'] for item in response.data]

    def test_review_filters_and_ordering(self):
        first = self.create_review(rating=3)
        second = self.create_review(
            reviewer=self.other_customer,
            business=self.other_business,
            rating=5,
        )
        business_ids = self.review_ids(
            f'/api/reviews/?business_user_id={self.business.id}'
        )
        reviewer_ids = self.review_ids(
            f'/api/reviews/?reviewer_id={self.other_customer.id}'
        )
        ordered_ids = self.review_ids('/api/reviews/?ordering=-rating')
        self.assertEqual(business_ids, [first.id])
        self.assertEqual(reviewer_ids, [second.id])
        self.assertEqual(ordered_ids[0], second.id)

    def test_base_info_returns_platform_statistics(self):
        Offer.objects.create(creator=self.business, title='Offer')
        self.create_review(rating=4)
        self.create_review(
            reviewer=self.other_customer,
            business=self.other_business,
            rating=5,
        )
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['offer_count'], 1)
        self.assertEqual(response.data['review_count'], 2)
        self.assertEqual(response.data['business_profile_count'], 2)
        self.assertEqual(response.data['average_rating'], 4.5)

    def test_base_info_returns_zero_average_without_reviews(self):
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.data['average_rating'], 0)

