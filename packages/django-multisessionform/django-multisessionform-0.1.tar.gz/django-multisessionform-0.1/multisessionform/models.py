from django.forms.models import modelform_factory
from forms import MSFForm, FullForm

class MultiSessionFormMixin(object):
    
    def is_complete(self):
        return len(self._meta.fields) == len(self.complete_fields(False))
    
    def get_first_incomplete_field(self):
        '''Returns first empty field or last field if all are complete
        '''
        if not self.is_complete() and not self.pk == None:
            return self.incomplete_fields()[0].name
        if self.is_complete():
            return self.complete_fields()[-1].name

    def complete_fields(self, ignore_required_fields = True):
        fields = []
        for field in self._meta.fields:
            if ignore_required_fields and field in self.get_required_fields():
                pass
            else:
                field_val = getattr(self,field.name) 
                if not field_val in (None,''):
                    try:
                        if not field_val.isspace():
                            fields.append(field)
                    except:
                        fields.append(field)
        return fields
      
    def incomplete_fields(self):
        return [field for field in self._meta.fields if field not in self.complete_fields(False)]

    def get_form_fields(self):
        fields = []
        required_fields = self.get_required_fields()
        for field in self._meta.fields:
            if field not in required_fields:
                fields.append(field)
        return fields
    
    @classmethod
    def get_required_fields(cls):
        fields = []
        for field in cls._meta.fields:
            if not field.null:
                fields.append(field)
        return fields
    
    @classmethod
    def multisessionform_factory(cls):
        try:
            return modelform_factory(cls, form=MSFForm, exclude=[f.name for f in cls.get_required_fields()])
        except Exception, e:
            print e
            
    @classmethod
    def fullform_factory(cls):
        try:
            return modelform_factory(cls, form=FullForm, exclude=[f.name for f in cls.get_required_fields()])
        except Exception, e:
            print e