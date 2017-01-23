## 0.8.0 -- 1/22/2017

**Added**

    * Cotent is rendered with the codehilite filter -- https://pythonhosted.org/Markdown/extensions/code_hilite.html

**Updated**

     * Now requires Pygments for help with codehilite extension


## 0.7.2 -- 11/24/2016

**Fixed**

    * Added date created ordering to the pages object that is stored in the cache file.


## 0.7.1 -- 11/24/2016

**Fixed**

    * Added slugify method to ensure that slugs are url safe/pretty


## 0.7.0 -- 11/23/2016

**Added**

    * watch_for_changes configuration setting that will automatically re-index the site when changes are found.


## 0.6.0 -- 10/30/2016

**Fixed**

    * All meta data from the page is passed into the templates

**Added**

    * The ability to nest template rendering by defining `templates` in the page meta data
    * Added date_created and date_modified to the page meta data
    * Added date_published as page meta data


## 0.5.1 -- 10/29/2016

**Fixed**

    * Made all configuration paths full paths.
    * Passing all of the pages to the rendered template as `pages`.


## 0.5.0 -- 10/25/2016

**Added**

    * Added the ability to set configuration options via a config.py file in the site's root


## 0.4.0 -- 10/23/2016

**Added**

    * Published meta-data flag for pages. Defaults to true


## 0.3.0 -- 10/23/2016

**Added**

    * Default handler for 404 and 500 pages
    * Simple help text to get the server running and indexing
    * default_error_title option


## 0.2.0 -- 10/23/2016

**Added**

    * base_template -- configuration option
    * A way to filter pages by tags

**Fixed**

    * Readme typos.


## 0.1.0 -- 10/22/2016

**Added**

    * Initial commit
