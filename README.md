# django-kernel
![License] [license-image]
[license-image]: https://img.shields.io/badge/license-MIT-blue.svg?style=flat
[license]: LICENSE.txt


# class KernelModel
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
#### Admin
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

--- soon ---



