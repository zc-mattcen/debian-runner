#!/usr/bin/env python3
#
# Whilst you can specify the keys in YAML in any order, this makes it hard to
# coordinate with multiple people.  With a well defined ordering that is
# checked by a linting tool, merging and coordination can be simplified.
#
"""Confirm the sort order of YAML files"""

import argparse
import io
import os
import sys
import yaml


def render_error_verbose(details):
    mark = details["mark"]
    message = details["message"]
    return f"{message}\n{mark}"


def render_error_action(details):
    mark = details["mark"]
    status = details["status"]
    message = details["message"]
    return f"::{status} file={mark.name},line={mark.line+1}::{message}"


def render_error_simple(details):
    mark = details["mark"]
    status = details["status"]
    message = details["message"]
    return f"{mark.name}:{mark.line+1}:{mark.column+1}: {status}: {message}"


def test_render():
    obj = {
        "mark": yaml.Mark("filename", 1, 2, 3, "File Line", 0),
        "message": "message",
        "status": "Error",
    }

    expect_verbose = "message\n" \
        "  in \"filename\", line 3, column 4:\n" \
        "    File Line\n" \
        "    ^"
    expect_action = "::Error file=filename,line=3::message"
    expect_simple = "filename:3:4: Error: message"

    assert (render_error_verbose(obj) == expect_verbose)
    assert (render_error_action(obj) == expect_action)
    assert (render_error_simple(obj) == expect_simple)


def output_error(mark, key1, key2):
    details = {}
    details["mark"] = mark
    details["status"] = "error"
    details["message"] = f"key '{key1}' must be before '{key2}'"

    renderlist = []

    # TODO:
    # - a commandline arg to enable different renderers
    renderlist.append(render_error_simple)
    renderlist.append(render_error_action)
    # renderlist.append(render_error_verbose)

    for render in renderlist:
        print(render(details))


def check_sorted(stream, debug=False):
    result = 0
    ctx_stack = []
    ctx = {}
    ctx["index"] = 0
    ctx["mod"] = -1  # dont check order until we start an ordered object

    pop_events = (yaml.SequenceEndEvent, yaml.MappingEndEvent)

    for event in yaml.parse(stream, yaml.SafeLoader):
        if debug:
            print(f"  D1: {ctx_stack}, {ctx}")
            print("    ", event)
            print("    ", event.start_mark)

        index = ctx["index"]
        ctx["index"] += 1

        if isinstance(event, yaml.SequenceStartEvent):
            ctx_stack.append(ctx)
            ctx = {}
            ctx["index"] = 0
            ctx["mod"] = -1  # dont check order in an array context
            continue

        if isinstance(event, yaml.MappingStartEvent):
            ctx_stack.append(ctx)
            ctx = {}
            ctx["index"] = 0
            ctx["mod"] = 2  # even numbers are keys, odd are the values
            continue

        if isinstance(event, pop_events):
            ctx = ctx_stack.pop()
            continue

        if not isinstance(event, yaml.ScalarEvent):
            continue

        # thus this isinstance(event, yaml.ScalarEvent)

        if ctx["mod"] == -1:
            # skip items in this context
            continue

        if index % ctx["mod"] != 0:
            # skip values
            continue

        if "prev" not in ctx:
            ctx["prev"] = None

        if ctx["prev"] is None:
            # We dont have a prev for comparison, so set it and skip
            ctx["prev"] = event.value
            continue

        if ctx["prev"] > event.value:
            result = 1
            output_error(event.start_mark, event.value, ctx['prev'])

        ctx["prev"] = event.value

    return result


def test_check_sorted():
    input_sorted = """
        aa:
            a:
            b:
        bb:
            a:
            b:

    """
    input_unsorted = """
        bb:
            b:
            a:
        aa:
            a:
            b:
    """

    assert (check_sorted(io.StringIO(input_sorted)) == 0)
    assert (check_sorted(io.StringIO(input_unsorted)) == 1)


def argparser():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument(
        "--debug",
        help="Output parsing events in sorted check",
        default=False,
        action="store_true",
    )

    args.add_argument("filename", nargs="+")

    r = args.parse_args()
    return r


def main():
    args = argparser()

    result = 0

    for filename in args.filename:
        if os.path.isdir(filename):
            for root, dirs, files in os.walk(filename):
                for file in files:
                    if file.endswith(".yml") or file.endswith(".yaml"):
                        stream = open(
                            os.path.join(root, file),
                            "r",
                            encoding="utf8"
                        )
                        result += check_sorted(
                            stream,
                            debug=args.debug,
                        )

        else:
            stream = open(filename, "r", encoding="utf8")
            result += check_sorted(stream, debug=args.debug)

    sys.exit(result)


if __name__ == "__main__":
    main()
