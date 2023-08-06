# deepdesk/data.py
# Copyright (C) 2014  Domino Marama
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import isodate
import json
import os
import password
import re
import shutil
import socket
import tempfile
import time
import uuid
import requests

from contextlib import contextmanager
from datetime import datetime
from glob import glob
from Stemmer import Stemmer

SYSTEM = 0
PUBLIC = 1
TRUSTED = 50
PRIVATE = 100

# the root directory for the database
root = os.path.join(os.getcwd(), "root")

# enable pretty formatting in saved records
pretty = True


def validate(value, rule):
    """
    validate(value, rule) -> bool

    Returns true if the value object passes the rule or false if it fails.
    Each item in a tuple or list must pass the rule or the validation will fail.

    Available rules are in the validators dict.

    >>> validate(23, "min 0|max 20")
    False
    >>> validate([0, 5, 12, 19], "min 0|max 20")
    True
    >>> validate("10.10.10.10", "ipv4")
    True
    >>> validate({"a":1,"b":2,"c":3}, "a|b")
    True
    """
    if isinstance(value, dict):
        # only validator for dict is to see if keys exist
        for r in rule.split("|"):
            if r not in value:
                return False
        return True
    elif isinstance(value, (list, tuple)):
        # all items must be valid
        for item in value:
            if not validate(item, rule):
                return False
        return True
    try:
        for r in rule.split("|"):
            # todo: improve re to allow escape quoted strings in rules
            #          none of current validators require this
            parts = re.findall(r'(?:(?<=["\']).*?(?=["\'])|\w+)', r)
            method = parts[0]
            args = [value]
            for n, i in enumerate(parts):
                if n:
                    cls = validators[value.__class__][method][n]
                    args.append(cls(i))
            if not validators[value.__class__][method][0](*args):
                return False
        return True
    except:
        return False


def isdate(value, format):
    # todo convert to isodate
    try:
        datetime.datetime.strptime(value, format)
        return True
    except ValueError:
        return False


def isemail(value):
    """
    isemail(value) -> bool

    Returns true if the value is an email address.

    >>> isemail("domino.marama@example.com")
    True
    >>> isemail("domino.marama@example")
    False
    """
    pattern = r'^[a-z0-9]+([._-][a-z0-9]+)*@([a-z0-9]+([._-][a-z0-9]+))+$'
    return re.match(pattern, value) is not None


def isipv4(value):
    """
    isipv4(value) -> bool

    Returns true if the value is an Internet Protocol Version 4 address.

    >>> isipv4("10.50.90.123")
    True
    >>> isipv4("10_50_90_123")
    False
    """
    try:
        socket.inet_pton(socket.AF_INET, value)
        return True
    except socket.error:
        return False


def isipv6(value):
    """
    isipv6(value) -> bool

    Returns true if the value is an Internet Protocol Version 6 address.

    >>> isipv6("c001:face:1015::")
    True
    >>> isipv6("ff0X::101")
    False
    """
    # todo? support multicast addresses eg ff0X::101
    try:
        socket.inet_pton(socket.AF_INET6, value)
        return True
    except socket.error:
        return False


def isurl(value):
    """
    isurl(value) -> bool

    Returns true if the value is a Uniform Resource Locator.

    >>> isurl("http://example.com")
    True
    >>> isurl("www.example.com")
    False
    """
    url_regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_regex.match(value) is not None

# each entry in validators is a class with a dict of rules
# each rule is a name with a tuple of the function and the class
# types for any arguments to the function

validators = {
    float: {
        'min': (float.__ge__, float),
        'max': (float.__le__, float),
        '>': (float.__gt__, float),
        '<': (float.__lt__, float)
        },
    int: {
        'min': (int.__ge__, int),
        'max': (int.__le__, int),
        '>': (int.__gt__, int),
        '<': (int.__lt__, int)
        },
    str: {
        'min': (lambda s, v: len(s) >= v, int),
        'max': (lambda s, v: len(s) <= v, int),
        'url': (isurl,),
        'ipv4': (isipv4,),
        'ipv6': (isipv6,),
        'email': (isemail,),
        'date': (isdate,)
        }
    }


