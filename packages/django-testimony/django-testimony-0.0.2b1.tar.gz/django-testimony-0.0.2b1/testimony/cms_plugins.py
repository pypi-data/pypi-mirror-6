from django.utils.translation import ugettext_lazy as _
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from models import Testimonial, TestimonialPlugin as TestimonialPluginModel


class TestimonialPlugin(CMSPluginBase):
    module = "Oddotter"
    model = TestimonialPluginModel
    name = _("Testimonials Listing")
    render_template = "testimony/plugin.html"
    text_enabled = True
    admin_preview = False
    fieldsets = (
        (None, {
            'fields': (
                'block',
                ('size', 'product'),
                ('list_type','template_path',),
        )}),
    )

    def render(self, context, instance, placeholder):
        list_type = instance.list_type or 0

        testimonials = Testimonial.objects.all().filter(published=True)
        if instance.product:
            testimonials = testimonials.filter(product=instance.product)
        testimonials = testimonials.order_by('?')

        max = instance.size
        if max > testimonials.count():
            max = testimonials.count()

        context.update({'testimonials':testimonials[:max],})
        context.update({'instance': instance,})
        context.update({'content': instance.render(context),})

        return context

plugin_pool.register_plugin(TestimonialPlugin)




    

