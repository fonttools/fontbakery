# Writing Specifications

Writing a custom Font Bakery specification can be a good start to either ensure the quality of a **single font project** or for a **font foundry** or otherwise **maintainer of a font library** to establish comprehensive quality standards and quality monitoring.

Font Bakery comes with a set of checks that can be included into such a custom specification according to the requirements of the author. These checks are mainly organized in specification modules named after OpenType tables and can be found at [`fontbakery.specifications.*`](https://github.com/googlefonts/fontbakery/blob/master/Lib/fontbakery/specifications). Naturally, when you are deciding to include a specification or just a single check into your custom specification, sooner or later you'll have to review it. Questions, remarks, improvements, additions, **more documentation** etc. are all welcome contributions. Please use our [issue tracker](https://github.com/googlefonts/fontbakery/issues) to contact us or send **pull requests**.

A Font Bakery Specification (an instance of the type `fontbakery.checkrunner.Spec`) is a container for the checks you want to run on your files. Usually a specification lives inside of a python module: one module contains one specification. You can either use one of the specifications that come with Font Bakery directly, located in [`fontbakery.specifications.*`](https://github.com/googlefonts/fontbakery/blob/master/Lib/fontbakery/specifications) or you can create a custom specification by writing your own checks and then optionally adding a selection of the other checks offered by Font Bakery.

[`fontbakery.specifications.googlefonts`](https://github.com/googlefonts/fontbakery/blob/master/Lib/fontbakery/specifications/googlefonts.py) is a custom specification and can be an interesting piece of code to inspect for some inspiration.

## From automatic discovery to full control

To create your own specification we added tools that reduce boilerplate code to a minimum. These tools are fully optional. But it is possible to use them if you need more control over the creation of a specification. This automatic discovery can be enabledor disabled based on the presence (and value) of some special names in the module of the specification:

* `specification`
* `spec_factory`
* `spec_imports`

To get or create a specification from a module, the function `get_module_specification(module)` in `fontbakery.checkrunner` is used:

> If the name `module.specification` is present the value of that is returned.
> Otherwise, if the name `module.spec_factory` is present, a new specification is created using `module.spec_factory` and then `specification.auto_register` is called with the module namespace.

Thus, the presence of the name `specification` disables the automatic use of `spec_factory` plus `specification.auto_register`. But you can consider calling `specification.auto_register(globals())` explicitly yourself near the end of your specification module or you can register the specification contents yourself.

```py
# specification = Spec(...)
# globals is a pythin builtin
specification.auto_register(globals())
```

### `specification.auto_register(symbol_table, filter_func=None)`

Whether you call `auto_register` yourself or if it is called automatically for you, it is important to understand how it operates: It looks at all values of its `symbol_table` argument (a namespace dict as returned from `globals()` or `module.__dict__`) and at all values imported using `spec_imports` (described below) if present in `symbol_table`.

If one of the items is an instance of one of `FontBakeryCheck`, `FontBakeryCondition`, `FontBakeryExpectedValue` the respective (public) interface methods: `specification.register_check`, `specification.specification` and `specification.register_expected_value` are called.

If an item is a python module (an instance of `types.ModuleType`) it is tried to get a specification from that module using `sub_specification = get_module_specification(item)`. This, in many cases, invokes `get_module_specification` recursively, which itself calls `auto_register` when indicated (see above). That new sub-specification is then included into the current auto-registering specification using `specification.merge_specification(sub_specification)` (see below).

When you are calling `specification.auto_register` explicitly yourself, you can also use the `filter_func` argument. This gives you finer control over which items are loaded into your specification, you can use it to implement blacklist and/or whitelist filtering.

Here is an example where [`filter_func` was needed due to a namespace clash.](https://github.com/googlefonts/fontbakery/pull/1770#issuecomment-380122216)

If a `filter_func` argument is defined it is called like `filter_func(type, name_or_id, item)` where:

* `type` is one of `"check"`, `"module"`, `"condition"`, `"expected_value"`, `"iterarg"`, `"derived_iterable"`, `"alias"`
* `name_or_id` is the name at which the item will be registered
* * `if type == 'check'`: the `check.id`
* * `if type == 'module'`: the module name (`module.__name__`)
* `item` is the item to be registered

If `filter_func` returns a falsy value for an item, the item will not be registered.

#### `spec_imports` used by `specification.auto_register`

If `spec_imports` is defined in a module namespace, `specification.auto_register` will use it to import modules and attributes of a module into the specification.

You could also use just the regular python `import` statement, which puts imports into the current module namespace and by that makes them discoverable for `specification.auto_register`. However, with that approach static linters like [flake8](https://gitlab.com/pycqa/flake8) and [pylint](https://www.pylint.org/) will complain about unused imports in your specification. That's why we added `spec_imports`.

`spec_imports` must be a list or tuple of import instructions, mimicking the `import module_name` and `from module_name import (identifier, ...)` syntax. *Disclaimer:* It could be more compatible to the python `import` statements, but the algorithm of python is rather complicated (feel free to contribute).

If an import instruction entry in `spec_imports` is a string: just try to import that module.
If an import instruction is not a string it is expected to be a two items iterable (tuple or list): `(module_name, (identifier, ...))`.

* If `module_name` consists of only "dots" (`.`) all `identifers` are imported as module names relative from the current module.
* Otherwise all `identifiers` are treated as attributes of the module with `module_name`, which also can be a relative import when using leading dots.

***NOTE:** one common pitfall is the python syntax for tuple literals. If a tuple has just one item, it still needs a comma after that item to make it a tuple and not just parentheses i.e. `("my_identifier", )`. For that reason the following examples use lists, although tuples, being immutable, are semantically a better fit.*

```py
# spec_imports examples

# Import relative to the current module the
# modules shared_conditions and ufo_sources.
# This includes all of the shared_conditions
# and ufo_sources specification into the
# current specification:
spec_imports = [".shared_conditions", ".ufo_sources"]

# The following is equivalent to the previous statement:
spec_imports = [
    [".", ["shared_conditions", "ufo_sources"]]
]

# Also same as above:
spec_imports = [
    ".shared_conditions",
    [".", [ "ufo_sources"]]
]
```

```py
# Here's an example copied from fontbakery.specifications.googlefonts
# This includes all of our Open Type specifications and some more into
# the googlefonts specification:
spec_imports = (
    ('.', ('general', 'cmap', 'head', 'os2', 'post', 'name',
       'hhea', 'dsig', 'hmtx', 'gpos', 'gdef', 'kern', 'glyf',
       'prep', 'fvar', 'shared_conditions')
    ), # IMPORTANT: this must be a tuple, note the trailing comma
)
```

```py
# Import just certain attributes from modules.
# Also, using absolute import module names:
spec_imports = [
    # like we do in fontbakery.specifications.fvar
    ('fontbakery.specifications.shared_conditions', ('is_variable_font',
            'regular_wght_coord', 'regular_wdth_coord', 'regular_slnt_coord',
            'regular_ital_coord', 'regular_opsz_coord', 'bold_wght_coord')),
    # just as an example: import a check and a dependency/condition of
    # that check from the googlefonts specific spec:
    ('fontbakery.specifications.googlefonts', (
        # "License URL matches License text on name table?"
        'com_google_fonts_check_030',
        # This condition is a dependency of the check above:
        'familyname',
    ))
]
```

### `specification.merge_specification(other_specification, filter_func=None)`

Copy all namespace items from `other_specification` to `specification`.

Namespace items are: `iterargs`, `derived_iterables`, `aliases`, `conditions`, `expected_values`.

Don't change any contents of `other_specification`, it may modify the loaded python module! That means sections are cloned not used directly.

Optional argument `filter_func`: see description in `auto_register`.

### `specification.test_expected_checks(expected_check_ids, exclusive=True)`

Self-test to make a sure spec maintainer is aware of changes in the spec.

Raises `SetupError` if expected check ids are missing in the spec, e.g. removed by an update.
If `exclusive=True` also raises `SetupError` if check ids are in the spec that are not in `expected_check_ids` e.g. newly added by an update.

This is handy if `spec.auto_register` is used and the spec maintainer is looking for a high level of control over the spec contents, especially for a warning when the spec contents have changed after an update of a dependency specification but it also makes specification maintenance a bit more laborious.

### `Section`

An ordered set of checks with a name.

Used to structure checks in a specification. A specification consists of one or more sections.

## Running specifications

```sh
$ fontbakery check-specification fontbakery ./path/to/fonts/*
```

## Writing Specifications: Quick start

A very basic specification with no apparent use but to document specifications, checks and conditions. For real world use cases look into the modules at [`fontbakery.specifications.*`](https://github.com/googlefonts/fontbakery/tree/master/Lib/fontbakery/specifications)

Execute:

```sh
# The example and other custom specs can be executed with this command:
$ fontbakery check-specification ./path/to/my/example_spec.py ./path/to/fonts/*

# But if you have installed your spec as a package, then use:
$ fontbakery check-specification my_package.example_spec ./path/to/fonts/*
```

Commented line by line:

```py
# To ensure a minimum compatibility with python versions > 3
from __future__ import (absolute_import,
               division,print_function, unicode_literals)
# We are going to define checks and conditons
from fontbakery.callable import check, condition
# All possible statuses a check can yield, in order of
# severity. The least severe being DEBUG. The most severe
# status emitted by a check is the end result of that check.
# DEBUG can't be an end result, the least severe status
# allowed as a check is PASS.
from fontbakery.checkrunner import (DEBUG, PASS,
               INFO, SKIP, WARN, FAIL, ERROR)
# Used to inform get_module_specification whether and
# how to create a specification. This
# example will create an instance of `FontsSpec`.
# The comment at the end of the line disables flake8
# and pylint to complain about unused imports.
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import

# At this point we already have a importable specification
# It needs some checks though, to be useful.

# spec_imports can be used to mix other specifications
# into this specification. We are only using two specifications
# for this example, containing checks for the accordingly
# named tables
spec_imports = [
    ['fontbakery.specifications', ['cmap', 'head']]
]

# Now we picked some checks from other specifications, but
# what about defining checks ourselves.


# We use `check` as a decorator to wrap an ordinary python
# function into an instance of FontBakeryCheck to prepare
# and mark it as a check.
# A check id is mandatory and must be globally and timely
# unique. See "Naming Things: check-ids" below.
@check(id='de.graphicore.fontbakery/examples/hello')
# This check will run only once as it has no iterable
# arguments. Since it has no arguments at all and because
# checks should be idempotent (and this one is), there's
# not much sense in having it all. It will run once
# and always yield the same result.
def hello_world():
  """Simple "Hello World" example."""
  # The function name of a check is not very important
  # to create it, only to import it from another module
  # or to call it directly, However, a short line of
  # human readable description is mandatory, preferable
  # via the docstring of the check.
  
  # A status of a check can be `return`ed or `yield`ed
  # depending on the nature of the check, `return`
  # can only return just one status while `yield`
  # makes a generator out of it and it can produce
  # many statuses.
  # A status also always must be a tuple of (Status, Message)
  # For `Message` a string is OK, but for unit testing
  # it turned out that an instance of `fontbakery.message.Message`
  # can be very useful. It can additionally provide
  # a status code, better suited to figure out the exact
  # check result.
  yield PASS, 'Hello World'

@check(id='de.graphicore.fontbakery/examples/has-R')
# This check will run once for each item in `fonts`.
# This is achieved via the iterag definition of font: fonts
def has_cap_r_in_name(font):
  """Filename contains an "R"."""
  # This test is not very useful again, but for each
  # input it can result in a PASS or a FAIL.
  if 'R' not in font:
    # This is our first check that can potentially fail.
    # To document this: return is also ok in a check.
    return FAIL, '"R" is not in font filename.'
  else:
    # since you can't return at one point in a function
    # and yield at another point, we always have to
    # use return within this check.
    return PASS, '"R" is in font filename.'


# conditions are used for the dependency injection as arguments
# and to decide if a test will be skipped
@condition
# ttFont is a condition built into FontSpec
# it returns an instance of fontTools.TTLib.TTFont
def is_ttf(ttFont):
   return 'glyf' in ttFont
   
@check(
    id='de.graphicore.fontbakery/examples/ttf_has_glyphs',
    # this check will be skipped if the font is not a ttf
    conditions=["is_ttf"]
)
# this also runs once per font in fonts, but its called with
# the ttFont instance
def has_ttf_glyphs(ttFont):
  """ It's bad when there are no glyphs in the TTF."""
  # savely use the "glyf" table, because of conditions="is_ttf"
  # we know it's available
  if not len(ttFont['glyf'].glyphs):
    return FAIL, "There are no glyphs in this TTF."
  return PASS, "Some gLyphs are in this TTF."
```

Now to disable the automatic creation and registration while creating an equivalent result:

```py
# maybe at the top of the file
from fontbakery.checkrunner import Section

# you can use a another name for the default section
# but this is what get_module_specification would do
specification = spec_factory(default_section=Section(__name__))
# IMPORTANT: after all checks etc. have ben defined:
specification.auto_register(globals())
```

Since we have the `specification` reference we can also use the `expected_check_ids` self check method.


```py
# putting this at the top of the file
# can give a guick overview:
expected_check_ids = (
    'de.graphicore.fontbakery/examples/hello',
    'de.graphicore.fontbakery/examples/has-R'
)
```

```py
# this must be at the end of the module,
# after all checks were added:
specification.test_expected_checks(expected_check_ids, exclusive=True)
```

You can also explicitly import and merge a specification:

```py
from fontbakery.specifications import os2
from fontbakery.checkrunner import get_module_specification
# using get_module_specification is the recommended way to get a
# specification from a module, because it takes care of creating it
# automatically if not explicitly defined.
os2_specification = get_module_specification(os2)
specification.merge_specification(os2_specification)
```


### Naming Things: check-ids

Check IDs should be **globally and temporally unique**. This means we once assign them and we never change them again. This can then be used to keep track of the history of checks and check-results. We already rely on this feature for our tooling and we'll rely more on it in the future. within a specification a check id must be unique as well, to make sharing of checks and mixing of specifications easier. Globally unique names are a good thing.

We want to encourage authors to contribute their own checks to the Font Bakery collection, if they are generally useful and fit into it. Therefore an agreement on how to create check ids is needed to avoid id-collisions.

[Reverse domain name notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation) has proven useful and a nice side effect is that contributors to Font Bakery will stay appreciated. Here are some examples:

`com.google.fonts/check/154`: while totally valid, we now think that more descriptive ids will be very helpful for humans like spec authors and maintainers. Only numbering is just harder to work with.

`com.daltonmaag/check/required-fields` and `de.graphicore.fontbakery/spec-examples/hello`: both examples are valid and more or less descriptive.

Of course, after your personal prefix, organizing names is up to you. One proposal is e.g. for tests that are specific to certain tables, the table name could be used as part of the check id.




### Naming Things: The Dependency Injection Namespace

***IMPORTANT:** Names can and will clash e.g. when sharing between specifications.* This is a good thing, because we need to be sure the right definitions are used for our spec. On the other hand, namespace hygiene will stay an ongoing topic.

The dependency injection of the Font Bakery Check runner is a feature that makes it easy to write actual check implementations.

**Example:** Run a check once for each `fontTools.ttLib.TTFont` instance of all `fonts`: Just use `ttFont` as a parameter name.

```py
# example from fontbakery.specifications.post
@check(id='com.google.fonts/check/015')
def com_google_fonts_check_015(ttFont):
  """Font has post table version 2?"""
  if ttFont['post'].formatType != 2:
    yield FAIL, ("Post table should be version 2 instead of {}."
                 " More info at https://github.com/google/fonts/"
                 "issues/215").format(ttFont['post'].formatType)
  else:
    yield PASS, "Font has post table version 2."
```

To achieve this, Font Bakery uses inspection (meta programming) to get the parameter names of a check (or condition) and then resolves these dependencies using the matching definitions in the specification namespace.

There's a collection of different types that together populate the specification namespace. We need almost all of them to make our example from above work. Yet in this case they are already predefined in `FontsSpec`, making this also a documentation of those.


#### `fonts` Expected Value

`FontSpec` also defines a command line argument `fonts`, which is then passed as a value to the check runner.

In order to to make the namespace aware of a value that's going to be provided when the check is executed, a `FontBakeryExpectedValue` is defined and added to the specification.

```py
from fontbakery.callable import FontBakeryExpectedValue
fonts_expected_value = FontBakeryExpectedValue(
      'fonts'
    , default=[]
    , description='A list of the font file paths to check.'
    , validator=lambda fonts: (True, None) if len(fonts) \
                                    else (False, 'Value is empty.')
)
# somehow added to spec, e.g.:
# specification.register_expected_value(fonts_expected_value)
```

`fonts` when used as a check argument will be something like:
```py
['Myfont-Regular.ttf', 'Myfont-Italic.ttf', ...]
```

#### `font` Iterarg

Iterargs (iterable arguments) are defined via the `Spec` constructor.

```py
specification = FontsSpec(
      ...,
      iterargs={'font': 'fonts'},
      ...
      )
```

This tells Font Bakery when we use `font` as a check parameter, to call the check once for each `font` in `fonts`.

```py
@check(id=...)
def once_per_font(font):
 ...

# Will be executed something along these lines:
once_per_font('Myfont-Regular.ttf')
once_per_font('Myfont-Italic.ttf')
once_per_font(...)
```

#### `ttFont` Condition

Conditions are somehow similar to checks: they are also functions and they are also using the same dependency injection mechanism like checks for their parameters. But they are also part of the namespace and dependency injection.

```
@condition
def ttFont(font):
   from fontTools.ttLib import TTFont
   return TTFont(font)

# somehow added to spec, e.g.:
# specification.register_condition(ttFont)
```

This, when used in a check as parameter, will inherit from the `font` iterarg, that the check will be executed once for each `font` in `fonts`. However, the argument passed will be an instance of `TTFont`:

```
@check(id=...)
def once_per_ttfont(ttFont):
 ...

# will be called like:
once_per_font(ttFont('Myfont-Regular.ttf'))
once_per_font(ttFont('Myfont-Italic.ttf'))
once_per_font( ttFont(...))
```

#### `ttFonts` Derived Iterables

Derived Iterables are not used in the example above, they however make it possible for a condition like `ttFont` to create an iterator for all of it values:

```py
specification = FontsSpec(
      ...,
      derived_iterables={'ttFonts': ('ttFont', True)}
      ...
      )
```

Makes it possible to:

```
@check(id=...)
def once_for_all_ttfonts(ttFonts):
 ...

# is called much like:
once_for_all_ttfonts([ttFont(font) for font in [
                  'Myfont-Regular.ttf', 'Myfont-Italic.ttf', ...]])
```

#### Aliases

Not used at the moment but meant to provide a mechanism to map existing names to new names. Maybe this feature will disappear again when we don't find a use case for it.

```py
specification = FontsSpec(
      ...,
      aliases={'new_name': 'old_name'},
      ...
      )
```


#### Explicit Namespace Overrides `force=True`

In order to make it possible to create checks and conditions that depend on values unknown in advance, it is possible to forcefully override certain namespace entries with a later definition. For this `FontBakeryCondition` and `FontBakeryExpected` value have an `force=True` optional parameter and for the other namespace types `specification.add_to_namespace` can be used directly, which provides the same parameter. *Just don't over do it and take care of namspace clashes carefully!*
