=========
SilvaPoll
=========

SilvaPoll is an extension to have traditional polls inside `Silva`_
sites. A question is asked on which the public can answer, and results
are displayed to those that do. The poll can be an independent page or
be embedded in a Silva Document as a Code Source.

Making a Poll
=============

Creating Silva Poll Questions
-----------------------------

After following the installation instructions you can add a Silva Poll
Question in the SMI. Fill in all required fields and save the
question, repeat this step for all questions. Separate answers by an
empty line.

Rendering the Silva Poll
------------------------

You can use the Poll Questions like documents, and send visitors there
via a link in content or navigation.

You can also embed Poll Questions in Silva Document. When editing a
document, click on external sources and add all of your questions
(don't forget to hit the "add external source" button ;-).

- Rendering the poll immediately:
  Publish your Silva Poll Questions and/or Silva Document and that's it.

- Rendering time based Silva Poll Questions and their result:
  In the SMI go to the publish tab of a Silva Poll Question and fill in dates as
  appropriate.

Fill in the options you would like to set:

- question display start time: time when a Silva Poll Question should
  be displayed for the public.

- question display end time: time when a Silva Poll Question should
  stop being displayed for the public.

- results display start time: time when the result of Silva Poll
  Question should be displayed for the public.

- results display end time: time when the result of Silva Poll
  Question should stop being displayed for the public.

Code repository
===============

You can find the code of this extension in Git:
https://github.com/silvacms/Products.SilvaPoll

.. _Silva: http://silvacms.org
