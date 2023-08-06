"""
Database exporters.
"""

import os
import re
import sys
import shutil
import codecs

from jinja2 import Environment, PackageLoader
from pkg_resources import resource_exists, resource_listdir, resource_filename

from util import make_directory
from config import config
import pkginfo
import flags


class Exporter(object):
    """
    Base class for database exporters.
    """

    #: Exporter name (for looking up templates).
    name = None

    def __init__(self, database):
        self.db = database

        # Set up Jinja templates and environment.
        templates = os.path.join('templates', self.name)
        self.loader = PackageLoader('ditz', templates)
        self.env = Environment(loader=self.loader,
                               trim_blocks=True, lstrip_blocks=True)

        # Add common filters.
        def issues(item):
            attr = item.__class__.__name__.lower()
            return [issue for issue in self.db.issues
                    if getattr(issue, attr) == item.name]

        rmap = {rel.name: rel for rel in self.db.project.releases}

        def release(issue):
            return rmap.get(issue.release, None)

        cmap = {comp.name: comp for comp in self.db.project.components}

        def component(issue):
            return cmap[issue.component]

        def dateformat(value, format="%Y-%m-%d"):
            return value.strftime(format)

        def timeformat(value, format="%Y-%m-%d %H:%M"):
            return value.strftime(format)

        self.addfilter(issues)
        self.addfilter(release)
        self.addfilter(component)
        self.addfilter(dateformat)
        self.addfilter(timeformat)

        self.setup()

    def setup(self):
        pass

    def addfilter(self, func):
        self.env.filters[func.func_name] = func

    def export(self, dirname):
        # Create output directory if required.
        make_directory(dirname)

        # Write files.
        self.write(dirname)

        # Copy static files, if any.
        static = os.path.join('static', self.name)
        if resource_exists(__name__, static):
            for name in resource_listdir(__name__, static):
                fname = os.path.join(static, name)
                src = resource_filename(__name__, fname)
                dst = os.path.join(dirname, name)
                shutil.copyfile(src, dst)

    def render(self, dirname, templatefile=None, targetfile=None,
               template=None, **kw):
        # Read template if required.
        if not template:
            template = self.env.get_template(templatefile)

        # Set target file if not specified.
        if not targetfile:
            targetfile = templatefile

        # Render template.
        text = template.render(version=pkginfo.__version__,
                               url=pkginfo.__url__,
                               **kw)

        # Write it to file.
        path = os.path.join(dirname, targetfile)
        with codecs.open(path, "w", encoding='utf-8') as fp:
            fp.write(text)

    def write(self, dirname):
        raise NotImplementedError


