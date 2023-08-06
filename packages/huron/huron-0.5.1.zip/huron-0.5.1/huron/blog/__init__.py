"""

.. module:: blog
   :platform: Unix
   :synopsis: Really simple blog application for Django

.. moduleauthor:: Thomas Durey <tominardi@gmail.com>

This application provides :

* Listing of blog entries
* Singles of blog entries
* RSS Feed
* Sitemap
* Administration

No templates by now. You have to create this templates to use this app :

* blog/single.html (receive a post object, categories and three random posts)
* blog/index.html (receive post list, categories, next an previous links)

"""