"""Compatibility models for the mentor sample-data script."""

from orders_app.models import Order as ProjectOrder


class OrderManagerAdapter:
    """Add the immutable snapshot required by the local Order model."""

    @staticmethod
    def get_or_create(defaults=None, **kwargs):
        """Create or retrieve an order using mentor script arguments."""
        defaults = dict(defaults or {})
        detail = kwargs.get('offer_detail')
        if detail is not None:
            OrderManagerAdapter._add_snapshot(defaults, detail)
        return ProjectOrder.objects.get_or_create(
            defaults=defaults,
            **kwargs,
        )

    @staticmethod
    def _add_snapshot(defaults, detail):
        """Add immutable offer-detail values to order defaults."""
        defaults.setdefault('title', detail.title)
        defaults.setdefault('revisions', detail.revisions)
        defaults.setdefault(
            'delivery_time_in_days',
            detail.delivery_time_in_days,
        )
        defaults.setdefault('price', detail.price)
        defaults.setdefault('features', detail.features)
        defaults.setdefault('offer_type', detail.offer_type)


class Order:
    """Expose the manager interface expected by the mentor script."""

    objects = OrderManagerAdapter()


__all__ = ['Order']
