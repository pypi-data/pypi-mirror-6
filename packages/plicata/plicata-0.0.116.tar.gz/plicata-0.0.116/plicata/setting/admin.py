from django.contrib import admin

from .models import Setting


class SettingAdmin(admin.ModelAdmin):
    pass


admin.site.re(Setting,SettingAdmin)
