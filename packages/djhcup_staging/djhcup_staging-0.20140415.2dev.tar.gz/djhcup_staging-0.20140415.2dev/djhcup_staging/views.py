# core Python packages
import datetime
import logging
import os
import sys


# third party packages
import pandas as pd
import pyhcup


# django packages
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.timezone import utc
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import connections as cnxns
from django.db import transaction as tx


# local project and app packages
import djhcup_staging
from djhcup_staging.models import State, DataSource, FileType, File, Column, ImportQueue, ImportBatch, ImportTable
from djhcup_staging.utils.misc import dead_batches


# move these into the local namespace
DJHCUP_IMPORT_PATHS = settings.DJHCUP_IMPORT_PATHS


# kludge workaround--move to config later
DJHCUP_DB_ENTRY = 'djhcup'

# start a logger
logger = logging.getLogger('default')


# Create your views here.
def index(request):
    logger.debug('Index requested')
    
    link_list = [
        {'display': 'Files',
         'href': reverse('file_inventory'),
         },
        {'display': 'Data source definitions',
         'href': reverse('source_inventory'),
         },
        {'display': 'Batches',
         'href': reverse('batch_inventory'),
         },
        ]

    link_list.extend([{'display': 'Incomplete Batch: %s' % x, 'href': '/batches/%d/' % x.pk} for x in ImportBatch.objects.filter(complete__isnull=True)])
    
    context = {
        'title': 'Hachoir: Staging', 
        'links': link_list,
        }
    template = 'djhcup_staging_base.html' #automagically looks in the templates directory for this app
    return render(request, template, context)


def source_inventory(request):
    logger.debug('DataSource inventory requested')
    sources = DataSource.objects.all()
    sources_tl = sources.filter(parent__isnull=True)
    sources_lst = [o for o in sources_tl]

    context = {
        'title': 'DataSource inventory', 
        'counts': [
            {'name': 'Total DataSources specified in database', 'value': sources.count()},
            {'name': 'Top-level DataSources (without a parent DataSource)', 'value': sources_tl.count()},
            ],
        'objects': sources_lst,
        'links': [],
        }
    
    if len(sources_lst) == 0:
        # no sources found--offer to plug in the defaults
        context['links'].append({
            'display': 'Populate default source definitions for HCUP and Texas PUDF&rarr;',
            'href': reverse('source_populate_defaults'),
            })
    
    template = 'djhcup_staging_inventory.html' #automagically looks in the templates directory for this app
    return render(request, template, context)


def source_populate_defaults(request):
    """Generate source definitions, patterns, etc. using defaults in utils.defaults
    """

    logger.info('Attempting to populate default source records')
    from utils import defaults
    
    try:
        e = None
        defaults.populate_hcup()
        logger.info('Populated HCUP source entries successfully')
        
        defaults.populate_pudf()
        logger.info('Populated Texas PUDF source entries successfully')
    except:
        e = sys.exc_info()[0]
        e_msg = 'Encountered an error while trying to populate HCUP and Texas PUDF default sources: %s' % e
        logger.error(e_msg)
    
    response_messages = []
    if e is None:
        response_messages.append({
            'content': 'Populated HCUP and Texas PUDF source entries successfully.',
            'type': 'info'
            })
    else:
        response_messages.append({
            'content': e_msg,
            'type': 'error'
            })
    
    context = {
        'title': 'Generate Master Table',
        'response_messages': response_messages,
        }
    
    template = 'djhcup_staging_base.html'
    return render(request, template, context)


def source_detail(request, source_id):
    logger.debug('DataSource %i detail requested' % int(source_id))
    
    source = DataSource.objects.get(pk=source_id)
    children = DataSource.objects.filter(parent=source)
    files = File.objects.filter(file_type__source=source)
    file_types = FileType.objects.filter(source=source)
    
    import_tables = ImportTable.objects.filter(source=source)
    
    context = {
        'object_type': type(source),
        'object': source,
        'children': children,
        'files': {
                  'content': files.exclude(file_type__content_type__in=['LOAD']),
                  'load': files.filter(file_type__content_type__in=['LOAD']),
                 },'staging/files/'
        'file_types': file_types,
        'import_tables': import_tables,
        }
    
    template = 'djhcup_staging_source_detail.html'
    return render(request, template, context)


