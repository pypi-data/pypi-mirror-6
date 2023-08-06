import re
from datetime import datetime
from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import User, Group
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import FieldDoesNotExist
from django.db.models.signals import post_save, pre_delete
from django.core.validators import RegexValidator
from avocado.core import utils
from avocado.core.models import Base, BasePlural, PublishArchiveMixin
from avocado.core.cache import post_save_cache, pre_delete_uncache, \
    cached_method
from avocado.conf import settings, dep_supported
from avocado import managers, history
from avocado.query.models import AbstractDataView, AbstractDataContext, \
    AbstractDataQuery
from avocado.query.translators import registry as translators
from avocado.query.operators import registry as operators
from avocado.lexicon.models import Lexicon
from avocado.stats.agg import Aggregator
from avocado import formatters


__all__ = ('DataCategory', 'DataConcept', 'DataField',
           'DataContext', 'DataView', 'DataQuery')


ident_re = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
validate_ident = RegexValidator(ident_re, _("Enter an 'identifier' that is a "
                                "valid Python variable name."),
                                'invalid')


class DataCategory(Base, PublishArchiveMixin):
    "A high-level organization for data concepts."
    # A reference to a parent for hierarchical categories
    parent = models.ForeignKey('self', null=True, blank=True,
                               related_name='children',
                               limit_choices_to={'parent__isnull': True},
                               help_text='Sub-categories are limited to '
                               'one-level deep')
    order = models.FloatField(null=True, blank=True, db_column='_order')

    objects = managers.DataCategoryManager()

    class Meta(object):
        ordering = ('parent__order', 'parent__name', 'order', 'name')
        verbose_name_plural = 'data categories'


