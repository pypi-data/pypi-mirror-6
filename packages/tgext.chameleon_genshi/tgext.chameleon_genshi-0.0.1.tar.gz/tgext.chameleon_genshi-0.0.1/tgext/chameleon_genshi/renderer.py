import tg
from tg.renderers.base import RendererFactory
from tg.render import cached_template
from markupsafe import Markup


try:
    import chameleon.genshi as chameleon_genshi
except ImportError:
    chameleon_genshi = None

if chameleon_genshi is not None:
    from chameleon.genshi.loader import TemplateLoader as ChameleonGenshiTemplateLoader
else:
    class ChameleonGenshiTemplateLoader(object): pass


class ChameleonGenshiRenderer(RendererFactory):
    engines = {'chameleon_genshi': {'content_type': 'text/html'}}
    with_tg_vars = True

    format_for_content_type = {
        'text/plain': 'text',
        'text/css': 'text',
        'text/html': 'xml',
        'text/xml': 'xml',
        'application/xml': 'xml',
        'application/xhtml+xml': 'xml',
        'application/atom+xml': 'xml',
        'application/rss+xml': 'xml',
        'application/soap+xml': 'xml',
        'image/svg+xml': 'xml'}

    @classmethod
    def create(cls, config, app_globals):
        """Setup a renderer and loader for the chameleon.genshi engine."""
        if chameleon_genshi is None:
            return None

        if config.get('use_dotted_templatenames', True):
            TemplateLoader = DottedTemplateLoader
            template_loader_args = {'dotted_finder': app_globals.dotted_filename_finder}
        else:
            TemplateLoader = ChameleonGenshiTemplateLoader
            template_loader_args = {}

        loader = TemplateLoader(search_path=config.paths.templates,
                                auto_reload=config.auto_reload_templates,
                                **template_loader_args)

        return {'chameleon_genshi': cls(loader, config)}

    def __init__(self, loader, config):
        self.load_template = loader.load
        self.tg_config = config

    def __call__(self, template_name, template_vars, **kwargs):
        """Render the template_vars with the Chameleon-Genshi template."""
        config = self.tg_config

        # Gets template format from content type or from config options
        format = kwargs.get('format')
        if not format:
            format = self.format_for_content_type.get(tg.response.content_type)
            if not format:
                format = config.get('templating.chameleon.genshi.format')
                if not format:
                    format = config.get('templating.genshi.method')
                    if not format or format not in ('xml', 'text'):
                        format = 'xml'

        def render_template():
            template = self.load_template(template_name, format=format)
            return Markup(template.render(**template_vars))

        return cached_template(template_name, render_template,
                               ns_options=('doctype', 'method'), **kwargs)


class DottedTemplateLoader(ChameleonGenshiTemplateLoader):
    """Chameleon.Genshi template loader supporting dotted filenames.

    Supports zipped applications and dotted filenames as well as path names.

    """
    def __init__(self, *args, **kwargs):
        self.template_extension = kwargs.pop('template_extension', '.html')
        self.dotted_finder = kwargs.pop('dotted_finder')

        super(DottedTemplateLoader, self).__init__(*args, **kwargs)

    def get_dotted_filename(self, filename):
        if not filename.endswith(self.template_extension):
            finder = self.dotted_finder
            filename = finder.get_dotted_filename(template_name=filename,
                                                  template_extension=self.template_extension)
        return filename

    def load(self, filename, format='xml'):
        """Actual loader function."""
        return super(DottedTemplateLoader, self).load(self.get_dotted_filename(filename), format)


