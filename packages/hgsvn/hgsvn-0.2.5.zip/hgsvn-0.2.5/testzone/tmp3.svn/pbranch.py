# pbranch.py - patch branches for Mercurial
#
# Copyright 2008 Peter Arrenbrecht <peter.arrenbrecht at gmail dot com>
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.

'''Patch Branches

This extension lets you develop patches collaboratively in special
topic branches of temporary clones of the main repository.

For more information:
http://www.selenic.com/mercurial/wiki/index.cgi/PatchBranches
'''

from mercurial.i18n import _
from mercurial.revlog import nullrev, nullid, short
from mercurial import util, commands, cmdutil, merge, hg, extensions, match
from mercurial import context
from mercurial import patch as _patch
from hgext import graphlog, patchbomb
import os, re, tempfile, sys, shlex

# work around hg 1.1 vs 1.2 incompatibility
try:
    from mercurial.error import RepoError #@UnusedImport
except:
    from mercurial.repo import RepoError #@UnresolvedImport @Reimport


BASENAME = '.%s'
INFOPATH = '.hgpatchinfo'
GRAPHPATH = 'pgraph'
DEPSPATH = os.path.join(INFOPATH, '%s.dep')
DESCPATH = os.path.join(INFOPATH, '%s.desc')

def updateto(ui, repo, branch):
    """update working copy to given branch"""
    if repo.dirstate.branch() != branch:
        ui.status(_("updating to %s\n" % branch))
        commands.update(ui, repo, branch)
        if repo.dirstate.branch() != branch:
            raise util.Abort(_('working copy not on branch %s') % branch)

def updatetonode(ui, repo, node):
    """update working copy to given node"""
    if repo.dirstate.parents()[0] != node:
        ui.status(_("updating to %s\n" % short(node)))
        commands.update(ui, repo, node)
        if repo.dirstate.parents()[0] != node:
            raise util.Abort(_('working copy not at %s') % short(node))

def commit(ui, repo, text, opts={}, files=None, patch=None):
    """commit with user/date as specified in opts

    If patch is set, do an in-memory commit of the dict {path: content} passed
    in files to the tip of the given patch.
    """
    date = opts.get('date')
    if date:
        date = util.parsedate(date)

    if patch:
        # files is {filename: content}
        def filectxfn(repo, ctx, path):
            return context.memfilectx(path, files[path], False, False, False)
        paths = [util.pconvert(p) for p in files.keys()]
        ctx = context.memctx(repo, (patch, None), text,
                             paths, filectxfn,
                             user=opts.get('user'), date=date,
                             extra={'branch': patch})
        node = repo.commitctx(ctx)
    else:
        # files is list
        if files:
            paths = [util.pconvert(p) for p in files]
            matcher = match.exact(repo.root, repo.getcwd(), paths)
        else:
            matcher = match.always(repo.root, repo.getcwd())
        node = repo.commit(match=matcher, text=text, user=opts.get('user'),
                           date=date)

    # FIXME refactor?
    # duplicate output from commands.commit()
    if not node:
        return
    cl = repo.changelog
    rev = cl.rev(node)
    parents = cl.parentrevs(rev)
    if rev - 1 in parents:
        # one of the parents was the old tip
        pass
    elif (parents == (nullrev, nullrev) or
          len(cl.heads(cl.node(parents[0]))) > 1 and
          (parents[1] == nullrev or len(cl.heads(cl.node(parents[1]))) > 1)):
        ui.status(_('created new head\n'))
    if ui.debugflag:
        ui.write(_('committed changeset %d:%s\n') % (rev,hex(node)))
    elif ui.verbose:
        ui.write(_('committed changeset %d:%s\n') % (rev,short(node)))

def needsmerge(repo, patch, dep):
    """return whether the patch needs a merge from the dependency"""
    try:
        patchrev = repo.lookup(patch)
        deprev = repo.lookup(dep)
    except:
        return True # either does not exist yet
    return deprev not in repo.changelog.reachable(patchrev, deprev)

def toposort(roots, connectedfunc, isreachablefunc):
    """return parents first

    connectedfunc(n) returns an iterable over the nodes connected
    to n.

    isreachablefunc(n, o) returns True iff o is reachable from n.
    """
    sorted = []
    seen = {}
    while roots:
        r = roots.pop(0)
        sorted.append(r)
        for c in connectedfunc(r):
            if c not in seen:
                isroot = True
                for o in roots:
                    if isreachablefunc(o, c):
                        isroot = False
                        break
                if isroot:
                    seen[c] = True
                    roots.append(c)
    return sorted

