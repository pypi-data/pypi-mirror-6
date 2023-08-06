import os
import datetime
import pyhcup

from django.utils.timezone import utc
from django.db import models
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.conf import settings

from djhcup_core.defaults import DATETIME_FORMAT


# Create your models here.
class State(models.Model):
    abbreviation = models.CharField(max_length=2, blank=False,
                                    db_index=True, help_text='Two-letter abbreviation for state')
    name = models.CharField(max_length=200, blank=False,
                            help_text='Full name of state')
    def __unicode__(self):
        return 'State: %s (%s)' % (self.name, self.abbreviation)


class DataSource(models.Model):
    """This is a node-based taxonomy of data sources. E.g. HCUP SID CORE is a data source abbreviated CORE, with parent SID, with parent HCUP"""
    parent = models.ForeignKey('self', default=None, blank=True, null=True)
    abbreviation = models.CharField(max_length=20, blank=False,
                                    db_index=True, help_text='Abbreviated name of data source e.g. SID')
    name = models.CharField(max_length=200, blank=False,
                            help_text='Full name of data source e.g. State Inpatient Database')
    description = models.TextField(blank=True)
        
    def _descriptor(self, separator="_"):
        abbrs = [self.abbreviation]
        if self.parent:
            current = self
            while current.parent:
                current = current.parent
                abbrs.append(current.abbreviation)
        return separator.join(abbrs[::-1])#reverse the order so it proceeds heirarchically
        
    def _hr_descriptor(self):
        return 'Source: %s' % self._descriptor(separator=">>")
    hr_descriptor = property(_hr_descriptor)
    
    def _mr_descriptor(self):
        return self._descriptor()
    mr_descriptor = property(_mr_descriptor)
    
    def _top_level_source(self):
        source = self
        while source.parent is not None:
            source = source.parent
        return source
    top_level_source = property(_top_level_source)
    
    def get_absolute_url(self):
        return reverse('djhcup_staging.views.source_detail', kwargs={'source_id': self.pk})
    
    def __unicode__(self):
        return self.hr_descriptor


class FileType(models.Model):
    """Holds regular expression patterns associated with filenames for DataSources

    Also indicates whether the pattern indicates a loadfile vs content file and if the file is compressed.
    """
    source = models.ForeignKey('DataSource')
    pattern = models.TextField(blank=False, help_text=escape('Regular expression for matching filenames. Must capture groups <state_abbr>, <year>, and <file_extension>, which will be used when recording a DataFile object later. For example, an HCUP SEDD CORE data file pattern might look like (?P<state_abbr>[A-Z]{2})_SEDD_(?P<year>[0-9]{4})_CORE\\.(?P<file_extension>asc)'))
    TYPE_CHOICES = [('LOAD', 'Loadfile (defines content)'),
                    ('CONTENTNH', 'Content (actual data) without header row'),
                    ('CONTENTWH', 'Content (actual data) with header row'),
                    ]
    content_type = models.CharField(max_length=10, choices=TYPE_CHOICES, blank=False, default='CONTENTNH')
    COMPRESSION_CHOICES = [('NONE', 'Uncompressed'),
                      ('ZIP', 'ZIP format (PKZIP)'),
                      ]
    compression = models.CharField(max_length=10, choices=COMPRESSION_CHOICES, blank=False, default='NONE')
    
    def _hr_descriptor(self):
        """Returns a shorthand description of the file type and compression"""
        if self.compression == 'NONE':
            compression_desc = 'uncompressed'
        else:
            compression_desc = '%scompressed' % (self.compression.lower())
        return '%s_%s' % (self.content_type.lower(), compression_desc)
    hr_descriptor = property(_hr_descriptor)
    
    def __unicode__(self):
        return 'FileType: %s %s' % (self.hr_descriptor, self.source)


