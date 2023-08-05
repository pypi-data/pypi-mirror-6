from django.test import TestCase
from models import MSFExample
from multisessionform.forms import MSFForm
from multisessionform.views import MultiSessionFormView
from django.forms import fields
from django.test.client import Client
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
import re

class MSFExampleTestCase(TestCase):
    def setUp(self):
        self.tester = MSFExample.objects.create(required_field_one ="lion")
        self.form_class = MSFExample.multisessionform_factory()
        
    def test_get_required_fields(self):
        self.assertEquals(MSFExample.get_required_fields(), 
                          [field for field in MSFExample._meta.fields if field.name in ('id','required_field_one')])
        
    def test_get_incomplete_fields(self):
        self.assertEquals(self.tester.incomplete_fields(), 
                          [field for field in MSFExample._meta.fields if field.name in ('integer_field','text_field')])
    
    def test_get_complete_fields(self):
        self.assertEquals(self.tester.complete_fields(),[])

        self.assertEquals(self.tester.complete_fields(False),
                          [field for field in MSFExample._meta.fields if field.name in ('id','required_field_one')])
                
        self.tester.integer_field = 1
        self.assertEquals(self.tester.complete_fields(),
                          [field for field in MSFExample._meta.fields if field.name in ('integer_field')])
        
    def test_first_incomplete_field(self):
        self.assertEqual(self.tester.get_first_incomplete_field(), "integer_field")
        
        self.tester.integer_field = 1
        self.assertEqual(self.tester.get_first_incomplete_field(), "text_field")
        
        self.tester.text_field = 'TEXT'
        self.assertEqual(self.tester.get_first_incomplete_field(), "text_field")
           
    def test_is_complete(self):
        self.assertEqual(self.tester.is_complete(), False)
        
        self.tester.integer_field = 1
        self.tester.text_field = ' '
        self.assertEqual(self.tester.is_complete(), False)
        
        self.tester.text_field = 'TEXT'
        self.assertEqual(self.tester.is_complete(), True)
        
    def test_multisessionform_factory(self):
        self.assertEquals(self.form_class.__name__, 'MSFExampleForm')
        
    def test_form_field_instantiation(self):
        self.assertRaises(NameError, self.form_class, 'foo_field')
        self.assertIsInstance(self.form_class(), MSFForm)
        
    def test_form_get_next_field_name(self):
        self.assertEquals(self.form_class().get_next_field_name(), 'text_field')
        self.assertEquals(self.form_class('integer_field').get_next_field_name(), 'text_field')
        self.assertEquals(self.form_class('text_field').get_next_field_name(), None)
        
    def test_form_correct_field(self):
        self.assertEquals(self.form_class().fields.keys(), ['integer_field',])
        self.assertEquals(len(self.form_class().fields.keys()), 1)
        self.assertIsInstance(self.form_class().fields['integer_field'], fields.IntegerField)
        
        self.assertEquals(self.form_class('integer_field').fields.keys(), ['integer_field',])
        self.assertEquals(len(self.form_class('integer_field').fields.keys()), 1)
        self.assertIsInstance(self.form_class('integer_field').fields['integer_field'], fields.IntegerField)
        self.assertTrue(self.form_class('integer_field').fields['integer_field'].required)
        
        self.assertEquals(self.form_class('text_field').fields.keys(), ['text_field',])
        self.assertEquals(len(self.form_class('text_field').fields.keys()), 1)
        self.assertIsInstance(self.form_class('text_field').fields['text_field'], fields.CharField)
        
    def test_form_sections(self):
        self.assertListEqual(self.form_class().sections, [{'name':'integer_field', 'display':'Integer field', 'value':None},
                                                          {'name':'text_field', 'display':'Text field', 'value':None}])
        
        self.tester.integer_field = 1
        self.assertListEqual(self.form_class(instance = self.tester).sections, [{'name':'integer_field', 'display':'Integer field', 'value':1},
                                                          {'name':'text_field', 'display':'Text field', 'value':None}])
        
        self.tester.text_field = "a"
        self.assertListEqual(self.form_class(instance = self.tester).sections, [{'name':'integer_field', 'display':'Integer field', 'value':1},
                                                          {'name':'text_field', 'display':'Text field', 'value':"a"}])
        
        self.tester.integer_field = None
        self.assertListEqual(self.form_class(instance = self.tester).sections, [{'name':'integer_field', 'display':'Integer field', 'value':None},
                                                          {'name':'text_field', 'display':'Text field', 'value':"a"}])

class MSFViewTestCase(TestCase):
    urls = 'multisessionform.tests.urls'
    def setUp(self):
        self.client = Client()
        self.tester = MSFExample.objects.create(required_field_one = "required")
        self.form_class = MSFExample.multisessionform_factory()
         
    def test_no_form_class(self):
        self.assertRaises(ImproperlyConfigured, lambda: self.client.get('/noform/'))
        self.assertRaisesMessage(ImproperlyConfigured, "No form_class defined", lambda: self.client.get('/noform/'))
        
    def test_no_template_name(self):
        self.assertRaises(ImproperlyConfigured, lambda: self.client.get('/notemplate/'))
        self.assertRaisesMessage(ImproperlyConfigured, "No template_name defined", lambda: self.client.get('/notemplate/'))
        
    def test_not_multisessionformmixin(self):
        self.assertRaises(ImproperlyConfigured, lambda: self.client.get('/notmixin/'))
        
    def test_get_bad_pk(self):
        response = self.client.get('/test/15/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(dict(response.items())['Location'], 'http://testserver/test/')
        
    def test_post_bad_pk(self):
        response = self.client.post('/test/15/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(dict(response.items())['Location'], 'http://testserver/test/')