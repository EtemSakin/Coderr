import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from decimal import Decimal  

from django.contrib.auth import get_user_model  
from django.db import transaction  

from app_auth.models import UserProfile  
from app_offers.models import Offer, OfferDetail  
from app_orders.models import Order  
from app_reviews.models import Review  

User = get_user_model()


USERS = [
    {
        'username': 'customer_guest',
        'email': 'customer_guest@test.de',
        'password': '123456',
        'type': 'customer',
        'first_name': 'Guest',
        'last_name': 'Customer',
        'profile': {
            'location': '',
            'tel': '',
            'description': 'Guest customer account',
        },
    },
    {
        'username': 'business_guest',
        'email': 'business_guest@test.de',
        'password': '123456',
        'type': 'business',
        'first_name': 'Guest',
        'last_name': 'Business',
        'profile': {
            'location': '',
            'tel': '',
            'description': 'Guest business account',
            'working_hours': '',
        },
    },
    {
        'username': 'customer1',
        'email': 'customer1@test.de',
        'password': 'testpass123',
        'type': 'customer',
        'first_name': 'Max',
        'last_name': 'Mustermann',
        'profile': {
            'location': 'Berlin',
            'tel': '+49 30 12345678',
            'description': 'Privatkunde aus Berlin',
        },
    },
    {
        'username': 'business1',
        'email': 'business1@test.de',
        'password': 'testpass123',
        'type': 'business',
        'first_name': 'Anna',
        'last_name': 'Schmidt',
        'profile': {
            'location': 'München',
            'tel': '+49 89 87654321',
            'description': 'Webentwicklerin mit 5 Jahren Erfahrung',
            'working_hours': 'Mo-Fr 9-17 Uhr',
        },
    },
    {
        'username': 'business2',
        'email': 'business2@test.de',
        'password': 'testpass123',
        'type': 'business',
        'first_name': 'Tom',
        'last_name': 'Weber',
        'profile': {
            'location': 'Hamburg',
            'tel': '+49 40 11223344',
            'description': 'Full-Stack Entwickler',
            'working_hours': 'Mo-Fr 10-18 Uhr',
        },
    },
    {
        'username': 'customer2',
        'email': 'customer2@test.de',
        'password': 'testpass123',
        'type': 'customer',
        'first_name': 'Lisa',
        'last_name': 'Müller',
        'profile': {
            'location': 'Frankfurt',
            'tel': '+49 69 55667788',
            'description': 'Projektmanagerin',
        },
    },
]

OFFERS = [
    {
        'username': 'business1',
        'title': 'Professionelle Webseite erstellen',
        'description': 'Ich erstelle eine moderne, responsive Webseite nach Ihren Wünschen.',
        'details': [
            {
                'title': 'Basis-Paket',
                'revisions': 2,
                'delivery_time_in_days': 7,
                'price': Decimal('299.99'),
                'features': ['5 Seiten', 'Kontaktformular', 'Responsive Design'],
                'offer_type': 'basic',
            },
            {
                'title': 'Standard-Paket',
                'revisions': 5,
                'delivery_time_in_days': 14,
                'price': Decimal('599.99'),
                'features': ['10 Seiten', 'Kontaktformular', 'Responsive Design', 'SEO Basis'],
                'offer_type': 'standard',
            },
            {
                'title': 'Premium-Paket',
                'revisions': -1,
                'delivery_time_in_days': 30,
                'price': Decimal('999.99'),
                'features': ['Unbegrenzte Seiten', 'Kontaktformular', 'Responsive Design', 'SEO Optimierung', 'CMS'],
                'offer_type': 'premium',
            },
        ],
    },
    {
        'username': 'business2',
        'title': 'Full-Stack Webentwicklung',
        'description': 'Komplette Webanwendungen mit Django, React und mehr.',
        'details': [
            {
                'title': 'Basic App',
                'revisions': 3,
                'delivery_time_in_days': 14,
                'price': Decimal('799.99'),
                'features': ['Frontend Entwicklung', 'Basis Backend', 'REST API'],
                'offer_type': 'basic',
            },
            {
                'title': 'Standard App',
                'revisions': 5,
                'delivery_time_in_days': 30,
                'price': Decimal('1499.99'),
                'features': ['Frontend + Backend', 'Datenbank Design', 'REST API', 'Authentifizierung'],
                'offer_type': 'standard',
            },
            {
                'title': 'Enterprise App',
                'revisions': -1,
                'delivery_time_in_days': 60,
                'price': Decimal('2999.99'),
                'features': ['Full-Stack Entwicklung', 'Datenbank Design', 'REST API', 'Authentifizierung', 'Tests', 'Deployment'],
                'offer_type': 'premium',
            },
        ],
    },
    {
        'username': 'business1',
        'title': 'WordPress Webseite',
        'description': 'Professionelle WordPress Webseite mit individuellem Theme.',
        'details': [
            {
                'title': 'WordPress Basis',
                'revisions': 3,
                'delivery_time_in_days': 10,
                'price': Decimal('249.99'),
                'features': ['WordPress Installation', 'Standard Theme', '5 Seiten'],
                'offer_type': 'basic',
            },
            {
                'title': 'WordPress Professionell',
                'revisions': 5,
                'delivery_time_in_days': 21,
                'price': Decimal('499.99'),
                'features': ['WordPress Installation', 'Individuelles Theme', '10 Seiten', 'Plugins'],
                'offer_type': 'standard',
            },
        ],
    },
]

