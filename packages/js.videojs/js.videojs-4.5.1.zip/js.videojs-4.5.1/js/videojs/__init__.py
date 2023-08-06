from fanstatic import Library, Resource, Group

library = Library('video.js', 'resources')

videojs_js = Resource(
    library, 'js/video.js', minified='js/video.min.js')

videojs_css = Resource(library, 'css/video-js.css')


def render_shockwave_url(url):
    return '''
        <script type="text/javascript">
            videojs.options.flash.swf = '%s';
        </script>''' % url

# Dependency, in order to get the path to the SWF to work.
videojs_shockwave = Resource(
    library, 'swf/video-js.swf',
    depends=[videojs_js],
    renderer=render_shockwave_url)

videojs = Group(depends=[videojs_js, videojs_css, videojs_shockwave])
