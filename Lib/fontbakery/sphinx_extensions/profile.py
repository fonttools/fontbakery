from typing import Any, List, Tuple, Dict #cast

from sphinx.application import Sphinx
# from sphinx.ext.autodoc import Documenter
from sphinx.ext.autodoc import ModuleLevelDocumenter
from sphinx.pycode import ModuleAnalyzer, PycodeError
#from sphinx.domains.python import PythonDomain
from sphinx.locale import __
from sphinx.domains.python import PyObject
from sphinx import addnodes
from sphinx.util.inspect import Signature #, isdescriptor, safe_getmembers, \
    # safe_getattr, object_description, is_builtin_class_method, \
    # isenumattribute, isclassmethod, isstaticmethod, isfunction, isbuiltin, ispartial, getdoc

import logging
logger = logging.getLogger(__name__)

# we can get source code first line numbers with this module for object
import inspect

from fontbakery.callable import (
                          FontbakeryCallable
                        , FontBakeryCondition
                        , FontBakeryCheck
                        , Disabled
                        , FontBakeryExpectedValue
                        )

# mute the style checks for unused names
# will be removed eventually
if False: #pylint: disable=using-constant-test
  FontbakeryCallable
  FontBakeryCondition
  FontBakeryCheck
  Disabled
  FontBakeryExpectedValue

__version__ = '0.0.1'


