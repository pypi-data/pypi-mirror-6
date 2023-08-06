Pelican Related Plugin
======================


Installation
------------

This plugin is not registered on PyPI. You should clone this repository and install through pip::

    git clone git@github.com:wutali/pelican_related.git
    cd pelican_related
    pip install -e .


Configuration
-------------

Put this code on your pelicanconf.py and customize it::

    RELATED_POSTS_MIN = 3 # Minimum number of posts to be shown.
    RELATED_POSTS_LIMIT = 6 # Limit number of posts to be shown.
    RELATED_POSTS_FROM_CATEGORY = True # Weight related posts based on category.
    RELATED_POSTS_FROM_TAGS = True # Weight related posts based on tags.
    RELATED_POSTS_SHUFFLE = True # Shuffle posts before show it.

    # If number of related posts is not up to the minimum, add some articles based on this setting.
    # You can choose the option from 'shuffle' or 'new'.
    RELATED_POSTS_NOT_ENOUGH = 'shuffle'


License
-------

Pelican Related is released under the MIT License. http://www.opensource.org/licenses/mit-license
