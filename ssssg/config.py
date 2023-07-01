from tornado.options import options, define


define('site_path', help=('the path to where all of the site files exist.'
    ' if site is the only  _path argument set, the app will assume values'
    ' for the other options'))
define('source_path', None, help=('the path to the directory containing the'
    ' source markdown files. If this is not set, it defaults to:'
    ' site_path/src'))
define('template_path', None, help=('the full path to the templates that will'
    ' be used to help build the site. If this is not set, it defaults to:'
    ' site_path/template'))
define('output_path', None, help=('the full path where the rendered final'
    ' files will be stored. If this is not set, it defaults to:'
    ' site_path/public'))
define('index_directories', False, help=(''))
