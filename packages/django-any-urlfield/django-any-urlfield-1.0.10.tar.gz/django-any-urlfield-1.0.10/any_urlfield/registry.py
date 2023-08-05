from django.contrib.contenttypes.models import ContentType
from django import forms
from django.db.utils import DatabaseError
from django.utils.translation import ugettext_lazy as _


# Avoid using common protocol names as prefix, this could clash in the future.
# Values starting with such prefix should be handled as external URL.
_invalid_prefixes = ('http', 'https', 'ftp', 'sftp', 'webdav', 'webdavs', 'afp', 'smb', 'git', 'svn', 'hg')

class UrlType(object):
    def __init__(self, model, form_field, widget, title, prefix, has_id_value):
        if form_field is None:
            # Generate default form field if nothing is provided.
            if has_id_value:
                form_field = forms.ModelChoiceField(queryset=model._default_manager.all(), widget=widget)
            else:
                form_field = forms.CharField(widget=widget)

        self.model = model
        self.form_field = form_field
        self.title = title
        self.prefix = prefix
        self.has_id_value = has_id_value


class UrlTypeRegistry(object):
    """
    Registration backend to administrate the various types.
    """

    def __init__(self):
        self._url_types = [UrlType(
            model=None,
            form_field=forms.URLField(label=_("External URL"), widget=forms.TextInput(attrs={'class': 'vTextField'})),
            widget=None,
            title=_("External URL"),
            prefix='http',   # no https needed, 'http' is a special constant.
            has_id_value=False
        )]


    def register(self, ModelClass, form_field=None, widget=None, title=None, prefix=None, has_id_value=True):
        """
        Register a custom model with the ``AnyUrlField``.
        """
        if any(urltype.model == ModelClass for urltype in self._url_types):
            raise ValueError("Model is already registered: '{0}'".format(ModelClass))

        try:
            ct = ContentType.objects.get_for_model(ModelClass)
        except DatabaseError:
            return   # skip at first syncdb

        if not prefix:
            # Store something descriptive, easier to lookup from raw database content.
            prefix = '{0}.{1}'.format(*ct.natural_key())
        if not title:
            title = ModelClass._meta.verbose_name

        if prefix in _invalid_prefixes:
            raise ValueError("Invalid prefix value: '{0}'.".format(prefix))
        if self[prefix] is not None:
            raise ValueError("Prefix is already registered: '{0}'".format(prefix))
        if form_field is not None and widget is not None:
            raise ValueError("Provide either a form_field or widget; use the widget parameter of the form field instead.")

        self._url_types.append(
            UrlType(ModelClass, form_field, widget, title, prefix, has_id_value)
        )


    # Accessing API is similar to `list` and '`dict`:

    def __iter__(self):
        return iter(self._url_types)


    def __getitem__(self, prefix):
        if prefix == 'https':
            prefix = 'http'

        for urltype in self._url_types:
            if urltype.prefix == prefix:
                return urltype
        return None


    def index(self, prefix):
        """
        Return the model index for a prefix.
        """
        # Any web domain will be handled by the standard URLField.
        if prefix == 'https':
            prefix = 'http'

        for i, urltype in enumerate(self._url_types):
            if urltype.prefix == prefix:
                return i
        return None