@contextmanager
def filelock(filenames):
    """
    Context locking function for thread safety.
    Takes a list of filenames or a single filename to lock.
    The actual lock files are generated from filename + '.lock'

    >>> with filelock(filename):
    >>>     # do thread safe stuff
    """
    if isinstance(filenames, str):
        locks = [filenames]
    for filename in locks:
        lock = filename + ".lock"
        repeats = 500
        while repeats and os.path.exists(lock):
            sleep(0.05)
            repeats -= 1
        if not repeats:
            raise TimeoutError
        open(lock, 'a')
    try:
        yield
    finally:
        for filename in locks:
            os.remove(filename + ".lock")


def browse(keyfragment="", all=False):
    """
    browse(keyfragment, all) -> list

    Returns a list of items stored in the location indicated by keyfragment.

    By default  the data section of root is browsed and only directories
    and records (.json files) are returned.

    If 'all' is True then the browse will start at the root itself and all files
    including .cit and .ref files are returned.

    >>> browse()
    ['menu', 'imports', 'schema.org', 'system']
    >>> browse("menu/schema.org")
    ['Data Type', 'Thing', 'Data Type.json', 'Thing.json']
    """
    if all:
        base = ""
    else:
        base = 'data'
    if keyfragment:
        path = os.path.join(root, base, *keyfragment.split('/'))
    else:
        path = os.path.join(root, base)
    assert os.path.abspath(path).startswith(root)
    try:
        if all:
            return os.listdir(path)
        else:
            return [p for p in os.listdir(path)
                    if not p.endswith((".cit", ".ref"))]
    except:
        return []


def savepath(*path):
    """
    savepath(path) -> path

    This ensures that path is below the root and creates the directories
    if they do not already exists.
    """
    filename = os.path.join(*path)
    assert os.path.abspath(filename).startswith(root)
    p = os.path.dirname(filename)
    os.makedirs(p, exist_ok=True)
    return filename


def search(value):
    """
    search(value) -> set

    This returns a set of matching keys for the search value.
    The search value can be a str or a list of str.

    >>> search("web")
    {'schema.org/WebPage', 'schema.org/WebPageElement', 'schema.org/WebApplication', 'schema.org/MedicalWebPage'}

    >>> search("page")
    {'schema.org/UserPageVisits', 'schema.org/WebPage', 'schema.org/ContactPage', 'schema.org/numberOfPages', 'schema.org/ItemPage', 'schema.org/representativeOfPage', 'schema.org/CollectionPage', 'schema.org/WebPageElement', 'schema.org/SearchResultsPage', 'schema.org/CheckoutPage', 'schema.org/MedicalWebPage', 'schema.org/mainContentOfPage', 'schema.org/printPage', 'schema.org/AboutPage', 'schema.org/primaryImageOfPage', 'schema.org/ProfilePage'}

    >>> search(["page", "web"])
    {'schema.org/WebPage', 'schema.org/WebPageElement', 'schema.org/MedicalWebPage'}
    """
    if isinstance(value, str):
        value = (value,)
    result = None
    with filelock(savepath(root, 'system', 'stemmer')):
        for word in [
                w.lower() for w in set(
                    _stemmer.stemWords(value))
                if w.lower() not in _search['stopwords']]:
            parts = re.findall('.' *  _search['pathsplit'], word)
            searchindex = "/".join(["/".join(parts), word])
            if not result:
                result = set(loadoptions(searchindex, 'search'))
            else:
                result = set([
                        r for r in loadoptions(searchindex, 'search')
                        if r in result])
    return result


def titlespace(s):
    """
    titlespace(str) -> str

    Adds spaces into TitleCase strings

    >>> titlespace("ThisWouldBeBetterWithSpaces")
    'This Would Be Better With Spaces'
    """
    return "".join([s[0]] + [
        " " + char if char.isupper() else char for char in s[1:]])


def indexlookup(entry, index, reverse=False):
    """
    indexlookup(entry, index, reverse) -> str

    An index is a store of unique entry, value pairs.

    >>> indexlookup(entry, index)
    value
    >>> indexlookup(value, index, True)
    entry
    """
    e = str(entry)
    filename = os.path.join(root, "index", index)
    with filelock(filename):
        with open(filename) as f:
            for line in f:
                if reverse:
                    b = keysplit(index)[0]
                    if e.startswith(b):
                        e = e[len(b):]
                    if line.endswith(e):
                        r = line[:-len(e) - 1]
                        if r[0] == "/":
                            r = keysplit(index)[0] + r
                        return r
                else:
                    e = e.replace(" ", "_")
                    if line.startswith(e):
                        r = line[1 + len(e):-1]
                        if r[0] == "/":
                            r = keysplit(index)[0] + r
                        return r
    return None


