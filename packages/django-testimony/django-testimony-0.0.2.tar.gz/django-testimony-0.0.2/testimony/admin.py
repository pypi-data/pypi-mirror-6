from django.contrib import admin
from models import Testimonial, TestimonialProduct

class TestimonialProductAdmin(admin.ModelAdmin):
    pass
admin.site.register(TestimonialProduct, TestimonialProductAdmin)

class TestimonialAdmin(admin.ModelAdmin):
    ### List display
    list_display = (
        'author',
        'product',
        'published',
        )
    list_editable = [
        'published',
        ]
    search_fields = [
        'author',
        'testimony',
        ]
    list_filter = [
        'published',
        ]
    #date_hierarchy = 'created'
    list_per_page = 100
    list_select_related = True

    ### Record display
    fieldsets = (
        ('General', {
            #'classes': ('collapse',),
            'description': 'General',
            'fields': (
                'author',
                'testimony',
                'product',
           )}),
        ('Admin', {
            #'classes': ('collapse',),
            'description': 'Publishing information bits.',
            'fields': (
                'published',
           )}),
        )
    #readonly_fields = ['date_given']
admin.site.register(Testimonial, TestimonialAdmin)



