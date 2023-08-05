Intoduction
=============

collective.slideshare does not add any new contenttypes. It adds new
views for your `Link` and `File` (currently archetypes only) contenttypes.

Configuration
-------------

You have to configure collective.slideshare first to be able to use it.
It requires an API KEY and a SHARED SECRET. Additionally you may provide
a username and password. If you do not provide usermane and password
you will be prompted for those every time you upload a file to slideshare.
You can obtain an API KEY at http://www.slideshare.net/developers/applyforapi

You can specify a policy for this behaviour:

* Always use the credentials provided, never prompt user for input
* Always ask user for his credentials
* Allow user to supply his credentials, if none are provided use the system credentials

Files can be automatically uploaded to SlideShare_ when you 'publish'
them. For this to work a workflow must be activated for Files and you
have to provide credentials and the policy must not require the user
to supply his own credentials.


Links
-----

When you add a link to a SlideShare_ presentation the product retrieves the
slideshare_id from SlideShare_ and embeds the presentation in your page.
Do NOT use the link given in the slideshare `<> Embed` option!
You can (de)activate the 'SlideShare View' at any time.


Files
-----

When you upload a Presentation you can change the view to 'SlideShare View'.
You will then be asked to provide your credentials to add this file to
SlideShare_ and the presentation will be embedded in the page. At
First you may see a 'This document has either been removed or made private by
its owner' message. This is to be expected as SlideShare_ needs a little
time to convert the presentation. Refresh the page after a little while.

Slideshow was removed from SlideShare_
---------------------------------------

When a presentation is removed from SlideShare_ you can simply change the
view back to the default view. However this does not remove the id from
the annotation. To remove the annotation you have to manually append
`@@slideshare_removeid.html` to your objects url.


- Code repository: https://github.com/collective/collective.slideshare
- Questions and comments to product-developers@lists.plone.org
- Report bugs at https://github.com/collective/collective.slideshare/issues

.. _SlideShare: http://www.slideshare.net/
