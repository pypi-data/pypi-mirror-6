from django.db import models
from django.core.exceptions import ValidationError
from django.template import TemplateSyntaxError, TemplateDoesNotExist, loader
from django.utils.translation import ugettext_lazy as _
from cms.models import CMSPlugin
import settings


class TestimonialProduct(models.Model):
    name = models.CharField(_("product name"), max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        ordering = ["name"]

class Testimonial(models.Model):
    author = models.CharField(_("author's name"), max_length=100)
    testimony = models.TextField(_("testimonial"), help_text='Describe your experience with us')
    published = models.BooleanField(_('published'), default=False, help_text='publish this testimonial to the public')
    product = models.ForeignKey(TestimonialProduct, blank=True, null=True)

    def __unicode__(self):
        return self.author

    class Meta:
        verbose_name = _('testimony')
        verbose_name_plural = _('testimonies')
        ordering = ["author"]



LIST_TYPE_CHOICES = (
        ('random', 'random'),
    )    
class TestimonialPlugin(CMSPlugin):
	
    block = models.CharField(_('Title'), max_length=200)
    size = models.IntegerField(_('size'), help_text='number of testimonials to show in this block')
    list_type = models.CharField(_('list type'), max_length=10, choices=LIST_TYPE_CHOICES, default=LIST_TYPE_CHOICES[0][0])
    product = models.ForeignKey(TestimonialProduct, blank=True, null=True, help_text="(chose nothing to select from all categories")
    template_path = models.CharField(_("Template"), max_length=100, choices=settings.TESTIMONY_TEMPLATES, default=settings.TESTIMONY_TEMPLATES[0],
        help_text=_('Enter a template (i.e. "testimony/list_default.html") which will be rendered.'))

    def __unicode__(self):
        return self.block
    
    def get_template(self):
        template_path = self.template_path or "testimony/list_default.html"
        try:
           testimonial_template = loader.get_template(template_path)
        except (TemplateSyntaxError, TemplateDoesNotExist), e:
            raise ValidationError(str(e))
       
        return testimonial_template
        
    def render(self, context):
        return self.get_template().render(context)
