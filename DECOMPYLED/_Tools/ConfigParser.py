# emacs-mode: -*- python-*-
"""Configuration file parser.

A setup file consists of sections, lead by a "[section]" header,
and followed by "name: value" entries, with continuations and such in
the style of RFC 822.

The option values can contain format strings which refer to other values in
the same section, or values in a special [DEFAULT] section.

For example:

    something: %(dir)s/whatever

would resolve the "%(dir)s" to the value of dir.  All reference
expansions are done late, on demand.

Intrinsic defaults can be specified by passing them into the
ConfigParser constructor as a dictionary.

class:

ConfigParser -- responsible for for parsing a list of
                configuration files, and managing the parsed database.

    methods:

    __init__(defaults=None)
        create the parser and specify a dictionary of intrinsic defaults.  The
        keys must be strings, the values must be appropriate for %()s string
        interpolation.  Note that `__name__' is always an intrinsic default;
        it's value is the section's name.

    sections()
        return all the configuration section names, sans DEFAULT

    has_section(section)
        return whether the given section exists

    has_option(section, option)
        return whether the given option exists in the given section

    options(section)
        return list of configuration options for the named section

    read(filenames)
        read and parse the list of named configuration files, given by
        name.  A single filename is also allowed.  Non-existing files
        are ignored.

    readfp(fp, filename=None)
        read and parse one configuration file, given as a file object.
        The filename defaults to fp.name; it is only used in error
        messages (if fp has no `name' attribute, the string `<???>' is used).

    get(section, option, raw=0, vars=None)
        return a string value for the named option.  All % interpolations are
        expanded in the return values, based on the defaults passed into the
        constructor and the DEFAULT section.  Additional substitutions may be
        provided using the `vars' argument, which must be a dictionary whose
        contents override any pre-existing defaults.

    getint(section, options)
        like get(), but convert value to an integer

    getfloat(section, options)
        like get(), but convert value to a float

    getboolean(section, options)
        like get(), but convert value to a boolean (currently case
        insensitively defined as 0, false, no, off for 0, and 1, true,
        yes, on for 1).  Returns 0 or 1.

    remove_section(section)
        remove the given file section and all its options

    remove_option(section, option)
        remove the given option from the given section

    set(section, option, value)
        set the given option

    write(fp)
        write the configuration state in .ini format
"""
import string
import types
import re
__all__ = ['NoSectionError',
 'DuplicateSectionError',
 'NoOptionError',
 'InterpolationError',
 'InterpolationDepthError',
 'ParsingError',
 'MissingSectionHeaderError',
 'ConfigParser',
 'MAX_INTERPOLATION_DEPTH']
DEFAULTSECT = 'DEFAULT'
MAX_INTERPOLATION_DEPTH = 10
class Error(Exception):
    __module__ = __name__

    def __init__(self, msg = ''):
        self._msg = msg
        Exception.__init__(self, msg)



    def __repr__(self):
        return self._msg


    __str__ = __repr__

class NoSectionError(Error):
    __module__ = __name__

    def __init__(self, section):
        Error.__init__(self, ('No section: %s' % section))
        self.section = section



class DuplicateSectionError(Error):
    __module__ = __name__

    def __init__(self, section):
        Error.__init__(self, ('Section %s already exists' % section))
        self.section = section



class NoOptionError(Error):
    __module__ = __name__

    def __init__(self, option, section):
        Error.__init__(self, ("No option `%s' in section: %s" % (option,
         section)))
        self.option = option
        self.section = section



class InterpolationError(Error):
    __module__ = __name__

    def __init__(self, reference, option, section, rawval):
        Error.__init__(self, ('Bad value substitution:\n\tsection: [%s]\n\toption : %s\n\tkey    : %s\n\trawval : %s\n' % (section,
         option,
         reference,
         rawval)))
        self.reference = reference
        self.option = option
        self.section = section



class InterpolationDepthError(Error):
    __module__ = __name__

    def __init__(self, option, section, rawval):
        Error.__init__(self, ('Value interpolation too deeply recursive:\n\tsection: [%s]\n\toption : %s\n\trawval : %s\n' % (section,
         option,
         rawval)))
        self.option = option
        self.section = section



class ParsingError(Error):
    __module__ = __name__

    def __init__(self, filename):
        Error.__init__(self, ('File contains parsing errors: %s' % filename))
        self.filename = filename
        self.errors = []



    def append(self, lineno, line):
        self.errors.append((lineno,
         line))
        self._msg = (self._msg + ('\n\t[line %2d]: %s' % (lineno,
         line)))



