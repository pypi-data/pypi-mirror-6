from django.conf import settings

class AuthorRouter(object):
     def db_for_read(self, model, **hints):
          """
          Attempts to read author models go to site db.
          """
          if model._meta.app_label == 'authors':
               return 'site'
          return None
     
     def db_for_write(self, model, **hints):
          """
          Attempts to write author models go to site db
          """
          if model._meta.app_label == 'authors':
               return 'site'
          return None
     
     def allow_relation(self, obj1, obj2, **hints):
          """
          Allow relations if a model in the authors app is involved.
          """
          if obj1._meta.app_label == 'authors' or \
                   obj2._meta.app_label == 'authors':
               return True
          return None
     
     def allow_syncdb(self, db, model):
          """
          Make sure the authors app only appears in the 'site'
          database.
          """
          if db == 'site':
               return model._meta.app_label == 'authors'
          elif model._meta.app_label == 'authors':
               return False
          return None
     