def octopusasciiedges(nodes, joinchar='\\'):
    """grapher for asciigraph on a list of nodes and their parents

    nodes must generate tuples (node, type, (char, lines), parents) where

     - parents must generate the parents of node, in sorted order,
     - char is the char to print as the node symbol, and
     - lines are the lines to display next to the node.

    Inserts artificial lines with joinchar as marker to make room
    when a node has >2 parents.
    """
    seen = []
    for node, type, (char, lines), parents in nodes:
        if node not in seen:
            seen.append(node)
        nodeidx = seen.index(node)

        knownparents = []
        newparents = []
        for parent in parents:
            if parent in seen:
                knownparents.append(parent)
            else:
                newparents.append(parent)

        ncols = len(seen)
        nextseen = seen[:]
        nextseen[nodeidx:nodeidx + 1] = newparents
        edges = [(nodeidx, nextseen.index(p)) for p in knownparents]

        while len(newparents) > 2:
            edges.append((nodeidx, nodeidx))
            edges.append((nodeidx, nodeidx + 1))
            nmorecols = +1
            yield (nodeidx, type, (char, lines), edges, ncols, nmorecols)
            char = joinchar
            lines = []
            seen = nextseen
            nodeidx += 1
            ncols += 1
            edges = []
            del newparents[0]

        if len(newparents) > 0:
            edges.append((nodeidx, nodeidx))
        if len(newparents) > 1:
            edges.append((nodeidx, nodeidx + 1))
        nmorecols = len(nextseen) - ncols
        seen = nextseen
        yield (nodeidx, type, (char, lines), edges, ncols, nmorecols)

class patchgraph(object):
    """manages a patch graph, caching dependency info"""

    def __init__(self, mgr):
        self.mgr = mgr
        self._nodes = []
        self._deps = {}
        self._fulldeps = {}
        self._messages = {}

    def aslist(self):
        return "\n".join(self.topolist()) + "\n"

    def astext(self, namesonly=False):
        desc = []
        for p in self.topolist():
            deps = self.deps(p)
            if deps:
                if namesonly:
                    desc.append(p)
                else:
                    desc.append("%s: %s" % (p, ", ".join(deps)))
        return "\n".join(desc) + "\n"

    def isnode(self, name):
        return name in self._deps

    def ensureisnode(self, name):
        if not self.isnode(name):
            self._isnonode(name)
        return name

    def _isnonode(self, name):
        raise util.Abort(_('branch %s is not in the patch graph') % (name))

    def isinner(self, name):
        return self._deps.get(name)

    def ensureisinner(self, name):
        self.ensureisnode(name)
        if not self.isinner(name):
            raise util.Abort(_('branch %s is a root in the patch graph (edit .hg/%s)') % (name, GRAPHPATH))
        return name

    def ispatch(self, name):
        return len(self._deps.get(name, [])) == 1

    def deps(self, name):
        return self._deps.get(name, [])

    def fulldeps(self, name):
        fulldeps = self._fulldeps.get(name)
        if fulldeps is None:
            deps = self.deps(name)
            fulldeps = set(deps)
            # assigning early avoids unbounded recursion with cycles
            self._fulldeps[name] = fulldeps
            for d in deps:
                for f in self.fulldeps(d):
                    if f == name:
                        raise util.Abort(_('patch dependency cycle detected involving %s and %s')
                                         % (name, d))
                    fulldeps.add(f)
        return fulldeps

    def message(self, name):
        msg = self._messages.get(name)
        if msg is None:
            msg = self._getmessage(name)
        return msg

    def _getmessage(self, name):
        return self.mgr.patchdesc(name)

    def ctx(self, name):
        return self.mgr.repo[name]

    def diffctx(self, name):
        self.ensureisinner(name)
        return (self.ctx(self.deps(name)[0]), self.ctx(name))

    def verify(self):
        """checks for cyclic dependencies"""
        for p in self._nodes:
            self.fulldeps(p)

    def topolist(self, names=None):
        """returns the dependency names in topological order (children first)"""
        if names is None:
            names = self._nodes
        alldeps = set([d for n in names for d in self.fulldeps(n)])
        roots = [n for n in names if n not in alldeps]
        empty = []
        def connfn(p): return self.deps(p) or empty
        def deepfn(p, o): return o in self.fulldeps(p)
        return toposort(roots, connfn, deepfn)

    def grapher(self, charfunc, linesfunc, names=None):
        """return grapher suitable for graphlog.ascii()"""
        def nodes():
            for name in self.topolist(names):
                parents = self.deps(name)
                yield (name,
                       graphlog.ASCIIDATA, (charfunc(name), linesfunc(name)),
                       parents)
        return octopusasciiedges(nodes())

    def pendingmerges(self, name):
        """return an iterator over the pending merges of the given node"""
        return self._checkheads(name, [])

    def _checkheads(self, name, through):
        repo = self.mgr.repo
        for dep in self.deps(name):
            # list (and process) earlier pending merges first
            for e in self._checkheads(dep, through + [dep]):
                yield e
            if needsmerge(repo, name, dep):
                yield (dep, through)

    def diff(self, patch, pats, opts):
        mgr = self.mgr
        repo = mgr.repo

        # find diff points
        predctx, thisctx = self.diffctx(patch)

        user = thisctx.user()
        date = thisctx.date()
        desc = self.message(patch) or ""

        # write patch header
        yield "# HG changeset patch\n"
        if user and not re.search("^# User ", desc):
            yield "# User %s\n" % user
        if date and not re.search("^# Date ", desc):
            yield "# Date %d %d\n" % util.parsedate(date)
        for l in desc.splitlines():
            yield "%s\n" % l
        yield "\n"

        # hide dates and state
        diffopts = opts.copy()
        diffopts["nodates"] = True
        diffopts["exclude"] = diffopts.get("exclude", []) + ["%s/" % repo.wjoin(INFOPATH)]

        # diff
        m = cmdutil.match(repo, pats, diffopts)
        for l in _patch.diff(repo, predctx.node(), thisctx.node(), match=m,
                             opts=_patch.diffopts(mgr.ui, diffopts)):
            yield l

    def diffopts(self, patch, opts):
        diffopts = opts.copy()

        # find diff points
        predctx, thisctx = self.diffctx(patch)
        diffopts["rev"] = ["%s:%s" % (predctx.rev(), thisctx.rev())]

        # hide state
        diffopts["exclude"] = diffopts.get("exclude", []) + ["%s/" % self.mgr.repo.wjoin(INFOPATH)]

        return diffopts

