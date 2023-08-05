from fanstatic import Library, Resource

library = Library('handlebars', 'resources')
handlebars = Resource(library, 'handlebars.js')
handlebars_runtime = Resource(library, 'handlebars.runtime.js')
