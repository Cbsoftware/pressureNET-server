from PIL import ImageFilter


class GaussianBlurSpec(object):

    def process(self, image):
        print 'blurring image'
        return image.filter(ImageFilter.GaussianBlur(radius=50))
