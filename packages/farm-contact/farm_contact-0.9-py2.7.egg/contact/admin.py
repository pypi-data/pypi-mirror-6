from django.contrib import admin
from .models import Enquiry, EnquiryType


class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'ip', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


class EnquiryTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Enquiry, EnquiryAdmin)
admin.site.register(EnquiryType, EnquiryTypeAdmin)