ORDERS = [
    {'customer': 'customer1', 'offer': 'Professionelle Webseite erstellen', 'offer_type': 'standard', 'status': 'completed'},
    {'customer': 'customer2', 'offer': 'Full-Stack Webentwicklung', 'offer_type': 'basic', 'status': 'in_progress'},
    {'customer': 'customer1', 'offer': 'Professionelle Webseite erstellen', 'offer_type': 'basic', 'status': 'completed'},
]

REVIEWS = [
    {
        'business': 'business1',
        'reviewer': 'customer1',
        'rating': 5,
        'description': 'Super Service! Die Webseite wurde pünktlich geliefert und sieht toll aus.',
    },
    {
        'business': 'business2',
        'reviewer': 'customer1',
        'rating': 4,
        'description': 'Gute Arbeit, etwas Verzögerung aber insgesamt zufriedenstellend.',
    },
    {
        'business': 'business1',
        'reviewer': 'customer2',
        'rating': 5,
        'description': 'Anna hat unsere Erwartungen übertroffen. Sehr zu empfehlen!',
    },
]


def create_users():
    users = {}
    for entry in USERS:
        data = dict(entry)
        profile = data.pop('profile')
        password = data.pop('password')
        user, created = User.objects.get_or_create(username=data['username'], defaults=data)
        if created:
            user.set_password(password)
            user.save()
            UserProfile.objects.create(user=user, **profile)
            print(f'Created user: {user.username}')
        users[user.username] = user
    return users


def create_offers(users):
    offers = {}
    for entry in OFFERS:
        data = dict(entry)
        details = data.pop('details')
        user = users[data.pop('username')]
        offer, created = Offer.objects.get_or_create(user=user, title=data['title'], defaults=data)
        if created:
            for detail in details:
                OfferDetail.objects.create(offer=offer, **detail)
            print(f'Created offer: {offer.title}')
        offers[offer.title] = offer
    return offers


def create_orders(users, offers):
    for entry in ORDERS:
        offer = offers[entry['offer']]
        detail = OfferDetail.objects.get(offer=offer, offer_type=entry['offer_type'])
        order, created = Order.objects.get_or_create(
            customer_user=users[entry['customer']],
            business_user=offer.user,
            offer_detail=detail,
            defaults={'status': entry['status']},
        )
        if created:
            print(f'Created order: {order.id}')


def create_reviews(users):
    for entry in REVIEWS:
        review, created = Review.objects.get_or_create(
            business_user=users[entry['business']],
            reviewer=users[entry['reviewer']],
            defaults={'rating': entry['rating'], 'description': entry['description']},
        )
        if created:
            print(f'Created review from {review.reviewer.username}')


# Run everything in a single transaction: if any step fails,
# all changes are rolled back to avoid partial sample data.
@transaction.atomic
def main():
    users = create_users()
    offers = create_offers(users)
    create_orders(users, offers)
    create_reviews(users)
    print('Sample data created successfully.')


if __name__ == '__main__':
    main()
