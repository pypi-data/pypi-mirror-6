.. _design_toplevel:

======
Design
======

The design of Stalker is mentioned in the following sections.

Introduction
============

As you probably have got by now Stalker is an Open Source Production Asset
Management System. Although it is designed VFX and Animation studios in mind,
its flexible Project Management muscles will allow it to be used in a wide
variety of fields.

An Asset Management Systems' duty is to hold the data which are created by the
users of the system in an organised manner, and let them quickly reach and find
their files. A Production Asset Management Systems' duty is, in addition to the
asset management systems', also handle the production steps or tasks and
allow the users of the system to collaborate. If more information about this
subject is needed, there are great books about Digital Asset Management (DAM)
Systems.

The usage of an asset management system in an animation/vfx studio is an
obligatory duty for the sake of the studio itself. Even the benefits of the
system becomes silly to be mentioned when compared to the lack of even a simple
system to organise stuff.

Every studio outside establishes and develops their own asset management
system. Stalker will try to be the framework that these proprietary asset
management systems will be build over. Thus reducing the work repeated on every
big projects' start.

Concepts
========

There are a couple of design concepts those needs to be clarified before any
further explanation of Stalker.

Stalker Object Model (SOM)
--------------------------

Stalker has a very robust object model, which is called
**Stalker Object Model** or **SOM**. The idea behind SOM is to create a simple
class hierarchy which is both usable right out of the box and also expandable
by the studios' pipeline TDs. SOM is actually a little bit more complex than
the basic possible model, it is designed in this way just to be able to create
a simple pipeline to be able to build the system on it.

Lets look at how a simple studio works and try to create our asset management
concepts around it.

An animation/vfx studios duty is to complete a
:class:`~stalker.models.project.Project`. A project, generally is about to
create a :class:`~stalker.models.sequence.Sequence` of
:class:`~stalker.models.shot.Shot`\ s which are a series of images those at the
end converts to a movie. So a sequence in general contains Shots. And Shots can
use :class:`~stalker.models.asset.Asset`\ s. So basically to complete a
project the studio should complete the shots and assets needed by those shots.

Furthermore all the Projects, Sequences, Shots or Assets are splitted in to
different :class:`~stalker.models.task.Task`\ s those need to be done
sequentially or in parallel to complete that project.

A Task relates to a work, a work is a quantity of time spend or going to be
spend for that specific task. The time spend on the course of completion of a
Task can be recorded with :class:`~stalker.models.task.TimeLog`\ s. TimeLogs
shows the time of an artist has spent for a certain Task. So it holds
information about how much **effort** has been spent to complete a Task.

During the completion of the Task or at the end of the work a **User** creates
:class:`~stalker.models.version.Versions` for that particular Task. Versions
are the different incarnations or the progress of the resultant product, and it
is connected to files in the fileserver or in Stalkers term the
:class:`~stalker.models.repository.Repository`.

All the names those shown in bold fonts are a class in SOM. and there are a
series of other classes to accommodate the needs of a
:class:`~stalker.models.studio.Studio`.

The inheritance diagram of the classes in the SOM is shown below:

.. include:: inheritance_diagram.rst

Stalker is a configurable and expandable system. Both of these feature allows
the system to have a flexible structure.

There are two levels of expansion, the first level is the simplest one, by just
adding different statuses, different types or these kind of things in
which Stalker's current design is ready to. This is explained in `How To
Customize Stalker`_

The second level of expansion is achieved by expanding the SOM. Expanding the
SOM includes creating new classes and database tables, and updating the old
ones which are already coming with Stalker. These expansion schemes are
further explained in `How To Extend SOM`_.

Features and Requirements
-------------------------
Features:

 1. Developed purely in Python (2.6 and over) using TDD (Test Driven
    Development) practices
 
 2. SQLAlchemy for the database back-end and ORM
 
 3. PyQt/PySide and Pyramid based web interfaces. All the interfaces designed
    in MVC structure.
 
 4. Jinja2 as the template engine
 
 5. Users are able to select their preferred database like PostgreSQL, MySQL,
    Oracle, SQLite etc. (whatever SQLAlchemy supports)
 
 6. It is possible to use both one or different databases for studio specific
    and project specific data. It is mostly beneficial when the setup uses
    SQLite. The project specific data could be kept in project folder as an
    SQLite db file and the studio specific data can be another SQLite db file
    or another database connection to PostgreSQL, MySQL, Oracle etc. databases.
    In an SQLite setup, the database can be backed up with the project folder
    itself.
 
 7. Uses Jinja2 as the template system for the file and folder naming
    convention will be used like:
    
    {repository.path}/{project.name}/assets/{asset.name}/{pipelineStep.name}/
    {asset.variation.name}/{asset.name}_{asset.type.name}_v{asset.version}.{
    asset.fileFormat.extension}
 
 8. file and folders and file sequences can be uploaded to the server as
    assets, and the server decides where to place the folder or file by using
    the template system.
 
 9. The event system gives full control for every CRUD (create/insert, read,
    update, delete) by giving step like before insert, after insert
    call-backs.
 
 10. The messaging system allows the users collaborate efficiently.

For usage exmaples see :ref:`tutorial_toplevel`

How To Customize Stalker
========================

This part explains the customization of Stalker.


How To Extend SOM
=================

This part explains how to extend Stalker Object Model or SOM.

