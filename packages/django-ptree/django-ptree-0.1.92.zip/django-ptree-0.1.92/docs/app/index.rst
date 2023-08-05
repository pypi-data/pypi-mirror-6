Writing a ptree app
*******************

Creating the app
================

First, choose a name for your app that is descriptive and short,
since you will be typing it and using it frequently.
For example, if you are implementing the `prisoner's dilemma <http://en.wikipedia.org/wiki/Prisoner's_dilemma>`__,
you can choose the name ``prisoner``.
If you are implementing the `public goods game <http://en.wikipedia.org/wiki/Public_goods_game>`_,
you can choose the name ``publicgoods``.

At your command line, go inside your project directory (the same directory as ``manage.py``),
and run this command, where ``your_app_name`` is the name you have chosen for your app::

    ptree startapp your_app_name

.. note::

    On Windows, you may have to do ``python ..\venv\Scripts\ptree startapp your_app_name``
    
This will create a new app based on a ptree template, with most of the structure already set up for you.

Think of this as a skeleton to which you can add as much as you want.
You can add your own classes, functions, methods, and attributes,
or import any 3rd-party modules.


Open your project for editing
=============================

Launch PyCharm, and select "Open Directory".
Navigate to the outer ``ptree_experiments`` directory (not the subfolder that has the same name) and click OK.
When the project opens, on the left-hand site you should see a directory tree that expands to the following::

    ptree_experiments/
        manage.py
        ptree_experiments/
            __init__.py
            settings.py
            urls.py
            wsgi.py    
        <your_app_name>
            management/
            static/
            templates/
            __init__.py
            admin.py
            forms.py
            models.py
            utilities.py
            views.py
            
Go to ``ptree_experiments/settings.py`` and append your app's name (as a string) to ``PTREE_EXPERIMENT_APPS``, like this::
    
    PTREE_EXPERIMENT_APPS = ('myappname',)

(Note the trailing comma, which is necessary.)    
    
Each of the files/folders in your app directory holds one component of your app. They are explained in the following pages:    

.. toctree::
   :maxdepth: 2
   
   models
   forms
   views
   templates
   management
   auxiliary-models 
   admin