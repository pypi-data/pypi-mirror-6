from fanstatic import Library, Resource

library = Library('chart', 'resources')
chart_js = Resource(library, 'Chart.js',
                    minified='Chart.min.js')