# ModuleLevelDocumenter(Documenter): Specialized Documenter subclass for objects on module level (functions,
# classes, data/constants). Implements: resolve_name
# https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/autodoc/__init__.py#L850
# Documenter
class FontBakeryCallableDocumenter(ModuleLevelDocumenter):
  """
  Specialized Documenter subclass for instances of FontBakeryCheck.
  """
  objtype = 'fontbakerycallable'
  can_doc_cls = FontbakeryCallable
  member_order = 30

  @classmethod
  def can_document_member(cls, member, membername, isattr, parent):
    # type: (Any, str, bool, Any) -> bool
    return isinstance(member, cls.can_doc_cls)

  def format_args(self): # pylint: disable=arguments-differ  # I am really not sure what went wrong here...
    # type: () -> str
    # We use the original signature from the wrapped _function
    has_retval = isinstance(self.object, FontBakeryCondition)
    sig = Signature(self.object._func, bound_method=False, has_retval=has_retval)
    args = sig.format_args()
    # escape backslashes for reST
    args = args.replace('\\', '\\\\')
    return args

  def format_name(self):
    # I'm using this to inject some new info into the check
    # search for the separator ":::" in this document to see where
    # the info is received. This is not a clean solution!
    #
    # in https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/autodoc/__init__.py#L374
    # it says:
    #  > This normally should be something that can be parsed by the generated
    #  > directive, but doesn't need to be (Sphinx will display it unparsed
    #  > then).
    # See below in `handle_signature`
    # where that ipdb debugger is started, usually that eception would be
    # dropped and we drop out of signature building. (RAISED here in `_handle_signature`
    # The ValueError when the regex doesn't match...)
    # seems like the slash (/) Is killing most of the header!
    # Otherwise the ids display fine, the dots are fine.
    # Also, in any case of name change, the [source] view is killed (removed!)
    # the document and also genindex.html anchor works so far (with 7 instead of /)
    #
    res = super().format_name()
    if self.objtype == 'fontbakerycheck':
      # A bit hackish, splitting somwhere else by ::: to retrieve the checkid
      # we can get the source file first line number of self.object:
      lineno = inspect.getsourcelines(self.object)[1]
      res =  self.object.id + ':::' + f'{lineno}' + ':::' + res#.replace('/', '7')
    # else:
    #   res = super().format_name()
    # print('formatted name:', res)
    # > formatted name: com.google.fonts/check/xavgcharwidth:::59:::com_google_fonts_check_xavgcharwidth
    # > formatted name: bold_wght_coord

    return res

    # handle_signature: com_google_fonts_check_post_table_version(ttFont, is_ttf) <desc_signature first="False"/>
    # sig signature: com_google_fonts_check_post_table_version(ttFont, is_ttf)
    # result: ('com_google_fonts_check_post_table_version', None) signode: <desc_signature class="" first="False" fullname="com_google_fonts_check_post_table_version" module="fontbakery.profiles.post"><desc_annotation xml:space="preserve">FontBakeryCheck </desc_annotation><desc_addname xml:space="preserve">fontbakery.profiles.post.</desc_addname><desc_name xml:space="preserve">com_google_fonts_check_post_table_version</desc_name><desc_parameterlist xml:space="preserve"><desc_parameter xml:space="preserve">ttFont</desc_parameter><desc_parameter xml:space="preserve">is_ttf</desc_parameter></desc_parameterlist></desc_signature>

  def generate(self, more_content=None, real_modname=None,
                                check_module=False, all_members=False):
    # type: (Any, str, bool, bool) -> None
    """Generate reST for the object given by *self.name*, and possibly for
    its members.

    If *more_content* is given, include that content. If *real_modname* is
    given, use that module name to find attribute docs. If *check_module* is
    True, only generate if the object is defined in the module name it is
    imported from. If *all_members* is True, document all members.
    """
    # print('generate', more_content, real_modname, check_module, all_members)
    # print(self.name)
    # print('---------------------')
    # > generate None fontbakery.profiles.post True True
    # > fontbakery.profiles.post::com_google_fonts_check_post_table_version
    # > ---------------------
    #
    # > generate None fontbakery.profiles.shared_conditions True True
    # > fontbakery.profiles.shared_conditions::glyph_metrics_stats
    # > ---------------------
    if not self.parse_name():
        # need a module to import
        logger.warning(
            __('don\'t know which module to import for autodocumenting '
               '%r (try placing a "module" or "currentmodule" directive '
               'in the document, or giving an explicit module name)') %
            self.name, type='autodoc')
        return


    # now, import the module and get object to document
    if not self.import_object():
        return

    # doesn't do anything!
    # if self.objtype == 'fontbakerycheck':
    #   self.name = self.object.id


    # If there is no real module defined, figure out which to use.
    # The real module is used in the module analyzer to look up the module
    # where the attribute documentation would actually be found in.
    # This is used for situations where you have a module that collects the
    # functions and classes of internal submodules.
    self.real_modname = real_modname or self.get_real_modname()  # type: str

    # try to also get a source code analyzer for attribute docs
    try:
        self.analyzer = ModuleAnalyzer.for_module(self.real_modname)
        # parse right now, to get PycodeErrors on parsing (results will
        # be cached anyway)
        self.analyzer.find_attr_docs()
    except PycodeError as err:
        logger.debug('[autodoc] module analyzer failed: %s', err)
        # no source file -- e.g. for builtin and C modules
        self.analyzer = None
        # at least add the module.__file__ as a dependency
        if hasattr(self.module, '__file__') and self.module.__file__:
            self.directive.filename_set.add(self.module.__file__)
    else:
        self.directive.filename_set.add(self.analyzer.srcname)


    # check __module__ of object (for members not given explicitly)
    if check_module:
        if not self.check_module():
            return


    sourcename = self.get_sourcename()


    # make sure that the result starts with an empty line.  This is
    # necessary for some situations where another directive preprocesses
    # reST and no starting newline is present
    self.add_line('', sourcename)


    # format the object's signature, if any
    sig = self.format_signature()

    # generate the directive header and options, if applicable
    self.add_directive_header(sig)
    self.add_line('', sourcename)


    # e.g. the module directive doesn't have content
    self.indent += self.content_indent


    # add all content (from docstrings, attribute docs etc.)
    self.add_content(more_content)


    # document members, if possible
    self.document_members(all_members)


class FontBakeryCheckDocumenter(FontBakeryCallableDocumenter):
  objtype = 'fontbakerycheck'
  can_doc_cls = FontBakeryCheck


class FontBakeryConditionDocumenter(FontBakeryCallableDocumenter):
  objtype = 'fontbakerycondition'
  can_doc_cls = FontBakeryCondition

from sphinx.domains.python import _pseudo_parse_arglist

import re
# REs for Python signatures
py_sig_re = re.compile(
    r'''^ ([\w.]*\.)?            # class name(s)
          (\w+)  \s*             # thing name
          (?: \(\s*(.*)\s*\)     # optional: arguments
           (?:\s* -> \s* (.*))?  #           return annotation
          )? $                   # and nothing more
          ''', re.VERBOSE)

