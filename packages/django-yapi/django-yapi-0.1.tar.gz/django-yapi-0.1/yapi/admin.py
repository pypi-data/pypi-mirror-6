from django.contrib import admin

from forms import ApiKeyModelForm
from models import ApiKey, ApiCall


class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'description', 'created_at', 'last_used', 'active')
    search_fields = ('user__email',)
    form = ApiKeyModelForm
admin.site.register(ApiKey, ApiKeyAdmin)
    

class ApiCallAdmin(admin.ModelAdmin):
    list_display = ('date', 'status', 'source_ip', 'endpoint', 'method', 'execution_time', 'user_agent',
                    'authentication_class', 'authentication_user')
    search_fields = ('source_ip',)
admin.site.register(ApiCall, ApiCallAdmin)