class HTMLExporter(Exporter):
    """
    A HTML database exporter.
    """

    name = 'html'

    def setup(self):
        def progressmeter(value, size=50):
            done = int(value * size)
            undone = max(0, size - done)
            return ("<span class='progress-meter'>" +
                    "<span class='progress-meter-done'>" +
                    ("&nbsp;" * done) +
                    "</span><span class='progress-meter-undone'>" +
                    ("&nbsp;" * undone) +
                    "</span></span>")

        def imagetag(issue, cls="inline-status-image"):
            if issue.status == flags.UNSTARTED:
                return ""

            text = flags.STATUS[issue.status]

            if issue.status == flags.CLOSED:
                text = flags.DISPOSITION[issue.disposition]

                if issue.disposition == flags.FIXED:
                    image = "green-check.png"
                elif issue.disposition == flags.WONTFIX:
                    image = "red-check.png"
                elif issue.disposition == flags.REORG:
                    image = "blue-check.png"
            elif issue.status == flags.IN_PROGRESS:
                image = "green-bar.png"
            elif issue.status == flags.PAUSED:
                image = "yellow-bar.png"

            return '<img class="%s" alt="%s" title="%s" src="%s">' % \
                   (cls, text, text, image)

        def sortkey(issue):
            text = issue.status
            if issue.closed:
                text += " " + issue.disposition
            return text

        def link(item, text=None, image=False, cls=None):
            if not item:
                return ""

            if not text:
                text = item.name

            filename = self.htmlfile(item)
            linktext = '<a href="%s">%s</a>' % (filename, text)

            if image:
                linktext += ' ' + imagetag(item)

            if cls:
                linktext = '<span class="%s">%s</span>' % (cls, linktext)

            return linktext

        idmap = {}
        for issue in self.db.issues:
            idmap[issue.id] = link(issue, image=True, cls="inline-issue-link")

        def addlinks(text):
            return self.db.convert_to_name(text, idmap)

        obscure = re.compile(r'(.+)@[\w.]+(.*)')

        def email(text):
            m = obscure.search(text)
            if m:
                return m.group(1) + '@...' + m.group(2)
            else:
                return text

        self.addfilter(link)
        self.addfilter(email)
        self.addfilter(sortkey)
        self.addfilter(addlinks)
        self.addfilter(imagetag)
        self.addfilter(progressmeter)

    def write(self, dirname):
        project = self.db.project
        showcomp = len(self.db.components) >= 2
        log = Logger()

        # Write index page.
        events = sorted(self.db.issue_events,
                        key=lambda x: x[0], reverse=True)

        log.start("Writing index page")

        count = config.getint('html', 'index_events')
        self.render(dirname, 'index.html', project=project,
                    issues=self.db.issues, activity=events[:count])

        log.finish()

        # Write a page for each release.
        log.start("Writing release pages")
        template = self.env.get_template("release.html")

        for rel in project.releases:
            path = self.htmlfile(rel)
            issues = [i for i in self.db.issues if i.release == rel.name]
            issues = sorted(issues, key=lambda x: x.creation_time)
            issues = list(reversed(issues))

            relevents = [e for e in events if e[4].release == rel.name]

            count = config.getint('html', 'release_events')
            self.render(dirname, template=template, targetfile=path,
                        project=project, release=rel, issues=issues,
                        activity=relevents[:count], show_components=showcomp)

        log.finish()

        # Write a page for each component.
        log.start("Writing component pages")
        template = self.env.get_template("component.html")

        for comp in project.components:
            path = self.htmlfile(comp)
            issues = [i for i in self.db.issues if i.component == comp.name]
            issues = sorted(issues, key=lambda x: x.creation_time)
            issues = list(reversed(issues))

            self.render(dirname, template=template, targetfile=path,
                        project=project, component=comp, issues=issues)

        log.finish()

        # Write a page for each issue.
        log.start("Writing issue pages")
        total = len(self.db.issues)
        template = self.env.get_template("issue.html")

        for num, issue in enumerate(self.db.issues, 1):
            log.percent(100.0 * num / total)
            path = self.htmlfile(issue)

            self.render(dirname, template=template, targetfile=path,
                        project=project, issue=issue)

        log.finish()

        # Write a page for unassigned issues.
        log.start("Writing unassigned issue page")
        issues = [i for i in self.db.issues if not i.release]
        issues = sorted(issues, key=lambda x: x.creation_time)
        issues = list(reversed(issues))

        self.render(dirname, 'unassigned.html', project=project,
                    issues=issues, show_components=showcomp)

        log.finish()

        # Write index file location.
        path = os.path.join(dirname, 'index.html')
        log.status("Local generated URL: file://%s" % os.path.abspath(path))

    def htmlfile(self, item):
        clsname = item.__class__.__name__
        name = getattr(item, "id", None) or getattr(item, "name")
        return "%s-%s.html" % (clsname.lower(), name)


class Logger(object):
    def __init__(self, stream=sys.stdout, dots="... "):
        self.stream = stream
        self.dots = dots

    def status(self, msg, newline=True):
        self.stream.write(msg + ("\n" if newline else ""))
        self.stream.flush()

    def start(self, msg):
        self.msg = msg

    def percent(self, value):
        self.status(self.msg + self.dots + ("%.0f%%" % value) + '\r', False)

    def finish(self):
        self.status(self.msg + self.dots + "done")
