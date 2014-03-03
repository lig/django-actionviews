DAV Tutorial
============

DAV allows you to define simple class that will serve several views united by 
the same ORM class or similar purpose. 

Let's say we have a Post model::

   class Post(models.Model):
   
       posted = models.DateTimeField(auto_now_add=True)
       title = models.CharField(max_length=255)
       text = models.TextField(null=True, blank=True)
   
       def __str__(self):
           return self.title

And we want to show a list of these posts. Using DAV we will define a class 
such a view::

   