def indexwalk(index):
    """Iterable key, entry pairs for index"""
    filename = os.path.join(root, "index", index)
    with filelock(filename):
        index_data = []
        with open(filename) as f:
            for line in f:
                entry, value = line.split(" ", 1)
                if value.startswith("/"):
                    value = keysplit(index)[0] + value
                index_data.append((entry, value.strip()))
    for line in index_data:
        yield line


def indexwrite(index, entry, value):
    """
    An index is a store of unique entry, value pairs.

    >>> indexwrite(
                    "user/email",
                    "domino.marama@example.com",
                    "person/domino.marama")
    """
    e = str(entry).replace(" ", "_")
    v = str(value)
    b = keysplit(index)[0]
    if v.startswith(b):
        v = v[len(b):]
    filename = savepath(root, "index", index)
    with filelock(filename):
        if os.path.isfile(filename):
            removeentry(filename, e, False)
        if value not in [None, "", [], {}, ()]:
            with open(filename, "a") as f:
                f.write("{} {}\n".format(e, v))


def removeentry(filename, entry, lock=True):
    """
    Deletes any references to entry from filename.
    """
    def remove(filename, entry):
        with open(filename) as f:
            fn = f.name
            with tempfile.NamedTemporaryFile(
                    prefix="deepdesk", delete=False) as t:
                tn = t.name
                for line in f:
                    e, value = line.split(" ", 1)
                    if e != entry:
                        t.write(line.encode())
        shutil.copyfile(tn, fn)
        os.remove(tn)

    if lock:
        with filelock(filename):
            remove(filename, entry)
            if not os.path.getsize(filename):
                os.remove(filename)
    else:
            remove(filename, entry)


def indexdelete(index, entry):
    """
    Deletes the entry for the index
    """
    indexwrite(index, entry, None)


def loadoptions(index, base="option"):
    """
    Returns a list of the options stored in base/index.
    """
    filename = os.path.join(root, base, index)
    with filelock(filename):
        if os.path.isfile(filename):
            with open(filename) as f:
                return [line.strip() for line in f]


def storeoption(index, value, base="option"):
    """
    Stores a unique option in base/index.
    """
    if value not in [None, "", [], {}, ()]:
        filename = savepath(root, base, index)
        with filelock(filename):
            if os.path.isfile(filename):
                with open(filename) as f:
                    for line in f:
                        if line.strip() == value:
                            return
            with open(filename, "a") as f:
                f.write(str(value) + "\n")


def keysplit(key):
    """
    keysplit(key) -> (folder, id)
    """
    parts = key.split("/")
    return ("/".join(parts[:-1]), parts[-1])