def file_inventory(request):
    logger.debug('File inventory requested')
    known_files = File.objects.all()
    content_files = known_files.exclude(file_type__content_type__in=['LOAD'])
    c_content_files = content_files.count()
    c_unmatched_content_files = content_files.filter(loadfile__isnull=True).count()
    c_matched_content_files = c_content_files - c_unmatched_content_files
    
    load_files = known_files.filter(file_type__content_type__in=['LOAD'])
    c_load_files = load_files.count()

    context = {
        'title': 'File Inventory', 
        'counts': [
            {'name': 'Total Content Files', 'value': c_content_files},
            {'name': 'Unmatched Content Files', 'value': c_unmatched_content_files},
            {'name': 'Matched Content Files', 'value': c_matched_content_files},
            {'name': 'Total Load Files', 'value': c_load_files},
            ],
        
        'links':   [{
                    'display': 'Discover files in DJHCUP_IMPORT_PATHS (%s)' % (DJHCUP_IMPORT_PATHS),
                    'href': reverse('file_discover'),
                    },
                    {
                    'display': 'Match discovered files',
                    'href': reverse('file_match'),
                    }],
        }
    template = 'djhcup_staging_inventory.html'
    return render(request, template, context)


def file_discover(request):
    template = 'djhcup_staging_base.html'
    
    discovered = []
    sources = DataSource.objects.all()
    file_types = FileType.objects.all().prefetch_related('source')
    states = State.objects.all()
    [state for state in states]#force fetch. I think...
        
    source_list = []

    for source in sources:
        for file_type in file_types:
            if source == file_type.source:
                #include this pattern with this source
                source_dict = {
                    'name': file_type,#TODO: this is kludgy work but would require work in the pyhcup library itself
                    'patterns': [file_type.pattern],
                    }
                source_list.append(source_dict)
    
    if len(source_list) > 1:
        result = {}
        result['pattern_count'] = len(source_list)
        logger.info("Retrieved %d patterns from the database, matching the following file types:" % (result['pattern_count']))
        [logger.info(str(x['name'])) for x in source_list]
    
        hits = []
        for p in DJHCUP_IMPORT_PATHS:
            phits = pyhcup.hachoir.discover(p, sources=source_list)
            if phits is not None:
                hits.extend(phits)
        
        if hits is None:
            logger.info("Discovered no file(s) in DJHCUP_IMPORT_PATHS (%s) matching patterns" % (DJHCUP_IMPORT_PATHS))
            
        else:
            logger.info("Discovered %d file(s) in DJHCUP_IMPORT_PATHS (%s) matching patterns" % (len(hits), DJHCUP_IMPORT_PATHS))
            
            for hit in hits:
                # append some housekeeping things that were impossible to know until regex was captured
                # then check to see if this hit is known in the db already; if not, add it

                # SUPER KLUDGE
                # All the Texas PUDF filenames omit TX, Texas, or any other indication of state.
                # However, they are the only ones which all begin with "PUDF" or "pudf"
                # Also the ones included in PyHCUP _do_ begin with tx
                if hit['filename'][:4].lower() == 'pudf' or hit['filename'][:2].lower() == 'tx':
                    state_abbr = 'TX'
                else:
                    # each of these should have a state_abbr by virtue of the captured regex patterns
                    state_abbr = hit['state_abbr']
                check_state = states.filter(abbreviation=state_abbr)
                if check_state:
                    state = check_state[0]
                else:
                    #heretofor an undocumented state
                    #add it and refresh the known states
                    state = State(abbreviation=state_abbr)
                    state.save()
                    states = State.objects.all()
                    [state for state in states]#force fetch. I think...
                
                candidate = {
                    'file_type': hit['source'],
                    'state': state,
                    'filename': hit['filename'],
                    'year': hit['year'], #captured by our regex, not a standard hachoir.discover result
                    'filename': hit['filename'],
                    'full_path': hit['full_path'],
                    'size_on_disk': hit['size_on_disk'],
                    }
                
                # omit if this full_path is already stored in the database somewhere
                check_exists = File.objects.filter(full_path=candidate['full_path']).count()
                if check_exists == 0:
                    discovery = File(**candidate)
                    discovery.save()
                    discovered.append(discovery)
            
            result['hit_count'] = len(hits)
            result['discovered_count'] = len(discovered)
            logger.info("%d file(s) already in the database. Added %d file(s) not previously in database" % (len(hits) - len(discovered), len(discovered)))
        
    else:
        logger.info("No patterns found")
            
    context = {
        'title': 'File Discovery',
        }
    return render(request, template, context)


