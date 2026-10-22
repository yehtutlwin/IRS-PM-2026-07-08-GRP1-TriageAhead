"""The terminal view: prints the current section whenever something changes, and reads
one-letter commands. Output is append-only so it works in any terminal."""
import queue
import sys
import threading
import time

OK, NO, WAIT = "[ok]", "[..]", "[  ]"


def _reader(q):
    for line in sys.stdin:
        q.put(line.strip().lower())
    q.put("q")


def render(snap, url):
    out = []
    if snap["finished"]:
        out.append("\nAll sections done." if not any(s["status"] == "skipped" for s in snap["sections"])
                   else "\nAll sections done (some skipped: " +
                   ", ".join(s["title"] for s in snap["sections"] if s["status"] == "skipped") + ").")
        out.append("b goes back a section, q quits.")
        return "\n".join(out)
    s = snap["section"]
    out.append("")
    out.append("=" * 72)
    out.append(s["title"])
    out.append("=" * 72)
    out.append(_wrap(s["why"]))
    out.append("")
    first_fix = None
    for c in s["checks"]:
        mark = OK if c["ok"] else (WAIT if c["ok"] is None else NO)
        opt = "  (optional)" if c["optional"] and not c["ok"] else ""
        out.append(f"  {mark} {c['title']}{opt}: {c['detail']}")
        if c["ok"] is False and first_fix is None and not c["optional"]:
            first_fix = c
    if first_fix is None:
        first_fix = next((c for c in s["checks"] if c["ok"] is False), None)
    out.append("")
    if s["passed"]:
        out.append(_wrap(s["done"]))
        out.append("")
        out.append(_items(s["items"] + s["aside"]))
        if url and any(i["path"] for i in s["items"] + s["aside"]):
            out.append(f"  (each file also opens from the web page, {url})")
        if s["items"] or s["aside"]:
            out.append("")
        out.append("Enter moves on to the next section.")
    elif first_fix is not None:
        out.append("Still needed: " + first_fix["title"])
        out.append(_wrap(first_fix["fix"]))
        if first_fix["command"]:
            out.append("")
            out.append("    " + first_fix["command"])
        out.append("")
        out.append("The guide checks again every two seconds. Enter checks now, s skips this section, q quits.")
        if s["aside"]:
            out.append("")
            out.append(_items(s["aside"]))
    if url:
        out.append(f"(the same page is open at {url})")
    return "\n".join(out)


def _wrap(text, width=96):
    """Paragraphs, bullets and bold as the texts carry them, for a terminal."""
    import textwrap
    out = []
    for para in text.split("\n\n"):
        lines = para.strip("\n").split("\n")
        if all(ln.startswith("- ") for ln in lines):
            for ln in lines:
                out.append(textwrap.fill(_plain(ln[2:]), width - 4, initial_indent="  - ", subsequent_indent="    "))
        else:
            out.append(textwrap.fill(_plain(" ".join(ln.strip() for ln in lines)), width))
        out.append("")
    return "\n".join(out).rstrip("\n")


def _items(items):
    out, grp = [], None
    for i in items:
        if i["group"] and i["group"] != grp:
            grp = i["group"]
            out.append(_plain(f"**{grp}**"))
        if i["command"]:
            out.append(f"  - {i['title']}. The command, for the second terminal:")
            out.append(f"      {i['command']}")
        elif not i["ready"]:
            out.append(f"  - {i['title']} (not yet)")
        else:
            out.append(f"  - {i['title']}: {i['url'] or i['path']}" + (f", {i['meta']}" if i["meta"] else ""))
        if i["note"]:
            out.append(_indent(_wrap(i["note"], 88), "      "))
    return "\n".join(out)


def _indent(text, pad):
    return "\n".join(pad + ln if ln.strip() else "" for ln in text.split("\n"))


def _plain(t):
    import re
    bold = sys.stdout.isatty()
    t = re.sub(r"\*\*(.+?)\*\*", (lambda m: "\033[1m" + m.group(1) + "\033[0m") if bold else (lambda m: m.group(1)), t)
    return t.replace("`", "")


def run(state, url):
    q = queue.Queue()
    threading.Thread(target=_reader, args=(q,), daemon=True).start()
    print("Setup guide for the ED triage pre-arrival intake assistant.")
    if url:
        print(f"Web page: {url}   (this terminal shows the same)")
    shown = None
    while True:
        snap = state.snapshot()
        key = (snap["version"], snap["index"], snap["finished"])
        if key != shown:
            print(render(snap, url))
            shown = key
        try:
            cmd = q.get(timeout=0.5)
        except queue.Empty:
            continue
        if cmd == "q":
            print("Bye.")
            return
        elif cmd == "s":
            state.action("skip")
        elif cmd == "b":
            state.action("back")
        elif cmd == "":
            if not state.action("continue"):
                state.action("recheck")
                time.sleep(0.3)
                shown = None     # reprint even if nothing changed, so Enter visibly does something
