from orders_app.models import Order as ProjectOrder


class OrderManagerAdapter:
    """Adds the immutable snapshot required by the local Order model."""

    @staticmethod
    def get_or_create(defaults=None, **kwargs):
        defaults = dict(defaults or {})
        detail = kwargs.get('offer_detail')
        if detail is not None:
            defaults.setdefault('title', detail.title)
            defaults.setdefault('revisions', detail.revisions)
            defaults.setdefault(
                'delivery_time_in_days',
                detail.delivery_time_in_days,
            )
            defaults.setdefault('price', detail.price)
            defaults.setdefault('features', detail.features)
            defaults.setdefault('offer_type', detail.offer_type)
        return ProjectOrder.objects.get_or_create(
            defaults=defaults,
            **kwargs,
        )


class Order:
    """Exposes the manager interface expected by the mentor script."""

    objects = OrderManagerAdapter()


__all__ = ['Order']