class DataField(BasePlural, PublishArchiveMixin):
    """Describes the significance and/or meaning behind some data. In addition,
    it defines the natural key of the Django field that represents the location
    of that data e.g. ``library.book.title``.
    """
    app_name = models.CharField(max_length=200)
    model_name = models.CharField(max_length=200)
    field_name = models.CharField(max_length=200)

    internal = models.BooleanField(default=False, help_text='Flag for '
                                   'internal use and does not abide by the '
                                   'published and archived rules.')

    # An optional unit for this field's data. In some cases databases may have
    # a separate column which denotes the unit for another column, but this is
    # not always the case. Measurement data, for example, should be
    # standardized in the database to allow for consistent querying, thus not
    # requiring a separate column denoting the unit per value.
    unit = models.CharField(max_length=30, null=True, blank=True)
    unit_plural = models.CharField(max_length=40, null=True, blank=True)

    # Although a category does not technically need to be defined, this is more
    # for workflow reasons than for when the concept is published. Automated
    # prcesses may create concepts on the fly, but not know which category they
    # should be linked to initially.
    category = models.ForeignKey(DataCategory, null=True, blank=True)

    # Set this field to true to make this field's values enumerable. This
    # should only be enabled for data that contains a discrete vocabulary, i.e.
    # no full text data.
    enumerable = models.BooleanField(default=False)

    # An optional translator which customizes input query conditions
    # to a format which is suitable for the database.
    translator = models.CharField(max_length=100, blank=True, null=True,
                                  choices=translators.choices)

    # This is used for the cache key to check if the cached values is stale.
    data_version = models.IntegerField(default=1, help_text='The current '
                                       'version of the underlying data for '
                                       'this field as of the last '
                                       'modification/update.')

    group = models.ForeignKey(Group, null=True, blank=True,
                              related_name='fields+')

    # Certain fields may not be relevant or appropriate for all
    # sites being deployed. This is primarily for preventing exposure of
    # access to private data from certain sites. For example, there may and
    # internal and external deployment of the same site. The internal site
    # has full access to all fields, while the external may have a limited set.
    # NOTE this is not reliable way to prevent exposure of sensitive data.
    # This should be used to simply hide _access_ to the concepts.
    sites = models.ManyToManyField(Site, blank=True, related_name='fields+')

    # The order of this datafield with respect to the category (if defined).
    order = models.FloatField(null=True, blank=True, db_column='_order')

    objects = managers.DataFieldManager()

    class Meta(object):
        unique_together = ('app_name', 'model_name', 'field_name')
        ordering = ('category__order', 'category__name', 'order', 'name')
        permissions = (
            ('view_datafield', 'Can view datafield'),
        )

    def __unicode__(self):
        if self.name:
            return self.name
        if self.lexicon or self.objectset:
            return self.model._meta.verbose_name
        return u'{0} {1}'.format(self.model._meta.verbose_name,
                                 self.field.verbose_name).title()

    def __len__(self):
        return self.size()

    def __nonzero__(self):
        "Takes precedence over __len__, so it is always truthy."
        return True

    # The natural key should be used any time fields are being exported
    # for integration in another system. It makes it trivial to map to new
    # data models since there are discrete parts (as suppose to using the
    # primary key).
    def natural_key(self):
        return self.app_name, self.model_name, self.field_name

    # Django Model Field-related Properties and Methods

    @property
    def real_model(self):
        "Returns the model class this datafield is associated with."
        if not hasattr(self, '_real_model'):
            self._real_model = models.get_model(self.app_name, self.model_name)
        return self._real_model

    @property
    def real_field(self):
        "Returns the field object this datafield is associated with."
        if self.real_model:
            try:
                return self.real_model._meta.get_field(self.field_name)
            except FieldDoesNotExist:
                pass

    @property
    def model(self):
        "Returns the model class this datafield represents."
        real_field = self.real_field
        # Handle foreign key fields to a Lexicon model
        if real_field and isinstance(real_field, models.ForeignKey) \
                and issubclass(real_field.rel.to, Lexicon):
            return real_field.rel.to
        return self.real_model

    @property
    def field(self):
        "Returns the field object this datafield represents."
        model = self.model

        if model:
            if issubclass(model, Lexicon):
                return model._meta.pk

            if dep_supported('objectset'):
                from objectset.models import ObjectSet

                if issubclass(model, ObjectSet):
                    return model._meta.pk

        return self.real_field

    @property
    def nullable(self):
        "Returns whether this field can contain NULL values."
        return self.field.null

    @property
    def internal_type(self):
        "Returns the internal type of the field this datafield represents."
        return utils.get_internal_type(self.field)

    @property
    def simple_type(self):
        """Returns a simple type mapped from the internal type."

        By default, it will use the field's internal type, but can be
        overridden by the ``SIMPLE_TYPE_MAP`` setting.
        """
        return utils.get_simple_type(self.field)

    @property
    def lexicon(self):
        """Returns true if the model is a subclass of Lexicon and this
        is the pk field. All other fields on the class are treated as
        normal datafields.
        """
        return self.model and issubclass(self.model, Lexicon) \
            and self.field == self.model._meta.pk

    @property
    def objectset(self):
        """Returns true if the model is a subclass of ObjectSet and this
        is the pk field. All other fields on the class are treated as
        normal datafields.
        """
        if dep_supported('objectset'):
            from objectset.models import ObjectSet

            return self.model and issubclass(self.model, ObjectSet) \
                and self.field == self.model._meta.pk

        return False

    @property
    def searchable(self):
        "Returns true if a text-field and is not an enumerable field."
        return self.simple_type == 'string' and not self.enumerable

    # Convenience Methods
    # Easier access to the underlying data for this data field

    def values_list(self):
        "Returns a `ValuesListQuerySet` of values for this field."
        if self.lexicon or self.objectset:
            return self.model.objects.values_list('pk', flat=True)
        return self.model.objects.values_list(self.field_name, flat=True)\
            .order_by(self.field_name).distinct()

    def search(self, query):
        "Rudimentary search for string-based values."
        if self.simple_type == 'string' or self.lexicon:
            if self.lexicon:
                field_name = 'value'
            else:
                field_name = self.field_name
            filters = {u'{0}__icontains'.format(field_name): query}
            return self.values_list().filter(**filters)

    def get_plural_unit(self):
        if self.unit_plural:
            plural = self.unit_plural
        elif self.unit and not self.unit.endswith('s'):
            plural = self.unit + 's'
        else:
            plural = self.unit
        return plural

    def get_label(self, value):
        """Gets the label for a particular raw data value.
        If this is classified as `searchable`, a database hit will occur.
        """
        if self.searchable:
            kwargs = {self.field_name: value}
            if self.lexicon:
                return self.model.objects.filter(**kwargs)\
                    .values_list('label', flat=True)[0]
            if self.objectset:
                return self.model.objects.filter(**kwargs)\
                    .values_list('name', flat=True)[0]
            return smart_unicode(value)
        return dict(self.choices()).get(value, smart_unicode(value))

    # Data-related Cached Properties
    # These may be cached until the underlying data changes
    @cached_method(version='data_version')
    def size(self):
        "Returns the count of distinct values."
        return self.values_list().count()

    @cached_method(version='data_version')
    def values(self):
        "Returns a distinct list of the values."
        return tuple(self.values_list())

    @cached_method(version='data_version')
    def labels(self):
        """Returns an ordered set of labels corresponding to the values.
        If this field represents to a Lexicon subclass, the `label` field
        will be used, otherwise the values will simply be unicoded.
        """
        if self.lexicon:
            return tuple(self.model.objects.values_list('label', flat=True))
        if self.objectset:
            if hasattr(self.model, 'label_field'):
                field = self.model.label_field
            else:
                field = 'pk'
            return tuple(self.model.objects.values_list(field, flat=True))
        # Unicode each value, use an iterator here to prevent loading the
        # raw values in memory
        return map(smart_unicode, iter(self.values_list()))

    @cached_method(version='data_version')
    def codes(self):
        "Returns a distinct set of coded values for this field"
        if self.lexicon:
            return tuple(self.model.objects.values_list('code', flat=True))

    def choices(self):
        "Returns a distinct set of choices for this field."
        return zip(self.values(), self.labels())

    def coded_choices(self):
        "Returns a distinct set of coded choices for this field."
        if self.lexicon:
            return zip(self.codes(), self.labels())

    def coded_values(self):
        "Returns a distinct set of coded values for this field."
        if self.lexicon:
            return zip(self.values(), self.codes())

    # Data Aggregation Properties
    def groupby(self, *args):
        return Aggregator(self.field).groupby(*args)

    @cached_method(version='data_version')
    def count(self, *args, **kwargs):
        "Returns an the aggregated counts."
        return Aggregator(self.field).count(*args, **kwargs)

    @cached_method(version='data_version')
    def max(self, *args):
        "Returns the maximum value."
        return Aggregator(self.field).max(*args)

    @cached_method(version='data_version')
    def min(self, *args):
        "Returns the minimum value."
        return Aggregator(self.field).min(*args)

    @cached_method(version='data_version')
    def avg(self, *args):
        "Returns the average value. Only applies to quantitative data."
        if self.simple_type == 'number':
            return Aggregator(self.field).avg(*args)

    @cached_method(version='data_version')
    def sum(self, *args):
        "Returns the sum of values. Only applies to quantitative data."
        if self.simple_type == 'number':
            return Aggregator(self.field).sum(*args)

    @cached_method(version='data_version')
    def stddev(self, *args):
        "Returns the standard deviation. Only applies to quantitative data."
        if self.simple_type == 'number':
            return Aggregator(self.field).stddev(*args)

    @cached_method(version='data_version')
    def variance(self, *args):
        "Returns the variance. Only applies to quantitative data."
        if self.simple_type == 'number':
            return Aggregator(self.field).variance(*args)

    # Translator Convenience Methods
    @property
    def operators(self):
        "Returns the valid operators for this datafield."
        trans = translators[self.translator]
        return [(x, operators[x].verbose_name) for x
                in trans.get_operators(self)]

    def translate(self, operator=None, value=None, tree=None, **context):
        "Convenince method for performing a translation on a query condition."
        trans = translators[self.translator]
        return trans.translate(self, operator, value, tree, **context)

    def validate(self, operator=None, value=None, tree=None, **context):
        "Convenince method for performing a translation on a query condition."
        trans = translators[self.translator]
        return trans.validate(self, operator, value, tree, **context)


