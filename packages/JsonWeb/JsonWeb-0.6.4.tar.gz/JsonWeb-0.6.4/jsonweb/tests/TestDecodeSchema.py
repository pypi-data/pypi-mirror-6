import json
import unittest

class TestDecodeSchema(unittest.TestCase):
    def setUp(self):
        from jsonweb.decode import _default_object_handlers
        _default_object_handlers.clear()
        print "clearing handlers"
        
    def test_decode_with_schema(self):
        from jsonweb.schema import ObjectSchema
        from jsonweb.schema.validators import String
        
        from jsonweb.decode import from_object, object_hook
        
        class PersonSchema(ObjectSchema):
            first_name = String()
            last_name = String()
            
        @from_object(schema=PersonSchema)
        class Person(object):
            def __init__(self, first_name, last_name):
                self.first_name = first_name
                self.last_name = last_name
        
        json_str = '{"__type__": "Person", "first_name": "shawn", "last_name": "adams"}'                
        person = json.loads(json_str, object_hook=object_hook())
        self.assertTrue(isinstance(person, Person))
        
    def test_schemas_do_not_run_when_validate_kw_is_false(self):
        from jsonweb.schema import ObjectSchema, ValidationError
        from jsonweb.schema.validators import String
        
        from jsonweb.decode import from_object, loader, ObjectDecodeError
        
        class PersonSchema(ObjectSchema):
            first_name = String()
            last_name = String()
            
        @from_object(schema=PersonSchema)
        class Person(object):
            def __init__(self, first_name, last_name):
                self.first_name = first_name
                self.last_name = last_name
        
        json_str = '{"__type__": "Person", "last_name": "adams"}'
        with self.assertRaises(ValidationError) as context:
            person = loader(json_str)        
        with self.assertRaises(ObjectDecodeError) as context:
            person = loader(json_str, validate=False)

    def test_decode_with_schema_raises_error(self):
        """
        when using a supplied schema test that a validation error
        is raised for invalid json.
        """
        
        from jsonweb.schema import ObjectSchema, ValidationError
        from jsonweb.schema.validators import String
        
        from jsonweb.decode import from_object, object_hook
        
        class PersonSchema(ObjectSchema):
            first_name = String()
            last_name = String()
            
        @from_object(schema=PersonSchema)
        class Person(object):
            def __init__(self, first_name, last_name):
                self.first_name = first_name
                self.last_name = last_name
        
        json_str = '{"__type__": "Person", "first_name": 123, "last_name": "adams"}'
        with self.assertRaises(ValidationError) as context:
            person = json.loads(json_str, object_hook=object_hook())
            
        exc = context.exception
        self.assertEqual(exc.errors["first_name"].message, "Expected str got int instead.")
        
    def test_class_name_as_string_to_ensuretype(self):
        """
        Test that we can pass a string for a class name to EnsureType. The class
        must of course be defined later and decorated with @from_object
        """
        from jsonweb.schema import ObjectSchema, ValidationError
        from jsonweb.schema.validators import String, Integer, EnsureType
        
        from jsonweb.decode import from_object, object_hook
        
                                
        class JobSchema(ObjectSchema):
            id = Integer()
            title = String()
            
        class PersonSchema(ObjectSchema):
            first_name = String()
            last_name = String()
            job = EnsureType("Job")
            
        @from_object(schema=JobSchema)
        class Job(object):
            def __init__(self, id, title):
                self.id = id
                self.title = title
                
        @from_object(schema=PersonSchema)
        class Person(object):
            def __init__(self, first_name, last_name, job):
                self.first_name = first_name
                self.last_name = last_name
                self.job = job
        
        obj = {
            "__type__": "Person",
            "first_name": "Shawn",
            "last_name": "Adams", 
            "id": 1, 
            "test": 12.0, 
            "job": {
                "__type__": "Job",
                "title": "zoo keeper", 
                "id": 1
        }}
                
        person = json.loads(json.dumps(obj), object_hook=object_hook())
        self.assertTrue(isinstance(person, Person))
        self.assertTrue(isinstance(person.job, Job))    
        
    def test_class_name_as_string_to_ensuretype_no_such_class(self):
        """
        Test that an error is raised if you pass a string name of a non
        existent class to EnsureType. Meaning it either was not defined or
        was not decorated with @from_object
        """
        
        from jsonweb.schema import ObjectSchema
        from jsonweb.schema.validators import String, Integer, EnsureType
        
        from jsonweb.decode import from_object, object_hook
        from jsonweb.exceptions import JsonWebError
        
                                
        class JobSchema(ObjectSchema):
            id = Integer()
            title = String()
            
        class PersonSchema(ObjectSchema):
            first_name = String()
            last_name = String()
            job = EnsureType("Job")#No such class Job
                
        @from_object(schema=PersonSchema)
        class Person(object):
            def __init__(self, first_name, last_name, job):
                self.first_name = first_name
                self.last_name = last_name
                self.job = job
        
        obj = {
            "__type__": "Person",
            "first_name": "Shawn",
            "last_name": "Adams", 
            "id": 1, 
            "test": 12.0, 
            "job": {
                "title": "zoo keeper", 
                "id": 1
        }}
        
        with self.assertRaises(JsonWebError) as context:
            person = json.loads(json.dumps(obj), object_hook=object_hook())
            
        exc = context.exception
        self.assertEqual(str(exc), "Cannot find class Job.")
        
    def test_mixed_type_schema(self):
        """
        Test ObjectSchema validates a mix of regular dicts and object hook classes.
        """
        from jsonweb.schema import ObjectSchema
        from jsonweb.schema.validators import String, List, EnsureType
        from jsonweb.decode import from_object, object_hook
        
        class TestRequestSchema(ObjectSchema):
            request_guid = String()
            players = List(EnsureType("Person"))
            
        class PersonSchema(ObjectSchema):
            first_name = String()
            last_name = String()
           
        @from_object(schema=PersonSchema)
        class Person(object):
            def __init__(self, first_name, last_name):
                self.first_name = first_name
                self.last_name = last_name
                
        obj = {
            "request_guid": "abcd",
            "persons": [{"__type__": "Person", "first_name": "shawn", "last_name": "adams"}]*2
        }
        
        request_obj = json.loads(json.dumps(obj), object_hook=object_hook())
        self.assertEqual(len(request_obj["persons"]), 2)
        self.assertTrue(isinstance(request_obj["persons"][0], Person))
        
    def test_map_schema_func(self):
        from jsonweb.schema import ObjectSchema, ValidationError, bind_schema
        from jsonweb.schema.validators import String
        from jsonweb.decode import from_object, loader
        
        class PersonSchema(ObjectSchema):
            first_name = String()
            last_name = String()
           
        @from_object()
        class Person(object):
            def __init__(self, first_name, last_name):
                self.first_name = first_name
                self.last_name = last_name        
                    
        bind_schema("Person", PersonSchema)
        with self.assertRaises(ValidationError) as context:
            loader('{"__type__": "Person"}')
            
    def test_map_schema_called_before_class_is_decorated(self):
        """
        Test binding a schema to a class before it is defined works.
        """
        from jsonweb.schema import ObjectSchema, ValidationError, bind_schema
        from jsonweb.schema.validators import String
        from jsonweb.decode import from_object, loader
        
        class PersonSchema(ObjectSchema):
            first_name = String()
            last_name = String()

        bind_schema("Person", PersonSchema)
        
        @from_object()
        class Person(object):
            def __init__(self, first_name, last_name):
                self.first_name = first_name
                self.last_name = last_name        
                    

        with self.assertRaises(ValidationError) as context:
            loader('{"__type__": "Person"}')
            
    def test_EnsureType_invoked_via_List_validator_honors_string_class_names(self):
        from jsonweb import loader
        from jsonweb.decode import from_object
        from jsonweb.schema import ObjectSchema
        from jsonweb.schema.validators import EnsureType, List, String, Integer
        
        class JobSchema(ObjectSchema):
            id = Integer()
            title = String()
            
        class PersonSchema(ObjectSchema):
            first_name = String()
            last_name = String()
            jobs = List(EnsureType("Job"))
            
        @from_object(schema=JobSchema)
        class Job(object):
            def __init__(self, id, title):
                self.id = id
                self.title = title
                
        @from_object(schema=PersonSchema)
        class Person(object):
            def __init__(self, first_name, last_name, jobs):
                self.first_name = first_name
                self.last_name = last_name
                self.jobs = jobs
        
        obj = {
            "__type__": "Person",
            "first_name": "Shawn",
            "last_name": "Adams", 
            "id": 1, 
            "test": 12.0, 
            "jobs": [{
                "__type__": "Job",
                "title": "zoo keeper", 
                "id": 1
            }]
        }
                
        person = loader(json.dumps(obj))
        self.assertTrue(isinstance(person, Person))
        self.assertTrue(isinstance(person.jobs, list))
        self.assertTrue(isinstance(person.jobs[0], Job))        
