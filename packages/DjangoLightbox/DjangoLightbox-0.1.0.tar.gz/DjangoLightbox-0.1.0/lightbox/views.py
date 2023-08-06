from django.views.generic import ListView
from django.conf import settings
from django.db import models
import base64

def encode_url(request):
    return base64.b64encode(request.META['PATH_INFO'])

class ImagePageContextMixin(object):

    """Brings in context for lightbox."""

    def encode_url(self):
        return base64.b64encode(self.request.META['PATH_INFO'])

    def get_context_data(self, *args, **kwargs):
        context = super(ImagePageContextMixin, self).get_context_data(*args, **kwargs)
        context['path'] = self.encode_url()
        return context


class ImagePageMixin(object):
    """
    This is meant to be an alternative for a full screen lightbox.
    The browser should be doing the work (eg supporting mousewheel, touch events).
    
    The page should take:
    1) A url to return to when the user activates the close button
    2) A number of images in a series.
        
    """    
    paginate_by = 1

    def image_clickable(self):
        return getattr(settings, 'LIGHTBOX_IMAGE_CLICKABLE', False)
        
        
        
    def get_styles(self):
        
        bgcolor = getattr(settings, 'LIGHTBOX_BG_COLOR', '#000')
        color = getattr(settings, 'LIGHTBOX_TXT_COLOR', '#fff')
        
        styles = {'bgcolor': bgcolor, 'color': color}
                    
        return styles


    
    def get_factors(self):
        """
        Return multiplication factors for defining the relationship between 
        window height/width and the size of the image.
        """
        height_factor = getattr(settings, 'LIGHTBOX_VIEWABLE_HEIGHT_FACTOR', 0.85)
        width_factor = getattr(settings, 'LIGHTBOX_VIEWABLE_WIDTH_FACTOR', 0.85)
        
        height_ratio = getattr(settings, 'LIGHTBOX_IMAGE_WINDOW_HEIGHT_FACTOR', 0.71)
        width_ratio = getattr(settings, 'LIGHTBOX_IMAGE_WINDOW_WIDTH_FACTOR', 0.71)
        
        factors = {'view_height': height_factor,
                     'view_width': width_factor,
                     'height_ratio': height_ratio,
                     'width_ratio': width_ratio,
                     }
    
        return factors
    
    def get_lightbox_width_height(self):
        
        """
        Return dimensions for sorl thumbnail.
        """
        
        if self.request.is_mobile:
            lightbox_width = getattr(settings, 'LIGHTBOX_WIDTH_MOBILE', '800')
            lightbox_height = (int(lightbox_width) / 4) * 3 # aspect ratio 4 : 3 for ipad
        else:
            lightbox_width = getattr(settings, 'LIGHTBOX_WIDTH', '1600')
            lightbox_height = (int(lightbox_width) / 16) * 9 # aspect ration 16 : 9 for most others
            
         
            
        return lightbox_width, 'x%d' % lightbox_height
        
    def get_queryset(self):
        
        # Get the model from the args, then also try to get the related model.
        # this is -- for now -- the first relationship we encounter
        model = models.get_model(self.kwargs['app'], self.kwargs['model'])
        qs = model.objects.get(pk=self.kwargs['pk'])
        # take related_name from urls.py keyword arg.
        if self.kwargs['related_name']:
            images = self.kwargs['related_name']
        obj = getattr(qs, images) 
        return obj.all()
            
    def get_context_data(self, *args, **kwargs):
        context = super(ImagePageMixin, self).get_context_data(**kwargs)

        context['lightbox_width'] = self.get_lightbox_width_height()[0]
        context['lightbox_height'] = self.get_lightbox_width_height()[1]
        context['lightbox_image_clickable'] = self.image_clickable()
        context['factors'] = self.get_factors()
        context['styles'] = self.get_styles()
        
        context['app'] = self.kwargs['app']
        context['model'] = self.kwargs['model']
        context['pk'] = self.kwargs['pk']
        context['path'] = self.kwargs['path']
        if self.kwargs.has_key('template'):
            self.template_name = self.kwargs['template']
        
        return context
    
    
    
class ImagePageView(ImagePageMixin, ListView):
    template_name = 'lightbox/base.html'