# PyObject: https://github.com/sphinx-doc/sphinx/blob/master/sphinx/domains/python.py#L189
# PyObject is a subclass of sphinx.directives.ObjectDescription
# ObjectDescription is a sphinx.util.docutils.SphinxDirective
# SphinxDirective is a docutils.parsers.rst.Directive
class PyFontBakeryObject(PyObject):
  """
  Description of a class-like object (classes, interfaces, exceptions).
  """

  allow_nesting = True

  @property
  def pretty_objtype(self):
    if self.objtype.startswith('fontbakery'):
      suffix = self.objtype[len('fontbakery'):]
      return 'FontBakery'  + suffix[0].upper() + suffix[1:]
    return self.objtype

  def get_signature_prefix(self, sig):
    # type: (str) -> str
    # import ipdb
    # ipdb.set_trace()
    # print('sig signature:', sig)
    # > sig signature: com_google_fonts_check_all_glyphs_have_codepoints(ttFont)

    return self.pretty_objtype + ' '

  # this is bullshit, returns two values but manipulates
  # signode massively, which is undocumented.
  # signode is an instance of <class 'sphinx.addnodes.desc_signature'>
  # from https://github.com/sphinx-doc/sphinx/blob/master/sphinx/domains/python.py#L237
  def _handle_signature(self, cid, lineno, sig, signode):
    # type: (str, addnodes.desc_signature) -> Tuple[str, str]
    """Transform a Python signature into RST nodes.

    Return (fully qualified name of the thing, classname if any).

    If inside a class, the current class name is handled intelligently:
    * it is stripped from the displayed name if present
    * it is added to the full name (return value) if not present

    This is the xml string result of signode, whitespace is not
    equivalent for readability.
    <desc_signature
        class=""
        first="False"
        fullname="com.google.fonts/check/all_glyphs_have_codepoints"
        module="fontbakery.profiles.cmap"
        >
            <desc_annotation
                xml:space="preserve">FontBakeryCheck </desc_annotation>
            <desc_addname
                xml:space="preserve">fontbakery.profiles.cmap.</desc_addname>
            <desc_name
                xml:space="preserve">com_google_fonts_check_all_glyphs_have_codepoints</desc_name>
            <desc_parameterlist
                xml:space="preserve">
                    <desc_parameter xml:space="preserve">ttFont</desc_parameter>
            </desc_parameterlist>
      </desc_signature>

    """
    m = py_sig_re.match(sig)
    if m is None:
      # this is the immediate fail!!!
      raise ValueError
    prefix, name, arglist, retann = m.groups()
    # print('prefix, name, arglist, retann =', prefix, name, arglist, retann)
    # > prefix, name, arglist, retann = None com_google_fonts_check_all_glyphs_have_codepoints ttFont None

    # determine module and class name (if applicable), as well as full name
    modname = self.options.get('module', self.env.ref_context.get('py:module'))
    classname = self.env.ref_context.get('py:class')
    if classname:
      add_module = False
      if prefix and (prefix == classname or
               prefix.startswith(classname + ".")):
        fullname = prefix + name
        # class name is given again in the signature
        prefix = prefix[len(classname):].lstrip('.')
      elif prefix:
        # class name is given in the signature, but different
        # (shouldn't happen)
        fullname = classname + '.' + prefix + name
      else:
        # class name is not given in the signature
        fullname = classname + '.' + name
    else:
      add_module = True
      if prefix:
        classname = prefix.rstrip('.')
        fullname = prefix + name
      else:
        classname = ''
        fullname = name


    signode['module'] = modname
    signode['class'] = classname
    signode['fullname'] = fullname
    signode.attributes['lineno'] = lineno


    #sig_prefix = self.get_signature_prefix(sig)
    #if sig_prefix:
    #  signode += addnodes.desc_annotation(sig_prefix, sig_prefix)


    if prefix:
      signode += addnodes.desc_addname(prefix, prefix)
    elif add_module and self.env.config.add_module_names:
      if modname and modname != 'exceptions':
        # exceptions are a special case, since they are documented in the
        # 'exceptions' module.
        #nodetext = modname + ' ID: '
        #signode += addnodes.desc_addname(nodetext, nodetext)
        pass


    signode += addnodes.desc_name(name, cid)
    if arglist:
      _pseudo_parse_arglist(signode, arglist)
    else:
      if self.needs_arglist():
        # for callables, add an empty parameter list
        signode += addnodes.desc_parameterlist()


    if retann:
      signode += addnodes.desc_returns(retann, retann)


    anno = self.options.get('annotation')
    if anno:
      signode += addnodes.desc_annotation(' ' + anno, ' ' + anno)


    return cid, prefix

  def handle_signature(self, sig, signode):
    # print('>>>>>>>>>>>>>>>>>handle_signature:', sig, signode)
    # > >>>>>>>>>>>>>>>>>handle_signature: com.google.fonts/check/all_glyphs_have_codepoints:::36:::com_google_fonts_check_all_glyphs_have_codepoints(ttFont) <desc_signature first="False"/>

    keepsig = f'sig{sig}'

    cid = None
    if ':::' in sig:
      cid, lineno, sig = sig.split(':::')
      # print('GOT id:', cid, lineno, 'for:', sig)
      # > GOT id: com.google.fonts/check/all_glyphs_have_codepoints 36 for: com_google_fonts_check_all_glyphs_have_codepoints(ttFont)

    res = '(NONE!)'
    try:
      res = self._handle_signature(cid, lineno, sig, signode) if cid is not None\
                      else super().handle_signature(sig, signode)
    except Exception as e:
      print('!!!', e)
      raise e

    return res

  # This ends in: path-to-docs/html/genindex.html
  def get_index_text(self, modname, name):
    # type: (str, Tuple[str, str]) -> str

    return f'{name[0]} ({self.pretty_objtype} in {modname})'
    # fontbakerycheck
    # modname: fontbakery.profiles.cmap
    # name_cls:('com_google_fonts_check_all_glyphs_have_codepoints', None)
    # return f' {self.objtype} modname: {modname} name_cls:{name_cls}'

  def add_target_and_index(self, name_cls, sig, signode):
    # type: (Tuple[str, str], str, addnodes.desc_signature) -> None
    modname = self.options.get('module', self.env.ref_context.get('py:module'))
    # fullname = (modname and modname + '.' or '') + name_cls[0]
    fullname = name_cls[0]
    # note target
    if fullname not in self.state.document.ids:
      signode['names'].append(fullname)
      signode['ids'].append(fullname)
      signode['first'] = (not self.names)
      self.state.document.note_explicit_target(signode)

      # note, there will be a change to this in a future release
      # https://github.com/sphinx-doc/sphinx/commit/259be8716ad4b2332aa4d7693d73400eb06fa7d7
      ## in the past (now)
      objects = self.env.domaindata['py']['objects']
      if fullname in objects:
        self.state_machine.reporter.warning(
            'duplicate object description of %s, ' % fullname +
            'other instance in ' +
            self.env.doc2path(objects[fullname][0]) +
            ', use :noindex: for one of them',
            line=self.lineno)
        objects[fullname] = (self.env.docname, self.objtype)
      ## in the future
      # domain = cast(PythonDomain, self.env.get_domain('py'))
      # domain.note_object(fullname, self.objtype)

    indextext = self.get_index_text(modname, name_cls)
    if indextext:
      self.indexnode['entries'].append(('single', indextext,
                                              fullname, '', None))

