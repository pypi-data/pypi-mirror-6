from django.db import transaction
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from avocado.models import DataField, DataConcept, DataCategory, \
    DataConceptField, DataView, DataContext, DataQuery
from avocado.forms import DataFieldAdminForm


class PublishedAdmin(admin.ModelAdmin):
    list_per_page = 25
    save_as = True
    actions_on_bottom = True

    # Filter by status
    list_filter = ('published', 'archived')

    # Archived are at the bottom, followed by unpublished, then by name
    ordering = ('archived', '-published', 'name')

    # List here to enable viewing the data
    readonly_fields = ('created', 'modified')
    # TODO change behavior to use Haystack
    search_fields = ('name', 'description', 'keywords')

    # Actions to toggle published and archived status
    actions = ('mark_published', 'mark_unpublished', 'mark_archived',
               'mark_unarchived')

    # Override to make the description consistent with the rest of
    # the actions
    def get_actions(self, request):
        actions = super(PublishedAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'][0].short_description = 'Delete'
        return actions

    def mark_published(self, request, queryset):
        queryset.update(published=True)
    mark_published.short_description = 'Publish'

    def mark_unpublished(self, request, queryset):
        queryset.update(published=False)
    mark_unpublished.short_description = 'Unpublish'

    def mark_archived(self, request, queryset):
        queryset.update(archived=True)
    mark_archived.short_description = 'Archive'

    def mark_unarchived(self, request, queryset):
        queryset.update(archived=False)
    mark_unarchived.short_description = 'Unarchive'


class LexiconListFilter(SimpleListFilter):
    title = _('lexicon')

    parameter_name = 'lexicon'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Yes')),
            ('0', _('No')),
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value:
            subquery = queryset.only('app_name', 'model_name', 'field_name')
            ids = [x.pk for x in subquery if x.lexicon]
            if value == '1':
                queryset = queryset.filter(id__in=ids)
            else:
                queryset = queryset.exclude(id__in=ids)
            return queryset


class ObjectSetListFilter(SimpleListFilter):
    title = _('objectset')

    parameter_name = 'objectset'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Yes')),
            ('0', _('No')),
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value:
            subquery = queryset.only('app_name', 'model_name', 'field_name')
            ids = [x.pk for x in subquery if x.objectset]
            if value == '1':
                queryset = queryset.filter(id__in=ids)
            else:
                queryset = queryset.exclude(id__in=ids)
            return queryset


class DataFieldAdmin(PublishedAdmin):
    form = DataFieldAdminForm

    list_display = ('name', 'published', 'archived', 'internal',
                    'orphan_status', 'model_name', 'enumerable',
                    'is_lexicon', 'is_objectset', 'related_dataconcepts')

    list_filter = ('published', 'archived', 'internal', 'model_name',
                   'enumerable', LexiconListFilter, ObjectSetListFilter)

    list_editable = ('published', 'archived', 'internal', 'enumerable')

    search_fields = ('name', 'description', 'keywords')

    readonly_fields = ('created', 'modified', 'data_version')

    actions = ('mark_published', 'mark_unpublished', 'mark_archived',
               'mark_unarchived', 'create_dataconcept_multi',
               'create_dataconcept_single')

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'name_plural',
                'description',
                'keywords',
                'unit',
                'unit_plural',
                'published',
                'archived',
            ),
        }),

        ('Internal Use', {
            'fields': ('internal',),
            'description': 'Flag as internal if this concept is is intended '
                           'for programmatic access only.',
        }),

        ('Query Modifiers', {
            'fields': ('translator', 'enumerable')
        }),

        ('Data Source', {
            'description': ('These fields should not be altered in-place. '
                            'If where this field is located has changed, '
                            'change these values and create a new field by '
                            'using "Save as new".'),
            'classes': ('collapse',),
            'fields': ('app_name', 'model_name', 'field_name'),
        }),

        ('Times of Interest', {
            'fields': ('created', 'modified'),
        }),
    )

    def orphan_status(self, obj):
        if obj.model is None:
            return 'Unknown Model'
        if obj.field is None:
            return 'Unknown Model Field'
        return 'OK'
    orphan_status.short_description = 'Orphan Status'

    def is_lexicon(self, obj):
        return obj.lexicon
    is_lexicon.short_description = 'Is Lexicon'

    def is_objectset(self, obj):
        return obj.objectset
    is_objectset.short_description = 'Is ObjectSet'

    def related_dataconcepts(self, obj):
        queryset = obj.concepts.only('id', 'name')
        reverse_name = 'admin:avocado_dataconcept_change'
        urlize = lambda x: u'<a href="{0}">{1}</a>'.format(reverse(
            reverse_name, args=[x.id]), x.name)
        return '<br>'.join(map(urlize, queryset)) or None
    related_dataconcepts.short_description = 'Related Data Concepts'
    related_dataconcepts.allow_tags = True

    def create_dataconcept_multi(self, request, queryset):
        for datafield in queryset:
            DataConcept.objects.create_from_field(datafield)
    create_dataconcept_multi.short_description = 'Create Data Concept for Each'

    @transaction.commit_on_success
    def create_dataconcept_single(self, request, queryset):
        fields = list(queryset)

        # If only a single field is selected with this action, directly map
        if len(fields) == 1:
            DataConcept.objects.create_from_field(fields[0])
            return

        max_length = DataConcept._meta.get_field_by_name('name')[0].max_length
        name = ', '.join([f.name for f in fields])[:max_length - 5] + '...'
        concept = DataConcept(name=u'"{0}"'.format(name))
        concept.save()
        for i, datafield in enumerate(queryset):
            DataConceptField(concept=concept, field=datafield, order=i).save()
    create_dataconcept_single.short_description = 'Create Data Concept for ' \
        'Selected'


