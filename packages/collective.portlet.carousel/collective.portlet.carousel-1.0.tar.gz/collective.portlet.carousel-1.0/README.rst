collective.portlet.carousel
==========================

A portlet to be used within panels (see collective.panels) for creating carousels. 

The carousel supports the following features:

* The carousel can be added to any page on the site, by just creating a panel, and 
  then add the carousel to the panel. In theory, the carousel could also be placed
  in the left or right columns.
* The carousel supports several renderings. By default a dexterity behavior should 
  be used for creating carousel elements. The behavior can be added to any type,
  i.e. a carousel can have elements of any time. Carousel elements can also 
  be marked using the carousel marker interface, in this case the "Dublin Core"
  renderer will be used, but can be customized by registering a "carousel-renderer"
  view (for the marker interface should work). 
* The source of the elements in the carousel can vary. Currently, collections and 
  references can be used as a source of the elements.

TODO
----

* Basic styling of the different renderings.
* Better documentation. 

Authors
------

* Bo Simonsen <bo@headnet.dk>
* Thomas Clement Mogensen <thomas@headnet.dk>
