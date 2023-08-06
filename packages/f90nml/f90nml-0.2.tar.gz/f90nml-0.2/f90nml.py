"""f90nml.py
Parse fortran namelist files into dicts of standard Python data types.
Contact: Marshall Ward <python@marshallward.org>
---
Distributed as part of f90nml, Copyright 2014 Marshall Ward
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
"""
import os
import shlex

__version__ = '0.2'

#---
def read(nml_fname):

    f = open(nml_fname, 'r')

    f90 = shlex.shlex(f)
    f90.commenters = '!'
    f90.escapedquotes = '\'"'
    f90.wordchars += '.-+'      # Include floating point characters
    tokens = iter(f90)

    # Store groups in case-insensitive dictionary
    nmls = NmlDict()

    for t in tokens:

        # Ignore tokens outside of namelist groups
        while t != '&':
            t = next(tokens)

        # Current token is now '&'

        g_name = next(tokens)
        g_vars = NmlDict()

        v_name = None
        v_idx = None
        v_vals = []

        prior_t = t
        t = next(tokens)

        # Current token is either a variable name or finalizer (/)

        while t != '/':

            # Skip commas
            if t == ',':
                prior_t = t
                t = next(tokens)

            # Advance token
            if not t == '/':
                prior_t = t
                t = next(tokens)

            if v_name:

                #---
                # Parse the prior token value

                # Skip variable names and end commas
                #if not t in ('(', '=') and not (prior_t, t) == (',', '/'):
                if not ( t == '=' or (t == '(' and not prior_t == '=')
                        or (prior_t, t) == (',', '/')  or prior_t == ')'):

                    # Skip ahead on first value
                    if prior_t == '=':
                        prior_t = t
                        t = next(tokens)

                    # Parse the variable string
                    if prior_t == ',' :
                        next_value = None
                    else:
                        next_value, t = parse_f90val(tokens, t, prior_t)

                    if v_idx:

                        v_i = next(v_idx)

                        if v_name in g_vars:
                            v_vals = g_vars[v_name]
                            if type(v_vals) != list:
                                v_vals = [v_vals]

                        try:
                            # Default Fortran indexing starts at 1
                            v_vals[v_i - 1] = next_value
                        except IndexError:
                            # Expand list to accomodate out-of-range indices
                            size = len(v_vals)
                            v_vals.extend(None for i in range(size, v_i))
                            v_vals[v_i - 1] = next_value
                    else:
                        v_vals.append(next_value)

                # Save then deactivate the current variable
                if t in ('(', '=', '/'):

                    if len(v_vals) == 1:
                        v_vals = v_vals[0]
                    g_vars[v_name] = v_vals

                    v_name = None
                    v_vals = []

            # Parse the indices of the current variable
            if t == '(' and not prior_t == '=':
                v_name, v_indices, t = parse_f90idx(tokens, t, prior_t)
                v_idx = gen_index(v_indices)

            if t == '=':
                # Activate the next variable
                if not v_name:
                    v_name = prior_t
                    v_idx = None

        # Append the grouplist to the namelist (including empty groups)
        nmls[g_name] = g_vars

    f.close()

    return nmls


#---
def write(nml, nml_fname):

    if os.path.isfile(nml_fname):
        raise IOError('File {} already exists.'.format(nml_fname))

    f = open(nml_fname, 'w')

    for grp in sorted(nml.keys()):
        f.write('&{}\n'.format(grp))

        grp_vars = nml[grp]
        for v_name in sorted(grp_vars.keys()):

            v_val = grp_vars[v_name]

            if type(v_val) == list:
                v_str = ', '.join([to_f90str(v) for v in v_val])
            else:
                v_str = to_f90str(v_val)

            f.write('    {} = {}\n'.format(v_name, v_str))

        f.write('/\n')

    f.close()


