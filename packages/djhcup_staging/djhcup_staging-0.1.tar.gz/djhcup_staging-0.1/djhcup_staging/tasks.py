# core Python packages
import datetime, os, logging, itertools
from copy import deepcopy


# third party packages
import pyhcup


# django packages
from django.utils.timezone import utc
from django.conf import settings
#import shortcuts to use with raw sql (!) later
from django.db import connections as cnxns
from django.db import transaction as tx
from django import db as djangodb


# local project and app packages
from djhcup_staging.models import State, DataSource, FileType, File, Column, ImportQueue, ImportBatch, ImportTable
from djhcup_staging.utils.misc import dead_batches


# pull these settings into local namespace
from djhcup_core.defaults import DJHCUP_IMPORT_PATHS


# start a logger
logger = logging.getLogger('default')


# make these tasks app-agnostic with @celery.shared_task
import celery
from celery.result import AsyncResult


HACHOIR_DB_ENTRY = 'djhcup'

@celery.shared_task
@tx.atomic # turn off autocommit
def reset_dead():
    """Resets dead (interrupted) ImportBatch and ImportQueue objects intelligently.
    
    Types of failure:
    
    1. batch is started but not complete and celery task is no longer held in queue or being processed
        --> ignore any related ImportQueue objects where completed is not null and status is SUCCESS
        --> delete db records in related ImportTable for state-year combinations on incomplete ImportQueue objects
        Code is written in for this below
    """
    
    b_reset = 0
    iq_reset = 0
    
    # grab a database cursor for use downstream
    cursor = cnxns[HACHOIR_DB_ENTRY].cursor()

    # get the dead batches
    dead_batch_qs = dead_batches()
    
    # loop through dead batches cleaning up individual ImportQueue entries
    for b in dead_batch_qs:
        # get related ImportQueue objects
        inc_iq_qs = ImportQueue.objects.filter(batch__pk=b.pk)
        
        # but leave any successful imports alone
        dead_iq_qs = inc_iq_qs.exclude(status='SUCCESS')
        
        # make a list of tuples representing the state-years to roll back
        rollback_lst = [(iq.file.state.abbreviation, iq.file.year) for iq in dead_iq_qs]
        
        # build a SQL delete statement and list of parameters to delete records for these dead imports
        sql = "DELETE FROM "
        
        # tack on table identity (w/optional schema)
        table = b.destination.name
        if b.destination.schema is not None:
            table = b.destination.schema + "." + table
        sql += table
        
        # form WHERE clause with placeholders
        sql += " WHERE " + " OR ".join("(STATE=%s AND YEAR=%s)" for rb in rollback_lst)
        
        # cap it off
        sql += ";"
        
        params = [val for y in rollback_lst for val in y]
        
        # execute the deletes
        cursor.execute(sql, params)
        
        # the staging db has auto-commit turned off by default
        tx.commit(using=HACHOIR_DB_ENTRY)
        
        [logger.info("Deleted records in %s for %s %s" % (table, v[0], v[1])) for v in rollback_lst]
        logger.info("Total records deleted: %s" % cursor.rowcount)
        
        # move on to resetting the ImportQueue objects themselves
        dead_iq_qs.update(start=None, complete=None, status='NEW')
        iq_reset += dead_iq_qs.count()
        
        # and, finally, the batch, too
        b.start=None
        b.complete=None
        b.status='NEW'
        b.save()
        
        b_reset += 1
    
    logger.info("Reset %s dead ImportBatch objects and %s ImportQueue objects" % (b_reset, iq_reset))
    return b_reset, iq_reset


