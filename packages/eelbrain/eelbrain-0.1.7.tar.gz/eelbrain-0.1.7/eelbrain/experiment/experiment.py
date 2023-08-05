# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>

from collections import defaultdict
from glob import glob
import itertools
import os
import re
import shutil
import subprocess

import numpy as np

from .. import fmtxt
from .. import ui
from ..utils.com import send_email, Notifier


def _etree_expand(node, state):
    for tk, tv in node.iteritems():
        if tk == '.':
            continue

        for k, v in state.iteritems():
            name = '{%s}' % tk
            if str(v).startswith(name):
                tv[k] = {'.': v.replace(name, '')}
        if len(tv) > 1:
            _etree_expand(tv, state)


def _etree_node_repr(node, name, indent=0):
    head = ' ' * indent
    out = [(name, head + node['.'])]
    for k, v in node.iteritems():
        if k == '.':
            continue

        out.extend(_etree_node_repr(v, k, indent=indent + 3))
    return out


class LayeredDict(dict):
    """Modify dictionary entries while keeping a history for resetting
    """
    def __init__(self, *args, **kwargs):
        self._layers = []
        self.level = 0

    def __repr__(self):
        rep = ("<LayeredDict at level %i: "
               "%r>" % (self.level, dict.__repr__(self)))
        return rep

    def get_lower(self, key, level, *args):
        """Retrieve a field value from any level

        Parameters
        ----------
        key : str
            the field name (dicitonary key).
        level : int
            The level from which to retrieve the value. -1 = the current level.
        """
        if level == self.level:
            return self[key]
        elif -self.level < level < self.level:
            ldict = self._layers[level]
            return ldict[key]
        else:
            err = ("Dict has only %i levels, requested "
                   "%i" % (self.level, level))
            raise ValueError(err)

    def increase_depth(self):
        """Increase depth to make changes while preserving values at the lower level

        Returns
        -------
        level : int
            New level.
        """
        self._layers.append(self.copy())
        self.level += 1
        return self.level

    def reset(self, level=None):
        """Reset the values

        Parameters
        ----------
        level : None | int
            If None, stay at the current level. With int, reset to a lower
            level. Negative values specify relative offset from current level.
        """
        if level is None:
            level = self.level
        elif level > self.level:
            err = ("Requested level (%i) higher than current level "
                   "(%i)" % (level, self.level))
            raise RuntimeError(err)

        if level == self.level:
            new = self._layers[-1]
        elif level < 0:
            while level < 0:
                new = self._layers.pop()
                level += 1
        else:
            while level < self.level:
                new = self._layers.pop()
                self.level -= 1

        self.clear()
        self.update(new)