def file_match(request):    
    #grab all known files and split them into content vs load files
    known_files = File.objects.all()
    unmatched_content = known_files.filter(loadfile__isnull=True).exclude(file_type__content_type__in=['LOAD'])
    loadfiles = known_files.filter(file_type__content_type__in=['LOAD'])
    logger.info("Found %d content files without loadfile matches." % len(unmatched_content))
    logger.info("Found %d loadfiles." % len(loadfiles))
    
    #prepare to count matches made
    matches_made = 0
    for unmatched in unmatched_content:
        matching_loadfile = None
        
        #match on state, year, and source (parent of file_type)
        possible_matches = loadfiles.filter(state=unmatched.state, year=unmatched.year, file_type__source=unmatched.file_type.source)
        if len(possible_matches) == 1:
            matching_loadfile = possible_matches[0]
            
        elif len(possible_matches) > 1:
            #check to see if all the possible_matches generate the same meta DataFrame
            #if they do, then they are functionally equivalent and we can pick one (the first) to match as the loadfile
            
            meta_df_list = [pyhcup.sas.meta_from_sas(lf.full_path) for lf in possible_matches]
            if all(x == meta_df_list[0] for x in meta_df_list):
                #these are functionally equivalent, so match the content to the first possible match
                matching_loadfile = possible_matches[0]
            else:
                #more than one match, and they generate different meta DataFrame objects
                #TODO: Build GUI for handling these besides the admin panel?
                logger.warning('More than one match (with differing meta content) for content %s: %s.' % (unmatched.pk, ', '.join([str(x.pk) for x in possible_matches])))
        
        if matching_loadfile is not None:
            unmatched.loadfile = matching_loadfile
            unmatched.save()
            matches_made += 1
    
    logger.info("Matched %s pairs of files with unambiguous similarity." % matches_made)
    
    context = {
        'title': 'File Matching',
        }
    template = 'djhcup_staging_base.html' #automagically looks in the templates directory for this app
    return render(request, template, context)


def src_gen_master_table(request, source_id):
    """For wide data, use all known loadfiles for source and generate one master table. For long data (or data which can be longed), make the corresponding fixed-style table.
    """
    
    source = DataSource.objects.get(pk=source_id)
    logger.info('Attempting to generate master table for %s' % source)
    
    cursor = cnxns[DJHCUP_DB_ENTRY].cursor()

    # need later for table creation, but want the value to be based on the start of the process
    now = datetime.datetime.utcnow().replace(tzinfo=utc).strftime("%Y%m%d%H%M%S")    
    db_table = "%s_%s" % (source.mr_descriptor, now)
    pk_fields = []
    index_fields = []
    
    # check to see whether this source has a LONG_MAPS entry, which would indicate it ought to be a long table
    from pyhcup.parser import LONG_MAPS
    if source.abbreviation in LONG_MAPS.keys():
        logger.info('Match found in LONG_MAPS. This should be a fixed-style long table.')
        create_sql = pyhcup.db.long_table_sql(db_table, str(source.abbreviation))
        index_fields = ['KEY', 'VISITLINK', 'STATE', 'YEAR']
    
    else:
        logger.info('No match found in LONG_MAPS. This should be a dynamically-generated wide table.')
        
        src_loadfiles = File.objects.filter(file_type__content_type__in=['LOAD'], file_type__source=source)
        logger.info('Found %d loadfile records matching source' % len(src_loadfiles))
        
        meta_list = []
        excluded = []
        for lf in src_loadfiles:
            try:
                if lf.state.abbreviation.lower() == 'tx':
                    # read the meta using the tx pudf stuff
                    mdf = pyhcup.tx.meta_from_txt(lf.full_path)
                    # mdf['state'] = 'tx'
                    # mdf['year']
                    augmented = pyhcup.meta.augment(mdf, dialect='pudf')
                
                else:
                    # read the meta using the sas stuff
                    mdf = pyhcup.sas.meta_from_sas(lf.full_path)
                    augmented = pyhcup.meta.augment(mdf)
                
                # in any case, put in the meta list collection
                meta_list.append(augmented)
                
            except:
                # failed to read these in for some reason; held here for debug
                excluded.append(lf.full_path)
        
        merged_meta = pyhcup.meta.merge(meta_list)
        logger.info('Merged %d meta DataFrames successfully, with %d columns after de-duplication' % (len(meta_list), len(merged_meta)))
        
        constraints = ['NULL']
        if source.top_level_source.abbreviation == 'HCUP':# redundant # and source.abbreviation not in LONG_MAPS.keys():
            pk_fields = ['year', 'state', 'key']
            index_fields += pk_fields
        
        create_sql = pyhcup.db.table_sql(merged_meta, db_table, pk_fields=pk_fields, ine=True, append_state=True, default_constraints=constraints)
        
    try:
        cursor.execute(create_sql)
        tx.commit(using=DJHCUP_DB_ENTRY)
    except:
        e = sys.exc_info()[0]
        raise Exception("Failed to create master table with query %s (%s)" % (create_sql, e))
    
    logger.info('Created master table %s with on database %s' % (db_table, DJHCUP_DB_ENTRY))
    
    if index_fields != None:
        try:
            for col in index_fields:
                index = pyhcup.db.index_sql(col, db_table)
                cursor.execute(index)
                tx.commit(using=DJHCUP_DB_ENTRY)
                logger.info('Created index for column %s with on table %s' % (col, db_table))
        except:
            raise Exception("Failed to create indexes on table, particularly one that should have resulted from this query: %s" % index)
    
    table_record = ImportTable(source=source, name=db_table, database=DJHCUP_DB_ENTRY)
    table_record.save()
    logger.info('Saved master table details as ImportTable record %d' % table_record.pk)
    
    context = {
        'title': 'Generate Master Table',
        }
    template = 'djhcup_staging_base.html'
    return render(request, template, context)