@celery.shared_task(bind=True, ignore_result=True)
def batch_import(self, batch_id, load_chunksize=5, placeholder_representation="%s"):
    """Attempts to import the indicated batch"""
    
    batch = ImportBatch.objects.get(pk=batch_id)
    batch.status = 'RECEIVED'
    batch.celery_task_id = self.request.id
    batch.save()
    
    enqueued = ImportQueue.objects.filter(batch=batch)
    destination = batch.destination
    logger.info('Found %s' % (batch))
    
    if batch.complete:
        response = 'Batch %i was previously completed at %s, and therefore will not be run' % (batch.pk, batch.complete)
        logger.error(response)
        return False
    
    elif enqueued.count() < 1:
        response = 'Batch %i has no items enqueued, and therefore will not be run' % batch.pk
        logger.warning(response)
        return True
    
    #make sure the items in the batch have the same data source as the destination table
    elif not all(x.file.file_type.source == destination.source for x in enqueued):
        response = 'One or more items enqueued in batch %i has a different data source than was used to generate the master table intended to receive data (destination master table data source is %s), and therefore the batch will not be run' % (batch.pk, batch.destination.source)
        logger.error(response)
        [logger.error('%s has data source %s' % (x, x.file.file_type.source)) for x in enqueued if x.file.file_type.source != destination.source]
        return False
        
    else:
        #proceed with batch import
        logger.info('All enqueued files appear to have same data source as destination (%s)' % destination.source)
        
        batch_begin = datetime.datetime.utcnow().replace(tzinfo=utc)
        batch.start = batch_begin
        batch.status = 'IN PROCESS'
        batch.save()
        logger.info('Begin batch %s' % (batch))
        
        # DEPRECATED
        """
        for load in enqueued:
            load.status = 'QUEUED'
            load.save()
            import_file(load.pk)
        
        return batch_complete.delay(batch.pk)
        """
        
        # make a chain from task signatures that churn through each enqueued object
        import_chain = celery.chain(
            import_file.si(load.pk) for load in enqueued
            )
        
        # this could, alternatively, be a task group
        
        # fire the chain
        import_chain()
        
        # put a task into background for periodic check that the batch has completed
        batch_complete.apply_async((batch.pk,), countdown=60)
        
        return True


@celery.shared_task(bind=True, ignore_result=True)
def import_file(self, importqueue_pk, insert_size=5, slice_size=1000):
    load = ImportQueue.objects.get(pk=importqueue_pk)
    load.celery_task_id = self.request.id
    load.save()
    
    destination = load.batch.destination
    similar_load_qs = ImportQueue.objects.filter(batch__destination=destination, file=load.file)
    similar_completed = similar_load_qs.filter(complete__isnull=False)
    similar_started = similar_load_qs.filter(start__isnull=False)
    

    if similar_completed.count() > 0:
        #appears to already have been imported. skip this one
        logger.warning('It looks like <%s> was already imported to <%s> at %s; skipping for now' % (load, destination, similar_completed[0].complete))
        load.fail()
        return False
    
    elif similar_started.count() > 0:
        #appears to already have been imported. skip this one
        logger.warning('It looks like an import was already started for importing <%s> to <%s> at %s; skipping for now' % (load, destination, similar_started[0].start))
        load.fail()
        return False

    else:
        # proceed with making the file happen
        load.status = 'IN PROCESS'
        load.start = datetime.datetime.utcnow().replace(tzinfo=utc)
        load.save()
        
        logger.info('Begin import of %s to %s' % (load, destination))
        
        tls = destination.source.top_level_source.abbreviation
        if tls == 'HCUP':
            meta = pyhcup.sas.meta_from_sas(load.file.loadfile.full_path)
            augmented = pyhcup.meta.augment(meta)
            
            #store the columns for future reference
            for k, v in augmented.T.to_dict().iteritems():
                #col_supplemental_meta = pyhcup.db.col_from_invalue(v['informat'])
                col = Column(
                    parent_file=load.file,
                    name=v['field'],
                    col_type=v['data_type'].upper(),
                    col_scale=v['scale'],
                    col_precision=v['length'],
                    informat=v['informat'],
                    )
                col.save()
        
        elif tls == 'PUDF':
            meta = pyhcup.tx.meta_from_txt(load.file.loadfile.full_path)
            augmented = pyhcup.meta.augment(meta, dialect='PUDF')
            
            #store the columns for future reference
            for k, v in augmented.T.to_dict().iteritems():
                #col_supplemental_meta = pyhcup.db.col_from_invalue(v['informat'])
                col = Column(
                    parent_file=load.file,
                    name=v['field'],
                    col_type=v['data_type'].upper(),
                    col_scale=v['scale'],
                    col_precision=v['length'],
                    # informat=v['informat'],
                    )
                col.save()
        
        if load.file.file_type.compression == 'NONE':
            #uncompressed
            handle = open(load.file.full_path)
        elif load.file.file_type.compression == 'ZIP':
            #pkzip compression
            handle = pyhcup.hachoir.openz(os.path.dirname(load.file.full_path), load.file.filename)
        
        # make a generator to yield one slice_size slice of the file in question at a time
        reader = pyhcup.parser.read(handle, meta, chunksize=slice_size)
        
        table = destination.name
        schema = destination.schema
        state = load.file.state.abbreviation
        year = load.file.year
        
        
        # take 5
        # loop through slices and dispatch chunker.chunks() for each
        # this is preferred to a chain so that it doesn't wait to start until after all the signatures are generated
        result_lst = []
        for df in reader:
            result_lst.append(chunker(
                    df,
                    table,
                    schema,
                    state,
                    year, 
                    insert_size
                    )
                )
        
        import_complete.apply_async((result_lst, load.pk), countdown=10)
        return True


