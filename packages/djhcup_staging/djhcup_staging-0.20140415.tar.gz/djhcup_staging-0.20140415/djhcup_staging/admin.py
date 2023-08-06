from django.contrib import admin

#import local models
from djhcup_staging.models import State, DataSource, FileType, File, Column, ImportQueue, ImportBatch, ImportTable

#Register models
admin.site.register(State)
admin.site.register(DataSource)
admin.site.register(FileType)
admin.site.register(File)
admin.site.register(Column)
admin.site.register(ImportQueue)

class QueueInline(admin.StackedInline):
    model = ImportQueue
    fields = ['file']
    extra = 3

class BatchAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['destination']}),
        ]
    inlines = [QueueInline]

admin.site.register(ImportBatch, BatchAdmin)
admin.site.register(ImportTable)