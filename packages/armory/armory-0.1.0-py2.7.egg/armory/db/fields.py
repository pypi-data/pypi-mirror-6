
from django.db import models
from django.core.exceptions import ValidationError
from ast import literal_eval


class UnicodeTextField(models.TextField):

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        def asteval(evalstring):
            result = literal_eval(evalstring)
            if not isinstance(result, unicode):
                try:
                    result = unicode(result)
                except:
                    errormsg = 'evaluated input value is %s:' % type(result)
                    errormsg += ' expected %s ' % type(unicode())
                    errormsg += ' result = %s' % result
                    errormsg += ' value = %s' % value
                    raise ValidationError(errormsg)
            return result
        if value == None:
            return unicode()
        elif isinstance(value, (str, unicode)):
            try:
                return asteval(value)
            except (SyntaxError, ValueError) as e:
                if isinstance(value, str):
                    return unicode(value)
                return value
        errormsg = 'UnicodeTextField cannot store %s values' % type(value)
        raise ValidationError(errormsg)

    def get_prep_value(self, value):
        if isinstance(value, unicode):
            return repr(value)
        elif isinstance(value, str):
            return repr(unicode(value))
        types = (type(str()), type(unicode()), type(value))
        errormsg = 'expecting %s or %s: got %s' % types
        raise ValidationError(errormsg)