@celery.shared_task
def chunker(df_slice, table, schema, state, year, insert_size=5):
    """These should be slices far too large to build a SQL string on; e.g. >100"""
    
    r = xrange(0, len(df_slice), insert_size)
    
    # build chunks of insert jobs and turn it into a group
    job = chunk_insert.chunks(
        zip(
            (df_slice[x:x+insert_size] for x in r),
            (table for x in r),
            (schema for x in r),
            (state for x in r),
            (year for x in r),
            ),
        10
        ).group()
    
    return job.delay() # gives back an async resultgroup object
    # for which .ready() will be True if all tasks have completed
    # and for which .successful() will be True if all tasks were successfully completed


@celery.shared_task
@tx.atomic # turn off autocommit
def chunk_insert(df_chunk, table, schema, state, year, placeholder_representation="%s"):    
    # everything we insert will always have a state and year associated with it
    # if they aren't already in the frame, add them from the passed values
    # (which should in turn be from the loadfile object)
    if 'state' not in df_chunk.columns.map(lambda x: str(x).lower()):
        df_chunk['state'] = state
    
    if 'year' not in df_chunk.columns.map(lambda x: str(x).lower()):
        df_chunk['year'] = year
        
    cursor = cnxns[HACHOIR_DB_ENTRY].cursor()
    
    df_chunk = pyhcup.parser.replace_sentinels(df_chunk)
    
    try:
        insert_sql, values = pyhcup.db.insert_sql(df_chunk, table=table, schema=schema, placeholder=placeholder_representation)
        #logger.debug('Generated sql and values lists (params)')
        cursor.execute(insert_sql, values)
        #logger.debug('Executed sql using params')
        
    except:
        e = sys.exc_info()[0]
        logger.warning('Failed to insert chunk; records from state-year %s-%s in table %s are likely incomplete and may need to be purged (%s)' % (state, year, table, e))
        return False
    
    tx.commit(using=HACHOIR_DB_ENTRY)
    #logger.debug('Committed transaction')
    
    # Do not hold a copy of the query.
    djangodb.reset_queries()
    #logger.debug('Inserted chunk successfully from state-year %s-%s to table %s' % (state, year, table))
    return cursor.rowcount


@celery.shared_task(bind=True, max_retries=None, default_retry_delay=10)
def import_complete(self, result_lst, importqueue_pk):
    """Checks periodically to see if these have completed and updates associated ImportQueue obj with outcome
    """
    
    iq = ImportQueue.objects.get(pk=importqueue_pk)
    des = iq.batch.destination
    
    
    if all(r.ready() for r in itertools.chain(*result_lst)):
        if all(r.successful() for r in itertools.chain(*result_lst)):
            iq.success()
            logger.info('Import complete: %s' % iq)
            return True
        else:
            iq.fail()
            logger.error('Import failed: %s' % iq)
            raise Exception('Import failed: %s' % iq)
    else:
        raise self.retry(exc=Exception('Import not yet complete: %s' % iq))


@celery.shared_task(bind=True, max_retries=None, default_retry_delay=60)# default_retry_delay=60)
def batch_complete(self, batch_pk):
    """Checks to see if each item in the batch has a completion timestamp in db, and updates batch db entry to reflect success/failure of overall batch.
    """
    
    # grab the django representation of this ImportBatch
    b = ImportBatch.objects.get(pk=batch_pk)
    
    # and, while we're at it, the associated ImportQueue objects
    enqueued = ImportQueue.objects.filter(batch=b)
    
    try:
        # test if all completed, one way or another
        if all(q.complete is not None for q in enqueued):
            
            # test if the outcomes were all SUCCESS
            if all(q.successful() for q in enqueued):
                b.success()
                logger.info('Batch completed successfully: %s' % b)
                return True
            else:
                b.fail()
                logger.error('One or more imports failed: %s' % b)
                return False
        else:
            # since some haven't completed yet, raise IncompleteStream and retry
            raise celery.exceptions.IncompleteStream
    
    except celery.exceptions.IncompleteStream as exc:
        # try again a little later, when the streams are more complete
        raise self.retry(exc=Exception('Batch not yet complete: %s' % b))