class Record:
    password = password.Password(keep_on_blank=True)

    @property
    def exists(self):
        """Record exists on disk"""
        return self.key.exists

    @property
    def iscurrent(self):
        """Record on disk has not been updated since record loaded"""
        return self.last_modified == self.key.last_modified

    def __init__(self, key="records", indict={}, profile='./system'):
        self.created = isodate.datetime_isoformat(datetime.now())
        self.profile = profile
        if isinstance(key, Key):
            key = key.value
        self.key = Key(key)
        resolvealias(self.key)
        self.hash = None
        self.salt = None
        self.owner = profile
        self.base = None
        self.fields = {}
        if os.path.isdir(self.key.filename):
            if os.path.isfile(os.path.join(self.key.filename, "meta")):
                self.key.filename = os.path.join(self.key.filename, "meta")

        filename = self.key.filename + ".json"
        if os.path.isfile(filename):
            with filelock(filename):
                self.last_modified = isodate.datetime_isoformat(
                    datetime.fromtimestamp(os.path.getmtime(filename))
                )
                with open(filename) as f:
                    self.importrecord(json.load(f, object_hook=loadhook))
        elif self.key.folder != "template":
            tkey = Key("template/" + key)
            filename = tkey.filename + ".json"
            if os.path.isfile(filename):
                with filelock(filename):
                    self.last_modified = os.path.getmtime(filename)
                    with open(filename) as f:
                        self.importrecord(
                            json.load(f, object_hook=includehook))
                        indict['base'] = tkey
        self.importrecord(indict)
        self.updateprivs()

    def importrecord(self, indict):
        """Imports indict into this record."""
        if '__record__' in indict:
            if 'owner' in indict:
                self.owner = indict['owner']
            if 'hash' in indict:
                self.hash = indict['hash']
                self.salt = indict['salt']
            if 'base' in indict:
                self.base = indict['base']
            if 'created' in indict:
                self.created = indict['created']
            indict = indict['value']
        for name, value in indict.items():
            if name in self.fields:
                if hasattr(self.fields[name], 'value'):
                    self.fields[name].value = value
                    continue
            self.fields[name] = value

    def updateprivs(self, user=None):
        """
        Update active priviledges (x.privs).

        x.privs is an int from 0 to 100 where 1 is public and 100 is
        the owner of the record. 0 is reserved for system (ie no access).
        """
        PUBLIC
        if user is None:
            user = self.profile
        if self.owner == user:
            self.privs = PRIVATE
        else:
            self.privs = PUBLIC

    def reindex(self, item=None):
        """Update all system indices for this record"""
        indexed = False
        if item is None:
            item = self.fields
        if isinstance(item, Index):
            indexed = True
            if item.index:
                indexwrite(item.index, item.value, self.key)
        elif isinstance(item, Collect):
            if item.active and item.index and item.value is not None:
                storeoption(item.index, item.value)
        elif isinstance(item, Key):
            if item.value != self.key.value:
                storeoption(self.key.filename + ".cit", item.value)
                storeoption(item.filename + ".ref", self.key.value)
        elif isinstance(item, Group):
            if item.index and item.value is not None:
                if item.value not in ["", [], ()]:
                    if not isinstance(item.value, dict):
                        if not isinstance(item.value, (list, tuple)):
                            v = [item.value]
                        else:
                            v = item.value
                    for value in v:
                        storeoption(
                            item.index,
                            self.key.value,
                            "group"),
        elif isinstance(item, Search):
            assert isinstance(item.value, str)
            if item.value:
                with filelock(savepath(root, 'data', 'system', 'stemmer')):
                    for word in [
                            w.lower() for w in set(
                                _stemmer.stemWords(item.value.split()))
                            if w.lower() not in _search['stopwords']]:
                        parts = re.findall('.' *  _search['pathsplit'], word)
                        filename = os.path.join(savepath(
                            root, 'search', *parts), word)
                        storeoption(filename, self.key.value)
        elif isinstance(item, (list, tuple)):
            for i in item:
                indexed = indexed or self.reindex(i)
        elif isinstance(item, dict):
            indexed = indexed or self.reindex(list(item.values()))
        if item == self.fields:
            if not indexed:
                storeoption("./unindexed", self.key.value, 'index')
        return indexed

    def deindex(self, item=None):
        """Remove all system indices for this record."""
        if item is None:
            item = self.fields
        if isinstance(item, Index):
            if item.index:
                indexRemove(item.index, item.value)
        elif isinstance(item, Key):
            if os.path.isfile(item.filename + ".json"):
                with filelock(item.filename + ".ref"):
                    removeentry(item.filename + ".ref", self.key.value)
        elif isinstance(item, Alias):
            filename = savepath(Key(alias).filename + ".json")
            if os.path.islink(filename):
                with filelock(filename):
                    os.remove(filename)
        elif isinstance(item, (list, tuple)):
            for i in item:
                self.reindex(i)
        elif isinstance(item, dict):
            self.reindex(list(item.values()))
        os.remove(self.key.filename + ".cit")
        # todo deindex Search & Group objects

    def purge(self):
        """Deindex and remove this record from disk."""
        self.deindex()
        if self.exists:
            os.remove(self.key.filename + ".json")

    def save(self):
        """Save this record to disk."""
        assert os.path.abspath(self.key.filename).startswith(root)
        p = os.path.dirname(self.key.filename)
        os.makedirs(p, exist_ok=True)
        if self.key.folder.startswith("template"):
            try:
                e = self.key.filename.split(".")[-1]
                if len(e) != 4:
                    raise Exception
                i = int(e)
                self.key.filename = self.key.filename[:-5]
            except:
                pass
            try:
                n = 1 + int(max(glob(self.key.filename + ".*"))[-4:])
            except:
                n = 1
            n = "000" + str(n)
            id = os.path.split(self.key.filename)[-1] + "." + n[-4:]
            self.key.value = "{}/{}".format(self.key.folder, id)
        filename = self.key.filename + ".json"
        with filelock(filename):
            with open(filename, "w") as f:
                if pretty:
                    json.dump(self, f, indent=4, sort_keys=True, cls=encoder)
                else:
                    json.dump(self, f, separators=(',', ':'), cls=encoder)
            if not self.key.folder.startswith("template"):
                self.reindex()

    def __setitem__(self, name, value):
        """x.__setitem__(i, y) <==> x[i]=y"""
        if name in self.fields and hasattr(self.fields[name], 'value'):
            self.fields[name].value = value
        else:
            self.fields[name] = value

    def __getitem__(self, name):
        """x.__getitem__(y) <==> x[y]"""
        value = self.fields[name]
        if isinstance(value, Access):
            if self.privs >= value.access:
                return value
            else:
                return None
        return value

    def __delitem__(self, name):
        """x.__delitem__(y) <==> del x[y]"""
        del(self.fields[name])

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        s = "indict={}".format(str(self.fields))
        if os.path.isfile(self.key.filename):
            s = "key='{}', ".format(self.key) + s
        return "Record({}, profile={})".format(s, self.profile)

    def __str__(self):
        """x.__str__() <==> str(x)"""
        return str(self.fields)

    def jsonencode(self):
        """Returns a json representation of the object."""
        d = {
            '__record__': self.key,
            'value': self.fields}
        d['owner'] = self.owner
        d['created'] = self.created
        if self.hash:
            d['hash'] = str(self.hash)
            if self.salt:
                d['salt'] = self.salt
            else:
                d['salt'] = True
        if self.base:
            d['base'] = self.base
        return d


