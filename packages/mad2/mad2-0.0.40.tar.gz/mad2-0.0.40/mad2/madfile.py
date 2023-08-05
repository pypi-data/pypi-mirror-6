import logging
import os

import jinja2

import Yaco

from mad2.exception import MadPermissionDenied

lg = logging.getLogger(__name__)
#lg.setLevel(logging.DEBUG)


def dummy_hook_method(*args, **kw):
    return None


class MadFile(object):
    """

    """
    def __init__(self,
                 filename,
                 base=Yaco.Yaco(),
                 hook_method=dummy_hook_method):

        self.dirmode = False
        dirname = os.path.dirname(filename)
        basename = os.path.basename(filename)

        lg.debug("Instantiating a madfile for '{}' / '{}'".format(dirname, basename))

        if os.path.isdir(filename):
            self.dirmode = True
            maddir = os.path.join(os.path.abspath(filename), '.mad', 'config')
            if not os.path.exists(maddir):
                os.makedirs(maddir)
            lg.debug("'{}' is a dir".format(filename))
            madname = os.path.join(maddir, '_root.config')
            filename = filename
        else:
            #looking at a filename
            if basename[-4:] == '.mad':

                if basename[0] == '.':
                    basename = basename[1:-4]
                else:
                    #old style - prob needs to go
                    basename = basename[:-4]

                madname = filename
                filename = os.path.join(dirname, basename)
            else:
                filename = filename
                madname = os.path.join(dirname, '.' + basename + '.mad')

        #lg.debug("madname: {}".format(madname))
        #lg.debug("filename: {}".format(filename))

        if os.path.exists(madname) and not os.access(madname, os.R_OK):
            raise MadPermissionDenied()

        #must make a copy - otherwise we're overwriting the same
        #object for the next instantiation
        self.all = base.copy()

        #for local data
        self.mad = Yaco.Yaco()

        self.all.filename = filename
        self.all.dirname = os.path.abspath(dirname)
        self.all.basename = basename
        self.all.madname = madname

        if os.path.exists(madname) and not os.path.exists(filename):
            lg.warning("Orphaned mad file: {}".format(madname))
            self.all.orphan = True

        self.hook_method = hook_method

        self.load()

    def collapse(self):
        rv = self.all.copy()
        rv.update(self.mad)
        return rv

    def __str__(self):
        return '<mad2.madfile.MadFile {}>'.format(self.all.madname)

    def get(self, key, default):
        data = self.collapse()
        return data.get(key, default)

    def __contains__(self, key):
        data = data.collapse()
        return key in data
    def __getitem__(self, key):
        data = self.collapse()
        return data.__getitem__(key)

    __getattr__ = __getitem__

    def keys(self):
        data = self.collapse()
        return data.keys()

    def simple(self):
        data = self.collapse()
        rv = {}
        kys = data.keys()
        for k in kys:
            if data[k] and not \
                    isinstance(data[k], dict):
                rv[k] = data[k]
        return rv

    def data(self, on_top_of={}):
        """Render data into a dict like format
        """
        lg.critical("really - using this??")
        if isinstance(on_top_of, Yaco.Yaco) or \
            isinstance(on_top_of, Yaco.PolyYaco):
            data = on_top_of.simple()

        data.update(self.all.simple())
        data.update(self.mad.simple())
        return data

    def render(self, text, base):

        jenv = jinja2.Environment(
            undefined=jinja2.DebugUndefined )

        rendered = text
        iteration = 0

        while '{{' in rendered or '{%' in rendered:
            #print('1', rendered, y['rabbit'])
            if iteration > 0 and rendered == last:
                #no improvement
                break
            last = rendered
            template = jenv.from_string(rendered)
            rendered = template.render(self.all)
            iteration += 1

        return rendered


    def load(self):
        #print(self.madname)

        self.hook_method('madfile_pre_load', self)
        if os.path.exists(self.madname):
            lg.debug("loading madfile {0}".format(self.madname))
            self.mad.load(self.madname)

        self.hook_method('madfile_load', self)
        self.hook_method('madfile_post_load', self)

    def save(self):
        self.hook_method('madfile_save', self)
        try:
            lg.debug("saving to %s" % self.madname)
            self.mad.save(self.madname)
        except IOError, e:
            if e.errno == 63:
                lg.warning("Can't save - filename too long: {}"\
                        .format(self.fullpath))
            else:
                raise

        self.hook_method('madfile_post_save', self)

    def pretty(self):
        return self.mad.pretty()
