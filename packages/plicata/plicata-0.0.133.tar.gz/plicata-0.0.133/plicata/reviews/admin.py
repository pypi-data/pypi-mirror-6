from django.contrib import admin

from .models import Review,Quote

class ReviewAdmin(admin.ModelAdmin):
    pass

class QuoteAdmin(admin.ModelAdmin):
    pass


admin.site.register(Review, ReviewAdmin)
admin.site.register(Quote, QuoteAdmin)




