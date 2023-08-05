=========
SilvaFind
=========

SilvaFind is a powerful search feature to allow easy creation of search forms
and result pages, both for users of the public site and for authors in the SMI.
Simple schemas can be defined to indicate which fields should be searchable.

Authors can add a *Silva Find* object anywhere and define which fields to
make searchable by end users of the public site, and/or which fields to
limit to a preset value. Authors also can determine which fields should be
displayed in the search results. All metadata set/fields are supported.

If you can't add the *Silva Find* object in the SMI you should make sure it's
checked in the *addables* section of the publication. If Silva Find is not 
checked, check it and uncheck the inheritance checkbox (otherwise inheritance 
will overrule it and uncheck it again).

By default all possible custom search criterion fields and result fields are 
available in the SMI. Besides that, the elements of all metadata sets are also
available as result fields. If these fields are indexed in the catalog, they
can also be used as search criterion fields. All available fields can be 
enabled/disabled in the SMI.

Besides this behavior, SilvaFind also allows you to manually override the list
of search criteria. This behavior is also intended for backwards compatibility,
but can be used to add your own custom fields from within other products.

For example the default global schema that SilvaFind installs
(``globalschema.py``) looks as follows::

    from Products.Silva.i18n import translate as _

    from Products.SilvaFind.schema import SearchSchema
    from Products.SilvaFind.schema import ResultsSchema

    from Products.SilvaFind.schema import ResultField
    from Products.SilvaFind.schema import FullTextCriterionField
    from Products.SilvaFind.schema import MetadataCriterionField
    from Products.SilvaFind.schema import MetatypeCriterionField
    from Products.SilvaFind.schema import DateRangeMetadataCriterionField

    globalSearchSchema = SearchSchema([
        MetatypeCriterionField(),
        FullTextCriterionField(),
        MetadataCriterionField('silva-content', 'maintitle'),
        MetadataCriterionField('silva-content', 'shorttitle'),
        DateRangeMetadataCriterionField('silva-extra', 'publicationtime'),
        ])

    globalResultsSchema = ResultsSchema([
        ResultField('get_title', _('Title')),
        ])

The result schema defines what fields get shown in the list of results, by
default as columns in a results table. There are currently 3 types of
result fields (plain vanilla, metatype and metadata), and it is not hard to
make your own. See schema.py for how that is done.

The following SearchField types exist for now, and of course it is possible
to roll your own:

``MetatypeCriterionField``
     allows the content that is to be searched, to be restricted to
     certain (one or more) content types.

``FulltextCriterionField``
     allows the fulltext of the content item to be searched.

``MetadataCriterionField`` 
     allows a specific metadata field of a specific metadata set to be
     searched.

``DateRangeMetadataCriterionField``
     allows a specific datetime based metadata field of a specific
     metadata set to be searched, using a date range.

``PathCriterionField``
     allows the content that is to be searched, to be restricted to be
     below a certain path. The path of the found children will always
     start with the supplied path, which is a string starting from the
     site root.

Making your own is as simple as creating a different SearchSchema and
ResultsSchema in your extension, and registering it in the install.py of
your extension. You can replace the global default search schema as
follows, assuming myOwnSearchSchema is a valid SearchSchema object::

    def register_search_schema(root):
        root.service_find.search_schema = myOwnSearchSchema
        root.service_find.manage_delObjects(['default'])
        SilvaFind.manage_addSilvaFind(
            root.service_find, 'default', 'Default search')
        default = root.service_find.default
        for field in root.service_find.getSearchSchema().getFields():
            fieldName = field.getName()
            default.shownFields[fieldName] = True
        default._p_changed = True

If your extension defines its own metadata-set, making the fields in
that set searchable by putting them in your schema is easy::

    myOwnSearchSchema = SearchSchema([

        ...

        MetadataCriterionField('my-metadataset', 'my-field1'),
        MetadataCriterionField('my-metadataset', 'my-field2'),

        ...

        ])

For a good example of how to customize and use SilvaFind from your own
extension, see the Silva DLCMS, which you can find here::

   svn co https://infrae.com/svn/dlcms/SilvaDLCMS/trunk/ SilvaDLCMS

and look at ``searchschema.py``.