class DataConcept(BasePlural, PublishArchiveMixin):
    """Our acceptance of an ontology is, I think, similar in principle to our
    acceptance of a scientific theory, say a system of physics; we adopt, at
    least insofar as we are reasonable, the simplest conceptual scheme into
    which the disordered fragments of raw experience can be fitted and
    arranged.

        -- Willard Van Orman Quine
    """

    ident = models.CharField(max_length=100, null=True, blank=True,
                             validators=[validate_ident], help_text='Unique '
                             'identifier that can be used for programmatic '
                             'access')

    internal = models.BooleanField(default=False, help_text='Flag for '
                                   'internal use and does not abide by '
                                   'the published and archived rules.')

    # Although a category does not technically need to be defined, this more
    # for workflow reasons than for when the concept is published. Automated
    # prcesses may create concepts on the fly, but not know which category they
    # should be linked to initially. the admin interface enforces choosing a
    # category when the concept is published
    category = models.ForeignKey(DataCategory, null=True, blank=True)

    # The associated fields for this concept. fields can be
    # associated with multiple concepts, thus the M2M
    fields = models.ManyToManyField(DataField, through='DataConceptField',
                                    related_name='concepts')

    group = models.ForeignKey(Group, null=True, blank=True,
                              related_name='concepts+')

    # Certain concepts may not be relevant or appropriate for all
    # sites being deployed. This is primarily for preventing exposure of
    # access to private data from certain sites. For example, there may and
    # internal and external deployment of the same site. The internal site
    # has full access to all fields, while the external may have a limited set.
    # NOTE this is not reliable way to prevent exposure of sensitive data.
    # This should be used to simply hide _access_ to the concepts.
    sites = models.ManyToManyField(Site, blank=True, related_name='concepts+')

    order = models.FloatField(null=True, blank=True, db_column='_order')

    # An optional formatter which provides custom formatting for this
    # concept relative to the associated fields.
    formatter_name = models.CharField('formatter', max_length=100, blank=True,
                                      null=True,
                                      choices=formatters.registry.choices)

    # A flag that denotes this concept is viewable, that is, this the concept
    # is appropriate to be used as a viewable interface. Non-viewable concepts
    # can be used to prevent exposing underlying data that may not be
    # appropriate for client consumption.
    viewable = models.BooleanField(default=True)

    # A flag that denotes this concept is 'queryable' which assumes fields
    # that DO NOT result in a nonsensicle representation of the concept.
    queryable = models.BooleanField(default=True)

    # A flag that denotes when this concept can be applied to an ORDER BY
    # Certain concepts are not appropriate because they are too complicated,
    # or a very specific abstraction that does not order by what it actually
    # represents.
    sortable = models.BooleanField(default=True)

    objects = managers.DataConceptManager()

    def format(self, *args, **kwargs):
        """Convenience method for formatting data relative to this concept's
        associated formatter. To prevent redundant initializations (say, in
        a tight loop) the formatter instance is cached until the formatter
        name changes.
        """
        name = self.formatter_name
        cache = getattr(self, '_formatter_cache', None)
        if not cache or name != cache[0]:
            formatter = formatters.registry.get(name)(self)
            self._formatter_cache = (name, formatter)
        else:
            formatter = cache[1]
        return formatter(*args, **kwargs)

    class Meta(object):
        app_label = 'avocado'
        ordering = ('category__order', 'category__name', 'order', 'name')
        permissions = (
            ('view_dataconcept', 'Can view dataconcept'),
        )


