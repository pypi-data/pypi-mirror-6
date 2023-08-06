"""
Internal Ditz objects.
"""

import os
import sys
import yaml
import hashlib
import random
import codecs
from datetime import datetime

from util import make_directory, check_value, DitzError
from flags import (STATUS, RELSTATUS, RELEASED, UNRELEASED, BUGFIX,
                   FEATURE, DISPOSITION, UNSTARTED, TYPE, SORT, CLOSED)


class DitzObject(yaml.YAMLObject):
    """
    Base class of a Ditz object appearing in a YAML file.

    Attributes:
        ditz_tag (str): Base YAML tag prefix.
        yaml_tag (str): YAML tag written to file.
        filename (str): YAML filename to read/write.
        attributes (list): List of recognized attributes.
        log_events (list): List of events.
    """

    yaml_loader = yaml.SafeLoader

    ditz_tag = "!ditz.rubyforge.org,2008-03-06"
    yaml_tag = None
    filename = None
    attributes = []

    def write(self, dirname="."):
        """
        Write object to its YAML file.

        Args:
            dirname (str, optional): Directory to write file into.
        """

        make_directory(dirname)
        path = os.path.join(dirname, self.filename)

        with codecs.open(path, "wb", encoding='utf-8') as fp:
            fp.write("--- ")
            write_yaml(self, fp)

    def event(self, username, text, comment=None, timestamp=None):
        """
        Add an event to the object's ``log_events`` list.

        Args:
            username (str): User name.
            text (str): Event description.
            comment (str, optional): User comment.
            timestamp (datetime, optional): Time of the event.
        """

        time = timestamp or datetime.now()
        self.log_events.append([time, username, text, comment or ""])

    def validate(self):
        """
        Check the object is a valid Ditz object.
        """

        events = getattr(self, "log_events", [])
        for num, data in enumerate(events, 1):
            if len(data) != 4:
                self._invalid("log_events entry %d has size %d instead of 4"
                              % (num, len(data)))

    def _invalid(self, msg):
        raise DitzError("%s: %s" % (self.filename, str(msg)))


class Project(DitzObject):
    yaml_tag = DitzObject.ditz_tag + '/project'
    filename = "project.yaml"
    attributes = ["name", "version", "components", "releases"]

    def __init__(self, name, version=0.5):
        self.name = name
        self.version = version
        self.components = [Component(name)]
        self.releases = []


class Release(DitzObject):
    yaml_tag = DitzObject.ditz_tag + '/release'
    attributes = ["name", "status", "release_time", "log_events"]

    def __init__(self, name, status=UNRELEASED, release_time=None):
        self.name = name
        self.status = status
        self.release_time = release_time
        self.log_events = []

        self.set_status(status)

    def set_status(self, status):
        check_value("status", status, RELSTATUS)
        self.status = status

    @property
    def released(self):
        return self.status == RELEASED

    def __repr__(self):
        return "<Release: %s>" % self.name


class Component(DitzObject):
    yaml_tag = DitzObject.ditz_tag + '/component'
    attributes = ["name"]

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Component: %s>" % self.name


class Issue(DitzObject):
    yaml_tag = DitzObject.ditz_tag + '/issue'
    template = "issue-%s.yaml"
    attributes = ["title", "desc", "type", "component", "release",
                  "reporter", "status", "disposition", "creation_time",
                  "references", "id", "log_events"]

    def __init__(self, title, desc="", type=BUGFIX, status=UNSTARTED,
                 disposition=None, creation_time=None, reporter=""):
        self.title = title.strip()
        self.desc = desc.strip()
        self.component = None
        self.release = None
        self.reporter = reporter

        self.set_type(type)
        self.set_status(status)
        self.set_disposition(disposition)

        self.creation_time = creation_time or datetime.now()
        self.id = self.make_id()

        self.references = []
        self.log_events = []

    @property
    def name(self):
        if self.type == BUGFIX:
            return self.title + " (bug)"
        elif self.type == FEATURE:
            return self.title + " (feature)"
        else:
            return self.title

    @property
    def closed(self):
        return self.status == CLOSED

    @property
    def filename(self):
        return self.template % self.id

    def set_type(self, type):
        check_value("type", type, TYPE)
        self.type = type

    def set_status(self, status):
        check_value("status", status, STATUS)
        self.status = status

    def set_disposition(self, disposition):
        if disposition:
            check_value("disposition", disposition, DISPOSITION)

        self.disposition = disposition

    def add_reference(self, reference):
        self.references.append(reference)
        return len(self.references)

    def grep(self, regexp):
        if regexp.search(self.title):
            return True

        if regexp.search(self.desc):
            return True

        for event in self.log_events:
            if regexp.search(event[3]):
                return True

        return False

    def make_id(self):
        strings = map(str, [self.creation_time, random.random(),
                            self.reporter, self.title, self.desc])
        return hashlib.sha1("\n".join(strings)).hexdigest()

    def __cmp__(self, other):
        if hasattr(other, "status"):
            val = cmp(SORT[self.status], SORT[other.status])
            if val:
                return val

        if hasattr(other, "creation_time"):
            return cmp(self.creation_time, other.creation_time)

        return 0

    def __repr__(self):
        return "<Issue: %s>" % self.id


