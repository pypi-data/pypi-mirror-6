"""Admin sites for the ``django-frequently`` app."""
from django.contrib import admin

from frequently import models


class EntryCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'fixed_position')
    list_editable = ('fixed_position', )


class EntryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('question',)}
    list_display = ('question', 'slug', 'fixed_position')
    list_editable = ('fixed_position', )


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('entry', 'user_email', 'submission_date', 'validation')

    def user_email(self, obj):
        if obj.user and obj.user.email:
            return "{0}".format(obj.user.email)
        return ""
    user_email.short_description = 'Email'


admin.site.register(models.Entry, EntryAdmin)
admin.site.register(models.EntryCategory, EntryCategoryAdmin)
admin.site.register(models.Feedback, FeedbackAdmin)
