from PIL import ImageFilter


class GaussianBlurSpec(object):

    def process(self, image):
        return image.filter(ImageFilter.GaussianBlur(radius=20))
