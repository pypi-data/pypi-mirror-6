from js.jquery import jquery
from js.jqueryui import jqueryui
import fanstatic


library = fanstatic.Library('colorpicker', 'resources')


colorpicker_css = fanstatic.Resource(
    library, 'jquery.colorpicker.css', minified='jquery.colorpicker.min.css')
colorpicker = fanstatic.Resource(
    library, 'jquery.colorpicker.js', minified='jquery.colorpicker.min.js',
    depends=[jquery, jqueryui, colorpicker_css])

cmyk_parser = fanstatic.Resource(
    library, 'jquery.ui.colorpicker-cmyk-parser.js')
cmyk_percentage_parser = fanstatic.Resource(
    library, 'jquery.ui.colorpicker-cmyk-percentage-parser.js')
swatches_crayola = fanstatic.Resource(
    library, 'jquery.ui.colorpicker-crayola.js')
swatches_pantone = fanstatic.Resource(
    library, 'jquery.ui.colorpicker-pantone.js')
swatches_ral = fanstatic.Resource(
    library, 'jquery.ui.colorpicker-ral-classic.js')