class desiredgraph(patchgraph):
    """manages the desired patch graph"""

    def __init__(self, mgr, desc):
        patchgraph.__init__(self, mgr)
        self._parse(desc)

    def _parse(self, desc):
        lines = (desc or "").splitlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            patch, rest = [e.strip() for e in line.split(':', 1)]
            deps = [d.strip() for d in rest.split(',')]
            self._nodes.append(patch)
            if len(deps) < 2:
                self._deps[patch] = deps
            else:
                base = BASENAME % patch
                self._nodes.append(base)
                self._deps[base] = deps
                self._deps[patch] = [base]

    def _isnonode(self, name):
        raise util.Abort(_('branch %s is not in the patch graph (edit .hg/%s)') % (name, GRAPHPATH))

    def pendingrebases(self, name, deps=None):
        deps = deps or self.deps(name)
        try:
            revmap = self.mgr.patchdeps(name)
        except RepoError:
            revmap = {}
        repo = self.mgr.repo
        for dep in deps:
            try:
                tip = repo[dep].hex()
            except RepoError:
                tip = "new"
            cur = revmap.get(dep)
            if cur != tip:
                yield dep

    def merge(self, leaves, opts):
        mgr = self.mgr
        ui = mgr.ui
        repo = mgr.repo

        # get list of branches to check; dependencies first
        names = self.topolist(leaves)
        names.reverse()

        branchtags = repo.branchtags()
        for name in names:
            if name in branchtags:
                deprevs = mgr.patchdeps(name)
            else:
                deprevs = {}

            depspath = DEPSPATH % name
            def writedeps():
                writeinfo(repo, depspath, "\n".join(deprevs.values()))

            def domerge(source, target, single, warn=""):
                sourcectx = repo[source]
                dir = repo.dirstate
                if dir.branch() == target and sourcectx.node() in dir.parents():
                    ui.status(_("%s: committing current merge from %s\n" % (target, source)))
                    mustcommit = True
                else:
                    updateto(ui, repo, target)
                    # hg merge source
                    ui.status(_("%s: merging from %s\n" % (target, source)))
                    stats = merge.update(repo, sourcectx.node(), True, False, False)
                    hg._showstats(repo, stats)
                    mustcommit = (stats[0] + stats[1] + stats[2] > 0
                                  or dir.parents()[1] != nullid)

                # check for unresolved conflicts
                ms = merge.mergestate(repo)
                unresolved = [f for f in ms if ms[f] == 'u']
                if len(unresolved) > 0:
                    raise util.Abort(_("use 'hg resolve' to handle unresolved file merges, then do 'hg pmerge' again\n%s" % warn))

                if mustcommit:
                    # record dep
                    if single:
                        deprevs.clear()
                    deprevs[source] = sourcectx.hex()
                    writedeps()
                    commit(ui, repo, "merge of %s" % source, opts)

            def domergeheads(sourcenode, targetnode):
                sourcectx = repo[sourcenode]
                targetctx = repo[targetnode]
                dir = repo.dirstate
                pars = dir.parents()
                if sourcectx.node() in pars and targetctx.node() in pars:
                    ui.status(_("%s: committing current merge from %s\n" % (targetctx.branch(), short(sourcectx.node()))))
                else:
                    updatetonode(ui, repo, targetctx.node())
                    ui.status(_("%s: merging from alternate head %s\n" % (targetctx.branch(), short(sourcectx.node()))))
                    stats = merge.update(repo, sourcectx.node(), True, False, False)
                    hg._showstats(repo, stats)
                ms = merge.mergestate(repo)
                unresolved = [f for f in ms if ms[f] == 'u']
                if unresolved == [depspath]:
                    ui.status(_("%s: resolving %s\n" % (targetctx.branch(), depspath)))
                    writedeps()
                    ms.mark(depspath, 'r')
                    unresolved = []
                if unresolved:
                    raise util.Abort(_("use 'hg resolve' to retry unresolved file merges, then do 'hg pmerge' again\n"))
                commit(ui, repo, "merge of alternate head %s" % sourcectx.hex(), opts)

            deps = self.deps(name)
            sources = [dep for dep in deps if needsmerge(repo, name, dep)]
            warn = _('problem merging dependencies; not compatible?\n')
            if sources:
                if len(deps) == 1:
                    domerge(deps[0], name, single=True)
                elif name not in branchtags:
                    # create base first time
                    first = deps[0]
                    ui.status(_("updating to %s\n" % first))
                    commands.update(ui, repo, first)
                    commands.branch(ui, repo, name)
                    deprevs[first] = repo[first].hex()
                    writedeps()
                    commit(ui, repo, "update patch dependencies", opts)
                    for source in deps[1:]:
                        domerge(source, name, single=False, warn=warn)
                else:
                    # exists, merge all pending deps
                    for source in sources:
                        domerge(source, name, single=False, warn=warn)

            # merge multiple branch heads
            # We do this after merging the bases because the bases may already
            # contain merges that resolve our conflicts.
            mainheadnode = repo[name].node()
            for otherheadnode in repo.branchheads(name):
                if otherheadnode != mainheadnode:
                    domergeheads(otherheadnode, mainheadnode)

            newdeps = False
            for dep in deps:
                if dep not in sources:
                    rev = repo[dep].hex()
                    if deprevs.get(dep) != rev:
                        deprevs[dep] = rev
                        newdeps = True
            for dep in [d for d in deprevs]:
                if dep not in deps:
                    del deprevs[dep]
                    newdeps = True
            if newdeps:
                updateto(ui, repo, name)
                ui.status(_("%s: updating dependencies\n" % name))
                writedeps()
                commit(ui, repo, "update patch dependencies", opts)