class Config(DitzObject):
    yaml_tag = DitzObject.ditz_tag + '/config'
    filename = ".ditz-config"
    attributes = ["name", "email", "issue_dir"]

    def __init__(self, name, email, issue_dir="issues"):
        self.name = name
        self.email = email
        self.issue_dir = issue_dir

    @property
    def username(self):
        return "%s <%s>" % (self.name, self.email)

    def __repr__(self):
        return "<Config: %s>" % self.name


def write_yaml(item, fp=None, parent=None, level=0):
    """
    Write YAML data to a stream.
    """

    # This should be using PyYAML's write function, but I can't get it to
    # write things the way I want -- i.e., reproduce the format that
    # rubyditz uses.  And datetimes don't get written in a format that
    # rubyditz can read back again.  Sigh.

    # This function is ghastly and evil, and shouldn't exist.  But it gets
    # the job of roundtripping done.

    if fp is None:
        fp = sys.stdout

    value = unicode(item)
    tag = getattr(item, "yaml_tag", None)
    indent = "  "

    if tag:
        fp.write(tag + " \n")
        seenref = False
        for attr in item.attributes:
            if attr == "id" and not seenref:
                fp.write("\n")

            fp.write(indent * (level - 1))
            fp.write("%s: " % attr)
            obj = getattr(item, attr)

            if obj and attr == "references":
                seenref = True

            write_yaml(obj, fp, item, level + 1)
    elif isinstance(item, dict):
        if parent:
            fp.write("\n")

        for key, obj in sorted(item.items()):
            fp.write(indent * (level - 1))
            fp.write("%s: " % key)
            write_yaml(obj, fp, item, level + 1)
    elif isinstance(item, list):
        if len(item) > 0:
            newline = doindent = not isinstance(parent, list)

            # This is a gross hack.  Look away now.
            if isinstance(parent, DitzObject) and level > 1:
                level -= 1

            if newline:
                fp.write("\n")

            for obj in item:
                if doindent:
                    fp.write(indent * (level - 1))
                else:
                    doindent = True

                fp.write("- ")
                write_yaml(obj, fp, item, level + 1)
        else:
            fp.write("[]\n")
    elif isinstance(item, datetime):
        fp.write("%s Z\n" % str(item))
    elif "\n" in value:
        fp.write("|-\n")

        if isinstance(parent, list) and level > 1:
            level -= 1

        for line in value.split("\n"):
            fp.write(indent * level)
            fp.write(line + "\n")
    elif item is None:
        fp.write("\n")
    else:
        quote = False
        if not value:
            quote = True
        elif value[0] in '"{}[]':
            quote = True
        elif value[0] != ':' and ":" in value:
            quote = True
        else:
            try:
                float(value)
                quote = True
            except ValueError:
                pass

        if quote:
            value = '"' + value.replace('"', r'\"') + '"'

        fp.write(value + "\n")


def find_config(basedir=".", error=False):
    """
    Return a Ditz config file in or above a base directory.
    """

    basedir = os.path.realpath(basedir)
    filename = Config.filename
    curdir = basedir

    while True:
        path = os.path.join(curdir, filename)
        if os.path.exists(path):
            return path

        pardir = os.path.split(curdir)[0]
        if pardir == curdir:
            if error:
                raise DitzError("can't find '%s' in or above '%s'"
                                % (filename, basedir))
            else:
                return None

        curdir = pardir
