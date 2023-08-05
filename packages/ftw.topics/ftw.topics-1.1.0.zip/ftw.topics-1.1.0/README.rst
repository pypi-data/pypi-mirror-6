ftw.topics
==========

This package integrates a subject tree into Plone.

Features
--------

- Dexterity based content types "Topic Tree" and "Topic" for
  creating a topic tree (subject tree).

- Archetypes schema extender, adding a reference field "topics" to
  all objects prividing `ITopicSupport` for assigning content to
  a topic.

- The topic-view lists all content referenced the topic.

- `Simplelayout`_ support for topics, so that additional content
  can be added to the topic view.


Usage
-----

- Add ``ftw.topics`` to your buildout configuration:

.. code:: ini

    [instance]
    eggs +=
        ftw.topics

- Install the default generic import profile.


ITopicSupport for Archetypes
----------------------------

For activating the schema extender install the `archetypes` extras:

.. code:: ini

    [instance]
    eggs +=
        ftw.topics [archetypes]


Enable the `ITopicSupport` interface on the archetypes content type classes
you want to have the `topics` reference field:


.. code:: xml

    <configure
        xmlns="http://namespaces.zope.org/zope"
        i18n_domain="my.package">

        <class class="my.package.content.mytype.MyTyp">
            <implements interface="ftw.topics.interfaces.ITopicSupport" />
        </class>

    </configure>

If you have `ftw.contentpage`_ installed, `ITopicSupport` is automatically enabled
for content pages.


ITopicSupport for Dexterity
---------------------------

If you would like to have the topics field on dexterity based types, use
the `ITopicSupportSchema` behavior:

.. code:: xml

    <?xml version="1.0"?>
    <object name="example.conference.presenter" meta_type="Dexterity FTI"
       xmlns:i18n="http://xml.zope.org/namespaces/i18n"
       i18n:domain="example.conference">

         <!-- enabled behaviors -->
         <property name="behaviors">
             <element value="ftw.topics.behavior.ITopicSupportSchema" />
         </property>

    </object>



Simplelayout support
--------------------

The `Simplelayout`_ support is using the block types of the `ftw.contentpage`_
package, so it installs the contentpage package.
Use the `simplelayout` extras for installing the required packages:

.. code:: ini

    [instance]
    eggs +=
        ftw.topics [simplelayout]

Install the simplelayout generic setup profile (`profile-ftw.topics:simplelayout`).


Customizing reference representations
-------------------------------------

The ``ITopicReferencePresentation`` adapters are responsible for rendering the
references on the topic view. The adapters consume all items they know and
render them in a section of the view.

`ftw.topics` includes an `ITopicReferencePresentation` for rendering content pages
and a default adapter for all contents which are not consumed by another adapter.

Adding a custom representation adapter is easy:

.. code:: python

    from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
    from ftw.topics.browser.representation import DefaultRepresentation
    from my.package.interfaces import IMyType
    from my.package import _

    class MyRepresentation(DefaultRepresentation):
        template = ViewPageTemplateFile('my_representation.pt')

        def consume(self, objects):
            for obj in objects:
                if IMyType.providedBy(obj):
                    self.objects.append(obj)
                else:
                    yield obj

        def title(self):
            return _(u'label_my_objects', default=u'My objects')

        def position(self):
            return 50


consume()
    Be sure that you yield all objects which you do not handle in your adapter.
    They will be passed up the pipeline until another adapter handles them.
    The last adapter is usually the default representation adapter, which consumes
    all left over objects.

title()
    Return the title for your section.

position()
    The adapters are ordered by position. The default adapter has the position 1000,
    the `ftw.contentpage` adapter has the position 100.

Register your adapter with ZCML:

.. code:: xml

    <configure xmlns="http://namespaces.zope.org/zope">

        <adapter
            factory=".representation.MyRepresentation"
            name="my_representation"
            />

    </configure>

Be sure you give the adapter a name, so that it does not conflict with other adapters.


Viewlets
--------

A viewlet shows all referenced topics on an object with ITopicSupport.

Links
-----

- Main github project repository: https://github.com/4teamwork/ftw.topics
- Issue tracker: https://github.com/4teamwork/ftw.topics/issues
- Package on pypi: http://pypi.python.org/pypi/ftw.topics
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.topics


Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.topics`` is licensed under GNU General Public License, version 2.

.. _Simplelayout: https://github.com/4teamwork/simplelayout.base
.. _ftw.contentpage: https://github.com/4teamwork/ftw.contentpage

.. image:: https://cruel-carlota.pagodabox.com/e7a1abb8fa1cd8c1a3a04072f499c85f
   :alt: githalytics.com
   :target: http://githalytics.com/4teamwork/ftw.topics
