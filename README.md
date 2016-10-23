# SSSSG (Super Simple Static Site Generator)

SSSSG is a very simple static site generator written in Python used to render Markdown files.

##Dependencies

* tornado
* markdown
* I wrote it in Python 3.5, but there shouldn't be any reason to run in 2.7

##Installation

```python
python setup.py install
```

##Usage

SSSSG is easy to use employing only two commands: `run` and `index`. You will need to setup your site files with the following rules:

1. Create a directory to store your pages. The directory name will be the name that you reference when you run the site.
2. Store all of your viewable files with a `.md` extension.
3. Add a `static` directory for your static files -- css, js, images, fonts, etc.

```
   /mark.com
        index.md
        about.md
        /static
            /css
                mark.css
            /js
                mark.js
```

###Pages

Pages are rendered using the markdown package and the `markdown.extensions.meta` extension. This allows for you to add custom meta-data to each page.

####SSSSG Supported Meta-data

* Title -- the page title
* Slug -- this will be how the page is referenced in the browser
* Tags -- a comma separated list of tags that you can use to identify a page

###Administration

Indexing your content and running the application is very simple

__index__

This command's job is to index your site's files.

```
python ssssg.py index /path/to/your/site.name
```

__run__

This command runs the site.

```
python ssssg.py run site.name
```

> currently SSSSG is designed to only run one site at a time. If you want to run multiple sites you simply spawn multiple instances of the run command pointing to different sites with different ports.


###Configuration Options

The default setup defines a few configuration options that can be overwritten at run-time (these can be found in ssssg/config.py):

* __port__ [7007] -- The port used to run the SSSSG app
* __cache\_file_directory__ [CWD + '/../caches'] -- the directory where to write the cache files generated by the SSSSG `index` command
* __four\_oh_four__ [CWD + '/pages/404.md'] -- The default 404 page to render
* __five\_oh_oh__ [CWD + '/pages/500.md'] -- The default 500 page to render
* __base\_template__ [CWD + '/pages/base.html'] -- The base template that will be loaded with every page
* __search\_template__ [CWD + '/pages/search.html'] -- The default template to use when rendering search results
* __default\_error_title__ ['Server Error'] -- The default title to show when there is an error rendering the page

To override during run-time simply pass a setting in with prepended by a single dash (-)

```
python ssssg.py run site.name -port=9999 -cache_file_directory=/some/path
```

##Extras

###Tag Search

SSSSG will allow you to list pages that match any tags defined in a query string. This feature uses the `search_template` option to render the resulting html.

```
http://my.site/?tags=cars,some+other+tag,money
```