class DataConceptField(models.Model):
    "Through model between DataConcept and DataField relationships."
    field = models.ForeignKey(DataField, related_name='concept_fields')
    concept = models.ForeignKey(DataConcept, related_name='concept_fields')

    name = models.CharField(max_length=100, null=True, blank=True)
    name_plural = models.CharField(max_length=100, null=True, blank=True)
    order = models.FloatField(null=True, blank=True, db_column='_order')

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta(object):
        ordering = ('order', 'name')

    def __unicode__(self):
        return unicode(self.name or self.field.name)

    def get_plural_name(self):
        return self.name_plural or self.field.get_plural_name()


class DataContext(AbstractDataContext, Base):
    """JSON object representing one or more data field conditions. The data may
    be a single condition, an array of conditions or a tree stucture.

    This corresponds to the `WHERE` statements in a SQL query.
    """
    session = models.BooleanField(default=False)
    template = models.BooleanField(default=False)
    default = models.BooleanField(default=False)

    # The parent this instance was derived from
    parent = models.ForeignKey('self', null=True, blank=True,
                               related_name='forks')

    # For authenticated users the `user` can be directly referenced,
    # otherwise the session key can be used.
    user = models.ForeignKey(User, null=True, blank=True,
                             related_name='datacontext+')
    session_key = models.CharField(max_length=40, null=True, blank=True)

    accessed = models.DateTimeField(default=datetime.now(), editable=False)
    objects = managers.DataContextManager()

    def __unicode__(self):
        toks = []

        # Identifier
        if self.name:
            toks.append(self.name)
        elif self.user_id:
            toks.append(unicode(self.user))
        elif self.session_key:
            toks.append(self.session_key)
        elif self.pk:
            toks.append('#{0}'.format(self.pk))
        else:
            toks.append('unsaved')

        # State
        if self.default:
            toks.append('default template')
        elif self.template:
            toks.append('template')
        elif self.session:
            toks.append('session')
        else:
            toks.append('rogue')

        return u'{0} ({1})'.format(*toks)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.template and self.default:
            queryset = self.__class__.objects.filter(template=True,
                                                     default=True)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                raise ValidationError('Only one default template can be '
                                      'defined')

    def save(self, *args, **kwargs):
        self.clean()
        super(self.__class__, self).save(*args, **kwargs)


