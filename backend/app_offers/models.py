from offers_app.models import Offer as ProjectOffer
from offers_app.models import OfferDetail


class OfferManagerAdapter:
    """Maps the mentor script's user field to creator."""

    @staticmethod
    def get_or_create(defaults=None, **kwargs):
        user = kwargs.pop('user', None)
        if user is not None:
            kwargs['creator'] = user
        return ProjectOffer.objects.get_or_create(
            defaults=defaults,
            **kwargs,
        )


class Offer:
    """Exposes the manager interface expected by the mentor script."""

    objects = OfferManagerAdapter()


if not hasattr(ProjectOffer, 'user'):
    ProjectOffer.user = property(lambda self: self.creator)


__all__ = ['Offer', 'OfferDetail']