class File(models.Model):
    file_type = models.ForeignKey('FileType')
    state = models.ForeignKey('State')
    year = models.IntegerField(blank=False, null=False, db_index=True)
    quarter = models.IntegerField(blank=True, null=True, default=None)
    filename = models.CharField(max_length=50, blank=False)
    full_path = models.CharField(max_length=200, blank=False)
    size_on_disk = models.BigIntegerField(blank=True, null=True)
    
    #partner file for actual loading, if this is a content file
    loadfile = models.ForeignKey('self', blank=True, default=None, null=True)
    
    
    def _hr_size(self):
        """Returns size in MB"""
        if self.size_on_disk:
            return self.size_on_disk/1000000
        else:
            return None
    hr_size = property(_hr_size)
    
    
    def _est_rows(self):
        if self.file_type.compression == 'NONE':
            full_size = self.hr_size
        else:
            full_size = 5*self.hr_size
        return 9850*full_size
    est_rows = property(_est_rows)
    
    
    def open(self):
        c = self.file_type.compression
        
        if c == 'NONE':
            # uncompressed
            handle = open(self.full_path)
        elif c == 'ZIP':
            # pkzip compression
            handle = pyhcup.hachoir.openz(os.path.dirname(self.full_path), self.filename)
        else:
            raise Exception("Unknown compression type %s; unable to generate file handle." % c)
        
        return handle
    
    
    class Meta:
        verbose_name = 'file'
        verbose_name_plural = 'files'
        ordering = ['file_type__source', 'state__abbreviation', 'year', 'file_type__compression', 'filename']
    
    
    def get_absolute_url(self):
        return reverse('djhcup_staging.views.file_detail', kwargs={'file_id': self.pk})
    
    
    def __unicode__(self):
        return 'File: %s (%s)' % (self.filename, self.file_type)


class ImportBatch(models.Model):
    destination = models.ForeignKey('ImportTable')
    name = models.CharField(max_length=200, blank=True, help_text="Optional name for this batch of imports")
    description = models.TextField(blank=True, help_text="Optional description for this batch of imports")
    STATUS_CHOICES = [('NEW', 'Not started'),
                      ('QUEUED', 'Request for processing sent'),
                      ('DISPATCHED', 'Sent to Celery'),
                      ('RECEIVED', 'Received by Celery'),
                      ('IN PROCESS', 'Running'),
                      ('FAILED', 'Failed to complete'),
                      ('SUCCESS', 'Completed successfully'),
                      ]
    status = models.CharField(max_length=15, blank=False, null=True, default='NEW', choices=STATUS_CHOICES)
    celery_task_id = models.TextField(blank=True, null=True, default=None)
    
    start = models.DateTimeField(blank=True, null=True, default=None)
    complete = models.DateTimeField(blank=True, null=True, default=None)

    #meta cruft
    created_at = models.DateTimeField(auto_now_add=True)
    #created_by = models.ForeignKey(django user object) #unimplemented
    void = models.BooleanField(default=False)
    voided_at = models.DateTimeField(blank=True, null=True, default=None)
    #voided_by = models.ForeignKey(django user object) #unimplemented
    
    class Meta:
        verbose_name_plural = 'import batches'
        
    def _hr_start(self):
        return self.start.strftime(DATETIME_FORMAT)
    hr_start = property(_hr_start)
    
    def _hr_complete(self):
        return self.complete.strftime(DATETIME_FORMAT)
    hr_complete = property(_hr_complete)
    
    def _runtime(self):
        if self.start and self.complete:
            return self.complete - self.start
        else:
            return None
    runtime = property(_runtime)
    
    def _hr_runtime(self):
        """Batch runtime in hours"""
        if self.runtime is not None:
            td = self.runtime
            return td.days*24+td.seconds/float(3600)
        else:
            return None
    hr_runtime = property(_hr_runtime)
    
    
    def fail(self):
        self.status = 'FAILED'
        self.complete = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()
    
    
    def success(self):
        self.status = 'SUCCESS'
        self.complete = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()
    
    
    def successful(self):
        if self.status == 'SUCCESS':
            return True
        else:
            return False
    
    
    def get_absolute_url(self):
        return reverse('djhcup_staging.views.batch_detail', kwargs={'batch_id': self.pk})
    
    def __unicode__(self):
        c_items = ImportQueue.objects.filter(batch=self).count()
        return "Batch %i [%s]: %d files, destination %s" % (self.pk, self.status, c_items, self.destination)