class Index:
    """
    Index field wrapper.
    Fields wrapped with index will have their value and the record.key
    stored in the index.
    """
    def __init__(self, value=None, index=""):
        self.value = value
        self.index = index

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        return "Index(\"{}\", \"{}\")".format(self.value, self.index)

    def __str__(self):
        """x.__str__() <==> str(x)"""
        return str(self.value)

    def jsonencode(self):
        """Returns a json representation of the object."""
        return {
            '__index__': self.index,
            'value': self.value}


class Access:
    """
    Access field wrapper.
    """
    def __init__(self, value=None, access=PRIVATE):
        self.value = value
        self.access = access

    def __str__(self):
        """x.__str__() <==> str(x)"""
        return str(self.value)

    def jsonencode(self):
        """Returns a json representation of the object."""
        return {
            '__access__': self.access,
            'value': self.value}


class Collect:
    """
    Collect field wrapper.
    Fields wrapped in a Collect will have their unique values stored
    in the collect index. If active is False, then no collecting takes place.
    This is useful for prebuilt collections such as country codes where
    the field value should be in the collection, but new values
    should not be added.
    """
    def __init__(self, value=None, index="", active=True):
        self.value = value
        self.index = index
        self.active = active

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        return "Collect(\"{}\", \"{}\, \"{}\")".format(
            self.value, self.index, self.active)

    def __str__(self):
        """x.__str__() <==> str(x)"""
        return str(self.value)

    def jsonencode(self):
        """Returns a json representation of the object."""
        return {
            '__collect__': self.index,
            'active': self.active,
            'value': self.value}


class Group:
    """
    Group field wrapper.
    Fields wrapped in a group will have their
    record.key stored in the group index for their values.
    """
    def __init__(self, value=None, index=""):
        self.value = value
        self.index = index

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        return "Group(\"{}\", \"{}\")".format(self.value, self.index)

    def __str__(self):
        """x.__str__() <==> str(x)"""
        return str(self.value)

    def jsonencode(self):
        """Returns a json representation of the object."""
        return {
            '__group__': self.index,
            'value': self.value}


class Include(dict):
    """
    Include class for templates.
    Normal records should use Key fields rather than Include.
    """
    def __init__(self, key):
        dict.__init__(self, {'__include__': key})