class DataView(AbstractDataView, Base):
    """JSON object representing one or more data field conditions. The data may
    be a single condition, an array of conditions or a tree stucture.

    This corresponds to the `SELECT` and `ORDER BY` statements in a SQL query.
    """
    session = models.BooleanField(default=False)
    template = models.BooleanField(default=False)
    default = models.BooleanField(default=False)

    # The parent this instance was derived from
    parent = models.ForeignKey('self', null=True, blank=True,
                               related_name='forks')

    # For authenticated users the `user` can be directly referenced,
    # otherwise the session key can be used.
    user = models.ForeignKey(User, null=True, blank=True,
                             related_name='dataview+')
    session_key = models.CharField(max_length=40, null=True, blank=True)

    accessed = models.DateTimeField(default=datetime.now(), editable=False)
    objects = managers.DataViewManager()

    def __unicode__(self):
        toks = []

        # Identifier
        if self.name:
            toks.append(self.name)
        elif self.user_id:
            toks.append(unicode(self.user))
        elif self.session_key:
            toks.append(self.session_key)
        elif self.pk:
            toks.append('#{0}'.format(self.pk))
        else:
            toks.append('unsaved')

        # State
        if self.default:
            toks.append('default template')
        elif self.template:
            toks.append('template')
        elif self.session:
            toks.append('session')
        else:
            toks.append('rogue')

        return u'{0} ({1})'.format(*toks)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.template and self.default:
            queryset = self.__class__.objects.filter(template=True,
                                                     default=True)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                raise ValidationError('Only one default template can be '
                                      'defined')

    def save(self, *args, **kwargs):
        self.clean()
        super(self.__class__, self).save(*args, **kwargs)


class DataQuery(AbstractDataQuery, Base):
    """
    JSON object representing a complete query.

    The query is constructed from a context(providing the 'WHERE' statements)
    and a view(providing the 'SELECT' and 'ORDER BY" statements). This
    corresponds to all the statements of the SQL query to dictate what info
    to retrieve, how to filter it, and the order to display it in.
    """
    session = models.BooleanField(default=False)
    template = models.BooleanField(default=False)
    default = models.BooleanField(default=False)

    # The parent this instance was derived from
    parent = models.ForeignKey('self', null=True, blank=True,
                               related_name='forks')

    # For authenticated users the `user` can be directly referenced,
    # otherwise the session key can be used.
    user = models.ForeignKey(User, null=True, blank=True,
                             related_name='dataquery+')
    session_key = models.CharField(max_length=40, null=True, blank=True)

    accessed = models.DateTimeField(default=datetime.now, editable=False)
    objects = managers.DataQueryManager()
    shared_users = models.ManyToManyField(User,
                                          related_name='shareddataquery+')

    # Flag indicating whether this is a public query or not. Public queries are
    # visible to all other users of the system while non-public queries are
    # only visible to the query owner and those in the shared_users collection.
    public = models.BooleanField(default=False)

    def __unicode__(self):
        toks = []

        # Identifier
        if self.name:
            toks.append(self.name)
        elif self.user_id:
            toks.append(unicode(self.user))
        elif self.session_key:
            toks.append(self.session_key)
        elif self.pk:
            toks.append('#{0}'.format(self.pk))
        else:
            toks.append('unsaved')

        # State
        if self.default:
            toks.append('default template')
        elif self.template:
            toks.append('template')
        elif self.session:
            toks.append('session')
        else:
            toks.append('rogue')

        return u'{0} ({1})'.format(*toks)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.template and self.default:
            queryset = self.__class__.objects.filter(template=True,
                                                     default=True)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                raise ValidationError('Only one default template can be '
                                      'defined')

    def save(self, *args, **kwargs):
        self.clean()
        super(self.__class__, self).save(*args, **kwargs)

    def share_with_user(self, email, create_user=True):
        """
        Attempts to add a user with the supplied email address to the list of
        shared users for this query. If create_user is set to True, users will
        be created for emails that are not already associated with an
        existing user.

        Returns True if the email was added to the list of shared users and
        False if the email wasn't added because it already exists or wasn't
        created.
        """
        # If the query is already shared then there is no need to share it
        # again.
        if self.shared_users.filter(email=email).exists():
            return False

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            if not create_user:
                return False
            else:
                user = utils.create_email_based_user(email)

        self.shared_users.add(user)
        self.save()

# Register instance-level cache invalidation handlers
post_save.connect(post_save_cache, sender=DataField)
post_save.connect(post_save_cache, sender=DataConcept)
post_save.connect(post_save_cache, sender=DataCategory)

pre_delete.connect(pre_delete_uncache, sender=DataField)
pre_delete.connect(pre_delete_uncache, sender=DataConcept)
pre_delete.connect(pre_delete_uncache, sender=DataCategory)

# Register with history API
if settings.HISTORY_ENABLED:
    history.register(DataContext, fields=('name', 'description', 'json'))
    history.register(DataView, fields=('name', 'description', 'json'))
    history.register(DataQuery, fields=('name', 'description', 'context_json',
                                        'view_json'))