class TreeModel(object):
    """A hierarchical collection of format strings and field values
    """
    owner = None  # email address as string (for notification)

    _fmt_pattern = re.compile('\{([\w-]+)\}')

    # a dictionary of static templates (i.e., templates that do not have any hooks)
    _templates = {}
    _defaults = {}

    _repr_args = ()
    _repr_kwargs = ()
    def __init__(self, **state):
        # scaffold for state
        self._fields = LayeredDict()
        self._field_values = LayeredDict()
        self._params = LayeredDict()

        # scaffold for hooks
        self._eval_handlers = defaultdict(list)
        self._post_set_handlers = defaultdict(list)
        self._set_handlers = {}

        # construct initial state: make all defaults available, then set as
        # many values as we can
        self._defaults = dict(self._defaults)
        self._defaults.update(state)
        for k, v in self._templates.iteritems():
            if v is None:  # secondary field
                pass
            elif isinstance(v, basestring):
                self._register_value(k, v)
            elif isinstance(v, tuple):
                self._register_field(k, v, v[0])
            else:
                err = ("Invalid templates field value: %r. Need None, tuple "
                       "or string" % v)
                raise TypeError(err)

        if self.owner:
            self.notification = Notifier(self.owner, 'MneExperiment task')

    def __repr__(self):
        args = [repr(self._fields[arg]) for arg in self._repr_args]
        kwargs = [(arg, repr(self._fields[arg])) for arg in self._repr_kwargs]

        for k in sorted(self._fields):
            if k in self._repr_args or k in self._repr_kwargs:
                continue
            elif '{' in self._fields[k]:
                continue

            v = self._fields[k]
            if v != self._fields.get_lower(k, level=0):
                kwargs.append((k, repr(v)))

        args.extend('='.join(pair) for pair in kwargs)
        args = ', '.join(args)
        return "%s(%s)" % (self.__class__.__name__, args)

    def _bind_eval(self, key, handler):
        self._eval_handlers[key].append(handler)

    def _bind_post_set(self, key, handler):
        self._post_set_handlers[key].append(handler)

    def _bind_set(self, key, handler):
        if key in self._set_handlers:
            raise KeyError("set-handler for %r already set" % key)
        self._set_handlers[key] = handler

    def _find_missing_fields(self, add=False):
        """Find all field names occurring in field values but not as fields

        Parameters
        ----------
        add : bool
            Add non-existent field names with default value ''.
        """
        fields = set()
        for k in self._fields.keys():
            temp = self._fields[k]
            for field in self._fmt_pattern.findall(temp):
                if field not in self._fields:
                    fields.add(field)

        if add:
            for field in fields:
                self._register_value(field, '')

        return fields

    def _register_field(self, key, values=None, default=None, set_handler=None,
                        eval_handler=None, post_set_handler=None):
        """Register an iterable field

        Parameters
        ----------
        key : str
            Name of the field.
        values : None | sequence of str
            Possible values for this field, if known.
        default : None | str
            Set the default value (if None, the first element in values).
        set_handler : None | callable
            Function to call instead of updating the state value,
        eval_handler : None | callable
            Function to use for evaluating a value before setting.
        post_set_handler : None | callable
            Function to call after the value is changed.
        """
        if key in self._fields:
            raise KeyError("Field already exists: %r" % key)

        if set_handler is not None:
            self._bind_set(key, set_handler)
        if eval_handler is not None:
            self._bind_eval(key, eval_handler)
        if post_set_handler is not None:
            self._bind_post_set(key, post_set_handler)

        default = self._defaults.get(key, default)

        if values is not None and len(values):
            if default is None:
                default = values[0]
            elif default not in values:
                err = ("Default %r for %r not in values "
                       "%s" % (default, key, str(values)))
                raise ValueError(err)

            self._field_values[key] = tuple(values)

        if default is None:
            self._fields[key] = default
        else:
            kwargs = {key: default, 'add':True}
            self.set(**kwargs)

    def _register_value(self, key, default, set_handler=None,
                        eval_handler=None, post_set_handler=None):
        """Register a value with handlers

        Parameters
        ----------
        key : str
            Name of the field.
        default : None | str
            Set the default value.
        set_handler : None | callable
            Function to call instead of updating the state value,
        eval_handler : None | callable
            Function to use for evaluating a value before setting.
        post_set_handler : None | callable
            Function to call after the value is changed.
        """
        if key in self._fields:
            raise KeyError("Field already exists: %r" % key)

        if set_handler is not None:
            self._bind_set(key, set_handler)
        if eval_handler is not None:
            self._bind_eval(key, eval_handler)
        if post_set_handler is not None:
            self._bind_post_set(key, post_set_handler)

        default = self._defaults.get(key, default)
        kwargs = {key: default, 'add':True}
        self.set(**kwargs)

    def _increase_depth(self):
        """Increase the depth of the settings by a level

        See also
        --------
        reset : reset to a lower level
        """
        self._fields.increase_depth()
        self._field_values.increase_depth()
        return self._params.increase_depth()

    def expand_template(self, temp, values=()):
        """
        Expand a template until all its subtemplates are neither in
        field names or in ``values``

        Parameters
        ----------
        values : container (implements __contains__)
            values which should not be expanded.
        """
        temp = self._fields.get(temp, temp)

        while True:
            stop = True
            for name in self._fmt_pattern.findall(temp):
                if (name in values) or (self._field_values.get(name, False)):
                    pass
                else:
                    temp = temp.replace('{%s}' % name, self._fields[name])
                    stop = False

            if stop:
                break

        return temp

    def find_keys(self, temp):
        """
        Find all terminal keys that are relevant for a template.

        Returns
        -------
        keys : set
            All terminal keys that are relevant for foormatting temp.
        """
        keys = set()
        temp = self._fields.get(temp, temp)

        for key in self._fmt_pattern.findall(temp):
            value = self._fields[key]
            if self._fmt_pattern.findall(value):
                keys = keys.union(self.find_keys(value))
            else:
                keys.add(key)

        return keys

    def format(self, string, vmatch=True, **kwargs):
        """Format a string (i.e., replace any '{xxx}' fields with their values)

        Parameters
        ----------
        string : str
            Template string.
        vmatch : bool
            For fields with known names, only allow existing field names.
        others :
            State parameters.

        Returns
        -------
        formatted_string : str
            The template temp formatted with current state values.
        """
        self.set(match=vmatch, **kwargs)

        while True:
            variables = self._fmt_pattern.findall(string)
            if variables:
                string = string.format(**self._fields)
            else:
                break

        return string

    def get(self, temp, **state):
        path = self.format('{%s}' % temp, **state)
        return path

    def get_field_values(self, field):
        values = self._field_values[field]
        return values

    def iter(self, fields, exclude={}, values={}, mail=False, prog=False,
             **constants):
        """
        Cycle the experiment's state through all values on the given fields

        Parameters
        ----------
        fields : list | str
            Field(s) over which should be iterated.
        exclude : dict  {str: str, str: iterator over str, ...}
            Values to exclude from the iteration with {name: value} and/or
            {name: (sequence of values, )} entries.
        values : dict  {str: iterator over str}
            Fields with custom values to iterate over (instead of the
            corresponding field values) with {name: (sequence of values)}
            entries.
        group : None | str
            If iterating over subjects, use this group ('all' or a name defined
            in experiment.groups).
        prog : bool | str
            Show a progress dialog; str for dialog title.
        mail : bool | str
            Send an email when iteration is finished. Can be True or an email
            address. If True, the notification is sent to :attr:`.owner`.
        others :
            Fields with constant values throughout the iteration.
        """
        if mail is True:
            mail = self.owner

        # set constants
        self.set(**constants)
        level = self._increase_depth()

        if isinstance(fields, basestring):
            fields = [fields]
            yield_str = True
        else:
            yield_str = False
        fields = list(set(fields).difference(constants).union(values))

        # gather possible values to iterate over
        field_values = {k: self.get_field_values(k) for k in fields}
        field_values.update(values)

        # exclude values
        for k in exclude:
            ex = exclude[k]
            if isinstance(ex, basestring):
                ex = (ex,)
            field_values[k] = [v for v in field_values[k] if not v in ex]

        # pick out the fields to iterate, but drop excluded cases:
        v_lists = []
        for field in fields:
            v_lists.append(field_values[field])

        if len(v_lists):
            if prog:
                i_max = np.prod(map(len, v_lists))
                if not isinstance(prog, str):
                    prog = "MNE Experiment Iterator"
                progm = ui.progress_monitor(i_max, prog, "")
                prog = True

            for v_list in itertools.product(*v_lists):
                if prog:
                    progm.message(' | '.join(map(str, v_list)))
                self.reset()
                values = dict(zip(fields, v_list))
                self.set(**values)

                if yield_str:
                    yield v_list[0]
                else:
                    yield v_list

                if prog:
                    progm.advance()
        else:
            yield ()

        self.reset(level - 1)
        if mail:
            send_email(mail, "Eelbrain Task Done", "I did as you desired, "
                       "my master.")

    def iter_temp(self, temp, exclude={}, values={}, mail=False, prog=False,
                  **constants):
        """
        Iterate through all paths conforming to a template given in ``temp``.

        Parameters
        ----------
        temp : str
            Name of a template in the MneExperiment.templates dictionary, or
            a path template with variables indicated as in ``'{var_name}'``
        """
        # if the name is an existing template, retrieve it
        keep = constants.keys() + values.keys()
        temp = self.expand_template(temp, values=keep)

        # find variables for iteration
        variables = set(self._fmt_pattern.findall(temp))

        for _ in self.iter(variables, exclude=exclude, values=values,
                           mail=mail, prog=prog, **constants):
            path = temp.format(**self._fields)
            yield path

    def reset(self, level=None):
        """Reset the depth of the settings to a lower level

        Parameters
        ----------
        level : None | int
            If None, stay at the current level. With int, reset to a lower
            level. Negative values specify relative offset from current level.
        """
        self._fields.reset(level)
        self._field_values.reset(level)
        self._params.reset(level)

    def set(self, match=True, **state):
        """Set the value of one or more fields.

        Parameters
        ----------
        match : bool
            For fields with stored values, only allow valid values.
        kwargs :
            Fields and values to set. Invalid fields raise a KeyError. Unless
            match == False, Invalid values raise a ValueError.
        """
        # fields with special set handlers
        for k in state.keys():
            if k in self._set_handlers:
                v = state.pop(k)
                self._set_handlers[k](v)

        # make sure only valid fields are set
        add = state.pop('add', False)
        if not add:
            for k in state:
                if k not in self._fields:
                    raise KeyError("No template named %r" % k)

        # eval all values
        for k in state.keys():
            handlers = self._eval_handlers[k]
            if handlers:
                for handler in handlers:
                    state[k] = handler(state[k])
            elif not match:
                pass
            elif k not in self._field_values:
                pass
            elif '*' in state[k]:
                pass
            elif state[k] not in self.get_field_values(k):
                err = ("Variable {k!r} has no value {v!r}. In order to "
                       "see valid values use e.list_values(); In order to "
                       "set a non-existent value, use e.set({k!s}={v!r}, "
                       "match=False).".format(k=k, v=state[k]))
                raise ValueError(err)

        self._fields.update(state)

        # call post_set handlers
        for k, v in state.iteritems():
            for handler in self._post_set_handlers[k]:
                handler(v)

    def show_fields(self, str_out=False):
        """
        Generate a table for all iterable fields and ther values.

        Parameters
        ----------
        str_out : bool
            Return the table as a string (instead of printing it).
        """
        lines = []
        for key in self._field_values:
            values = list(self.get_field_values(key))
            line = '%s:' % key
            head_len = len(line) + 1
            while values:
                v = repr(values.pop(0))
                if values:
                    v += ','
                if len(v) < 80 - head_len:
                    line += ' ' + v
                else:
                    lines.append(line)
                    line = ' ' * head_len + v

                if not values:
                    lines.append(line)

        table = os.linesep.join(lines)
        if str_out:
            return table
        else:
            print table

    def show_state(self, temp=None, empty=False):
        """
        List all top-level fields and their values (i.e., fields whose values
        do not contain templates).

        Parameters
        ----------
        temp : None | str
            Only show variables relevant to this template.
        empty : bool
            Show empty variables (items whose value is the empty string '').

        Returns
        -------
        state : Table
            Table of (relevant) variables and their values.
        """
        table = fmtxt.Table('lll')
        table.cells('Key', '*', 'Value')
        table.caption('*: Value is modified from initialization state.')
        table.midrule()

        if temp is None:
            keys = (k for k, v in self._fields.iteritems()
                    if (not '{' in v) and len(v) < 60)
        else:
            keys = self.find_keys(temp)

        for k in sorted(keys):
            v = self._fields[k]
            if v != self._fields.get_lower(k, level=0):
                mod = '*'
            else:
                mod = ''

            if empty or mod or v:
                table.cells(k, mod, repr(v))

        return table

    def show_tree(self, root='root'):
        """
        Print a tree of the filehierarchy implicit in the templates

        Parameters
        ----------
        root : str
            Name of the root template (e.g., 'besa-root').
        """
        tree = {'.': root}
        root_temp = '{%s}' % root
        for k, v in self._fields.iteritems():
            if str(v).startswith(root_temp):
                tree[k] = {'.': v.replace(root_temp, '')}
        _etree_expand(tree, self._fields)
        nodes = _etree_node_repr(tree, root)
        name_len = max(len(n) for n, _ in nodes)
        path_len = max(len(p) for _, p in nodes)
        pad = ' ' * (80 - name_len - path_len)
        print os.linesep.join(n.ljust(name_len) + pad + p.ljust(path_len) for n, p in nodes)


