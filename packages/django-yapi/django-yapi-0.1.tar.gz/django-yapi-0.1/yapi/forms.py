import logging
from django.forms.models import ModelForm

from models import ApiKey
from utils import generate_key

# Instantiate logger.
logger = logging.getLogger(__name__)

class ApiKeyModelForm(ModelForm):
    """
    Override model admin form in order to add a button that will make a new
    API key to be generated and saved.
    """
    class Meta:
        model = ApiKey
        
    def __init__(self, *args, **kwargs):
        super(ApiKeyModelForm, self).__init__(*args, **kwargs)
        self.generate_key = False
    
    def clean(self, *args, **kwargs):
        cleaned_data = super(ApiKeyModelForm, self).clean(*args, **kwargs)
        if self.data.has_key('generate_key'):
            self.generate_key = True
        return cleaned_data
    
    def save(self, commit=True):
        model = super(ApiKeyModelForm, self).save(commit=False)
        if self.generate_key:
            model.key = generate_key(model.user.email)
        if commit:
            model.save()
        return model