class MissingSectionHeaderError(ParsingError):
    __module__ = __name__

    def __init__(self, filename, lineno, line):
        Error.__init__(self, ('File contains no section headers.\nfile: %s, line: %d\n%s' % (filename,
         lineno,
         line)))
        self.filename = filename
        self.lineno = lineno
        self.line = line



class ConfigParser:
    __module__ = __name__

    def __init__(self, defaults = None):
        self._ConfigParser__sections = {}
        if (defaults is None):
            self._ConfigParser__defaults = {}
        else:
            self._ConfigParser__defaults = defaults



    def defaults(self):
        return self._ConfigParser__defaults



    def sections(self):
        """Return a list of section names, excluding [DEFAULT]"""
        return self._ConfigParser__sections.keys()



    def add_section(self, section):
        """Create a new section in the configuration.

        Raise DuplicateSectionError if a section by the specified name
        already exists.
        """
        if self._ConfigParser__sections.has_key(section):
            raise DuplicateSectionError(section)
        self._ConfigParser__sections[section] = {}



    def has_section(self, section):
        """Indicate whether the named section is present in the configuration.

        The DEFAULT section is not acknowledged.
        """
        return (section in self.sections())



    def options(self, section):
        """Return a list of option names for the given section name."""
        try:
            opts = self._ConfigParser__sections[section].copy()
        except KeyError:
            raise NoSectionError(section)
        opts.update(self._ConfigParser__defaults)
        if opts.has_key('__name__'):
            del opts['__name__']
        return opts.keys()



    def read(self, filenames):
        """Read and parse a filename or a list of filenames.

        Files that cannot be opened are silently ignored; this is
        designed so that you can specify a list of potential
        configuration file locations (e.g. current directory, user's
        home directory, systemwide directory), and all existing
        configuration files in the list will be read.  A single
        filename may also be given.
        """
        if (type(filenames) in types.StringTypes):
            filenames = [filenames]
        for filename in filenames:
            try:
                fp = open(filename)
            except IOError:
                continue
            self._ConfigParser__read(fp, filename)
            fp.close()




    def readfp(self, fp, filename = None):
        """Like read() but the argument must be a file-like object.

        The `fp' argument must have a `readline' method.  Optional
        second argument is the `filename', which if not given, is
        taken from fp.name.  If fp has no `name' attribute, `<???>' is
        used.

        """
        if (filename is None):
            try:
                filename = fp.name
            except AttributeError:
                filename = '<???>'
        self._ConfigParser__read(fp, filename)



    def get(self, section, option, raw = 0, vars = None):
        """Get an option value for a given section.

        All % interpolations are expanded in the return values, based on the
        defaults passed into the constructor, unless the optional argument
        `raw' is true.  Additional substitutions may be provided using the
        `vars' argument, which must be a dictionary whose contents overrides
        any pre-existing defaults.

        The section DEFAULT is special.
        """
        try:
            sectdict = self._ConfigParser__sections[section].copy()
        except KeyError:
            if (section == DEFAULTSECT):
                sectdict = {}
            else:
                raise NoSectionError(section)
        d = self._ConfigParser__defaults.copy()
        d.update(sectdict)
        if vars:
            d.update(vars)
        option = self.optionxform(option)
        try:
            rawval = d[option]
        except KeyError:
            raise NoOptionError(option, section)
        if raw:
            return rawval
        value = rawval
        depth = 0
        while (depth < 10):
            depth = (depth + 1)
            if (value.find('%(') >= 0):
                try:
                    value = (value % d)
                except KeyError, key:
                    raise InterpolationError(key, option, section, rawval)
            else:
                break

        if (value.find('%(') >= 0):
            raise InterpolationDepthError(option, section, rawval)
        return value



    def __get(self, section, conv, option):
        return conv(self.get(section, option))



    def getint(self, section, option):
        return self._ConfigParser__get(section, string.atoi, option)



    def getfloat(self, section, option):
        return self._ConfigParser__get(section, string.atof, option)



    def getboolean(self, section, option):
        states = {'1': 1,
         'yes': 1,
         'true': 1,
         'on': 1,
         '0': 0,
         'no': 0,
         'false': 0,
         'off': 0}
        v = self.get(section, option)
        if (not states.has_key(v.lower())):
            raise ValueError, ('Not a boolean: %s' % v)
        return states[v.lower()]



    def optionxform(self, optionstr):
        return optionstr.lower()



    def has_option(self, section, option):
        """Check for the existence of a given option in a given section."""
        if ((not section) or (section == 'DEFAULT')):
            return self._ConfigParser__defaults.has_key(option)
        elif (not self.has_section(section)):
            return 0
        else:
            option = self.optionxform(option)
            return self._ConfigParser__sections[section].has_key(option)



    def set(self, section, option, value):
        """Set an option."""
        if ((not section) or (section == 'DEFAULT')):
            sectdict = self._ConfigParser__defaults
        else:
            try:
                sectdict = self._ConfigParser__sections[section]
            except KeyError:
                raise NoSectionError(section)
        option = self.optionxform(option)
        sectdict[option] = value



    def write(self, fp):
        """Write an .ini-format representation of the configuration state."""
        if self._ConfigParser__defaults:
            fp.write('[DEFAULT]\n')
            for (key, value,) in self._ConfigParser__defaults.items():
                fp.write(('%s = %s\n' % (key,
                 str(value).replace('\n', '\n\t'))))

            fp.write('\n')
        for section in self.sections():
            fp.write((('[' + section) + ']\n'))
            sectdict = self._ConfigParser__sections[section]
            for (key, value,) in sectdict.items():
                if (key == '__name__'):
                    continue
                fp.write(('%s = %s\n' % (key,
                 str(value).replace('\n', '\n\t'))))

            fp.write('\n')




    def remove_option(self, section, option):
        """Remove an option."""
        if ((not section) or (section == 'DEFAULT')):
            sectdict = self._ConfigParser__defaults
        else:
            try:
                sectdict = self._ConfigParser__sections[section]
            except KeyError:
                raise NoSectionError(section)
        option = self.optionxform(option)
        existed = sectdict.has_key(option)
        if existed:
            del sectdict[option]
        return existed



    def remove_section(self, section):
        """Remove a file section."""
        if self._ConfigParser__sections.has_key(section):
            del self._ConfigParser__sections[section]
            return 1
        else:
            return 0


    SECTCRE = re.compile('\\[(?P<header>[^]]+)\\]')
    OPTCRE = re.compile('(?P<option>[]\\-[\\w_.*,(){}]+)[ \\t]*(?P<vi>[:=])[ \\t]*(?P<value>.*)$')

    def __read(self, fp, fpname):
        """Parse a sectioned setup file.

        The sections in setup file contains a title line at the top,
        indicated by a name in square brackets (`[]'), plus key/value
        options lines, indicated by `name: value' format lines.
        Continuation are represented by an embedded newline then
        leading whitespace.  Blank lines, lines beginning with a '#',
        and just about everything else is ignored.
        """
        cursect = None
        optname = None
        lineno = 0
        e = None
        while 1:
            line = fp.readline()
            if (not line):
                break
            lineno = (lineno + 1)
            if ((line.strip() == '') or (line[0] in '#;')):
                continue
            if ((line.split()[0].lower() == 'rem') and (line[0] in 'rR')):
                continue
            if ((line[0] in ' \t') and ((cursect is not None) and optname)):
                value = line.strip()
                if value:
                    k = self.optionxform(optname)
                    cursect[k] = ('%s\n%s' % (cursect[k],
                     value))
            else:
                mo = self.SECTCRE.match(line)
                if mo:
                    sectname = mo.group('header')
                    if self._ConfigParser__sections.has_key(sectname):
                        cursect = self._ConfigParser__sections[sectname]
                    elif (sectname == DEFAULTSECT):
                        cursect = self._ConfigParser__defaults
                    else:
                        cursect = {'__name__': sectname}
                        self._ConfigParser__sections[sectname] = cursect
                    optname = None
                elif (cursect is None):
                    raise MissingSectionHeaderError(fpname, lineno, `line`)
                else:
                    mo = self.OPTCRE.match(line)
                    if mo:
                        (optname, vi, optval,) = mo.group('option', 'vi', 'value')
                        if ((vi in ('=',
                         ':')) and (';' in optval)):
                            pos = optval.find(';')
                            if (pos and (optval[(pos - 1)] in string.whitespace)):
                                optval = optval[:pos]
                        optval = optval.strip()
                        if (optval == '""'):
                            optval = ''
                        cursect[self.optionxform(optname)] = optval
                    else:
                        if (not e):
                            e = ParsingError(fpname)
                        e.append(lineno, `line`)

        if e:
            raise e




# local variables:
# tab-width: 4