class FileTree(TreeModel):
    """
    :class:`TreeModel` subclass for representing a file system hierarchy.
    """
    _repr_args = ('root',)
    def __init__(self, **state):
        TreeModel.__init__(self, **state)
        self._make_handlers = {}
        self._register_field('root', set_handler=self.set_root)

    def _bind_make(self, key, handler):
        if key in self._make_handlers:
            raise RuntimeError("Make handler for %r already defined." % key)
        self._make_handlers[key] = handler

    def set_root(self, root):
        root = os.path.expanduser(root)
        if not os.path.exists(root):
            raise IOError("Root does not exist: %r" % root)
        self._fields['root'] = root

    def get(self, temp, fmatch=True, vmatch=True, match=True, mkdir=False,
            make=False, **kwargs):
        """
        Retrieve a formatted template

        With match=True, '*' are expanded to match a file,
        and if there is not a unique match, an error is raised. With
        mkdir=True, the directory containing the file is created if it does not
        exist.

        Parameters
        ----------
        temp : str
            Name of the requested template.
        fmatch : bool
            "File-match": If the template contains asterisk ('*'), use glob to
            fill it in. An IOError is raised if the pattern does not match
            exactly one file.
        vmatch : bool
            "Value match": Require existence of the assigned value (only
            applies for fields with stored values).
        match : bool
            Do any matching (i.e., match=False sets fmatch as well as vmatch
            to False).
        mkdir : bool
            If the directory containing the file does not exist, create it.
        make : bool
            If a requested file does not exists, make it if possible.
        kwargs :
            Set any state values.
        """
        if not match:
            fmatch = vmatch = False

        path = TreeModel.get(self, temp, vmatch=vmatch, **kwargs)
        path = os.path.expanduser(path)

        # assert the presence of the file
        if fmatch and ('*' in path):
            paths = glob(path)
            if len(paths) == 1:
                path = paths[0]
            elif len(paths) > 1:
                err = "More than one files match %r: %r" % (path, paths)
                raise IOError(err)
            else:
                raise IOError("No file found for %r" % path)

        # create the directory
        if mkdir:
            dirname = os.path.dirname(path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

        # make the file
        if make and not os.path.exists(path) and temp in self._make_handlers:
            if temp in self._make_handlers:
                level = self._increase_depth()
                self._make_handlers[temp]()
                self.reset(level - 1)
            else:
                raise RuntimeError("No make handler for %r." % temp)

        return path

    def show_file_status(self, temp, row, col=None, count=True, present='X',
                         absent='-', **kwargs):
        """
        Compile a table about the existence of files

        Parameters
        ----------
        temp : str
            The name of the path template for the files to examine.
        row : str
            Field over which to alternate rows.
        col : None | str
            Field over which to alternate columns.
        count : bool
            Add a column with a number for each subject.
        present : str
            String to display when a given file is present.
        absent : str
            String to display when a given file is absent.

        Examples
        --------
        >>> e.show_file_status('raw-file', 'subject', 'raw')
             Subject   Clm   Lp40   Hp.1-lp40   Hp1-lp40
        ------------------------------------------------
         0   AD001     X     X      X           -
         1   AD002     X     X      X           -
        ...
        """
        if col is None:
            ncol = 1
        else:
            col_v = self.get_field_values(col)
            ncol = len(col_v)

        # table header
        table = fmtxt.Table('r' * bool(count) + 'l' * (ncol + 1))
        if count:
            table.cell()
        table.cell(row.capitalize())
        if col is None:
            table.cell(temp.capitalize())
        else:
            for name in col_v:
                table.cell(name.capitalize())
        table.midrule()

        # body
        for i, row_v in enumerate(self.iter(row, **kwargs)):
            if count:
                table.cell(i)
            table.cell(row_v)
            exist = []
            if col is None:
                path = self.get(temp)
                exist.append(os.path.exists(path))
            else:
                for v in col_v:
                    path = self.get(temp, **{col: v})
                    exist.append(os.path.exists(path))

            for exists in exist:
                if exists:
                    table.cell(present)
                else:
                    table.cell(absent)

        return table

    def show_file_status_mult(self, files, fields, count=True, present='X',
                              absent='-', **kwargs):
        """
        Compile a table about the existence of multiple files

        Parameters
        ----------
        files : str | list of str
            The names of the path templates whose existence to list.
        fields : str | list of str
            The names of the variables for which to list files (i.e., for each
            unique combination of ``fields``, list ``files``).
        count : bool
            Add a column with a number for each subject.
        present : str
            String to display when a given file is present.
        absent : str
            String to display when a given file is absent.

        Examples
        --------
        >>> e.show_file_status_mult(['raw-file', 'trans-file', 'fwd-file'],
        ... 'subject')
             Subject   Raw-file   Trans-file   Fwd-file
        -----------------------------------------------
         0   AD001     X          X            X
         1   AD002     X          X            X
         2   AD003     X          X            X
        ...
        """
        if not isinstance(files, (list, tuple)):
            files = [files]
        if not isinstance(fields, (list, tuple)):
            fields = [fields]

        ncol = (len(fields) + len(files))
        table = fmtxt.Table('r' * bool(count) + 'l' * ncol)
        if count:
            table.cell()
        for name in fields + files:
            table.cell(name.capitalize())
        table.midrule()

        for i, _ in enumerate(self.iter(fields, **kwargs)):
            if count:
                table.cell(i)

            for field in fields:
                table.cell(self.get(field))

            for temp in files:
                path = self.get(temp)
                if os.path.exists(path):
                    table.cell(present)
                else:
                    table.cell(absent)

        return table

    def show_in_finder(self, temp, **kwargs):
        "Reveals the file corresponding to the ``temp`` template in the Finder."
        fname = self.get(temp, **kwargs)
        subprocess.call(["open", "-R", fname])

    def push(self, dst_root, names, overwrite=False, **kwargs):
        """Copy files to another experiment root folder.

        Before copying any files the user is asked for confirmation.

        Parameters
        ----------
        dst_root : str
            Path to the root to which the files should be copied.
        names : str | sequence of str
            Name(s) of the template(s) of the files that should be copied.
        overwrite : bool
            What to do if the target file already exists.
        others :
            Update experiment state.

        Notes
        -----
        Use ``e.show_tree()`` to find out which element(s) to copy.
        """
        if isinstance(names, basestring):
            names = [names]

        # find files
        files = []
        for name in names:
            for src in self.iter_temp(name, **kwargs):
                if '*' in src:
                    raise NotImplementedError("Can't fnmatch here yet")

                if os.path.exists(src):
                    dst = self.get(name, root=dst_root)
                    if src == dst:
                        raise ValueError("Source == destination (%r)" % src)

                    if os.path.exists(dst):
                        flag = 'o' if overwrite else 'e'
                    else:
                        flag = ' '
                else:
                    dst = None
                    flag = 'm'
                files.append((src, dst, flag))

        # prompt for confirmation
        root = self.get('root')
        n_root = len(root)
        for src, dst, flag in files:
            if src.startswith(root):
                src = src[n_root:]
            print(' '.join((flag, src[-78:])))
        print("Flags: o=overwrite, e=skip, it exists, m=skip, source is "
              "missing")
        msg = "Proceed? (confirm with 'yes'): "
        if raw_input(msg) != 'yes':
            return

        # copy the files
        for src, dst, flag in files:
            if flag in ('e', 'm'):
                continue

            dirpath = os.path.dirname(dst)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)

            if os.path.isdir(src):
                if flag == 'o':
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy(src, dst)

    def rename(self, old, new):
        """
        Rename a files corresponding to a pattern (or template)

        Parameters
        ----------
        old : str
            Template for the files to be renamed. Can interpret '*', but will
            raise an error in cases where more than one file fit the pattern.
        new : str
            Template for the new names.

        Examples
        --------
        The following command will collect a specific file for each subject and
        place it in a common folder:

        >>> e.rename('{root}/{subject}/info.txt',
                     '/some_other_place/{subject}s_info.txt'
        """
        new = self.expand_template(new)
        files = []
        for old_name in self.iter_temp(old):
            if '*' in old_name:
                matches = glob(old_name)
                if len(matches) == 1:
                    old_name = matches[0]
                elif len(matches) > 1:
                    err = ("Several files fit the pattern %r" % old_name)
                    raise ValueError(err)

            if os.path.exists(old_name):
                new_name = self.format(new)
                files.append((old_name, new_name))

        if not files:
            print "No files found for %r" % old
            return

        old_pf = os.path.commonprefix([pair[0] for pair in files])
        new_pf = os.path.commonprefix([pair[1] for pair in files])
        n_pf_old = len(old_pf)
        n_pf_new = len(new_pf)

        table = fmtxt.Table('lll')
        table.cells('Old', '', 'New')
        table.midrule()
        table.caption("%s -> %s" % (old_pf, new_pf))
        for old, new in files:
            table.cells(old[n_pf_old:], '->', new[n_pf_new:])

        print table

        msg = "Rename %s files (confirm with 'yes')? " % len(files)
        if raw_input(msg) == 'yes':
            for old, new in files:
                dirname = os.path.dirname(new)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                os.rename(old, new)

    def rm(self, temp, exclude={}, values={}, v=False, **constants):
        """
        Remove all files corresponding to a template

        Asks for confirmation before deleting anything. Uses glob, so
        individual templates can be set to '*'.

        Parameters
        ----------
        temp : str
            The template.
        exclude : dict
            Exclude specific values by field.
        values : dict
            Provide specific values by field.
        v : bool
            Verbose mode (print all filename patterns that are searched).
        others :
            Set fields.
        """
        files = []
        for fname in self.iter_temp(temp, exclude=exclude, values=values,
                                    **constants):
            fnames = glob(fname)
            if v:
                print "%s -> %i" % (fname, len(fnames))
            if fnames:
                files.extend(fnames)
            elif os.path.exists(fname):
                files.append(fname)

        if files:
            root = self.get('root')
            print "root: %s\n" % root
            root_len = len(root)
            for name in files:
                if name.startswith(root):
                    print name[root_len:]
                else:
                    print name
            msg = "Delete %i files (confirm with 'yes')? " % len(files)
            if raw_input(msg) == 'yes':
                for path in files:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
        else:
            print "No files found for %r" % temp

