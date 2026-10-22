"""One state shared by the terminal view and the web page: which section is current,
what each check said last, and the actions either view can take."""
import threading
import time

from . import files


class State:
    INTERVAL = 2.0

    def __init__(self, sections, root):
        self.sections = sections
        self.root = root
        self.index = 0
        self.results = {}            # (section id, check id) -> (ok, detail)
        self.skipped = set()         # section ids
        self.finished = False
        self.version = 0
        self.last_checked = 0.0
        self.lock = threading.Lock()
        self._wake = threading.Event()

    # ---- reading
    @property
    def section(self):
        return None if self.finished else self.sections[self.index]

    @staticmethod
    def _item(i):
        return {"title": i.title, "path": i.path, "note": i.note, "url": i.url, "command": i.command,
                "group": i.group, "meta": i.meta, "ready": i.ready, "note_html": files.markdown(i.note)}

    def _key(self, s, c):
        return (s.id, c.id)

    def check_passed(self, c, s=None):
        r = self.results.get(self._key(s or self.section, c))
        return bool(r and r[0])

    def section_passed(self, s=None):
        s = s or self.section
        return s is not None and all(self.check_passed(c, s) for c in s.checks if not c.optional)

    def snapshot(self):
        with self.lock:
            s = self.section
            return {
                "version": self.version,
                "finished": self.finished,
                "index": self.index,
                "last_checked": self.last_checked,
                "sections": [{"id": x.id, "title": x.title,
                              "status": "skipped" if x.id in self.skipped else
                                        "done" if (i < self.index or self.finished) else
                                        "current" if i == self.index else "pending"}
                             for i, x in enumerate(self.sections)],
                "section": None if s is None else {
                    "id": s.id, "title": s.title, "why": s.why, "done": s.done,
                    "why_html": files.markdown(s.why), "done_html": files.markdown(s.done),
                    "passed": self.section_passed(s),
                    "items": [self._item(i) for i in (s.items() if callable(s.items) else s.items)],
                    "aside": [self._item(i) for i in (s.aside() if callable(s.aside) else s.aside)],
                    "checks": [{"id": c.id, "title": c.title, "fix": c.fix() if callable(c.fix) else c.fix,
                                "fix_html": files.markdown(c.fix() if callable(c.fix) else c.fix),
                                "command": c.command() if callable(c.command) else c.command,
                                "optional": c.optional,
                                "ok": self.results.get(self._key(s, c), (None, ""))[0],
                                "detail": self.results.get(self._key(s, c), (None, "not checked yet"))[1]}
                               for c in s.checks],
                },
            }

    # ---- checking
    def start_checking(self):
        self._run_checks()                      # once before the first frame, so it never says "not checked yet"
        threading.Thread(target=self._loop, daemon=True).start()

    def recheck_now(self):
        self._wake.set()

    def _loop(self):
        while True:
            self._run_checks()
            self._wake.wait(self.INTERVAL)
            self._wake.clear()

    def _run_checks(self, s=None):
        s = s or self.section
        if s is None:
            return
        new = {}
        for c in s.checks:
            try:
                ok, detail = c.run()
            except Exception as e:           # a check that crashes is a failed check, not a crashed guide
                ok, detail = False, f"check failed to run: {e}"
            new[self._key(s, c)] = (bool(ok), str(detail))
        with self.lock:
            changed = any(self.results.get(k) != v for k, v in new.items())
            self.results.update(new)
            self.last_checked = time.time()
            if changed:
                self.version += 1

    # ---- actions (from either view)
    def action(self, name):
        with self.lock:
            where = (self.index, self.finished)
            if name == "recheck":
                target = None
            elif name in ("continue", "skip") and not self.finished and (name == "skip" or self.section_passed()):
                target = self.index + 1 if self.index + 1 < len(self.sections) else None
            elif name == "back" and (self.index > 0 or self.finished):
                target = self.index if self.finished else self.index - 1
            else:
                return False
        if name != "recheck":
            if target is not None:
                self._run_checks(self.sections[target])   # so the next section's first frame is complete
            with self.lock:
                if (self.index, self.finished) == where:  # the other view has not moved it meanwhile
                    if name == "skip":
                        self.skipped.add(self.sections[self.index].id)
                    if name == "back":
                        self.finished = False
                        self.index = target
                        self.skipped.discard(self.sections[target].id)
                        self.version += 1
                    else:
                        self._advance()
        self.recheck_now()
        return True

    def _advance(self):
        if self.index + 1 < len(self.sections):
            self.index += 1
        else:
            self.finished = True
        self.version += 1