# Copied a lot from napoleon extension:
# https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/napoleon/__init__.py
# To get started, hooking into autodoc seems the way to go, hence that was
# a good fit.

def setup(app):
  # type: (Sphinx) -> Dict[str, Any]
  """Sphinx extension setup function.
  When the extension is loaded, Sphinx imports this module and executes
  the ``setup()`` function, which in turn notifies Sphinx of everything
  the extension offers.
  Parameters
  ----------
  app : sphinx.application.Sphinx
      Application object representing the Sphinx process
  See Also
  --------
  `The Sphinx documentation on Extensions
  <http://sphinx-doc.org/extensions.html>`_
  `The Extension Tutorial <http://sphinx-doc.org/extdev/tutorial.html>`_
  `The Extension API <http://sphinx-doc.org/extdev/appapi.html>`_
  """
  if not isinstance(app, Sphinx):
      # probably called by tests
      return {'version': __version__, 'parallel_read_safe': True}

  # _patch_python_domain()

  #=> this:
  app.add_autodocumenter(FontBakeryCallableDocumenter)
  app.add_autodocumenter(FontBakeryCheckDocumenter)
  app.add_autodocumenter(FontBakeryConditionDocumenter)

  # https://github.com/sphinx-doc/sphinx/blob/master/sphinx/domains/python.py
  app.add_directive_to_domain('py', 'fontbakerycallable', PyFontBakeryObject, override=False)
  app.add_directive_to_domain('py', 'fontbakerycheck', PyFontBakeryObject, override=False)
  app.add_directive_to_domain('py', 'fontbakerycondition', PyFontBakeryObject, override=False)

  # => see e.g.: https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/autodoc/__init__.py#L984


  app.setup_extension('sphinx.ext.autodoc')
  app.connect('autodoc-process-docstring', _process_docstring)
  app.connect('autodoc-skip-member', _skip_member)

  #for name, (default, rebuild) in Config._config_values.items():
  #    app.add_config_value(name, default, rebuild)
  return {'version': __version__, 'parallel_read_safe': True}