class graphatrev(patchgraph):
    """manages the patch graph as defined by a given starting rev"""

    def __init__(self, mgr, revid='.'):
        patchgraph.__init__(self, mgr)
        self._noderevs = {}
        self._loadfrom(revid)

    def _loadfrom(self, revid):
        name = self.mgr.repo[revid].branch()
        self._nodes.append(name)
        self._noderevs[name] = revid
        revs = self.mgr.patchdeprevs(name, revid)
        self._deps[name] = [self._loadfrom(rev) for rev in revs]
        return name

    def _getmessage(self, name):
        if name in self._noderevs:
            return self.mgr.patchdesc(name, self._noderevs[name])
        return None

    def ctx(self, name):
        return self.mgr.repo[self._noderevs[name]]

    def _isnonode(self, name):
        raise util.Abort(_('branch %s is not in the patch graph (maybe update to it, or use --tips?)') % (name))

class graphattips(patchgraph):
    """manages the patch graph as defined by the tips of the branches"""

    def __init__(self, mgr):
        patchgraph.__init__(self, mgr)
        repo = mgr.repo
        for b, headrev in repo.branchtags().iteritems():
            if 'close' not in repo.changelog.read(headrev)[5]:
                self._loadfrom(b, needed=False)

    def _loadfrom(self, revid, needed):
        name = self.mgr.repo[revid].branch()
        if name not in self._nodes:
            revs = self.mgr.patchdeprevs(name)
            if needed or revs:
                self._nodes.append(name)
                self._deps[name] = [self._loadfrom(rev, needed=True)
                                    for rev in revs]
        return name

    def _isnonode(self, name):
        raise util.Abort(_('branch %s is not in the patch graph (maybe need to pmerge?)') % (name))

def isinternal(name):
    return name.startswith('.')

class patchonlygraph(patchgraph):

    def __init__(self, mgr, graph):
        patchgraph.__init__(self, mgr)
        self.graph = graph
        self._loadfrom(graph)

    def _loadfrom(self, graph):
        for name in graph.topolist():
            if not isinternal(name):
                deps = graph.deps(name)
                if deps and isinternal(deps[0]):
                    deps = graph.deps(deps[0])
                self._nodes.append(name)
                self._deps[name] = deps

def catfile(path):
    if not os.path.exists(path):
        return None
    f = file(path, "r")
    try:
        return f.read()
    finally:
        f.close()

def writefile(path, text):
    f = file(path, "w")
    try:
        f.write(text)
    finally:
        f.close()

def catinfo(ctx, path):
    """return data from a patch info file as committed in the given context"""
    p = util.pconvert(path)
    if p in ctx.manifest():
        return ctx[p].data()
    return None

def writeinfo(repo, path, text):
    """write data to a patch info file to be committed in the given context"""
    f = repo.wopener(path, 'w')
    if text:
        f.write(text)
    f.close()
    if repo.dirstate[path] not in 'amn':
        repo.add([util.pconvert(path)])

