# django-class-backed-field

This field will allow you to store a string in the database and passes it as the first and only arg to a constructor.  The best use I've found for this so far is the ability to store the id of an object in the database, and then make a REST call using that id.

This is an example of a models.py you could create in your application.

```python
from class_backed_field.fields import ClassBackedField

class OverSimplfiedGistPost(object):
    def __init__(self, gist_id):
        json_of_gist = requests.get("https://api.github.com/gists/%s" % gist_id).json()
        self.id = json_of_gist['id']
        self.text = [file_data['content'] for filename, file_data in json_of_gist['files'].items()]
        self.browser_url = json_of_gist['html_url']

id_retriving_lambda = lambda x: str(x.id)

class RemoteGist(models.Model):
    user = fields.ForgeinKey(User)
    gist = ClassBackedField(represents=OverSimplfiedGistPost, db_value_generator=id_retriving_lambda, max_length=255)
```

RemoteGist is now searchable using the id of the gist, or an instance of the gist. Also, it will get the latest information from GitHub everytime the object is used.

Example of usage:

```python
my_gist = RemoteGist.objects.create(gist="5867996")
retrived_gist_from_string = RemoteGist.objects.get(gist="5867996")
instance_of_gist = OverSimplfiedGistPost("5867996")
retrived_gist_from_object = RemoteGist.object.get(gist=instance_of_gist)

print retrived_gist_from_string.gist.browser_url
```