def _skip_member(app, what, name, obj, skip, options):
  # type: (Sphinx, str, str, Any, bool, Any) -> bool
  """Determine if private and special class members are included in docs.
  The following settings in conf.py determine if private and special class
  members or init methods are included in the generated documentation:
  * ``napoleon_include_init_with_doc`` --
    include init methods if they have docstrings
  * ``napoleon_include_private_with_doc`` --
    include private members if they have docstrings
  * ``napoleon_include_special_with_doc`` --
    include special members if they have docstrings
  Parameters
  ----------
  app : sphinx.application.Sphinx
      Application object representing the Sphinx process
  what : str
      A string specifying the type of the object to which the member
      belongs. Valid values: "module", "class", "exception", "function",
      "method", "attribute".
  name : str
      The name of the member.
  obj : module, class, exception, function, method, or attribute.
      For example, if the member is the __init__ method of class A, then
      `obj` will be `A.__init__`.
  skip : bool
      A boolean indicating if autodoc will skip this member if `_skip_member`
      does not override the decision
  options : sphinx.ext.autodoc.Options
      The options given to the directive: an object with attributes
      inherited_members, undoc_members, show_inheritance and noindex that
      are True if the flag option of same name was given to the auto
      directive.
  Returns
  -------
  bool
      True if the member should be skipped during creation of the docs,
      False if it should be included in the docs.
  """
  if name in ['conditions',
              'description',
              'documentation',
              'id',
              'name',
              'rationale',
              'check_skip_filter',
              'is_librebarcode']:
    return True
  else:
    return None


def _process_docstring(app, what, name, obj, options, lines):
  # type: (Sphinx, str, str, Any, Any, List[str]) -> None
  """Process the docstring for a given python object.
  Called when autodoc has read and processed a docstring. `lines` is a list
  of docstring lines that `_process_docstring` modifies in place to change
  what Sphinx outputs.
  The following settings in conf.py control what styles of docstrings will
  be parsed:
  * ``napoleon_google_docstring`` -- parse Google style docstrings
  * ``napoleon_numpy_docstring`` -- parse NumPy style docstrings
  Parameters
  ----------
  app : sphinx.application.Sphinx
      Application object representing the Sphinx process.
  what : str
      A string specifying the type of the object to which the docstring
      belongs. Valid values: "module", "class", "exception", "function",
      "method", "attribute".
  name : str
      The fully qualified name of the object.
  obj : module, class, exception, function, method, or attribute
      The object to which the docstring belongs.
  options : sphinx.ext.autodoc.Options
      The options given to the directive: an object with attributes
      inherited_members, undoc_members, show_inheritance and noindex that
      are True if the flag option of same name was given to the auto
      directive.
  lines : list of str
      The lines of the docstring, see above.
      .. note:: `lines` is modified *in place*
  """

  if hasattr(obj, 'rationale') and obj.rationale:
    lines.append("**Rationale:**")

    for line in obj.rationale.split('\n'):
      lines.append(line)
