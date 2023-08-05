# Datatable View

This package is used in conjunction with the jQuery plugin [DataTables](http://http://datatables.net/), and supports state-saving detection with [fnSetFilteringDelay](http://datatables.net/plug-ins/api).  The package consists of a class-based view, and a small collection of utilities for rendering table data from models.

Dependencies: [dateutil](http://labix.org/python-dateutil) library for flexible, fault-tolerant date parsing.

## Table of Contents
* [Usage](#usage)
* [Column declaration](#column-declaration)
* [Other datatable_options](#other-datatable_options)
* [DatatableView attributes and methods](#datatableview-attributes-and-methods)
* [x-editable datatables](#x-editable-datatables)
* [Custom table rendering](#custom-table-rendering)
* [Modifying dataTables JavaScript options](#modifying-datatables-javascript-options)
* [Advanced sorting of pure virtual columns](#advanced-sorting-of-pure-virtual-columns)
* [Utility helper methods for custom callbacks](#utility-helper-methods-for-custom-callbacks)
* [Javascript "clear" event](#javascript-clear-event)
* [Authors](#authors)
* [Copyright and license](#copyright-and-license)

## Usage

The basic template for usage in a view is shown below.

```python
# views.py

from datatableview.views import DatatableView
from myapp.models import MyModel

class MyListView(DatatableView):
    datatable_options = {
        'columns': ['field_name1', 'field_name2'],
    }

    def get_queryset(self):
        return MyModel.objects.filter(user=self.request.user)
```

`DatatableView` inherits from the generic `ListView` built-in view.  This means that as a foundation, a datatable-enhanced view requires very little extra configuration to get off the ground.  Methods such as `get_queryset()` function normally.

The simplest way to output this simple table as HTML in a template is to use the `datatable` context variable, which `DatatableView` makes available via `get_context_data()`.  (So if you override `get_context_data()`, be sure to call `super()`!).

Thus, in your template ("mymodel_list.html" if we're following the standard ListView template naming scheme), you would echo the value where you want the table to appear:

```html
{# mymodel_list.html #}

{% block media %}
    <script type="text/javascript" src="{{ STATIC_URL }}js/jquery.dataTable.js"></script>
    <script type="text/javascript" src="{{ STATIC_URL }}js/datatableview.js"></script>
{% endblock %}

{% block content %}
    {{ datatable }}
{% endblock %}
```

The `datatable` context variable is a basic object that has a unicode representation matching the configuration options specified in the originating view.  The output is a table skeleton of just table headers, annotated with information that the provided `datatableview.js` file will use to
detect and bootstrap the table's interactive features, including fetching the first batch of AJAX data.

Each of the generated datatable `<th>` elements have a custom attribute "data-name", whose values are just the header name put through the `slugify` template filter.  This provides a simple way for CSS to be provided on the page to specify style attributes such as column width:

```css
.datatable th[data-name="slugified-field-name"] {
    width: 20%;
}
```

#### Using a datatable inside of another view

Using the above `MyListView` we can integrate this into another view (DetailView, EditView,
TemplateView, etc.) as follows. The function `get_datatable_structure` is a wrapper to integrate
datatables into your other views with little pain.

```python
# views.py
from datatableview.utils import get_datatable_structure

class MyTemplateView(TemplateView):
    template_name = "template.html"

    def get_context_data(self, **kwargs):
        context = super(MyTemplateView, self).get_context_data(**kwargs)

        ajax_url = reverse('myapp:list')
        options = MyListView.datatable_options.copy()
        context['datatable'] = get_datatable_structure(ajax_url, MyModel, options)
        return context
```

Then use `{{ datatable }}` inside of your template as detailed above.


## Column declaration

While the first natural step is to display columns backed by concrete fields on your model, it doesn't take long to find yourself requiring richer output information.

#### Changing the column's display name

The column header's displayed title is by default a mangling of the field name given in the column options.  For example, "field_name1" turns into "Field name" if left alone.  To give it an arbitrary label better suited for the frontend, change the entry in the column options to a 2-tuple of the friendly name and the model field name:

```python
datatable_options = {
    'columns': [
        ("Friendly Name", 'field_name1'),
        'field_name2',
    ],
}
```

`field_name2` is left to behave normally, while `field_name1` will display on the table as "Friendly Name".

Django's relationship-spanning lookups can be used here as well:

```python
datatable_options = {
    'columns': [
        ('Company Name', 'company__name'),
        'field_name2',
    ]
}
```

#### Compound columns

When a column in the table is actually built using data from multiple model fields, such as a series of fields that together form a full address, the column options can be given to provide the necessary hints for the searching logic to do the right thing.

Since multiple model fields together aren't likely to make a very good table header label, you should use the format in the section just above, where you provide a custom name.

Using the example of a compound address table column:

```python
datatable_options = {
    'columns': [
        ('Address', ['street_line1', 'street_line2', 'city', 'state']),
        'field_name2',
    ],
}
```

This configuration will produce a column titled "Address", whose contents is all of the database field values joined with a space.  That format might not be good enough for something as punctuated as an address should be, so you should consult the [Customizing column output](#customizing-column-output) section below to understand how to manually format the table cell contents beyond this default.  This configuration, however, is fully capable of providing database-backed searching features for the listed columns.

#### Pure virtual columns

If you need a table column that has no specific database-backed field, whether because it's a purely computed value from a model's method or for some other complex manipulation, a virtual column name can be used in the options:

```
datatable_options = {
    'columns': [
        'Fictitious',
        'field_name2',
    ],
}
```

In this example the column called "Fictitious" is capitalized to help keep clear its virtual nature.  When the view logic goes to interpret the column options, it will find that "Fictitious" is not a valid field name, given the model defined by the view (or taken from the view's queryset).  The column has no database fields to back it, which means this column currently has no way to provide its value.

Continue to the next section [Customizing column output](#customizing-column-output) to create a mechanism for providing arbitrary column data.

#### Customizing column output

When each resulting record returned by the queryset is serialized to JSON for transport back to the client, each column has a chance to modify its displayed value.

Each column name (whether concrete, compound, or virtual) will be used to check the view for callback methods.  If the method exists, it will be called and passed the instance of the object being rendered.  The method can return whatever it wants.  If the column is database-backed by a model field, one would expect the output to simply be some lightly decorated version of the same thing.

A contrived example following from the original configuration sample:

```python
class MyListView(DatatableView):
    datatable_options = {
        'columns': [
            ('Friendly Name', 'field_name1'),
            'field_name2',
        ],
    }

    # ... get_queryset() or model should be defined

    def get_column_Friendly_Name_data(self, instance, *args, **kwargs):
        return "{:.2f}".format(instance.field_name1)

    def get_column_field_name2_data(self, instance, *args, **kwargs):
        return "<em>{}</em>".format(self.field_name2)
```

As shown, methods in the form `get_column_FIELD_NAME_data()` can be defined on the view to override the output of the column.

**IMPORTANT**: In the case of these two sample fields, both are concrete, being backed by real database fields.  The data returned by these methods are consequently for display purposes.  Any time that concrete model fields back a column, those fields are used for sorting and searching, not the output of the callback methods.

As demonstrated in the example, it is the actual column name that is used for the callback method naming style, where case is unmodified and non-alphanumeric characters are collapsed to underscores.  If a friendly name is "Completion: Percentage", the mangled name used for method lookup would be "Completion_Percentage", ultimately pointing to a method called `get_column_Completion_Percentage_data()`.

**NOTE**: These methods should take the `*args` and `**kwargs` argument names for good practice.  Their use is described in the following section [Handling expensive data generation](#handling-expensive-data-generation).  By default the view will only send one keyword argument: `default_value` is the value fetched from the specified model field(s), if any.

If ever the name mangling is unintuitive or unnecessarily complex, callback names can also be given via the column's 0-based index.  In the example above, the method names could could instead be given as `get_column_0_data()` and `get_column_1_data()` respectively.

Alternatively, columns can explicitly declare a method name as part of the column configuration, using a 3-tuple instead of a 2-tuple:

```python
class MyListView(DatatableView):
    datatable_options = {
        'columns': [
            ('Friendly Name', 'field_name1', 'get_friendly_data'),
            'field_name2',
        ],
    }

    # ...

    def get_friendly_data(self, instance, *args, **kwargs):
        return "{:.2f}".format(instance.field_name1)
```

If the callback name in the configuration (e.g., `"get_friendly_data"`) were a full callable function instead of a string, the function would be used directly, as opposed to looking up any method on the view itself.

Finally, a purely virtual table column can also declare an explicit callback name using the 3-tuple pattern:

```python
class MyListView(DatatableView):
    datatable_options = {
        'columns': [
            ('Fictitious', None, 'get_fictitious_data'),
            'field_name2',
        ],
    }

    # ...

    def get_fictitious_data(self, instance, *args, **kwargs):
        return instance.get_generated_data()
```

Note that because the column is completely virtual and has no model fields backing it, `None` is provided in the place of a field name (or list of field names).

#### Handling expensive data generation

The callback methods described in [Customizing column output](#customizing-column-output) are very helpful for generating interactive data columns, such as links to deeper views, cross links to other sections of the site, or just computed mashups of data not strictly represented in any set of columns.

If multiple of the callback methods needs to do some expensive computation, each model instance (or record, in the terminology of the frontend datatable) can preload arbitrary values that will be sent to all of the view's data-supplying callback methods, either as `*args` or `**kwargs`, depending on how you prefer your implementation.

The special method `preload_record_data()` can return these values, computed once per record and passed to the various callbacks without slamming the database or CPU any heavier than expected:

```python
class MyListView(DatatableView):
    datatable_options = {
        'columns': [
            ('Fictitious', None, 'get_fictitious_data'),
            'field_name2',
        ],
    }

    # ...

    def preload_record_data(self, instance):
        users = instance.get_authorized_users()

        return (users,)

    def get_fictitious_data(self, instance, users, *args, **kwargs):
        return instance.get_generated_data(users)
```

In this example, `preload_record_data()` creates a value, presumably some kind of iterable of User objects, and returns it as a 1-tuple.  This 1-tuple will be expanded and sent to all callbacks, which led us to change our callback signature to include a `users` argument.

Alternatively, a tuple with more elements can be returned with whatever data is crunched:

```
def preload_record_data(self, instance):
    users = instance.get_authorized_users()
    groups = instance.get_authorized_groups()

    return (users, groups)

def get_fictitious_data(self, instance, users, groups, *args, **kwargs):
    return instance.get_generated_data(users)
```

A callback is of course not required to use the data sent to it, since pre-crunched data might only be relevant to a handful of the callbacks.

If the object returned by `preload_record_data()` is a dictionary, not a tuple or list, it will be instead unpacked as the `**kwargs` for the callback methods.

Currently the two return types can not be mixed.

## Other datatable_options
`'columns'` is just one of the top-level keys for the `datatable_options` structure.

#### `ordering`
_Default: `[]`_

A list of field orderings.  Prefix `-` and `+` are valid, and field names should be the Django field name if the column is singular and concrete, or else the field name should be the column's "Pretty Name" if the field is compound or purely virtual.  Consequently, `['-Friendly Name', '+field2_name']` is a valid ordering definition

#### `search_fields`
_Default: `[]`_

A list of filter-like ORM fields that are always appended to the list of search fields when a search is performed on the table.  `search_fields` should only contain ORM paths to fields that aren't already in the column definitions, since those are already searched by default.  Instead, this option allows the arbitrary addition of search channels, where the data may not be visible to the frontend, but known by the user.  For example, a datatable of user accounts may not show the geographic country associated with their profile, but the country can be made searchable by using something like `['profile__country__name']` as the `search_fields` value.

#### `unsortable_columns`
_Default: `[]`_

A list of column names (the Django field name for simple single-field columns, or else the "Friendly Name" for compound or virtual ones) that should not render sorting arrows on the datatable headers.

#### `hidden_columns`
_Default: `[]`_

A list of column names (the Django field name for simple single-field columns, or else the "Friendly Name" for compound or virtual ones) that should use the `bVisible=false` datatables option.  This allows the frontend to hide the data while keeping it available for searches and client-side export features.

#### `structure_template`
_Default: `"datatableview/default_structure.html"`_

The default template name that a datatable structure will render when coerced to unicode.  This template is normally responsible for rendering a table with a `class="datatable"` attribute that will be detected by the packaged `datatableview.js` code.  The table's `th` header elements dump the configuration options given to them by the view's `datatable_options` so that the javascript can read them and configure the table correctly.

#### `result_counter_id`
_Default: `"id_count"`_

Any time the table's contents changes, the javascript will look on the page for a DOM element with the ID given by this value.  The DOM node's contents will be replace with the `iTotal` javascript value, which is the number of visible results remaining after a search.

This is slightly tied to the business logic of the origin project that generated this Django package.  This functionality might be more intuitively accessed for users of traditional `dataTables.js` by modifying the library's callbacks (see [Modifying dataTables JavaScript options](#modifying-datatables-javascript-options)).

## DatatableView attributes and methods
#### ``datatable_options`` and ``get_datatable_options()``
This is the central dict structure that contains all of the options discussed above.

You can modify the options at runtime via the ``get_datatable_options()`` method, but be careful how you change mutable structures.  By default, adding or remove keys to the class-wide definition on ``self`` will yield strange duplication issues.

If you are modifying the class-defined dict, **make a copy** of the dict and any column lists, or else the object will persist across connections and every time you reload the page, you'll find your dynamic modifications compounding and causing errors!

#### ``datatable_context_name`` and ``get_datatable_context_name()``
**Default**: ``"datatable"``

Specifies the variable name to be used in the template context for the ``datatable`` structure object.  As with the built-in Django generic views, the method overrides the attribute.

#### ``get_json_response_object(object_list, total, filtered_total)``
This is the method responsible for building the response dictionary that will be the JSON response to the AJAX query.  If any paging is required, ``object_list`` is shortened to match the correct offset and length.  The default implementation then runs each item in ``object_list`` through the column data callbacks, and adds the ``total`` and ``filtered_total`` statistics into the response object.

``total`` is the number of records on the base queryset _before_ any searches were applied, while ``filtered_total`` is the number of records _after_ the searches were applied.  Note that ``filtered_total`` is not the length of the page, as the page length is likely a static number such as 25, and a search might yield more results than that, presented on multiple pages.

The resulting object might look like this:

```python
{
    "aaData": [
        {
            "1": "10",
            "0": "<a href=\"/object/10/\">My Object</a>",
            "DT_RowId": 10
        }
    ],
    "iTotalRecords": 57,
    "iTotalDisplayRecords": 1,
    "sEcho": "48"
}
```

Note that the keys in this object are now named as the dataTables.js system expects.

This object will be serialized directly into JSON without any further modifications, so if the view needs to put additional items into the response for custom client-side operations, this is the correct place to do that.

## x-editable datatables

If you wish to create in-place editable tables over ajax, you can use the [x-editable](http://vitalets.github.io/x-editable/docs.html) Javascript tools.  This allows you an almost zero-configuration option for basic tables.

The [``make_xeditable()``](#make_xeditable) helper function can be used as a column callback.  It can accept various options for customization, or given directly for default behavior.

Note that the following strategy officially supports only fields found directly on the originating queryset model.

In order for the xedtiable Javascript to succesfully POST ajax updates for client-side changes, you will need to either supply a custom ``url`` paramater to the helper function which will fulfill the ajax requirements, or you can just change the parent class of your view from ``DatatableView`` to ``XEditableDatatableView``.

For example, you can pick and choose which columns receive the special x-editable treatment by simply providing the helper as a callback for that column:

```python
from datatableview.views import XEditableDatatableView
from datatableview.helpers import make_xeditable

class EditableView(XEditableDatatableView):
	datatable_options = {
	    'columns': [
	        ("Friendly Name", 'field_name1', make_xeditable),
	        'field_name2',
	    ],
	}
```

See the [``make_xeditable()``](#make_xeditable) helper reference for the details of how to customize how it works.

Finally, to get the client-side table rendering to activate the xeditable Javascript, add something such as this to your template:

```javascript
function confirm_datatable_options(options) {
    var xeditable_options = {};
    var xeditable_row_callback = datatableview.make_xeditable(xeditable_options);
    options.fnRowCallback = xeditable_row_callback;
    return options;
}
```

This takes advantage of the global ``confirm_datatable_options()`` function hook that datatableview.js will consult when it automatically detects a rendered datatable.  (See [Modifying dataTables JavaScript options](#modifying-datatables-javascript-options) for more about this strategy.)

In this example, we're using the global ``datatableview`` Javascript object to access a factory function named after the ``make_xeditable`` helper.  Provide it with options you wish to pass through to the initialization of the xeditable Javascript.  The options will have a CSRF token added to the ajax headers when POST updates occur (with the help of the Django-provided CSRF cookie).  The options will also be modified to include a simple xeditable ``success`` handler to raise any validation error messages raised during the POST.

With this piece in place, the work done with the ``helpers.make_xeditable()`` will now be picked up and initialized correctly.

## Custom table rendering

By default, a DatatableView includes an object in the context called `datatable`, whose unicode rendering is the table skeleton.  Together with the supplied generic javascript file, the datatable is automatically brought to life according to the view's configuration.

If the table needs custom rendering, you can instead iterate over the `datatable` object in the template.  An equivalent to the default skeleton can be rendered in this style by using the following template HTML:

```html
# object_list.html

{# ... #}
<table class="datatable" data-url="{{ datatable.url }}">
    <tr>
        {% for name, attributes in datatable %}
        <th data-name="{{ name|slugify }}" {{ attributes }}>{{ name }}</th>
        {% endfor %}
    </tr>
</table>
```

The table should provide the class "datatable" for the provided datatableview.js code to pick up on it.  If desired, you can omit the classname and bootstrap the datatable yourself with the skeleton provided.  More Javascript methods will be made available in the future to accommodate that strategy.

The `table`'s "data-url" attribute is the url that dataTables.js will use to fetch the ajax data.  By default this is just the value of ``request.path``, pointing back to the original view.

The `th` "data-name" attribute isn't required for any dataTables.js functionality, but it provides a useful CSS selector hook for styling column widths, etc.

the `attributes` value is a pre-rendered HTML string of custom data-* attributes that provide configuration details to datatableview.js when it detects the datatable skeleton, such as sorting being enabled or disabled.

## Modifying dataTables JavaScript options

The supplied datatableview.js will bootstrap any `".datatable"` elements on the page, but if the options need to be modified or supplemented before the datatable is created, you have a chance to do as you will before the datatable constructor is called.

datatableview.js will attempt to call a global function `confirm_datatable_options()`, sending it two arguments: `options` and `datatable`.  This global function will be called for every datatable being generated on the page, so your function should be capable of handling multiple datatables if necessary.

`confirm_datatable_options()` should return the options object, modified or not.

In the most common case, where only one datatable exists on the page, or if all datatables are having the same modification made to their options, you can even omit the `datatable` parameter on the your function declaration.

A good example of using this function is to supply extra non-standard callbacks to datatables.js, such as the one `fnServerParams` which enables the client to push extra arbitrary data into the server query.

```javascript
// object_list.html
<script type="text/javascript">
    function confirm_datatable_options(options) {
        options.fnServerParams = function(aoData){
            aoData.push({'name': "myvar", 'value': "myvalue"})
        }

        return options;
    }
</script>
```

All of the datatables.js options can be specified here, including options enabled by the various datatables.js plugins.

## Advanced sorting of pure virtual columns

When columns backed by concrete database fields are sorted, the sort behavior is straightforward: model field value is the data source, irrespective of presentation modifications made through the  functions described in [Customizing column output](#customizing-column-output).  But when the column has no direct correlation with a database field, what then?

The obvious answer is that the custom-built return value from the column's callback is the value, but that value might contain HTML data that completely subverts intuitive sorting.  Instead, the sorting operation needs to work on what the end-user sees, excluding the fancy markup.

To accomplish this, the callbacks are optionally capable of returning a 2-tuple of values, the first being the full HTML data to be dumped into the table, the second being the stripped version:

```python
def get_column_fictitious_data(self, instance, *args, **kwargs):
    rich_data = """<a href="%s">%s</a>""" % (instance.get_absolute_url(), instance)
    plain_data = unicode(instance)
    return (rich_data, plain_data)
```

Since stripping the HTML out of the return value is the most common requirement, `DatatableView` does this by default if you return a single value.  That makes the above example more verbose than it needs to be.

This is equivalent, using the built-in default behavior just described:

```python
def get_column_fictitious_data(self, instance, *args, **kwargs):
    rich_data = """<a href="%s">%s</a>""" % (instance.get_absolute_url(), instance)
    return rich_data
```

This mechanism empowers you to design a compound column that sorts intuitively for the data presented by the table.  For example, if a column displays a dynamic fraction for the number of questions on a survey answered out of the dynamic total, even sorting the raw text data in the column might produce table behavior that doesn't match expectations.  What one might realistically expect is that the column sorts based on the percentage completion, but that's not even a displayed value.

To solve the problem, the callback can return a crunched percentage value as the second value:

```python
def get_column_Questions_Answered_data(self, instance, *args, **kwargs):
    num_answered = instance.get_answered_questions().count()
    total = instance.get_total_questions().count()

    rich_data = "%s / %s" % (num_answered, total)
    plain_data = 1. * num_answered / total

    return (rich_data, plain_data)
```

This secondary value is only used in the server-side processing.  The JSON data returned to the client will be the first value.

## Utility helper methods for custom callbacks

There are several common processing types that get done on column data, so a `helpers` module is provided with a few functions that can be used inside of your callbacks, or directly supplied as the callback, saving you the trouble of even defining an extra method on the view.

Consequent to the multiple possible usage styles, several of the helper functions can be called in different ways with different parameters, through the help of a wrapping decorator function.  Each helper describes how it can be used.

#### `link_to_model()`
_Description: Returns HTML in the pattern of `<a href="{{ instance.get_absolute_url }}">{{ instance }}</a>`_

##### _As a callback:_ `link_to_model` or `link_to_model(key=None)`
When the helper is supplied directly as the callback handler in the column declaration, it should not be called.  The reference to the helper can act as a fully working callback, meaning that it accepts the row's object `instance` and all `*args` and `**kwargs`, including the supplied `default_value` argument.

For database-backed columns where a model field is given in the column declaration, `default_value` will be consulted for a True-like value.  Failing that, the text will be generated as `unicode(instance)`.

For virtual or compound fields where the model field is `None`, `default_value` will always evaluate to `False` and will thereby defer the value to `unicode(instance)`.

Examples:

```python
datatable_options = {
    'columns': [
        # text becomes `myfield`'s value, or unicode(instance) if None, False, etc
        ('My Field', 'myfield', link_to_model),

        # text is always unicode(instance), since there is never a database field value
        ('My Field', None, link_to_model),
    ],
}
```

To specify a custom attribute on the instance that should be the target for ``link_to_model``, call the helper with a ``key`` argument, where ``key`` is a mapping function that will take the instance and return a different model instance.  Likely this will simply look up a ForeignKey field value:

```python
datatable_options = {
    'columns': [
        # Wrong!  This would end up passing the instance into the helper, which would only
        # link to the main instance with the misleading text of "owner__name"'s value.
        ('Owner', 'owner__name', link_to_model),
        
        # Right!  Defers the lookup of the helper's target object via a key-mapping function
        ('Owner', 'owner__name', link_to_model(key=operator.attrgetter('owner'))),
    ],
}
```

##### _As a function:_ `link_to_model(instance, text=None, *args, **kwargs)`
If `text` is provided, it will be used as the displayed hyperlinked HTML.  If `text` is `None`, `""`, `False`, or some other empty value, the helper falls back to the `unicode(instance)` will be used.

If you choose to send all of the same `**kwargs` that your custom callback initially received, the `default_value` option will be available to the helper.  Its priority as the selected value for `text` is between an explicitly supplied `text` argument and the fallback `unicode(instance)`.

Examples:

```python
def get_column_myfield_data(self, instance, *args, **kwargs):
    # Simplest usage, text=unicode(instance)
    return link_to_model(instance)

    # Overrides linked text, although the URL is still retrieved from
    # instance.get_absolute_url()
    return link_to_model(instance, text="Custom text")

    # Sends the `default_value` kwarg that contains the database field value from the original
    # column declaration.  If it's available and coerces to something True-like, it will be
    # used.  Otherwise, it will be passed up and unicode(instance) will be preferred.
    return link_to_model(instance, **kwargs)

    # Explicitly ensures that the database field's value, regardless of it being `None` or
    # `False`, is used as the link text.
    return link_to_model(instance, text=unicode(kwargs['default_value']))
```


#### `itemgetter()`
_Description: Like the built-in `operator.itemgetter()`, but allows for `*args` and `**kwargs` in the workflow._

##### _As a callback:_ `itemgetter(k, ellipsis=False, key=None)`
By supplying an index or key name, this helper returns a callable that will stand in as the callback, which when called returns the index-notation `k` of the operating value.  If `default_value` is unavailable or is False-like, the instance itself is accessed for the index lookup.

If ``k`` is a ``slice``-type object and ``ellipsis`` is True, the string ``"..."`` will be appended to the resulting sliced string.  If ``ellipsis`` is itself a string, it will be used as the appended text, allowing you to supply something like ``&hellip;``.

If provided, ``key`` should be a mapping function that takes the row's model ``instance`` and returns the value to use in place of the ``instance``, prior to using ``k`` as a lookup.

Examples:

```python
datatable_options = {
    'columns': [
        # Takes the slice `[:50]` of `full_description`.  This works because `slice(0, 50)` is
        # a valid index access value: mylist[slice(0, 2)] is the same as mylist[0:2].
        ('Description', 'full_description', helpers.itemgetter(slice(0, 50), ellipsis=True)),
        
        # Condense the "description" text of a related model, via "self.book.full_description"
        ('Description', 'book__full_description', helpers.itemgetter(slice(0, 50), key=helpers.attrgetter('book')))
    ],
}
```

#### `attrgetter()`
_Description: Like the built-in `operator.attrgetter()`, but allows for `*args` and `**kwargs` in the workflow.  If the fetched attribute value is callable, this helper calls it, allowing for method names to be given._

##### _As a callback:_ `attrgetter(attr, key=None)`
Provided an attribute name, this helper returns a callable that will stand in as the callback, which when called fetches that attribute from the row's model `instance`.  If that fetched value is callable, the helper calls it with no arguments and uses that as the new value.  This allows the helper to be given a method name, which is a common way to access data for a virtual or compound table column.

If provided, ``key`` should be a mapping function that takes the row's model ``instance`` and returns the value to use in place of the ``instance``, prior to looking up ``attr``.

Examples:

```python
datatable_options = {
    'columns': [
        # On a purely virtual field, this helper bridges the gap to calling a method without
        # having to declare a method on the view.
        ('Ficticious', None, helpers.attrgetter('get_ficticious_data')),

        # On compound fields, the model may already define a method for returning the data
        ('Address', ['street_name', 'city', 'state', 'zip'], helpers.attrgetter('get_address')),

        # Models might also provide data to a virtual column via a property on the model class
        ('My Field', None, helpers.attrgetter('my_property')),
        
        # Call a method on an attribute (attribute of attribute), such as self.home.get_address()
        # This gets wordy and hard to follow, but is a useful strategy nonetheless.
        # The outer user of attrgetter is applied last, so instance gets mapped to "instance.home"
        # prior to the "get_address" lookup.
        ('Address', ['home__street_name',
                     'home__city',
                     'home__state',
                     'home__zip'], helpers.attrgetter('get_address', key=helpers.attrgetter('home'))),
    ],
}
```

#### `make_boolean_checkmark()`
_Description: Returns the unicode entity `&#10004;` ("&#10004;") if the supplied value is True-like._

##### _As a callback:_ `make_boolean_checkmark(key=None)`
If provided, `key` should be a mapping function that takes the row's model `instance` and returns the value to be consulted for this function's check.

If the helper is given as a bare reference or called without any arguments, then the default `key` function is the equivalent of fetching the `default_value`, allowing for extremely easy use:

Examples:

```python
datatable_options = {
    'columns': [
        # Automatically reads the 'myfield' value and emits "#&10004;" for True and "" for False
        ('My Field', 'myfield', make_boolean_checkmark),

        # If "Is Verified" is virtual, one could chain the helper "attrgetter" to access a
        # property or method name to supply the boolean value.
        ('Is Verified', None, make_boolean_checkmark(key=helpers.attrgetter('get_is_verified'))),

        # If the above case didn't need to access a method, but rather a normal attribute, like
        # a property, one could use the built-in operator.attrgetter instead of the one in the
        # `helpers` module.
        ('Is Verified', None, make_boolean_checkmark(key=operator.attrgetter('is_verified'))),
    ],
}
```

##### _As a function:_ `make_boolean_checkmark(value, true_value="#&10004;", false_value="", *args, **kwargs)`
If the value is True-like, `true_value` is returned.  Otherwise, `false_value` is returned.

Examples:

```python
def get_column_myfield_data(self, instance, *args, **kwargs):
    # Simplest usage
    return make_boolean_checkmark(instance.is_verified)
```

#### `format_date()`
_Description: Takes a `strftime`-style format specifier to apply to a datetime object._

##### _As a callback:_ `format_date(format_string, key=None)`
If `key` is provided, it will be given the row's model `instance` to fetch a datetime to work with.  Without a `key` function, this helper will operate on the database field provided in the column declaration.

Examples:

```python
datatable_options = {
    'columns': [
        # Simplest use of the helper as a deferred formatter.
        ('Date created', 'created_date', format_date('%m/%d/%Y')),

        # Using the `attrgetter` helper to fetch a dynamic datetime from the instance.
        ('Last admin modification', None, format_date('%m/%d/%Y', \
                key=helpers.attrgetter('get_last_admin_modification'))),
    ],
}
```

#### `format()`
_Description: Takes a new-style format string (of the "{}".format(value) variety) to apply to the column value.  See <http://docs.python.org/2/library/string.html#format-examples> for help with the syntax._

##### _As a callback:_ `format(format_string, cast=None)`
Applies the `format_string` to the column value, or else to the instance itself if no value is available, such as on a virtual column.  The formatting call is given the value as a positional argument, and the row's model `instance` as the keyword argument `"obj"`.

`cast` should a mapping function that coerces the value to a type suitable for sending into the formatting process, if necessary.

Examples:

```python
datatable_options = {
    'columns': [
        # Simplest use of the helper as a deferred formatter, adding locale digit seperators.
        ('Total cost', 'total_cost', helpers.format('{:,}')),

        # Use of the cast argument, where the model field value is a string
        ('Total cost', 'total_cost', helpers.format('{:.2f}', cast=float)),
    ],
}
```

#### `make_xeditable()`
_Description: Receives xeditable-supported keyword arguments to generate a clickable ``<a>`` tag that can be detected by client-side xeditable Javascript.  See [x-editable-datatables](#x-editable-datatables) for an example Javascript initialization._

The only difference between using this helper as a standalone function and as a direct column callback is when the ``instance`` argument is provided.  The helper can be called without the instance, and it will return a ``functools.partial`` function wrapping whatever keyword arguments you provided.  That returned ``partial`` can again be called with new arguments.  It will continue to return ``partial`` objects until finally the ``instance`` is provided.

Before providing examples, following is a list of keyword arguments at are officially recognized by the helper function, none of which are required:

* ``type``: Defaults to the basic type of the Django field (e.g., "text", "number", "datetime")
* ``title``: Defaults to empty
* ``placeholder``: Defaults to the value of ``title`` if not provided
* ``url``: Defaults to ``request.path``, so that the ``XEditableDatatableView`` can service the ajax updates.
* ``pk``: Defaults to the pk of the supplied instance.  The instance should be the first argument to ``make_xeditable`` for the default to work as intended.
* ``source``: Defaults to ``request.path``, so that the ``XEditableDatatableView`` can service ajax queries for the ``choices`` data of the field.

These arguments correspond to the ``data-*`` HTML attribute API supported by the x-editable library.  If other ``data-*`` attributes need to be set on the resulting clickable HTML element for x-editable to work on, pass them in a list to the helper, and then specify them in the kwargs:

```python
make_xeditable(extra_attrs=['data_mystuff'], data_mystuff="somevalue")
```

Without the ``extra_attrs`` list, ``data_mystuff`` would not be treated as an attribute intended for the HTML output.  Note that kwarg prefixes of ``data_`` will get converted to ``data-`` for rendering into HTML attributes.  This allows you to easily specify them as Python kwargs.

##### _As a callback:_ `make_xeditable([**kwargs])`

The primary goal of this callback is to allow zero-configuration usage, where the helper is passed directly as the column's data supplier.  ``kwargs`` can be specified as required, or chained together as discussed above.

Examples:

```python
datatable_options = {
    'columns': [
        # Simplest usage
        ('Full Description', 'description', make_xeditable)),
        
        # Customized type
        ('Full Description', 'description', make_xeditable(type="textarea"))),
    ],
}

# Use as a factory to set options in advance
textarea_xeditable = make_xeditable(type="textarea")
datatable_options = {
    'columns': [
        # Returned factory can be used directly
        ('Full Description', 'description', textarea_xeditable),

        # The factory can also accept new kwargs
        ('Full Description', 'description', textarea_xeditable(placeholder="15 words or more")),
    ],
}
```

##### _As a function:_ `make_xeditable(instance, [**kwargs])`
As a function, you will likely supply your ``instance`` and ``kwargs`` at the same time, but chaining together calls to the ``partial`` factories is still possible.

Examples:

```python
def get_column_myfield_data(self, instance, *args, **kwargs):
    # Simplest usage
    # Note that "default_value" and "field_data" are arguments that get sent to column callbacks,
    # and this helper wants to make use of those for minimum-fuss configuration.
    return make_xeditable(instance, **kwargs)

    # With custom xeditable options
    return make_xeditable(instance, type="textarea", **kwargs)

    # With non-standard data-* attributes
    special_value = instance.special_value
    return make_xeditable(instance, extra_attrs=['data_special'], data_special=special_value, **kwargs)

    # Chaining functools.partial factories
    # Note: "select" and "select2" types will require that the model field as ``choices`` defined.
    select2_xedtiable = make_xeditable(type="select2", **kwargs)
    return select2_xedtiable(instance, title="")

    # If you need to avoid sending a real instance for some reason, you should specify the pk
    # separately.  "type" will default to "text", since it cannot be read from the model instance's
    # Django field.  "field_data" is required for automatic update url generation, but can be
    # omitted if you are going to supply the "url" kwarg.  If "field_data" is not provided and the
    # field is a "select"/"select2", you'll need to also send the "source" kwarg for the choices
    # url to be provided.
    # Try to avoid this scenario.  It starts to make less sense the harder you try :)
    return make_xeditable(some_primitive_value, pk=some_pk, field_data=("myfield",))
```

## Javascript "clear" event
The datatable code that instantiates your table takes a liberty to add a "clear" button next to the search field.  (This may change in the future, since it's not a vanilla dataTables.js behavior.)  When it is clicked, it emits a ``clear.datatable`` event.

Internally this is used to trigger the clearing of the search field, but you can bind to this event from anywhere else in your project, as the event bubbles up the DOM tree:

```javascript
// For jQuery < 1.7, use .bind() instead of .on()
$(document).on('clear.datatable', function(event, oTable){
    // ...
});
```

## Authors

* Tim Valenta
* Steven Klass


## Copyright and license

Copyright (c) 2012-2013 Pivotal Energy Solutions.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this work except in compliance with the License.
You may obtain a copy of the License in the LICENSE file, or at:

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