# FIXME memoize some things later
class patchmanager:

    def __init__(self, ui, repo, opts):
        self.ui = ui
        self.repo = repo

    def currpatch(self):
        return self.repo.dirstate.branch()

    def _patchinfo(self, name, rev, path):
        ctx = self.repo[rev or name]
        return catinfo(ctx, path % name)

    def patchdesc(self, name, rev=None):
        return self._patchinfo(name, rev, DESCPATH)

    def updatepatchdesc(self, name, newtext, opts):
        if newtext != self.patchdesc(name):
            path = DESCPATH % name
            if name == self.currpatch():
                writeinfo(self.repo, path, newtext)
                commit(self.ui, self.repo, "update patch description", opts,
                       files=[path])
            else:
                commit(self.ui, self.repo, "update patch description", opts,
                       files={path: newtext}, patch=name)

    def patchdeprevs(self, name, rev=None):
        return (self._patchinfo(name, rev, DEPSPATH) or "").splitlines()

    def patchdeps(self, name, rev=None):
        revs = self.patchdeprevs(name, rev)
        deps = {}
        for r in revs:
            deps[self.repo[r].branch()] = r
        return deps

    def graphdescpath(self, name=GRAPHPATH):
        return self.repo.join(name)

    def hasgraphdesc(self):
        return os.path.exists(self.graphdescpath())

    def graphdesc(self):
        path = self.graphdescpath()
        if os.path.exists(path):
            return catfile(path)
        oldpath = self.graphdescpath("patchgraph")
        if os.path.exists(oldpath):
            self.ui.status(_("renamed .hg/patchgraph to .hg/pgraph\n"))
            os.rename(oldpath, path)
        return catfile(path)

    def updategraphdesc(self, newtext):
        if newtext != self.graphdesc():
            writefile(self.graphdescpath(), newtext)

    def creategraphdesc(self):
        graph = self.patchonlygraph(self.graphattips())
        desc = graph.astext()
        if desc.strip():
            writefile(self.graphdescpath(), desc)
            return desc
        return ''

    def desiredgraph(self):
        desc = self.graphdesc()
        if desc is None:
            desc = self.creategraphdesc()
            if desc:
                self.ui.status(_("created graph description from current tips\n"))
        return desiredgraph(self, desc)

    def graphatrev(self, revid='.'):
        return graphatrev(self, revid)

    def graphattips(self):
        return graphattips(self)

    def graphforopts(self, opts, default='d'):
        desired = opts.get('desired')
        atrev = opts.get('rev')
        tips = opts.get('tips')
        if (desired and 1 or 0) + (atrev and 1 or 0) + (tips and 1 or 0) > 1:
            raise util.Abort(_('--tips, --rev, and --desired are incompatible'))
        if tips:
            return self.graphattips()
        elif atrev:
            return self.graphatrev(atrev)
        elif desired:
            return self.desiredgraph()
        elif default == 'r':
            return self.graphatrev()
        else:
            return self.desiredgraph()

    def patchonlygraph(self, graph):
        return patchonlygraph(self, graph)

def edittext(ui, repo, oldtext, opts):
    # run editor in the repository root
    text = opts.get('text')
    if text:
        return text
    if opts.get('stdin'):
        return sys.stdin.read()
    olddir = os.getcwd()
    os.chdir(repo.root)
    try:
        return ui.edit(oldtext or "", opts.get('user'))
    finally:
        os.chdir(olddir)

def cmdnew(ui, repo, patch, **opts):
    """start a new patch branch

    Starts a new branch called PATCHNAME based on the current branch.
    Adds the branch to the patch graph as a new line.

    If there are pending changes, you can use -p/--preserve to carry them
    over to the new branch uncommitted.

    If --text or --stdin is supplied, creates and commits the patch
    message in the same commit.
    """
    mgr = patchmanager(ui, repo, opts)
    base = repo['.']
    files = []

    # handle patch message
    if opts.get("text") or opts.get("stdin"):
        newtext = edittext(ui, repo, "", opts)
        descfile = DESCPATH % patch
        writeinfo(repo, descfile, newtext)
        files.append(descfile)

    # add to patch graph
    descpath = mgr.graphdescpath()
    desc = catfile(descpath) or ''
    if desc and not desc.endswith('\n'):
        desc += '\n'
    writefile(descpath, "%s%s: %s\n" % (desc, patch, base.branch()))

    # update deps
    depsfile = DEPSPATH % patch
    writeinfo(repo, depsfile, base.hex())
    files.append(depsfile)

    # commit to new branch
    commands.branch(ui, repo, patch)
    if not opts.get("preserve"):
        files=None
    commit(ui, repo, "start new patch on %s" % base.branch(), opts, files=files)

def cmdprintgraph(ui, repo, *patches, **opts):
    """print an ASCII art rendering of the patch dependency graph

    If you provide a list of patch names, only they and their direct
    dependencies are printed.
    """
    mgr = patchmanager(ui, repo, opts)
    graph = mgr.graphforopts(opts)

    if opts.get("as_list"):
        ui.write(graph.aslist())
        return

    if opts.get("as_text"):
        ui.write(graph.astext(ui.quiet))
        return

    currbranch = repo['.'].branch()
    def charfunc(patch):
        if patch == currbranch:
            return '@'
        return 'o'
    if opts.get('status'):
        def linesfunc(patch):
            if not graph.ispatch(patch):
                return [patch]
            ui.pushbuffer()
            cmdstatus(ui, repo, patch)
            status = ui.popbuffer().split("\n")[:-1]
            return [patch] + [" * %s" % s for s in status]
    elif opts.get('message'):
        withname = opts.get('with_name')
        def linesfunc(patch):
            msg = (graph.message(patch) or "\n").splitlines()
            if withname:
                msg[0] = "[%s] %s" % (patch, msg[0])
            return msg + ['']
    elif opts.get('title'):
        withname = opts.get('with_name')
        def linesfunc(patch):
            title = (graph.message(patch) or "\n").splitlines()[0]
            if withname:
                return ["[%s] %s" % (patch, title)]
            return [title]
    elif ui.verbose:
        def linesfunc(patch): return ["%s@%s" % (patch, graph.ctx(patch).rev())]
    else:
        def linesfunc(patch): return [patch]
    if not patches:
        patches = None

    visgraph = opts.get('full') and graph or mgr.patchonlygraph(graph)
    grapher = visgraph.grapher(charfunc=charfunc, linesfunc=linesfunc, names=patches)
    graphlog.ascii(ui, grapher)

