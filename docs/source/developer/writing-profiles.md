# Writing Profiles

A Font Bakery Profile is a container for a set of checks to be run on fonts and other associated files. Different foundries and manufacturers may have different quality control standards, and therefore may wish to include or exclude certain checks.

This list of checks is defined inside a Python module: one module contains one profile. Font Bakery comes with a number of profiles, located in [`fontbakery.profiles.*`](https://github.com/fonttools/fontbakery/blob/main/Lib/fontbakery/profiles), which can be used directly, but you can also create a custom profile. A custom profile specifies which checks to include, in which sections; a profile may also include other profiles by reference. Writing a custom Font Bakery profile can be a good way to either ensure the quality of a **single font project**, or for a **font foundry** or **maintainer of a font library** to establish comprehensive quality standards and quality monitoring.

Font Bakery comes with a set of checks that can be included into such a custom profile according to the requirements of the author. These checks are mainly organized in Python modules named after OpenType tables, and can be found at [`fontbakery.checks.*`](https://github.com/fonttools/fontbakery/blob/main/Lib/fontbakery/checks).

When you decide to include a profile or a single check from a Font Bakery profile into your own custom profile, you'll end up reading and reviewing the check's Python code. We welcome questions, remarks, improvements, additions, **more documentation** and other contributions. Please use our [issue tracker](https://github.com/fonttools/fontbakery/issues) to contact us or send **pull requests**.

[`fontbakery.profiles.googlefonts`](https://github.com/fonttools/fontbakery/blob/main/Lib/fontbakery/profiles/googlefonts.py) is a custom profile and can be an interesting piece of code to inspect for some inspiration.

## Anatomy of a profile

A profile is a Python module which has one significant variable: `PROFILE`.
This variable is a dictionary with the following keys:

- `sections`: A dictionary mapping section names to a list of check IDs.
- `include_profiles`: A list of other profile names to include.
- `exclude_checks`: A list of check IDs to exclude.
- `overrides`: A dictionary mapping check IDs to a list of *overrides*.
- `configuration_defaults`: A dictionary mapping check IDs to a namespace of configuration variables.
- `check_definitions`: A list of Python modules containing additional check implementations.

Let's look at each of these in turn.

The most basic profile, which runs a single check, looks like this:

```python
PROFILE = {
  "sections": {
    "My single check": [ "com.google.fonts/check/render_own_name" ]
  }
}
```

We declare a section, which is a grouping of checks with a title, and then list the checks - a single check in this case - which are run in that section.

You can build up your own profile out of all the checks available in the `fontbakery.checks` package, but it's more likely that you'll want to make use of some "pre-packaged" profiles as a starting point. The "opentype" profile contains some basic checks for compliance with the OpenType standard, so we'll probably want to use all of these. Let's add those all to our profile:

```python
PROFILE = {
  "sections": {
    "My single check": [ "com.google.fonts/check/render_own_name" ]
  },
  "include_profiles": [ "opentype" ]
}
```

But then there may be certain checks from included profiles that, as a foundry, you've decided that you don't need to run:

```python
PROFILE = {
  "sections": {
    "My single check": [ "com.google.fonts/check/render_own_name" ]
  },
  "include_profiles": [ "opentype" ],
  "exclude_checks": [ "com.google.fonts/check/family_naming_recommendations" ]
}
```

There may also be checks that you want to run, but for your purposes you would like a different level of severity to the original implementation; for example, the "universal" profile (a set of commonly agreed best-practices for font development) will FAIL a font if it has transformed components in the `glyf` table - something which can cause rendering errors in some environments. Arguably that's not a bug in the font but in the renderer, so you might decide only to receive a WARNing about it. To do this, you add an *override* like so:

```python
  "overrides": {
    "com.google.fonts/check/transformed_components": [
      {
          "code": "transformed-components",
          "status": "WARN",
          "reason": "Renderers should fix their bugs, I'm not doing it",
      },
    ],
  }
```

Each check ID is mapped to a list of overrides, which is a dictionary with three keys: `code` is the message code reported by the check; (The same check can report several different message codes depending on what it found, and you have the flexibility to override them all separately.) `status` is the new, overridden status; `reason` will be displayed with the check result to explain why this result has been overridden.

Finally, some checks may expect to find certain constant values in the profile. For example, `com.google.fonts/check/file_size` checks if a font's size on disk is too big. How big is determined by the `WARN_SIZE` and `FONT_SIZE` constants, which are specified in the profile like so:

```python
    "configuration_defaults": {
        "com.google.fonts/check/file_size": {
            "WARN_SIZE": 1 * 1024 * 1024,
            "FAIL_SIZE": 9 * 1024 * 1024,
        }
    },
```

These constant values can be overriden by the user using a configuration file - see the user documentation.

Note that when you inherit a list of checks from another profile using `include_profiles`, you don't (currently) inherit the configuration defaults, and need to specify those yourself.

## Running profiles

```sh
$ fontbakery check-profile myprofile ./path/to/fonts/*
```

## Writing checks

If in your profile you want to check for something we don't currently add a check for - great! We would encourage you to write one. In fact, we would encourage you to also contribute it back to fontbakery so that others can benefit. (Although you don't have to.)

A check implementation is a Python function. To create a private check implementation that you don't want to share with the rest of the world (even though we gave you this amazing font QA tool for absolutely free), you can add the `check_definitions` key to your profile variable; this is a list of Python modules to load for checks. Then you can add your Python function to this new module.

To create your own *public* check implementation, simply either add a new file to the `fontbakery.checks` package (all files in this package are loaded and executed by the check runner) or add a new function to an existing file which contains similar or related checks.

A file containing checks usually begins by including the *prelude*, a Python package with a bunch of helpful imports:

```
from fontbakery.prelude import check, Message, INFO, PASS, FAIL, WARN
```

Your check implementation will use the `@check` decorator to tell Fontbakery that it's a check, and to give certain useful metadata about what it does:

```python
@check(
    id="com.myfoundry/check/has_FNRD_table",
    rationale="""
        All MyFoundry fonts should contain a `FNRD` table as a subtle
        reference to The Illuminatus! Trilogy.
    """,
    severity=23
)
def check_has_FNRD_table(ttFont):
  #... definition goes here...
```

> **Naming Things: check-ids**

> Check IDs should ideally be **globally and temporally unique**. This means we once assign them and we never change them again. We plan to start enforcing this after FontBakery version 1.0.0 is released. This can then be used to keep track of the history of checks and check-results. We already rely on this feature for our tooling and we'll rely more on it in the future. within a profile a check id must be unique as well, to make sharing of checks and mixing of profiles easier. Globally unique names are a good thing.

> We want to encourage authors to contribute their own checks to the Font Bakery collection, if they are generally useful and fit into it. Therefore an agreement on how to create check ids is needed to avoid id-collisions.

> [Reverse domain name notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation) has proven useful and a nice side effect is that contributors to Font Bakery will stay appreciated. Here are some examples: `com.daltonmaag/check/required-fields` and `de.graphicore.fontbakery/profile-examples/hello`: both examples are valid and more or less descriptive.

> Of course, after your personal prefix, organizing names is up to you. One proposal is e.g. for checks that are specific to certain tables, the table name could be used as part of the check id.

Now let's look at that definition:

```python
def check_has_FNRD_table(ttFont):
  if "FNRD" not in ttFont:
    yield FAIL, Message("no-FNRD", "FNRD table was not present")
  elif ttFont["FNRD"].compile(ttFont) != b'\x23':
    yield WARN, Message("bad-FNRD", "FNRD table had incorrect contents")
  else:
    yield PASS
```

Notice that this function takes a `ttFont` parameter - we'll talk about the parameters soon - and then `yield`s a check status and (if it's not a PASS) a `Message` object. We `yield` rather than `return` to allow the check to potentially return multiple statuses. The message object comprises of a code - so that it can be overriden, as we described above - and a message text.

### Parameters

You'll notice that our check implementation above took a `ttFont` parameter.This is part of the dependency injection feature of the FontBakery check runner, which makes it easier to write check implementations. To understand this, we need to step back and understand how the check runner works.

Fontbakery first builds a `CheckRunContext` object wrapping up all the file names that were passed in on the command line, the configuration, and a few other things. Each filename to be tested is categorized according to known filename patterns, and wrapped in a subclass of a `Testable`. For example, a file ending `.ttf` or `.otf` is wrapped in a `Font` object, a `.ufo` directory turns into a `Ufo` object, and so on. These objects have a `.file` property which stores the original filename.

Most checks are run on a single testable file - in the case of the check above, a `Font` object. Here's how we could write the above check definition more explicitly:

```Python
from fontTools.ttLib import TTFont

@check(...)
def check_has_FNRD_table(font: Font):
  ttFont = TTFont(font.file)
  if "FNRD" not in ttFont:
    ...
```

Every `Font` object (.ttf or .otf file on the command line) will get passed to a check which takes a `font` parameter; but `Ufo` objects will not be passed to these checks. (They will only get passed to checks which take a `ufo` parameter.)

So how did our original check definition (`def check_has_FNRD_table(ttFont)`) work? This doesn't have a `font` parameter and we didn't get a `Font` object passed to us. Well, the issue with the "explicit" form, while it is easy to understand, is that it requires every single check definition to call `TTFont`, parse the font file, and so on. This is a waste of work. Similarly, it's fairly common to want to know what codepoints are in a font, and we don't want every check working it out for itself.

When there are common "questions we want to ask" about a font - its glyphset, its parsed TTFont object, etc. - we want to ask those questions once and cache the answer. So the definition of the `Font` object contains the following code:

```python
    @cached_property
    def ttFont(self):
        return TTFont(self.file)

    @cached_property
    def font_codepoints(self):
        return set(self.ttFont.getBestCmap().keys())
```

(You can see the full list of methods in the `fontbakery.testables` module.) This means that we can call `font.ttFont`, and get the same cached `TTFont` object each time - the font parsing only has to happen once. These cached properties are called "conditions" in Fontbakery-speak, for reasons we'll explain a little later.

So here's a slight improvement on the above check definition:

```Python
@check(...)
def check_has_FNRD_table(font: Font):
  if "FNRD" not in font.ttFont:  # Use cached TTFont, don't parse it ourselves
    ...
```

This is better, but it still doesn't explain why `check_has_FNRD_table(ttFont)` works. But here's where the check runner gets clever and does something called "dependency injection": instead of taking a parameter `font` to get a `Font` object, your check can declare a parameter *with the same name as any condition* (that is, any method on the "testable" object) and the check will be called with the result of that condition as the parameter.

That's how we got `ttFont` to feed us a `TTFont` object: it noticed the parameter naming, figured that we wanted to call the `.ttFont` condition, did that under the hood, and handed the result to the check.

Of course, this is a short-cut and has the danger of getting things wrong. If both `Ufo` and `Font` objects have a `font_codepoints` condition, and your check uses `font_codepoints` as a parameter, what Fontbakery does is officially undefined behaviour - although in reality it will probably attempt to call the check on both types of object. This may or may not be what you want.

This is why in general you should follow the [Zen of Python](https://peps.python.org/pep-0020/) ("Explicit is better than implicit, simple is better than complex") and use `font` and `ufo` as parameters, and then call the conditions on them as methods rather than using the "clever" dependency injection mechanism.

But given that it is *extremely* common for font-based checks to operate off a `TTFont` object, the mechanism turns out to be very helpful and it's a well-known convention, so it's there if you want it.

### Running on all the testables

While most checks deal with a single "testable" (generally a `Font`) at a time, other checks need to run against all the files on the command line. For example, you might want to check that all fonts in a family have the same family name.

To enable this, Fontbakery extends the dependency injection idea a little further: when matching the names of parameters, if the name is not found as a method on the current `Testable`, Fontbakery sees if there is a method on the `CheckRunContext` with the same name, and if it is, calls that instead. In other words, the names of any methods on the `CheckRunContext` object can also be used as parameters to checks. Each type of testable (fonts, UFO files, Glyphs sources, README.md files, etc.) have their own "collection" method on the `CheckRunContext` (`.fonts`, `.ufos`...) which returns the list of files to be tested matching that type.

In practice, what this means is that you can say:

```Python
@check(...)
def check_all_same_family_name(fonts):
```

and receive a list of `Font` objects representing all the font files passed in on the command line.

As a further optimization for check writers, `CheckRunContext` has a `.ttFonts` method, which calls `.ttFont` on each `Font`. Combining this with dependency injection again, you can say:

```Python
@check(...)
def check_all_same_family_name(ttFonts):
    family_names = [tt["name"].getDebugName(1) for tt in ttFonts]
    if any(family_name != family_names[0] for family_name in family_names):
        ...
```

This helps you to check things about the context as a whole. In other cases, you might want to check the status of one file, while "being aware" of the whole collection of testables. To enable this, each testable object has a `.context` property which refers back to the `CheckRunContext` object. And of course you can use dependency injection to say:

```Python
@check(...)
def check_italic_has_matching_roman(ttFont, context):
    # Let's assume ttFont is known to be italic, we'll show how later.
    romans = [font.ttFont for font in context.fonts if not font.is_italic]
    if any(is_matching_roman(roman, ttFont) for roman in romans):
        yield PASS
```

But this is... exceptional. The more you keep things simple, the better for everyone.

### Skipping checks

Coming back to the question of why these cached "questions to ask" are called "conditions": the initial use of them was to be able to make checks conditional on certain situations. So a `Font` has condition methods like `.is_variable_font`, `.is_cff` and so on. If a check decorator specifies these condition names in its metadata, *the check will only be run on those testables for which the condition method returns true*:

```python
@check(
    id="com.myfoundry/check/cff_names_match",
    conditions=["is_cff"]
)
def check_cff_names_match(ttFont):
```

The check runner performs the moral equivalent of:

```python
for font in testables.font:
    if font.is_cff:
        yield from check_cff_names_match(font.ttFont)
    else:
        yield "SKIP", "Unfulfilled condition: is_cff"
```

You can match multiple conditions, and again these can be methods on the individual testable or on the `CheckRunContext` object, and *all* have to return a true value for the check to run. One useful condition on the `CheckRunContext` is `.network`, which tells you if network checks are enabled or disabled on the command line. Checks which use the Internet should declare the `network` condition.

```python
@check(
    id="com.myfoundry/check/lookup_on_fontsinuse",
    conditions=["network"]
)
```

### Declaring your own conditions

Finally, if you have your own "questions to ask" about a testable or about the run context - particularly those you are likely to ask more than once in different checks, and hence it's worth caching the result - you can declare your own conditions. This is done with the `@condition` decorator (available for import as part of the `fontbakery.prelude`), and you can see examples of it in the `fontbakery.checks.shared_conditions` module:

```python
@condition(CheckRunContext)
def are_ttf(collection):
    return all(f.is_ttf for f in collection.fonts)
```

The `@condition` decorator adds a cached property to a class; it is exactly the moral equivalent of:

```python
class CheckRunContext:
    @cached_property
    def are_ttf(self):
        return all(f.is_ttf for f in self.fonts)
```

If you think that other checks may end up using your shiny new condition, you can add it to `fontbakery.checks.shared_conditions`; if not, you can place the condition definition in the file containing your check definitions.