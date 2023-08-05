# Copyright (c) 2009-2012 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Qt4 high level widgets for hg repo changelogs and filelogs
"""
import difflib
from itertools import imap

try:
    from mercurial.error import LookupError as HgLookupError
except ImportError:
    from mercurial.revlog import LookupError as HgLookupError

from PyQt4 import QtCore, QtGui, Qsci
from PyQt4.QtCore import Qt, pyqtSignal

from hgviewlib.util import exec_flag_changed, isbfile, bfilepath, tounicode
from hgviewlib.config import HgConfig

from hgviewlib.qt4 import icon as geticon
from hgviewlib.qt4.hgfiledialog import FileViewer, FileDiffViewer
from hgviewlib.qt4.lexers import get_lexer
from hgviewlib.qt4.blockmatcher import BlockList

qsci = Qsci.QsciScintilla

class Annotator(qsci):
    # we use a QScintilla for the annotator cause it makes
    # it much easier to keep the text area and the annotator sync
    # (same font rendering etc). However, it have the drawback of making much
    # more difficult to implement things like QTextBrowser.anchorClicked, which
    # would have been nice to directly go to the annotated revision...
    def __init__(self, textarea, parent=None):
        qsci.__init__(self, parent)

        self.setFrameStyle(0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setReadOnly(True)
        self.sizePolicy().setControlType(QtGui.QSizePolicy.Slider)
        self.setMinimumWidth(20)
        self.setMaximumWidth(40) # XXX TODO make this computed
        self.setFont(textarea.font())
        self.setMarginWidth(0, '')
        self.setMarginWidth(1, '')

        self.SendScintilla(qsci.SCI_SETCURSOR, 2)
        self.SendScintilla(qsci.SCI_SETCARETSTYLE, 0)

        # used to set a background color for every annotating rev
        N = 32
        self.markers = []
        for i in range(N):
            marker = self.markerDefine(qsci.Background)
            color = 0x7FFF00 + (i-N/2)*256/N*256*256 - i*256/N*256 + i*256/N
            self.SendScintilla(qsci.SCI_MARKERSETBACK, marker, color)
            self.markers.append(marker)

        textarea.verticalScrollBar().valueChanged[int].connect(
                self.verticalScrollBar().setValue)

    def setFilectx(self, fctx):
        ann = [f.rev() for f, __ in fctx.annotate(follow=True)]
        self.setText('\n'.join(imap(str, ann)))
        allrevs = list(sorted(set(ann)))
        for i, rev in enumerate(ann):
            idx = allrevs.index(rev)
            self.markerAdd(i, self.markers[idx % len(self.markers)])


class HgQsci(qsci):

    def __init__(self, *args, **kwargs):
        super(HgQsci, self).__init__(*args, **kwargs)
        super(HgQsci, self).setUtf8(True)
        self.actions = {}
        self.createActions()
        self.setFrameStyle(0)

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setReadOnly(True)

        self.SendScintilla(qsci.SCI_SETCARETSTYLE, 0)

        # margin 1 is used for line numbers
        self.setMarginLineNumbers(1, True)
        self.setMarginWidth(1, '000')

        self.SendScintilla(qsci.SCI_INDICSETSTYLE, 8, qsci.INDIC_ROUNDBOX)
        self.SendScintilla(qsci.SCI_INDICSETUNDER, 8, True)
        self.SendScintilla(qsci.SCI_INDICSETFORE, 8, 0xBBFFFF)
        self.SendScintilla(qsci.SCI_INDICSETSTYLE, 9, qsci.INDIC_ROUNDBOX)
        self.SendScintilla(qsci.SCI_INDICSETUNDER, 9, True)
        self.SendScintilla(qsci.SCI_INDICSETFORE, 9, 0x58A8FF)

        # hide margin 0 (markers)
        self.SendScintilla(qsci.SCI_SETMARGINTYPEN, 0, 0)
        self.SendScintilla(qsci.SCI_SETMARGINWIDTHN, 0, 0)

        # define markers for colorize zones of diff
        self.markerplus = self.markerDefine(qsci.Background)
        self.SendScintilla(qsci.SCI_MARKERSETBACK, self.markerplus, 0xB0FFA0)
        self.markerminus = self.markerDefine(qsci.Background)
        self.SendScintilla(qsci.SCI_MARKERSETBACK, self.markerminus, 0xA0A0FF)
        self.markertriangle = self.markerDefine(qsci.Background)
        self.SendScintilla(qsci.SCI_MARKERSETBACK, self.markertriangle, 0xFFA0A0)

    def _action_defs(self):
        return [
            ("diffmode", self.tr("Diff mode"), 'diffmode' ,
             self.tr('Enable/Disable Diff mode'), None, None),
            ("ignorews", self.tr("Ignore all space"), None ,
             self.tr('Enable/Disable white space checking when comparing lines'), None, None),
            ("annmode", self.tr("Annotate mode"), None,
             self.tr('Enable/Disable Annotate mode'), None, None),
            ("next", self.tr('Next hunk'), 'down', self.tr('Jump to the next hunk'),
             Qt.ALT + Qt.Key_Down, None),
            ("prev", self.tr('Prior hunk'), 'up', self.tr('Jump to the previous hunk'),
             Qt.ALT + Qt.Key_Up, None),
            ("show-big-file", self.tr('Display heavy file'), 'heavy',
             self.tr('Display file Content even if it is marked as too big'
                     '[config: maxfilesize]'),
             None, None),

        ]

    def createActions(self):
        self.actions = {}
        for name, desc, icon, tip, key, cb in self._action_defs():
            act = QtGui.QAction(desc, self)
            if icon:
                act.setIcon(geticon(icon))
            if tip:
                act.setStatusTip(tip)
            if key:
                act.setShortcut(key)
            if cb:
                act.triggered.connect(cb)
            self.actions[name] = act
            self.addAction(act)
        self.actions['diffmode'].setCheckable(True)
        self.actions['ignorews'].setCheckable(True)
        self.actions['annmode'].setCheckable(True)
        self.actions['show-big-file'].setCheckable(True)

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        for act in [None, 'diffmode', 'prev', 'next',
                    None, 'show-big-file', None, 'ignorews']:
            if act:
                menu.addAction(self.actions[act])
            else:
                menu.addSeparator()
        menu.exec_(event.globalPos())

    def clear_highlights(self):
        n = self.length()
        self.SendScintilla(qsci.SCI_SETINDICATORCURRENT, 8) # highlight
        self.SendScintilla(qsci.SCI_INDICATORCLEARRANGE, 0, n)
        self.SendScintilla(qsci.SCI_SETINDICATORCURRENT, 9) # current found
                                                            # occurrence
        self.SendScintilla(qsci.SCI_INDICATORCLEARRANGE, 0, n)

    def highlight_current_search_string(self, pos, text):
        line = self.SendScintilla(qsci.SCI_LINEFROMPOSITION, pos)
        self.ensureLineVisible(line)
        self.SendScintilla(qsci.SCI_SETINDICATORCURRENT, 9)
        self.SendScintilla(qsci.SCI_INDICATORCLEARRANGE, 0, pos)
        self.SendScintilla(qsci.SCI_INDICATORFILLRANGE, pos, len(text))

    def search_and_highlight_string(self, text):
        data = unicode(self.text())
        self.SendScintilla(qsci.SCI_SETINDICATORCURRENT, 8)
        pos = [data.find(text)]
        n = len(text)
        while pos[-1] > -1:
            self.SendScintilla(qsci.SCI_INDICATORFILLRANGE, pos[-1], n)
            pos.append(data.find(text, pos[-1]+1))
        return [x for x in pos if x > -1]


class HgFileView(QtGui.QFrame):

    message_logged = pyqtSignal(str, int)
    rev_for_diff_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        self._diff = None
        self._diffs = None
        self.cfg = None
        QtGui.QFrame.__init__(self, parent)
        framelayout = QtGui.QVBoxLayout(self)
        framelayout.setContentsMargins(0, 0, 0, 0)
        framelayout.setSpacing(0)

        self.info_frame = QtGui.QFrame()
        framelayout.addWidget(self.info_frame)
        l = QtGui.QVBoxLayout()
        self.info_frame.setLayout(l)
        self.filenamelabel = QtGui.QLabel()
        self.filenamelabel.setWordWrap(True)
        self.filenamelabel.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByKeyboard|
            QtCore.Qt.TextSelectableByMouse|
            QtCore.Qt.LinksAccessibleByMouse)
        self.filenamelabel.linkActivated.connect(
            lambda link: self.displayFile(show_big_file=True))
        self.execflaglabel = QtGui.QLabel()
        self.execflaglabel.setWordWrap(True)
        l.addWidget(self.filenamelabel)
        l.addWidget(self.execflaglabel)
        self.execflaglabel.hide()

        self.filedata_frame = QtGui.QFrame()
        framelayout.addWidget(self.filedata_frame)
        l = QtGui.QHBoxLayout()
        l.setContentsMargins(0,0,0,0)
        l.setSpacing(0)
        self.filedata_frame.setLayout(l)

        self.sci = HgQsci(self)
        l.addWidget(self.sci, 1)

        ll = QtGui.QVBoxLayout()
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(0)
        l.insertLayout(0, ll)

        ll2 = QtGui.QHBoxLayout()
        ll2.setContentsMargins(0, 0, 0, 0)
        ll2.setSpacing(0)
        ll.addLayout(ll2)

        # used to fill height of the horizontal scroll bar
        w = QtGui.QWidget(self)
        ll.addWidget(w)
        self._spacer = w

        self.blk = BlockList(self)
        self.blk.linkScrollBar(self.sci.verticalScrollBar())
        ll2.addWidget(self.blk)
        self.blk.setVisible(False)

        self.ann = Annotator(self.sci, self)
        ll2.addWidget(self.ann)
        self.ann.setVisible(False)

        self._model = None
        self._ctx = None
        self._filename = None
        self._annotate = False
        self._find_text = None
        self._mode = "diff" # can be 'diff' or 'file'
        self.filedata = None

        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.idle_fill_files)
        self.sci.actions['diffmode'].toggled[bool].connect(self.setMode)
        self.sci.actions['ignorews'].toggled[bool].connect(
            lambda value: self.setUiConfig('diff', 'ignorews', value))
        self.sci.actions['annmode'].toggled[bool].connect(self.setAnnotate)
        self.sci.actions['prev'].triggered.connect(self.prevDiff)
        self.sci.actions['next'].triggered.connect(self.nextDiff)
        self.sci.actions['show-big-file'].toggled[bool].connect(self.showBigFile)
        self.sci.actions['diffmode'].setChecked(True)

    def resizeEvent(self, event):
        QtGui.QFrame.resizeEvent(self, event)
        h = self.sci.horizontalScrollBar().height()
        self._spacer.setMinimumHeight(h)
        self._spacer.setMaximumHeight(h)

    def showBigFile(self, state):
        """Force displaying the content related to a file considered previously as
        too big.
        """
        if not self._model.graph:
            return
        if not state:
            self._model.graph.maxfilesize = self.cfg.getMaxFileSize()
        else:
            self._model.graph.maxfilesize = -1
        self.displayFile()

    def setMode(self, mode):
        if isinstance(mode, bool):
            mode = ['file', 'diff'][mode]
        assert mode in ('diff', 'file')

        self.sci.actions['annmode'].setEnabled(not mode)
        self.sci.actions['next'].setEnabled(not mode)
        self.sci.actions['prev'].setEnabled(not mode)
        if mode != self._mode:
            self._mode = mode
            self.blk.setVisible(self._mode == 'file')
            self.ann.setVisible(self._mode == 'file' and self._annotate)

            self.displayFile()

    def setUiConfig(self, section, name, value):
        if self._model.repo.ui._tcfg.get(section, name) == value:
            return
        self._model.repo.ui._tcfg.set(section, name, value, source='hgview')
        self.displayFile()

    def setAnnotate(self, ann):
        self._annotate = ann
        if ann:
            self.displayFile()

    def setModel(self, model):
        # XXX we really need only the "Graph" instance
        self._model = model
        self.cfg = HgConfig(self._model.repo.ui)
        if self._model.graph:
            is_show_big_file = self._model.graph.maxfilesize < 0
        else:
            is_show_big_file = self.cfg.getMaxFileSize()
        self.sci.actions['show-big-file'].setChecked(is_show_big_file)
        self.sci.actions['ignorews'].setChecked(model.repo.ui.configbool('diff', 'ignorews'))
        self.sci.clear()

    def setContext(self, ctx):
        self._ctx = ctx
        self._p_rev = None
        self.sci.clear()

    def rev(self):
        return self._ctx.rev()

    def filename(self):
        return self._filename

    def displayDiff(self, rev):
        if rev != self._p_rev:
            self.displayFile(rev=rev)

    def displayFile(self, filename=None, rev=None, show_big_file=None):
        if filename is None:
            filename = self._filename

        self._realfilename = filename
        if isbfile(filename):
            self._filename = bfilepath(filename)
        else:
            self._filename = filename

        if rev is not None:
            self._p_rev = rev
            self.rev_for_diff_changed.emit(rev)
        self.sci.clear()
        self.ann.clear()
        self.filenamelabel.setText(" ")
        self.execflaglabel.clear()
        if filename is None:
            return
        try:
            filectx = self._ctx.filectx(self._realfilename)

        except HgLookupError: # occur on deleted files
            return
        if self._mode == 'diff' and self._p_rev is not None:
            mode = self._p_rev
        else:
            mode = self._mode
        if show_big_file:
            flag, data = self._model.graph.filedata(filename, self._ctx.rev(), mode, maxfilesize=-1)
        else:
            flag, data = self._model.graph.filedata(filename, self._ctx.rev(), mode)
        if flag == 'file too big':
            self.filedata_frame.hide()
            message = (('<center>'
                        'File size (%s) greater than configured maximum value: '
                        '<font color="red"> maxfilesize=%i</font><br>'
                        '<br>'
                        '<a href="show-big-file">Click to display anyway '
                        '<img src=":/icons/heavy_small.png" width="16" height="16"></a>.'
                        '</center>') % (data, self.cfg.getMaxFileSize()))
            self.filenamelabel.setText(message)
            return
        else:
            self.filedata_frame.show()
        if flag == '-':
            return
        if flag == '':
            return

        lexer = get_lexer(filename, data, flag, self.cfg)
        if flag == "+":
            nlines = data.count('\n')
            self.sci.setMarginWidth(1, str(nlines)+'0')
        self.sci.setLexer(lexer)
        self._cur_lexer = lexer
        if data not in (u'file too big', u'binary file'):
            self.filedata = data
        else:
            self.filedata = None

        flag = exec_flag_changed(filectx)
        if flag:
            self.execflaglabel.setText(u"<b>exec mode has been <font color='red'>%s</font></b>" % flag)
            self.execflaglabel.show()
        else:
            self.execflaglabel.hide()

        labeltxt = u''
        if isbfile(self._realfilename):
            labeltxt += u'[bfile tracked] '
        labeltxt += u"<b>%s</b>" % tounicode(self._filename)

        if self._p_rev is not None:
            labeltxt += u' (diff from rev %s)' % self._p_rev
        renamed = filectx.renamed()
        if renamed:
            labeltxt += u' <i>(renamed from %s)</i>' % tounicode(bfilepath(renamed[0]))
        self.filenamelabel.setText(labeltxt)

        self.sci.setText(data)
        if self._find_text:
            self.highlightSearchString(self._find_text)
        self.sci.actions['prev'].setEnabled(False)
        self.updateDiffDecorations()
        if self._mode == 'file' and self._annotate:
            if filectx.rev() is None: # XXX hide also for binary files
                self.ann.setVisible(False)
            else:
                self.ann.setVisible(self._annotate)
                if lexer is not None:
                    self.ann.setFont(lexer.font(0))
                else:
                    self.ann.setFont(self.sci.font())
                self.ann.setFilectx(filectx)
        return True

    def updateDiffDecorations(self):
        """
        Recompute the diff and starts the timer
        responsible for filling diff decoration markers
        """
        self.blk.clear()
        if self._mode == 'file' and self.filedata is not None:
            if self.timer.isActive():
                self.timer.stop()

            parent = self._model.graph.fileparent(self._filename, self._ctx.rev())
            if parent is None:
                return
            m = self._ctx.filectx(self._filename).renamed()
            if m:
                pfilename, __ = m
            else:
                pfilename = self._filename
            _, parentdata = self._model.graph.filedata(pfilename,
                                                       parent, 'file')
            if parentdata is not None:
                filedata = self.filedata.splitlines()
                parentdata = parentdata.splitlines()
                self._diff = difflib.SequenceMatcher(None,
                                                     parentdata,
                                                     filedata,)
                self._diffs = []
                self.blk.syncPageStep()
                self.timer.start()

    def _nextDiff(self):
        if self._mode == 'file':
            row, __ = self.sci.getCursorPosition()
            lo = 0
            for i, (lo, __) in enumerate(self._diffs):
                if lo > row:
                    last = (i == (len(self._diffs)-1))
                    break
            else:
                return False
            self.sci.setCursorPosition(lo, 0)
            self.sci.verticalScrollBar().setValue(lo)
            return not last

    def nextDiff(self):
        notlast = self._nextDiff()
        self.sci.actions['next'].setEnabled(self.fileMode() and notlast and self.nDiffs())
        self.sci.actions['prev'].setEnabled(self.fileMode() and self.nDiffs())

    def _prevDiff(self):
        if self._mode == 'file':
            row, __ = self.sci.getCursorPosition()
            lo = 0
            for i, (lo, hi) in enumerate(reversed(self._diffs)):
                if hi < row:
                    first = (i == (len(self._diffs)-1))
                    break
            else:
                return False
            self.sci.setCursorPosition(lo, 0)
            self.sci.verticalScrollBar().setValue(lo)
            return not first

    def prevDiff(self):
        notfirst = self._prevDiff()
        self.sci.actions['prev'].setEnabled(self.fileMode() and notfirst and self.nDiffs())
        self.sci.actions['next'].setEnabled(self.fileMode() and self.nDiffs())

    def nextLine(self):
        x, y = self.sci.getCursorPosition()
        self.sci.setCursorPosition(x+1, y)

    def prevLine(self):
        x, y = self.sci.getCursorPosition()
        self.sci.setCursorPosition(x-1, y)

    def nextCol(self):
        x, y = self.sci.getCursorPosition()
        self.sci.setCursorPosition(x, y+1)

    def prevCol(self):
        x, y = self.sci.getCursorPosition()
        self.sci.setCursorPosition(x, y-1)

    def nDiffs(self):
        return len(self._diffs)

    def diffMode(self):
        return self._mode == 'diff'
    def fileMode(self):
        return self._mode == 'file'

    def searchString(self, text):
        self._find_text = text
        self.sci.clear_highlights()
        findpos = self.highlightSearchString(self._find_text)
        if findpos:
            def finditer(self, findpos):
                if self._find_text:
                    for pos in findpos:
                        self.sci.highlight_current_search_string(pos, self._find_text)
                        yield self._ctx.rev(), self._filename, pos
            return finditer(self, findpos)

    def highlightSearchString(self, text):
        pos = self.sci.search_and_highlight_string(text)
        msg = u"Found %d occurrences of '%s' in current file or diff" % \
              (len(pos), tounicode(text))
        self.message_logged.emit(msg, 2000)
        return pos

    def verticalScrollBar(self):
        return self.sci.verticalScrollBar()

    def idle_fill_files(self):
        # we make a burst of diff-lines computed at once, but we
        # disable GUI updates for efficiency reasons, then only
        # refresh GUI at the end of the burst
        self.sci.setUpdatesEnabled(False)
        self.blk.setUpdatesEnabled(False)
        for __ in range(30): # burst pool
            if self._diff is None or not self._diff.get_opcodes():
                self._diff = None
                self.timer.stop()
                self.sci.actions['next'].setEnabled(self.fileMode() and self.nDiffs())
                break

            tag, __, __, blo, bhi = self._diff.get_opcodes().pop(0)
            if tag == 'replace':
                self._diffs.append([blo, bhi])
                self.blk.addBlock('x', blo, bhi)
                for i in range(blo, bhi):
                    self.sci.markerAdd(i, self.sci.markertriangle)

            elif tag == 'delete':
                pass

            elif tag == 'insert':
                self._diffs.append([blo, bhi])
                self.blk.addBlock('+', blo, bhi)
                for i in range(blo, bhi):
                    self.sci.markerAdd(i, self.sci.markerplus)

            elif tag == 'equal':
                pass

            else:
                raise ValueError, 'unknown tag %r' % (tag,)

        # ok, let's enable GUI refresh for code viewers and diff-block displayers
        self.sci.setUpdatesEnabled(True)
        self.blk.setUpdatesEnabled(True)


class HgFileListView(QtGui.QTableView):
    """
    A QTableView for displaying a HgFileListModel
    """

    file_selected = pyqtSignal([str, int], [str])

    def __init__(self, parent=None):
        QtGui.QTableView.__init__(self, parent)
        self.setShowGrid(False)
        self.verticalHeader().hide()
        self.verticalHeader().setDefaultSectionSize(20)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setTextElideMode(Qt.ElideLeft)

        self.horizontalHeader().setToolTip('Double click to toggle merge mode')

        self.createActions()

        self.horizontalHeader().sectionDoubleClicked[int].connect(
                self.toggleFullFileList)
        self.doubleClicked.connect(self.fileActivated)

        self.horizontalHeader().sectionResized[int, int, int].connect(
                self.sectionResized)
        self._diff_dialogs = {}
        self._nav_dialogs = {}

    def setModel(self, model):
        QtGui.QTableView.setModel(self, model)
        model.layoutChanged.connect(self.fileSelected)
        self.selectionModel().currentRowChanged.connect(
                self.fileSelected)
        self.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)

    def currentFile(self):
        index = self.currentIndex()
        return self.model().fileFromIndex(index)

    def fileSelected(self, index=None, *args):
        if index is None:
            index = self.currentIndex()
        sel_file = self.model().fileFromIndex(index)
        from_rev = self.model().revFromIndex(index)
        # signal get unicode as input
        if from_rev is None:
            self.file_selected[str].emit(tounicode(sel_file))
        else:
            self.file_selected[str, int].emit(tounicode(sel_file), from_rev)

    def selectFile(self, filename):
        self.setCurrentIndex(self.model().indexFromFile(filename))

    def fileActivated(self, index, alternate=False):
        sel_file = self.model().fileFromIndex(index)
        if sel_file is '':
            return
        if alternate:
            self.navigate(sel_file)
        else:
            self.diffNavigate(sel_file)

    def toggleFullFileList(self, *args):
        self.model().toggleFullFileList()

    def navigate(self, filename=None):
        self._navigate(filename, FileViewer, self._nav_dialogs)

    def diffNavigate(self, filename=None):
        self._navigate(filename, FileDiffViewer, self._diff_dialogs)

    def _navigate(self, filename, dlgclass, dlgdict):
        if filename is None:
            filename = self.currentFile()
        model = self.model()
        if filename and len(model.repo.file(filename))>0:
            if filename not in dlgdict:
                dlg = dlgclass(model.repo, filename,
                               repoviewer=self.window())
                dlgdict[filename] = dlg

                dlg.setWindowTitle('Hg file log viewer')
            dlg = dlgdict[filename]
            dlg.goto(model.current_ctx.rev())
            dlg.show()
            dlg.raise_()
            dlg.activateWindow()

    def _action_defs(self):
        a = [("navigate", self.tr("Navigate"), None ,
              self.tr('Navigate the revision tree of this file'), None, self.navigate),
             ("diffnavigate", self.tr("Diff-mode navigate"), None,
              self.tr('Navigate the revision tree of this file in diff mode'), None, self.diffNavigate),
             ]
        return a

    def createActions(self):
        self._actions = {}
        for name, desc, icon, tip, key, cb in self._action_defs():
            act = QtGui.QAction(desc, self)
            if icon:
                act.setIcon(geticon(icon))
            if tip:
                act.setStatusTip(tip)
            if key:
                act.setShortcut(key)
            if cb:
                act.triggered.connect(cb)
            self._actions[name] = act
            self.addAction(act)

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        for act in ['navigate', 'diffnavigate']:
            if act:
                menu.addAction(self._actions[act])
            else:
                menu.addSeparator()
        menu.exec_(event.globalPos())

    def resizeEvent(self, event):
        vp_width = self.viewport().width()
        col_widths = [self.columnWidth(i) \
                      for i in range(1, self.model().columnCount())]
        col_width = vp_width - sum(col_widths)
        col_width = max(col_width, 50)
        self.setColumnWidth(0, col_width)
        QtGui.QTableView.resizeEvent(self, event)

    def sectionResized(self, idx, oldsize, newsize):
        if idx == 1:
            self.model().setDiffWidth(newsize)

    def nextFile(self):
        row = self.currentIndex().row()
        self.setCurrentIndex(self.model().index(min(row+1,
                             self.model().rowCount() - 1), 0))
    def prevFile(self):
        row = self.currentIndex().row()
        self.setCurrentIndex(self.model().index(max(row - 1, 0), 0))
