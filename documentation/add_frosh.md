# Add a Frosh Page for New Year

1. fix link on [`csss-site/src/events/templates/events/frosh/frosh_week.html`](../csss-site/src/events/templates/events/frosh/frosh_week.html) to point to new frosh page instead of under contruction page
2. Follow the example of the previous years and add the necessary URL patterns under [`csss-site/src/events/urls.py`](../csss-site/src/events/urls.py). You will need to add a url pattern for each new webpage you intend to make
3. Create a new views file for the frosh year under [`csss-site/src/events/views/frosh`](../csss-site/src/events/views/frosh). You can take a look at the views from previous years to see how to populate it.
4. You will also need to actually put the static files<sup>[1]</sup> on the repo, they will need to go under a new folder in [`csss-site/src/events/static/events_static/frosh`](../csss-site/src/events/static/events_static/frosh)
5. The html page[s] that you intend to make will go under their appropriate folder name in [`csss-site/src/events/templates/events/frosh`](../csss-site/src/events/templates/events/frosh).
   2 thing to keep in mind about the html pages.
   1. In order to reference any static files<sup>[1]</sup>, you will need to reference them by use of the static tags `{% static %}`. Do a search through the previous year's html page for `{% static` for an example of how that is done. If you are using Pycharm for working on the site, you can actually see Pycharm autosuggesting what files/folders are available as you type in the path in the `static` tag
   2. You will need to place the tag `{% load staticfiles %}` at the top of any html file that will be using a static file
`

<sup>[1]</sup> - css, js, images, etc