class ImportQueue(models.Model):
    batch = models.ForeignKey('ImportBatch')
    file = models.ForeignKey('File',
        limit_choices_to = {'loadfile__isnull': False,},
        help_text="Must point to a non-loadfile with a loadfile matched to it; this file and the import batch's destination must belong to the same data source or the batch will fail to execute")
    start = models.DateTimeField(blank=True, null=True, default=None)
    complete = models.DateTimeField(blank=True, null=True, default=None)
    STATUS_CHOICES = [('NEW', 'Not started'),
                      ('QUEUED', 'Request for processing sent'),
                      ('DISPATCHED', 'Sent to Celery'),
                      ('RECEIVED', 'Received by Celery'),
                      ('IN PROCESS', 'Running'),
                      ('FAILED', 'Failed to complete'),
                      ('SUCCESS', 'Completed successfully'),
                      ]
    status = models.CharField(max_length=15, blank=False, null=True, default='NEW', choices=STATUS_CHOICES)
    celery_task_id = models.TextField(blank=True, null=True, default=None)
    
    #meta cruft
    created_at = models.DateTimeField(auto_now_add=True)
    #created_by = models.ForeignKey(django user object) #unimplemented
    void = models.BooleanField(default=False)
    voided_at = models.DateTimeField(blank=True, null=True, default=None)
    #voided_by = models.ForeignKey(django user object) #unimplemented
    
    def _hr_start(self):
        return self.start.strftime(DATETIME_FORMAT)
    hr_start = property(_hr_start)
    
    def _hr_complete(self):
        return self.complete.strftime(DATETIME_FORMAT)
    hr_complete = property(_hr_complete)
    
    def _runtime(self):
        if self.start and self.complete:
            return self.complete - self.start
        else:
            return None
    runtime = property(_runtime)
    
    def _hr_runtime(self):
        """File runtime in hours"""
        if self.runtime is not None:
            td = self.runtime
            return td.days*24+td.seconds/float(3600)
        else:
            return None
    hr_runtime = property(_hr_runtime)
    
    def _est_runtime(self):
        # default to average across all SID CORE state-years as of 2014-03-28
        width = 164
        try:
            # attempt to find precise width for this file
            m = pyhcup.meta.get(self.file.state.abbreviation, self.file.year)
            if m is not None:
                width = len(m)
        except:
            pass
        
        est_values_per_minute = 4.5 * 10**6
        rows_per_minute = est_values_per_minute / float(width)
        rows_per_hour = rows_per_minute * 60
        
        return self.file.est_rows/(rows_per_hour)
    est_runtime = property(_est_runtime)
    
    
    class Meta:
        verbose_name = 'enqueued item'
        verbose_name_plural = 'enqueued items'
    
    
    def fail(self):
        self.status = 'FAILED'
        self.complete = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()
    
    
    def success(self):
        self.status = 'SUCCESS'
        self.complete = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()
    
    
    def successful(self):
        if self.status == 'SUCCESS':
            return True
        else:
            return False
    
    
    def record_columns(self):
        tls = self.batch.destination.source.top_level_source.abbreviation
        cols_saved = 0
        
        if tls == 'HCUP':
            meta = pyhcup.sas.meta_from_sas(self.file.loadfile.full_path)
            augmented = pyhcup.meta.augment(meta)
            
            # store the columns for future reference
            for k, v in augmented.T.to_dict().iteritems():
                #col_supplemental_meta = pyhcup.db.col_from_invalue(v['informat'])
                col = Column(
                    parent_file=self.file,
                    name=v['field'],
                    col_type=v['data_type'].upper(),
                    col_scale=v['scale'],
                    col_precision=v['length'],
                    informat=v['informat'],
                    )
                col.save()
                cols_saved += 1
        
        elif tls == 'PUDF':
            meta = pyhcup.tx.meta_from_txt(self.file.loadfile.full_path)
            augmented = pyhcup.meta.augment(meta, dialect='PUDF')
            
            # store the columns for future reference
            for k, v in augmented.T.to_dict().iteritems():
                # col_supplemental_meta = pyhcup.db.col_from_invalue(v['informat'])
                col = Column(
                    parent_file=self.file,
                    name=v['field'],
                    col_type=v['data_type'].upper(),
                    col_scale=v['scale'],
                    col_precision=v['length'],
                    # informat=v['informat'],
                    )
                col.save()
                cols_saved += 1
                
        else:
            raise Exception('No loadfile parser associated with top-level source %s' % tls)
        
        return cols_saved
    
    
    def get_meta(self):
        tls = self.batch.destination.source.top_level_source.abbreviation
        
        if tls == 'HCUP':
            loader = pyhcup.sas.meta_from_sas
        
        elif tls == 'PUDF':
            loader = pyhcup.tx.meta_from_txt
        
        else:
            raise Exception('No loadfile parser associated with top-level source %s' % tls)
        
        
        loadfile = self.file.loadfile
        
        if loadfile is None:
            raise Exception('No loadfile associated with file %s'% self.file)
        else:
            meta = loader(loadfile.full_path)
        
        return meta
    
    
    def __unicode__(self):
        return "Enqueued item %s [%s]: %s, destination %s" % (self.pk, self.status, self.file.filename, self.batch.destination.name)


