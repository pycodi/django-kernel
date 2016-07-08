### Abstract Kernel Model Project
![License] [license-image]
[license-image]: https://img.shields.io/badge/license-MIT-blue.svg?style=flat
[license]: LICENSE.txt

#### Requirements
 * Django (1.7+, 1.8, 1.9)
 * djangorestframework (> 3.0) (option)

#### Support
 * Django: 1.8, 1.9
 * Python: 2.7, 3.4, 3.5

#### Setup

Add MY_APPS to settings.py and at the INSTALLED_APPS like this:
```
MY_APPS = [
  'project' #example
]

INSTALLED_APPS = MY_APPS + [ ... ]
````
It is necessary to register the classes in admin, if ADMIN == True
```python
for app in settings.MY_APPS:
    for cls in [m for m in apps.get_app_config(app).get_models()]:
        if hasattr(cls, 'ADMIN'):
            if cls.ADMIN:
                admin.site.register(cls, cls.get_admin_class())
```                


### class KernelModel
Large Abstract Kernel model for Django project
```python
@python_2_unicode_compatible
class KernelModel(models.Model):
    external_id = models.CharField(_('External Code'), max_length=120, editable=False, default=uuid.uuid4)
    created_date = models.DateTimeField(auto_now=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    
    REST = False
    ADMIN = False
```    
##### Admin
If Admin = True,  model inherited from the KernelModel will be added in the Django admin. 

Example:
```python
@python_2_unicode_compatible
class Document(KernelModel):
    name = models.CharField(max_length=200)

    ADMIN = True

    def __str__(self):
        return self.name
``` 
#### REST 
REST = True, needed if you use django-rest-framework

#### Class KernelModel methods
```python
@classmethod
def get_admin_class(cls):
    from kernel.admin.kernel import BaseAdmin
    class Admin(BaseAdmin):
        pass
   return Admin
```        
Return class admin for Model



