from django.contrib import admin
from models import DbConfig, Query, Dashboard

class DbConfigAdmin(admin.ModelAdmin):
  list_display = ["name", "user", "host", "db"]
  list_filter = ["host"]
admin.site.register(DbConfig, DbConfigAdmin)

class QueryAdmin(admin.ModelAdmin):
    pass
admin.site.register(Query, QueryAdmin)

class DashboardAdmin(admin.ModelAdmin):
    pass
admin.site.register(Dashboard, DashboardAdmin)