class ImportTable(models.Model):
    source = models.ForeignKey('DataSource', help_text="Data source for which this table was created as a 'master' import table")
    name = models.CharField(max_length=250, blank=False)
    schema = models.CharField(max_length=250, blank=True)
    database = models.CharField(max_length=250, blank=True, help_text="Leave blank to use default connection specified in Django's setings.py file")
    #TODO: consider adding a col count
    #col_count = models.IntegerField(blank=False)
    
    #meta cruft
    created_at = models.DateTimeField(auto_now_add=True)
    #created_by = models.ForeignKey(django user object) #unimplemented
    void = models.BooleanField(default=False)
    voided_at = models.DateTimeField(blank=True, null=True, default=None)
    #voided_by = models.ForeignKey(django user object) #unimplemented
    
    def __unicode__(self):
        return "Master Table %d (%s)" % (self.pk, self.name)


class Column(models.Model):
    #TODO: determine if this is to know what columns are in a raw master table
    #... or if this is to know what columns are available from each imported state (*I think it's this one)
    #... or agnostic of import status, what columns are in a discovered loadfile
    #... or what
    parent_file = models.ForeignKey('File')
    name = models.CharField(max_length=200, blank=False,
                            db_index=True)
    
    TYPE_CHOICES = [('VARCHAR', 'Character (string)'),
                    ('NUMERIC', 'Numeric (decimal)'),
                    ('INT', 'Integer (+/- 2.1E8)'),
                    ('BIGINT', 'Integer (+/- 9.2E18)'),
                    ('BOOLEAN', 'True/False'),
                    ]
    col_type = models.CharField(max_length=100, choices=TYPE_CHOICES, blank=False)
    col_scale = models.IntegerField(blank=True, null=True, help_text='Decimal places for numeric fields')
    col_precision = models.IntegerField(blank=True, null=True, help_text='Total sigfigs for numeric fields')
    informat = models.CharField(max_length=100, blank=True, default=None, null=True,
                                help_text='SAS load informat this column is based on, if applicable')