def cmdeditmessage(ui, repo, *patches, **opts):
    """edit the patch message"""
    mgr = patchmanager(ui, repo, opts)
    if patches:
        patch = patches[0]
    else:
        patch = mgr.currpatch()
    newtext = edittext(ui, repo, mgr.patchdesc(patch), opts)
    mgr.updatepatchdesc(patch, newtext, opts)

def cmdprintmessage(ui, repo, *patches, **opts):
    """print the patch message(s)"""
    mgr = patchmanager(ui, repo, opts)
    if not patches:
        patches = [mgr.currpatch()]
    for p in patches:
        ui.write("%s:\n%s\n" % (p, mgr.patchdesc(p)))

def cmddiff(ui, repo, *pats, **opts):
    """prints the final diff for the current or given patch branch

    The diff is written in a format suitable for 'hg import'.
    Uses the current patch description, and the user and date of
    the last commit in the patch branch (unless overridden in the
    patch description using '# User' and '# Date').
    """
    mgr = patchmanager(ui, repo, opts)
    graph = mgr.graphforopts(opts, 'r')
    if pats:
        patch = pats[0]
        pats = pats[1:]
    else:
        patch = mgr.currpatch()
    for l in graph.diff(patch, pats, opts):
        ui.write("%s" % l)

def cmdextdiff(ui, repo, extdiff, *pats, **opts):
    """combines pdiff and extdiff

    See `hg help pdiff` and `hg help extdiff` for details.
    """
    mgr = patchmanager(ui, repo, opts)
    graph = mgr.graphforopts(opts, 'r')
    del opts['rev']
    del opts['tips']
    if pats:
        patch = pats[0]
        pats = pats[1:]
    else:
        patch = mgr.currpatch()
    opts = graph.diffopts(patch, opts)
    extdiff(ui, repo, *pats, **opts)

def rstriplf(s):
    if s and s.endswith("\n"):
        return s[:-1]
    return s

def diffstoexport(ui, repo, patches, opts):
    mgr = patchmanager(ui, repo, opts)
    graph = mgr.graphforopts(opts, 'r')
    if not patches:
        patches = None
    if opts.get("with_deps") or not patches:
        patches = [p for p in graph.topolist(patches) if graph.ispatch(p)]
        patches.reverse()
    diffs = [[rstriplf(l) for l in graph.diff(p, [], opts)] for p in patches]
    if not diffs:
        raise util.Abort(_('no patches to export'))
    return patches, diffs

def cmdemail(ui, repo, *patches, **opts):
    """send patches by email

    Sends the named patches (or else all patches) by email, using the
    `hg email` command. Needs the patchbomb extension to be present to work.

    See `hg help email` for details on the email sending options.
    """
    patches, diffs = diffstoexport(ui, repo, patches, opts)
    opts['patches'] = diffs
    opts['patchnames'] = patches
    return patchbomb.patchbomb(ui, repo, **opts)

def cmdexport(ui, repo, *patches, **opts):
    """exports patches

    Exports the named patches (or else all patches) like `hg export`.

    If --queue is given, exports to .hg/patches, or the given target dir.
    Overwrites .hg/patches/series, unless --no-series is given. The target
    dir is created if it does not exist.
    """
    patches, diffs = diffstoexport(ui, repo, patches, opts)
    if opts.get('queue'):
        tgt = opts.get('target_dir')
        if not tgt:
            tgt = repo.join('patches')
        if not os.path.exists(tgt):
            os.mkdir(tgt)
            ui.note("%s created\n" % tgt)
        opener = util.opener(tgt)
        ext = opts.get("ext") or ""
        if not opts.get('no_series'):
            series = opener('series', 'w')
            try:
                for p in patches:
                    series.write("%s\n" % (p + ext))
            finally:
                series.close()
        for p, d in zip(patches, diffs):
            f = opener(p + ext, 'w')
            try:
                for l in d:
                    f.write("%s\n" % l)
            finally:
                f.close()
    else:
        for d in diffs:
            for l in d:
                ui.write("%s\n" % l)
            ui.write("\n")

def cmdstatus(ui, repo, *patches, **opts):
    """print status of current (or given) patch branch
    """
    mgr = patchmanager(ui, repo, opts)
    graph = mgr.desiredgraph()
    if not patches:
        patches = [mgr.currpatch()]
    havepending = False
    for patch in patches:
        heads = repo.branchheads(patch)
        if len(heads) > 1:
            ui.status(_('needs merge of %i heads\n') % len(heads))
            havepending = True
        for dep, through in graph.pendingmerges(patch):
            if through:
                ui.status(_('needs merge with %s (through %s)\n') %
                          (dep, ", ".join(through)))
            else:
                ui.status(_('needs merge with %s\n') % dep)
            havepending = True
        for dep in graph.pendingrebases(patch):
            ui.status(_('needs update of diff base to tip of %s\n') % dep)
            havepending = True
    return havepending

