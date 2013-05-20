from django.views.generic.base import TemplateView


index = TemplateView.as_view(template_name='home/index.html')
livestream = TemplateView.as_view(template_name='home/livestream.html')
about = TemplateView.as_view(template_name='home/about.html')