class DataConceptFieldInlineAdmin(admin.TabularInline):
    model = DataConceptField


class DataConceptAdmin(PublishedAdmin):
    list_display = ('name', 'published', 'archived', 'internal', 'category',
                    'order', 'formatter_name', 'viewable', 'queryable',
                    'sortable', 'related_datafields')

    list_editable = ('published', 'archived', 'internal', 'category', 'order',
                     'formatter_name', 'viewable', 'queryable', 'sortable')

    list_filter = ('published', 'archived', 'category', 'formatter_name',
                   'viewable', 'queryable', 'sortable')

    inlines = [DataConceptFieldInlineAdmin]

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'name_plural',
                'description',
                'keywords',
                'category',
                'order',
                'published',
                'archived',
            ),
        }),

        ('Internal Use', {
            'fields': ('internal', 'ident'),
            'description': 'Flag as internal if this concept is is intended '
                           'for programmatic access only.',
        }),

        ('Modifiers', {
            'fields': ('formatter_name', 'viewable', 'queryable', 'sortable'),
        }),

        ('Times of Interest', {
            'fields': ('created', 'modified'),
        }),
    )

    def related_datafields(self, obj):
        queryset = obj.fields.only('id', 'name')
        reverse_name = 'admin:avocado_datafield_change'
        urlize = lambda x: u'<a href="{0}">{1}</a>'.format(reverse(
            reverse_name, args=[x.id]), x.name)
        return '<br>'.join(map(urlize, queryset)) or None
    related_datafields.short_description = 'Related Data Fields'
    related_datafields.allow_tags = True


class DataCategoryAdmin(admin.ModelAdmin):
    model = DataCategory

    list_display = ('name', 'parent', 'order')

    list_editable = ('parent', 'order')


class DataViewAdmin(admin.ModelAdmin):
    readonly_fields = ('session_key', 'sql')

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'description',
                'keywords',
            ),
        }),

        ('User', {
            'fields': ('user', 'session_key', 'session')
        }),

        ('Template', {
            'fields': ('template', 'default')
        }),

        ('JSON', {
            'fields': ('json',),
            'description': 'JSON representation of the view',
        }),

        ('SQL', {
            'fields': ('sql',),
            'description': 'Formatted SQL representation of the view',
        }),
    )

    def sql(self, obj):
        sql = obj.sql()
        try:
            import sqlparse
            sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
        except ImportError:
            pass
        return u'<pre>{0}</pre>'.format(sql)
    sql.short_description = 'SQL'
    sql.allow_tags = True


class DataContextAdmin(admin.ModelAdmin):
    readonly_fields = ('session_key', 'count', 'sql')

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'description',
                'keywords',
            ),
        }),

        ('User', {
            'fields': ('user', 'session_key', 'session')
        }),

        ('Template', {
            'fields': ('template', 'default')
        }),

        ('Stats', {
            'fields': ('count',)
        }),

        ('JSON', {
            'fields': ('json',),
            'description': 'JSON representation of the context',
        }),

        ('SQL', {
            'fields': ('sql',),
            'description': 'Formatted SQL representation of the context',
        }),
    )

    def sql(self, obj):
        sql = obj.sql()
        try:
            import sqlparse
            sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
        except ImportError:
            pass
        return u'<pre>{0}</pre>'.format(sql)
    sql.short_description = 'SQL'
    sql.allow_tags = True


class DataQueryAdmin(admin.ModelAdmin):
    readonly_fields = ('distinct_count', 'record_count', 'session_key', 'sql')

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'description',
                'keywords',
                'public',
            ),
        }),

        ('User', {
            'fields': ('user', 'session_key', 'session')
        }),

        ('Template', {
            'fields': ('template', 'default')
        }),

        ('Stats', {
            'fields': ('distinct_count', 'record_count')
        }),

        ('JSON', {
            'fields': ('view_json', 'context_json'),
            'description': 'JSON representation of the context and view',
        }),

        ('SQL', {
            'fields': ('sql',),
            'description': 'Formatted SQL representation of the query',
        }),
    )

    def sql(self, obj):
        sql = obj.sql()
        try:
            import sqlparse
            sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
        except ImportError:
            pass
        return u'<pre>{0}</pre>'.format(sql)
    sql.short_description = 'SQL'
    sql.allow_tags = True


admin.site.register(DataField, DataFieldAdmin)
admin.site.register(DataConcept, DataConceptAdmin)
admin.site.register(DataCategory, DataCategoryAdmin)

admin.site.register(DataView, DataViewAdmin)
admin.site.register(DataContext, DataContextAdmin)
admin.site.register(DataQuery, DataQueryAdmin)