def wrappull(origfn, ui, repo, *args, **opts):
    if not os.path.exists(repo.join(GRAPHPATH)):
        return origfn(ui, repo, *args, **opts)
    pg = patchmanager(ui, repo, {})
    pre = pg.graphattips().astext()
    res = origfn(ui, repo, *args, **opts)
    post = pg.graphattips().astext()
    if pre != post:
        ui.status(_("inferred graph has changed; use 'hg pgraph --tips' to view\n"))
    return res

def wrapupdate(origfn, ui, repo, *args, **opts):
    if not os.path.exists(repo.join(GRAPHPATH)):
        return origfn(ui, repo, *args, **opts)
    res = origfn(ui, repo, *args, **opts)
    if cmdstatus(ui, repo):
        ui.status(_("use 'hg pmerge'\n"))
    return res

def cmdmerge(ui, repo, *patches, **opts):
    """merge pending heads from dependencies into patch branches

    Pending heads occur when you commit to a dependency. It creates a new head
    that must be merged into dependent patches.

    This command merges pending heads from dependencies into dependent patches.
    It recursively descends into dependencies, and stops on merge conflicts.
    When this happens, fix the merge, commit, and run pmerge again.

    This command always processes the selected patch(es) and their dependencies
    (transitive). With --all, all patches are selected. Otherwise, if none are
    specified explicitly, the current patch is selected.
    """
    mgr = patchmanager(ui, repo, opts)
    graph = mgr.desiredgraph()
    if opts.get('all'):
        patches = None
    elif not patches:
        patches = [mgr.currpatch()]
    graph.merge(patches, opts)

def cmdbackout(ui, repo, *pats, **opts):
    """backs out the current patch branch (undoes all its changes)

    This commits a new changeset that undoes all of the changes
    introduced by the patch. This is similar to 'hg backout', but
    backs out an entire patch.

    Use this to delete patches: backout and merge the backout to
    children, then rebase the children and delete the patch.
    """
    mgr = patchmanager(ui, repo, opts)
    patch = mgr.currpatch()
    graph = mgr.graphatrev()
    basectx, thisctx = graph.diffctx(patch)
    ui.status(_('backing out to %s\n') % basectx.branch())

    tempname = tempfile.mktemp('-backout.diff')
    try:

        # diff
        diffopts = {'exclude': (opts.get('exclude') or []) + ["%s/" % INFOPATH],
                    'include': opts.get('include') or [],
                    'git':True,
                    'nodates':True}
        m = cmdutil.match(repo, pats, diffopts)
        diff = _patch.diff(repo, thisctx.node(), basectx.node(), match=m,
                           opts=_patch.diffopts(ui, diffopts))
        temp = file(tempname, 'w')
        try:
            for l in diff: temp.write(l)
        finally:
            temp.close()

        # patch
        files = {}
        _patch.patch(tempname, ui, strip=1, cwd=repo.root, files=files)
        files = _patch.updatedir(ui, repo, files)

    finally:
        try: os.unlink(tempname)
        except: pass

    # commit
    commit(ui, repo, 'backout patch branch %s' % patch, opts)


# FIXME
# - support rev range
# - support copies
# - support modes
# - support walk opts
# - consider applying reverse diff, then update back to get 3-way-merge
def cmdreapply(ui, repo, rev, **opts):
    """reverts the working copy of all files touched by REV to REV

    Use this to backport part of a changeset to a dependency. First,
    reapply the changeset, then remove everything that does not belong
    into the dependency again. Then commit and pmerge to dependents.
    """
    node = repo.lookup(rev)
    bcx = repo[node]
    for f in bcx.files():
        bf = bcx[f]
        if f in bcx:
            ui.note("copying %s\n" % f)
            wf = repo.wopener(bf.path(), "w")
            wf.write(bf.data())
            wf.close()
        else:
            ui.note("deleting %s\n" % f)
            util.unlink(repo.wjoin(bf.path()))


def noshortopts(opts, only=''):
    def noshort(short):
        if only and short not in only:
            return short
        return ''
    return [(noshort(short), full, val, desc) for (short, full, val, desc) in opts]

graphopts = [
          ('r', 'rev', '', _('show local graph for this revision')),
          ('', 'tips', None, _('show graph defined by branch tips')),
             ]

graphoptsdes = graphopts + [
          ('', 'desired', None, _('show graph defined by .hg/pgraph file')),
             ]

