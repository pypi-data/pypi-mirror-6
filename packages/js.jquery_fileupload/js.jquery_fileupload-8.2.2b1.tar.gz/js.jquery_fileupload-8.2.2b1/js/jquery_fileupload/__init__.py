from fanstatic import Group, Library, Resource

import js.bootstrap
import js.jquery
import js.jqueryui

library = Library('jquery_fileupload', 'resources')

jquery_getimagedata = Resource(
    library, 'vendor/jquery.getimagedata.min.js',
)

tmpl_js = Resource(
    library, 'js/tmpl.min.js',
    depends=[
        js.jqueryui.ui_widget,
        jquery_getimagedata,
    ],
)

load_image_js = Resource(
    library, 'js/load-image.min.js',
    depends=[
        tmpl_js,
    ],
)

canvas_to_blob_js = Resource(
    library, 'js/canvas-to-blob.min.js',
    depends=[
        load_image_js,
    ],
)

iframe_transport_js = Resource(
    library, 'js/jquery.iframe-transport.js',
    depends=[
        canvas_to_blob_js,
    ],
)

fileupload_js = Resource(
    library, 'js/jquery.fileupload.js',
    depends=[
        js.bootstrap.bootstrap,
        js.jquery.jquery,
        iframe_transport_js,
    ],
)

fileupload_process_js = Resource(
    library, 'js/jquery.fileupload-process.js',
    depends=[
        fileupload_js,
    ],
)

fileupload_image_js = Resource(
    library, 'js/jquery.fileupload-image.js',
    depends=[
        fileupload_process_js,
    ],
)

fileupload_ui_css = Resource(
    library, 'css/jquery.fileupload-ui.css',
)

fileupload_ui_js = Resource(
    library, 'js/jquery.fileupload-ui.js',
    depends=[
        fileupload_ui_css,
        fileupload_image_js,
    ],
)

jquery_fileupload = Group([
    fileupload_ui_js,
])
