django-socialshareprivacy
=========================

This Django applcation makes the jQuery Plug-In socialshareprivacy from heise.de available in django templates.
The plugin will show disabled buttons for the share adn tweet buttons, these disabled buttons are hosted locally. If the user wants to share or tweet he has to first click the disabled button which will then load the real button from facebook, G+ or Twitter. A second click on the buttons will then actually share the page. This basically means that the possibility of sharing is available but until the user interacts with the buttons no data is transmitted to the social networks.

The home of the jQuery plugin is http://www.heise.de/extras/socialshareprivacy/.

This application uses the same version numbers as the jQuery plugin and appends a third digit to allow for application releases independently of the plugin.

Installation
============

Install via pip:

    pip install django-socialshareprivacy

then add `socialshareprivacy`to your INSTALLED_APPS.

In your template load the socialshareprivacy templatetags library

    {% load socialshareprivacy_tags %}

add an empty div used to display the buttons

    <div id="socialshareprivacy"></div>

and include the neccessary javascript by calling the template tag `socialshareprivacy` 

    {% socialshareprivacy %}


In the default thediv to hold the buttons has to have an id of socialshareprivacy you can change 
that to what ever you want and then call the template tag with the correct selector

    <div id="share_buttons"></div>

    {% socialshareprivacy '#share_buttons' %}
    

Configuration
=============

If you need to configure any of the plugins options override the template `socialshareprivacy\socialshareprivacy.html`
The context of the template supplies the variables `selector` which contains the jQuery selector and 
the variable `STATIC_URL` from the project settings.

Help
====
For help open an issue here https://github.com/adsworth/django-socialshareprivacy/issues
License
=======
The original jQuery plugin socialshareprivacy is distributed uner the MIT license.

This Django application is also distributed under the MIT license. See the LICENSE file in this directory/repository.