cmdtable = {

    "^pnew":
        (cmdnew,
         [('t', 'text', '', _('text of patch message')),
          ('p', 'preserve', None, _('preserve pending changes in working copy')),
          ('', 'stdin', None, _('read the patch message from stdin')),
         ] + commands.commitopts2,
         _('hg pnew [OPTION]... PATCHNAME')),

    "^pgraph":
        (cmdprintgraph,
         [('s', 'status', None, _('show status')),
          ('m', 'message', None, _('show patch message')),
          ('t', 'title', None, _('show first line of patch message')),
          ('n', 'with-name', None, _('prepend title with [patch name]')),
          ('', 'full', None, _('show graph including internal diff base branches')),
          ('', 'as-text', None, _('show graph as text like in .hg/pgraph')),
          ('', 'as-list', None, _('show only patch and base names')),
         ] + graphopts,
         _('hg pgraph [OPTION]... [PATCH]...')),

    "^peditmessage|pemsg":
        (cmdeditmessage,
         [('t', 'text', '', _('text of message')),
          ('', 'stdin', None, _('read the message from stdin')),
          ('m', 'message', _('updated'), _('commit message')),
         ] + commands.commitopts2,
         _('hg peditmessage [OPTION]... [PATCH]')),

    "^pmessage":
        (cmdprintmessage,
         [('t', 'title', None, _('show first line of patch message')),
          ('n', 'with-name', None, _('prepend title with [patch name]')),
         ],
         _('hg pmessage [OPTION]... [PATCH]...')),

    "^pstatus":
        (cmdstatus,
         [
         ],
         _('hg pstatus [OPTION]... [PATCH]...')),

    "^pmerge":
        (cmdmerge,
         [('a', 'all', None, _('merge in all patches')),
         ] + commands.commitopts2,
         _('hg pmerge [OPTION]... [PATCH]...')),

    "^pdiff":
        (cmddiff,
         [] + graphoptsdes + commands.diffopts + commands.diffopts2 + commands.walkopts,
         _('hg pdiff [OPTION]... [PATCH] [FILE]...')),

    "^pemail":
        (cmdemail,
         [('d', 'with-deps', None, _('send recursive dependencies too')),
         ] + graphoptsdes + noshortopts(patchbomb.emailopts, 'd') + noshortopts(commands.diffopts + commands.diffopts2),
         _('hg pemail [OPTION]... [PATCH]...')),

    "^pexport":
        (cmdexport,
         [('d', 'with-deps', None, _('send recursive dependencies too')),
          ('', 'queue', None, _('export to queue dir (.hg/patches)')),
          ('', 'target-dir', '', _('target queue dir')),
          ('', 'ext', '', _('patch file extension')),
         ] + graphoptsdes + noshortopts(commands.diffopts + commands.diffopts2, 'dq'),
         _('hg pexport [OPTION]... [PATCH]...')),

    "pbackout":
        (cmdbackout,
         [
         ] + commands.walkopts + commands.commitopts2,
         _('hg pbackout [OPTION]... [FILE]...')),

    "reapply":
        (cmdreapply,
         [
         ],
         _('hg reapply REV')),

    }

def uisetup(ui):

    try:
        hgcolor = extensions.find('color')
        _setupcmd, colordiff, _diff_effects = \
            hgcolor._setupcmd, hgcolor.colordiff, hgcolor._diff_effects
        _setupcmd(ui, 'pdiff', cmdtable, colordiff, _diff_effects)
        _setupcmd(ui, 'pexport', cmdtable, colordiff, _diff_effects)
    except:
        pass

    try:
        hgextdiff = extensions.find('extdiff')
        extdiff, dodiff, extdiffcmds = \
            hgextdiff.extdiff, hgextdiff.dodiff, hgextdiff.cmdtable
        def innerextdiff(ui, repo, *pats, **opts):
            return cmdextdiff(ui, repo, extdiff, *pats, **opts)
        innerextdiff.__doc__ = cmdextdiff.__doc__
        extdiffcmd = extdiffcmds['extdiff']
        extdiffopts = extdiffcmd[1][0:2] # -p and -o
        pdiffcmd = cmdtable['^pdiff']
        pdiffopts = pdiffcmd[1][0:2] # --tips and --rev
        cmdtable['pextdiff'] = (innerextdiff,
                                extdiffopts + pdiffopts + commands.walkopts,
                                _('hg pextdiff [OPTION]... [PATCH] [FILE]...'))

        # add custom commands (copied from extdiff.py)
        for cmd, path in ui.configitems('extdiff'):
            if cmd.startswith('cmd.'):
                cmd = cmd[4:]
                if not path: path = cmd
                diffopts = ui.config('extdiff', 'opts.' + cmd, '')
                diffopts = diffopts and [diffopts] or []
            elif cmd.startswith('opts.'):
                continue
            else:
                # command = path opts
                if path:
                    diffopts = shlex.split(path)
                    path = diffopts.pop(0)
                else:
                    path, diffopts = cmd, []
            def save(cmd, path, diffopts):
                '''use closure to save diff command to use'''
                def differ(ui, repo, *pats, **opts):
                    return dodiff(ui, repo, path, diffopts, pats, opts)
                def mydiff(ui, repo, *pats, **opts):
                    return cmdextdiff(ui, repo, differ, *pats, **opts)
                mydiff.__doc__ = '''use %(path)s to view patch

    See `hg help pdiff` and `hg help extdiff` for details.''' % {
                    'path': util.uirepr(path),
                    }
                return mydiff
            name = 'p%s' % cmd
            cmdtable[name] = (save(cmd, path, diffopts),
                             pdiffopts + commands.walkopts,
                             _('hg %s [OPTION]... [PATCH] [FILE]...') % name)

    except:
        pass

extensions.wrapcommand(commands.table, "update", wrapupdate)
extensions.wrapcommand(commands.table, "pull", wrappull)