class Key:
    @property
    def last_modified(self):
        """last modified time stamp"""
        return isodate.datetime_isoformat(
            datetime.fromtimestamp(os.path.getmtime(self.filename+".json")))

    @property
    def exists(self):
        """Record exists for this Key"""
        return os.path.isfile(self.filename + ".json")

    def __init__(self, value="record"):
        self.value = value

    def __setattr__(self, name, value):
        """x.__setattr__('name', value) <==> x.name = value"""
        object.__setattr__(self, name, value)
        if name == 'value':
            object.__setattr__(self, 'value', os.path.splitext(value)[0])
            if "/" in value:
                try:
                    if value[-37] != "/":
                        raise Exception
                    object.__setattr__(
                        self, 'id',
                        str(uuid.UUID(value[-36:].replace("/", "-"))))
                    object.__setattr__(self, 'folder', value[:-37])
                except:
                    folder, id = keysplit(value)
                    object.__setattr__(self, 'id', id)
                    object.__setattr__(self, 'folder', folder)
            else:
                try:
                    e = value.split(".")[-1]
                    if len(e) != 4:
                        raise Exception
                    i = int(e)
                    value = value[:-5]
                except:
                    pass
                u = str(uuid.uuid4())
                object.__setattr__(self, 'folder', value)
                object.__setattr__(self, 'id', u)
                object.__setattr__(self, 'value', "{}/{}".format(value, u))
        if name in ['folder', 'id', 'value']:
            object.__setattr__(
                self, 'filename',
                "/".join([
                    root, "data",
                    self.folder.replace('/', os.sep),
                    self.id.replace('-', '/')]))
            if self.folder == "template":
                try:
                    object.__setattr__(
                        self, 'filename',
                        max(glob(self.filename + ".*")))
                    object.__setattr__(
                        self, 'id',
                        self.id + self.filename[-5:])
                    object.__setattr__(
                        self, 'value',
                        "{}/{}".format(self.folder, self.id))
                except:
                    pass

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        return "Key(\"{}\")".format(self.value)

    def __str__(self):
        """x.__str__() <==> str(x)"""
        return self.value

    def jsonencode(self):
        """Returns a json representation of the object."""
        return {'__key__': self.value}

    def open(self):
        """Returns the Record for this key"""
        if self.value[-1] == "/":
            self.value = self.value[:-1]
        return Record(self.value)


class Search:
    """
    Search field wrapper.
    Strings wrapped with search will have their words stored in the
    search indices.
    """
    def __init__(self, value=None):
        self.value = value

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        return "Search(\"{}\")".format(self.value)

    def __str__(self):
        """x.__str__() <==> str(x)"""
        return str(self.value)

    def jsonencode(self):
        """Returns a json representation of the object."""
        return {'__search__': self.value}


class Validate:
    """
    Validate field wrapper.
    Provides validation features for the wrapped field.
    """
    @property
    def isValid(self):
        return validate(self.value, self.rule)

    def __init__(self, value=None, rule=""):
        self.value = value
        self.rule = rule

    def __repr__(self):
        return ("Validate({}, \"{}\")".format(str(self.value), self.rule))

    def __str__(self):
        """x.__str__() <==> str(x)"""
        return str(self.value)

    def jsonencode(self):
        """Returns a json representation of the object."""
        return {
            '__validate__': self.rule,
            'value': self.value}


def resolvealias(key):
    """
    If key is an alias then update to the linked record details.
    """
    assert os.path.abspath(key.filename).startswith(root)
    filename = key.filename + ".json"
    if os.path.islink(filename):
        object.__setattr__(
            key, 'filename', os.path.splitext(os.readlink(filename))[0])
        newkey = key.filename[len(root) + 1:].replace(os.sep, '/')
        object.__setattr__(key, 'value', newkey)
        f, id = keysplit(newkey)
        object.__setattr__(key, 'folder', f)
        object.__setattr__(key, 'id', id)


def storealias(key, alias):
    """
    Stores an alias for the given key.
    An alias is an alternate key which will refers to the same record.
    """
    if isinstance(alias, Key):
        alias = alias.value
    filename = savepath(Key(alias).filename + ".json")
    with filelock(filename):
        if os.path.islink(filename):
            os.remove(filename)
        os.symlink(key.filename + ".json", filename)


