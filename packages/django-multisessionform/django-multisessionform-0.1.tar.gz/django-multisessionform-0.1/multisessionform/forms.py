from django.forms.models import ModelForm

class MSFForm(ModelForm):
    my_current_field = None
    sections = None
    def __init__(self, current_field = None, *args, **kwargs):
        super(MSFForm, self).__init__(*args, **kwargs)
        self.sections = []
        
        if current_field is None:
            self.my_current_field = self.fields.keys()[0]
        else:
            self.my_current_field = current_field
        
        if not self.my_current_field in self.fields:
            raise NameError("Field %s not in Form Fields" % (self.my_current_field))
        
        for field in self.fields:
            hf = {}
            hf['name'] = field
            hf['display'] = self.fields[field].label
            try:
                hf['value'] =  self.initial[field]
            except:
                hf['value'] = None
            self.sections.append(hf)

        self.fields = {self.my_current_field: self.fields[self.my_current_field]}
        self.fields[self.my_current_field].required = True
            
    def get_next_field_name(self):
        try:
            for hf in self.sections:
                if hf['name'] == self.my_current_field:
                    return self.sections[self.sections.index(hf)+1]['name']
        except:
            return None
        
class FullForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FullForm, self).__init__(*args, **kwargs)