# Add a Frosh Page for New Year

1. fix link on [`csss-site/src/events/frosh/templates/frosh/frosh_week.html`](../csss-site/src/events/frosh/templates/frosh/frosh_week.html) to point to new frosh page instead of under contruction page
2. Follow the example of the previous years and add the necessary URL patterns under [`csss-site/src/events/frosh/urls.py`](../csss-site/src/events/frosh/urls.py). You will need to add a url pattern for each new webpage you intend to make
3. Create a new views file for the frosh year under [`csss-site/src/events/frosh/views`](../csss-site/src/events/frosh/views). You can take a look at the views from previous years to see how to populate it.
4. You will also need to actually put the static files<sup>[1]</sup> on the repo, they will need to go under a new folder in [`csss-site/src/events/frosh/static/frosh_static`](../csss-site/src/events/frosh/static/frosh_static)
5. The html page[s] that you intend to make will go under their appropriate folder name in [`csss-site/src/events/frosh/templates/frosh`](../csss-site/src/events/frosh/templates/frosh).
   2 thing to keep in mind about the html pages.
   1. In order to reference any static files<sup>[1]</sup>, you will need to reference them by use of the static tags `{% static %}`. Do a search through the previous year's html page for `{% static` for an example of how that is done. If you are using Pycharm for working on the site, you can actually see Pycharm autosuggesting what files/folders are available as you type in the path in the `static` tag
   2. You will need to place the tag `{% load staticfiles %}` at the top of any html file that will be using a static file


<sup>[1]</sup> - css, js, images, etc

# Add a Page for a New Mountain Madness

1. Follow the example of the previous years and add the necessary URL patterns under [`csss-site/src/events/mountain_madness/urls.py`](../csss-site/src/events/mountain_madness/urls.py). You will need to add a url pattern for each new webpage you intend to make
2. Create a new views function for the mountain madness under [`csss-site/src/events/mountain_madness/views.py`](../csss-site/src/events/mountain_madness/views.py). You can take a look at the functions from previous years to see how to populate it.
3. You will also need to actually put the static files<sup>[1]</sup> on the repo, they will need to go under a new folder in [`csss-site/src/events/mountain_madness/static/mountain_madness_static`](../csss-site/src/events/mountain_madness/static/mountain_madness_static)
4. The html page[s] that you intend to make will go under their appropriate folder name in [`csss-site/src/events/mountain_madness/templates/mountain_madness`](../csss-site/src/events/mountain_madness/templates/mountain_madness).
   2 thing to keep in mind about the html pages.
   1. In order to reference any static files<sup>[1]</sup>, you will need to reference them by use of the static tags `{% static %}`. Do a search through the previous year's html page for `{% static` for an example of how that is done. If you are using Pycharm for working on the site, you can actually see Pycharm autosuggesting what files/folders are available as you type in the path in the `static` tag
   2. You will need to place the tag `{% load staticfiles %}` at the top of any html file that will be using a static file



# Add a Page for a New Fall Hacks

1. Follow the example of the previous years and add the necessary URL patterns under [`csss-site/src/events/fall_hacks/urls.py`](../csss-site/src/events/fall_hacks/urls.py). You will need to add a url pattern for each new webpage you intend to make
2. Create a new views function for the Fall Hacks under [`csss-site/src/events/fall_hacks/views.py`](../csss-site/src/events/fall_hacks/views.py). You can take a look at the functions from previous years to see how to populate it.
3. You will also need to actually put the static files<sup>[1]</sup> on the repo, they will need to go under a new folder in [`csss-site/src/events/fall_hacks/static/fall_hacks_static`](../csss-site/src/events/fall_hacks/static/fall_hacks_static)
4. The html page[s] that you intend to make will go under their appropriate folder name in [`csss-site/src/events/fall_hacks/templates/fall_hacks`](../csss-site/src/events/fall_hacks/templates/fall_hacks).
   2 thing to keep in mind about the html pages.
   1. In order to reference any static files<sup>[1]</sup>, you will need to reference them by use of the static tags `{% static %}`. Do a search through the previous year's html page for `{% static` for an example of how that is done. If you are using Pycharm for working on the site, you can actually see Pycharm autosuggesting what files/folders are available as you type in the path in the `static` tag
   2. You will need to place the tag `{% load staticfiles %}` at the top of any html file that will be using a static file


