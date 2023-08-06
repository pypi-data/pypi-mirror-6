# local project and app packages
from djhcup_staging.models import ImportBatch

def dead_batches():
    # grab queryset for batches started but not completed
    inc_batch_qs = ImportBatch.objects.filter(start__isnull=False, complete__isnull=True)
    
    # need this object to check task status
    from celery.result import AsyncResult
    
    # filter down to those which are ongoing, as determined by an active (ready()==False) celery task
    wip_batch_qs = inc_batch_qs.filter(
        pk__in=(b.pk for b in inc_batch_qs if not AsyncResult(b.celery_task_id).ready())
        )
    
    # exclude the ongoing batches from the total incomplete batches
    # this generates the queryset of dead batches
    dead_batch_qs = inc_batch_qs.exclude(pk__in=[b.pk for b in wip_batch_qs])
    
    return dead_batch_qs