def init():
    """
    Initialise root database
    """
    # setup system records
    _search.save()
    # import schema.org
    schema = Record("imports/schema.org")
    if not schema.fields:
        schema.fields = requests.get("http://schema.rdfs.org/all.json").json()
    schema.save()
    r = Record("schema.org/meta")
    update = True
    if r.exists:
        if schema.fields['valid'] != r.fields['valid']:
            r.fields['valid'] = schema.fields['valid']
            r.save()
        else:
            update = False
    if update:
        for section in schema.fields:
            for datatype in schema.fields[section]:
                if section == 'valid':
                    continue
                key = "schema.org/" + schema.fields[section][datatype]['id']
                record = Record(key, indict=schema.fields[section][datatype])
                record.fields['id'] = \
                    Key("schema.org/" + str(record.fields['id'])).value
                for name in [
                        'supertypes',
                        'ancestors',
                        'subtypes',
                        'properties',
                        'specific_properties',
                        'domains',
                        'ranges']:
                    if name in record.fields:
                        record.fields[name] = [
                            Key("schema.org/" + a)
                            for a in record.fields[name]]
                if not isinstance(record.fields['label'], Search):
                    record.fields['label'] = Search(
                        record.fields['label'],
                        "schema.org")
                record.save()
                if 'ancestors' in record.fields and section.endswith('types'):
                    alias = "/".join(['menu', 'schema.org'] + [
                        titlespace(s.id) for s in record['ancestors']] + [
                        str(record['label'])])
                    storealias(record.key, alias)

    # import hydra-cg core
    hydra = Record("imports/hydra-cg.com/core")
    if not hydra.fields:
        url = "http://www.hydra-cg.com/spec/latest/core/core.jsonld"
        hydra.fields = requests.get(url).json()
    hydra.save()


# Hooks and Encoder for json

def loadhook(dct):
    if '__key__' in dct:
        return Key(dct['__key__'])
    elif '__validate__' in dct:
        return Validate(dct['value'], dct['__validate__'])
    elif '__access__' in dct:
        return Access(dct['value'], dct['__access__'])
    elif '__collect__' in dct:
        return Collect(dct['value'], dct['__collect__'])
    elif '__group__' in dct:
        return Group(dct['value'], dct['__group__'])
    elif '__index__' in dct:
        return Index(dct['value'], dct['__index__'])
    elif '__search__' in dct:
        return Search(dct['__search__'])
    elif '__include__' in dct:
        return Include(dct['__include__'])
    return dct


def includehook(dct):
    if '__include__' in dct:
        return Record(key=dct['__include__']).fields
    return loadhook(dct)


class Encoder(json.JSONEncoder):
    def default(self, item):
        try:
            return item.jsonencode()
        except:
            return json.JSONEncoder.default(self, item)

encoder = Encoder

_search=Record("system/search")
if not _search.exists:
    _search.fields.update(
        {
            'stemmer': "english",
            'cache': 0,
            'pathsplit': 3,
            'stopwords': sorted(['them', 'then', 'thei', 'she', 'what', 'would', 'own', 'no', 'either', 'off', 'wa', 'we', 'but', 'often', 'all', 'not', 'nor', 'where', 'should', 'abl', 'almost', 'get', 'on', 'of', 'onli', 'or', 'could', 'also', 'into', 'our', 'must', 'your', 'for', 'other', 'els', 'dear', 'most', 'and', 'some', 'do', 'ani', 'whom', 'among', 'thi', 'the', 'might', 'him', 'like', 'me', 'had', 'becaus', 'their', 'did', 'my', 'been', 'can', 'while', 'doe', 'why', 'ever', 'rather', 'too', 'neither', 'who', 'with', 'when', 'these', 'so', 'i', 'sinc', 'have', 'how', 'after', 'sai', 'u', 'you', 'ti', 'were', 'to', 'across', 'that', 'which', 'than', 'an', 'am', 'got', 'yet', 'ar', 'at', 'cannot', 'hi', 'he', 'howev', 'ha', 'from', 'let', 'mai', 'said', 'a', 'be', 'want', 'least', 'by', 'twa', 'it', 'her', 'there', 'just', 'if', 'everi', 'in', 'will']),
        }
    )

_stemmer = Stemmer(_search['stemmer'], _search['cache'])
