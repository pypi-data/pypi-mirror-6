import logging

from pelican import signals, utils, urlwrappers

logger = logging.getLogger(__name__)


def init(pelican):
    if 'CATEGORY_SLUGS' in pelican.settings:
        replace_urlwrapper_slugify(
            urlwrappers.Category,
            pelican.settings['CATEGORY_SLUGS'])

    if 'TAG_SLUGS' in pelican.settings:
        replace_urlwrapper_slugify(
            urlwrappers.Tag,
            pelican.settings['TAG_SLUGS'])


def replace_slugify(pelican):
    if 'SLUG_FUNC' in pelican.settings:
        slugify = pelican.settings['SLUG_FUNC']

        import pelican.contents, pelican.utils, pelican.urlwrappers
        pelican.urlwrappers.slugify = slugify
        pelican.utils.slugify = slugify
        pelican.contents.slugify = slugify


def dict_slugify(name, slug_substitutions, slug_dict):
    slug = slug_dict.get(name)
    if not slug:
        if name:
            logger.warning("A slug for '%s' could not found." % name)
        return utils.slugify(name)
    return slug


def make_urlwrapper_patch(slugs):
    slug_dict = dict(slugs)

    def __init__(self, name, settings):
        self.settings = settings
        self.name = name

    def _normalize_key(self, other):
        return dict_slugify(
            other.name,
            self.settings.get('SLUG_SUBSTITUTIONS', ()),
            slug_dict)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.slug = dict_slugify(
            name,
            self.settings.get('SLUG_SUBSTITUTIONS', ()),
            slug_dict)

    return __init__, _normalize_key, name


def replace_urlwrapper_slugify(cls, slugs):
    cls.__init__, cls._normalize_key, cls.name = make_urlwrapper_patch(slugs)


def register():
    signals.initialized.connect(init)
    signals.initialized.connect(replace_slugify)
