from celery.task import task

from leetchi.exceptions import APIError, DecodeError


@task
def create_strong_authentication(user_id, beneficiary_id=None):
    from .compat import User
    from .models import StrongAuthentication, Beneficiary

    logger = create_strong_authentication.get_logger()

    user = User.objects.get(pk=user_id)

    beneficiary = None

    if beneficiary_id:
        beneficiary = Beneficiary.objects.get(pk=beneficiary_id)

    auth = StrongAuthentication(user=user, beneficiary=beneficiary)

    try:
        auth.save()
    except APIError, exc:
        logger.error(exc)
    else:
        return auth


@task
def sync_resource(resource_klass, resource_id):
    from leetchi.base import DoesNotExist

    logger = sync_resource.get_logger()

    try:

        resource = resource_klass.objects.get(pk=resource_id)
        resource.sync_status()

        resource_name = resource_klass.__name__

        if resource.is_completed:
            if resource.is_success:
                logger.info(u'[%s]: set succeeded for %d, from leetchi resource %d' %
                            (resource_name, resource.pk, resource.resource_id))
            else:
                logger.info(u'[%s]: set aborted for %d, from leetchi resource %d' %
                            (resource_name, resource.pk, resource.resource_id))
        else:
            logger.info(u'[%s]: do nothing for %d, from leetchi resource %d' %
                        (resource_name, resource.pk, resource.resource_id))

    except (APIError, DecodeError, DoesNotExist), e:
        logger.error(e)


@task
def update_user(user_id, **kwargs):
    from .compat import User
    from .api import handler
    from .models import Wallet

    user = User.objects.get(pk=user_id)

    wallet = Wallet.objects.get_for_model(user)

    if wallet:
        payer = wallet.user

        for k, v in kwargs.items():
            setattr(payer, k, v)

        payer.save(handler)


@task
def sync_amount(wallet_id):
    from .models import Wallet

    logger = sync_amount.get_logger()

    wallet = Wallet.objects.get(pk=wallet_id)
    wallet.sync_amount()

    logger.info('[Wallet] Syncing amount for %s' % wallet_id)
