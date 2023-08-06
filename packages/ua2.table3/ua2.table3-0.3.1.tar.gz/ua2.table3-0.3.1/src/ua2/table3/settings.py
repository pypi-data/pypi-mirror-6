from django.conf import settings

CFG_TABLE_PLUGINS = getattr(settings, 'TABLE_PLUGINS', [])
CFG_TABLE_ROW_PER_PAGE = getattr(settings, 'TABLE_ROW_PER_PAGE', 20)
CFG_TABLE_PAGE_PER_SEGMENT = getattr(settings, 'TABLE_PAGE_PER_SEGMENT', 5)
CFG_TABLE_PAGINATOR = getattr(settings, 'TABLE_PAGINATOR', None)
