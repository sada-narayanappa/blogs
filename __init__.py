import os

print ("Initializing example_app folder: " + os.getcwd())
if (os.path.exists("blogs/services.py")):
    from . import services
    from . import suggestindex
    from . import ESservice
else:
    print("Blogs Services file does not exist")
    