def batch_inventory(request):
    logger.debug('Batch inventory requested')
    batches = ImportBatch.objects.all()
    completed = batches.filter(complete__isnull=False)
    not_started = batches.filter(start__isnull=True)
    started = batches.filter(start__isnull=False, complete__isnull=True)
    
    dead = dead_batches()
    if dead:
        # don't include dead batches in the started listing
        started = started.exclude(pk__in=[d.pk for d in dead])

    context = {
        'title': 'Batch inventory', 
        'counts': [
            {'name': 'Total batches', 'value': batches.count()},
            {'name': 'Not started', 'value': not_started.count()},
            {'name': 'Started', 'value': started.count()},
            {'name': 'Completed', 'value': completed.count()},
            ],
        'dead': dead,
        'not_started': not_started,
        'started': started,
        'completed': completed,
        }
    template = 'djhcup_staging_batch_inventory.html' # automagically looks in the templates directory for this app
    return render(request, template, context)


def batch_detail(request, batch_id):
    logger.debug('Batch %s detail requested' % batch_id)
    batch = ImportBatch.objects.get(pk=batch_id)
    enqueued_files = ImportQueue.objects.filter(batch=batch)
    
    context = {
        'title': 'Details for %s' % batch,
        'batch': batch,
        'enqueued_files': enqueued_files,
        }
    if enqueued_files.count() > 0:
        context['eta'] = sum([f.est_runtime for f in enqueued_files])
    
    template = 'djhcup_staging_batch_detail.html'
    return render(request, template, context)


def batch_import(request, batch_id, load_chunksize=5, placeholder_representation="%s"):
    """Schedules the indicated batch_id for import using Celery"""
    logger.debug('Batch %s import requested' % batch_id)
    
    # import tasks for this module
    from djhcup_staging import tasks
    
    logger.info('Attempting to call a Celery task for importing batch_id %i' % (int(batch_id)))
    tresult = tasks.batch_import.delay(batch_id, load_chunksize, placeholder_representation)
    
    response = "Batch has been dispatched to Celery in thread %s; its completion state is %s" % (tresult, tresult.state)
    logger.info(response)
    
    context = {
        'title': 'Import Batch',
        'response_messages': [{'content': response, 'type': 'info'}],
        }
    template = 'djhcup_staging_base.html'
    return render(request, template, context)


def batch_reset_dead(request):
    """Dispatches a celery task to reset interrupted ImportBatch objects and their associated ImportQueue objects.
    """
    from djhcup_staging import tasks
    
    logger.info('Attempting to call a Celery task for resetting dead batches')
    tresult = tasks.reset_dead.delay()
    
    response = 'Reset request has been dispatched to Celery in thread %s; its completion state is %s' % (tresult, tresult.state)
    logger.info(response)
    
    context = {
        'title': 'Import Batch',
        'response_messages': [{'content': response, 'type': 'info'}],
        }
    template = 'djhcup_staging_base.html'
    return render(request, template, context)
    