#---
def to_f90str(v):
    """Convert primitive Python types to equivalent Fortran strings"""

    # TODO: Hash this somehow
    if type(v) is int:
        return str(v)
    elif type(v) is float:
        # TODO: Floating point precision?
        return str(v)
    elif type(v) is bool:
        return '.{}.'.format(str(v).lower())
    elif type(v) is complex:
        return '({}, {})'.format(v.real, v.imag)
    elif type(v) is str:
        return '\'{}\''.format(v)
    elif v is None:
        return ''
    else:
        raise ValueError('Type {} of {} cannot be converted to a Fortran type.'
                         ''.format(type(v), v))


#---
def parse_f90val(tokens, t, s):
    """Convert string repr of Fortran type to equivalent Python type."""
    assert type(s) is str

    # Construct the complex string
    if s == '(':
        s_re = t
        next(tokens)
        s_im = next(tokens)

        t = next(tokens)

        s = '({}, {})'.format(s_re, s_im)


    recast_funcs = [int, float, f90complex, f90bool, f90str]

    for f90type in recast_funcs:
        try:
            v = f90type(s)
            return v, t
        except ValueError:
            continue

    # If all test failed, then raise ValueError
    raise ValueError('Could not convert {} to a Python data type.'.format(s))


#---
def f90complex(s):
    assert type(s) == str

    if s[0] == '(' and s[-1] == ')' and len(s.split(',')) == 2:
        s_re, s_im = s[1:-1].split(',', 1)

        # NOTE: Failed float(str) will raise ValueError
        return complex(float(s_re), float(s_im))
    else:
        raise ValueError('{} must be in complex number form (x, y)'.format(s))


#---
def f90bool(s):
    assert type(s) == str

    try:
        s_bool = s[1].lower() if s.startswith('.') else s[0].lower()
    except IndexError:
        raise ValueError('{} is not a valid logical constant.'.format(s))

    if s_bool == 't':
        return True
    elif s_bool == 'f':
        return False
    else:
        raise ValueError('{} is not a valid logical constant.'.format(s))


#---
def f90str(s):
    assert type(s) == str

    f90quotes = ["'", '"']

    if s[0] in f90quotes and s[-1] in f90quotes:
        return s[1:-1]

    raise ValueError


#---
def parse_f90idx(tokens, t, prior_t):

        idx_end = (',', ')')

        v_name = prior_t
        v_indices = []
        i_start = i_end = i_stride = None

        # Start index
        t = next(tokens)
        try:
            i_start = int(t)
            t = next(tokens)
        except ValueError:
            if t in idx_end:
                raise ValueError('{} index cannot be empty.'
                                 ''.format(v_name))
            elif not t == ':':
                raise

        # End index
        if t == ':':
            t = next(tokens)
            try:
                i_end = int(t)
                t = next(tokens)
            except ValueError:
                if t == ':':
                    raise ValueError('{} end index cannot be implicit '
                                     'when using stride.'
                                     ''.format(v_name))
                elif not t in idx_end:
                    raise
        elif t in idx_end:
            # Replace index with single-index range
            if i_start:
                i_end = i_start

        # Stride index
        if t == ':':
            t = next(tokens)
            try:
                i_stride = int(t)
            except ValueError:
                if t == ')':
                    raise ValueError('{} stride index cannot be '
                                     'implicit.'.format(v_name))
                else:
                    raise

            if i_stride == 0:
                raise ValueError('{} stride index cannot be zero.'
                                 ''.format(v_name))

            t = next(tokens)

        if not t in idx_end:
            raise ValueError('{} index did not terminate '
                             'correctly.'.format(v_name))

        idx_triplet = (i_start, i_end, i_stride)
        v_indices.append((idx_triplet))
        t = next(tokens)

        return v_name, v_indices, t


#---
def gen_index(idx):
    # TODO: Multidimensional support (numpy)
    i_s, i_e, d_i = idx[0]

    if not i_s:
        i_s = 1

    # TODO: infinite i_e?
    if not i_e:
        i_e = 10000

    if not d_i:
        d_i = 1

    i = i_s
    while i <= i_e:
        yield i
        i += d_i


#---
class NmlDict(dict):
    def __setitem__(self, key, value):
        super(NmlDict, self).__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super(NmlDict, self).__getitem__(key.lower())
