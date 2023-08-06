from pyramid.scaffolds import PyramidTemplate


class WebAppTemplate(PyramidTemplate):
    _template_dir = 'webapp'
    summary = 'Pyramid Webapp project using hybrid routing'