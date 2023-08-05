from PIL import Image
from tw2.core import Validator, ValidationError
from tw2.forms import FileValidator
from tg.i18n import lazy_ugettext as l_



class RangeDateValidator(Validator):
    def __init__(self, from_date, to_date, **kw):
        super(RangeDateValidator, self).__init__(**kw)
        self.from_date = from_date
        self.to_date = to_date

    def _validate_python(self, values, state=None):
        if values.get(self.from_date) > values.get(self.to_date):
            raise ValidationError(l_('Starting date must be previous than ending date'), self)


class ImageValidator(FileValidator):

    format = ()
    size = ()
    def __init__(self, **kw):
        super(ImageValidator, self).__init__(**kw)


    def _validate_python(self, image, state=None):
        try:
            img = Image.open(image.file)
            image.file.seek(0)
        except:
            raise ValidationError(l_('Invalid Image'), self)
        if self.format and img.format.lower() not in self.format:
            raise ValidationError(l_('Image format is invalid, must be %s' % (self.format,)), self)
        if self.size and img.size != self.size:
            raise ValidationError(l_('Image size must be %s * %s' % (self.size[0], self.size[1])), self)
