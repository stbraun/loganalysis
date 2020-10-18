"""Log analysis functions.

Tools for interactive analysis of log files.
"""

import re

from jupyter_commons.output import print_md


async def read_log(log_file):
    """Read log file.

    Asynchronous generator.

    :param log_file: path to log file.
    :type log_file: str
    """
    with open(log_file, "r") as fd:
        more = True
        while more:
            try:
                more = False
                for line in fd.readlines():
                    yield line.strip()
            except UnicodeDecodeError as err:
                print(err)
                more = True


def de_qualify(qualified):
    """Takes a name with package, class and method and removes the package.

    Useful for Java classes.

    :param qualified: <path>.<class>.<method>
    :type qualified: str
    :return: <class>.<method>
    :rtype: str
    """
    parts = qualified.split(".")
    return parts[-2] + "." + parts[-1] if len(parts) > 2 else qualified


async def extract_info(log_file):
    """Extract log information.

    To annotate a logfile with comments just add lines starting with `###`.
    Lines starting with `###` are extracted and returned as list of these lines.
    One line holding the name of the log file is added.

    :param log_file: path to log file.
    :type log_file: str
    :return: list of info lines.
    :rtype: [str]
    """
    info = []
    marker = "###"
    info.append(f"{marker} Logfile: {log_file}")
    async for line in read_log(log_file):
        if line.startswith(marker):
            info.append(line)
    return info


async def print_info(log_file):
    """Print log information.

    See `extract_info` for detail.

    :param log_file: path to log file.
    :type log_file: str
    """
    info = await extract_info(log_file)
    print_md("**----- Logfile information -----**")
    for line in info:
        print(f"    {line}")


async def extract_matches(log_file, regex, with_timestamp=False):
    """Extract lines matching given regular expression.

    If there is a group specified in regex, only the group is extracted. If
    'with_timestamp' is True timestamp of the item is prepended to group.

    :param log_file: path to log file.
    :type log_file: str
    :param regex: regular expression a line needs to match.
    :type regex: str
    :param with_timestamp: True to prepend log timestamp in case of group match.
    :type with_timestamp: bool
    :return: list of matching lines.
    :rtype: [str]
    """
    logs = []
    async for line in read_log(log_file):
        result = re.search(regex, line)
        if result:
            if len(result.groups()) > 0:
                results = list(result.groups())
                if with_timestamp:
                    ts = extract_timestamp(line)
                    results.insert(0, ts)
                logs.append(" - ".join(results))
            else:
                logs.append(line)
    return logs


async def print_matches(
    log_file, regex, sort=False, unique=False, msg=None, with_timestamp=False
):
    """Print lines matching given regular expression.

    If there is a group specified in regex, only the group is extracted.

    :param log_file: path to log file.
    :type log_file: str
    :param regex: regular expression a line needs to match.
    :type regex: str
    :param sort: True to sort output.
    :type sort: bool
    :param unique: True to print only unique lines.
    :type unique: bool
    :param msg: string describing the matched object, e.g. 'exception'
    :type msg: str
    :param with_timestamp: True to prepend log timestamp.
    :type with_timestamp: bool
    :return: matched lines
    :rtype: [str]
    """
    unique_lines = None
    lines = await extract_matches(log_file, regex, with_timestamp)
    if msg is None:
        msg = f"regex '{regex}'"
    if unique:
        unique_lines = set(lines)
        print_md(
            f"**{len(unique_lines)}** unique of **{len(lines)}** total lines found for {msg}."
        )
    else:
        print_md(f"**{len(lines)}** entries found for {msg}.")
    print()
    processed_lines = unique_lines if unique else lines
    if sort:
        processed_lines = sorted(list(processed_lines))
    for line in processed_lines:
        print(line)
    return processed_lines


async def extract_levels(log_file, levels, include_thread=True):
    """Extract all logs matching levels.

    Logs that occur multiple times (timestamp excluded) will be reported once
    with a count of the occurrences.

    :param log_file: path to log file.
    :type log_file: str
    :param levels: one or more log levels, e.g. [WARN, ERROR].
    :type levels: str or [str]
    :param include_thread: consider thread when comparing two logs.
    :type include_thread: bool
    :return: dictionary of logs and counts.
    :rtype: dict[int: (int, str)]
    """
    logs = {}  # id: (count, log)
    log_id = 0
    levels_ = levels if isinstance(levels, str) else "|".join(levels)
    if include_thread:
        rex = rf"\s(\[[\w\-]+\]\s+({levels_})\s.*$)"
    else:
        rex = rf"\s\[[\w\-]+\]\s+(({levels_})\s.*$)"
    async for line in read_log(log_file):
        result = re.search(rex, line)
        if result:
            log = result.group(1)
            for id_, (count, log_) in logs.items():
                if log == log_:
                    logs[id_] = count + 1, log
                    break
            else:
                logs[log_id] = (1, log)
                log_id += 1
    return logs


async def print_errors(log_file, include_thread=False):
    """Print ERROR logs.

    :param log_file: path to log file.
    :type log_file: str
    :param include_thread: consider thread when comparing two logs.
    :type include_thread: bool
    """
    errors = await extract_levels(log_file, "ERROR", include_thread=include_thread)
    for err in errors.values():
        print(err)
    else:
        print_md("**----> no ERROR logs in log file.**")


async def extract_stacks(log_file):
    """Extract all stack traces from log file.

    Stack traces that occur multiple times times will be extracted once
    with a count of their occurrence.

    :param log_file: path to log file.
    :type log_file: str
    :return: dictionary of stack id and tuple of count and trace.
    :rtype: {int: (int, [str])}
    """
    in_stack = False
    stack = None
    stacks = {}  # id: stack
    stack_id = 0
    rex = r"\s?at\s([A-Za-z][\w\.\$\<\>]+)"
    rex_ln = r"\s?at\s.+\(.*(\:\d+)\)"
    async for line in read_log(log_file):
        # print(f">> - {line}")
        result = re.search(rex, line)
        if result:
            if not in_stack:
                in_stack = True
                stack = []
            item = result.group(1)
            entry = de_qualify(item) + "()"
            res_ln = re.search(rex_ln, line)
            if res_ln:
                line_num = res_ln.group(1)
                entry += line_num
            stack.append(entry)
        else:
            if in_stack:
                # stack.reverse()
                for id_, (cnt, stack_) in stacks.items():
                    if stack == stack_:
                        stacks[id_] = cnt + 1, stack
                        break
                else:
                    stacks[stack_id] = (1, stack)
                    stack_id += 1
                in_stack = False
    return stacks


async def print_stacks(log_file):
    """Print all stack traces from log file.

    Stack traces that occur multiple times times will be printed once
    with a count of their occurrence.

    :param log_file: path to log file.
    :type log_file: str
    """
    stacks = await extract_stacks(log_file)
    if len(stacks) == 0:
        print_md("**-----> No stack traces in log file.**")
    for stack in stacks.values():
        print_md(f"----- Occurrence **{stack[0]}** times -----")
        for item in stack[1]:
            print(f"    {item}")


async def print_exceptions(log_file, sort=False, unique=False):
    """Print exceptions found in given log file.

    :param log_file: path to log file.
    :type log_file: str
    :param sort: True to sort exceptions.
    :type sort: bool
    :param unique: True to print only unique exceptions.
    :type unique: bool
    """
    await print_matches(log_file, r"\s(\w*Exception\w*)[^\w]", unique=unique, sort=sort)


def extract_timestamp(line):
    """Extract timestamp from log item.

    :param line: log item.
    :type line: str
    :return: timestamp or empty string
    :rtype: str
    """
    rex = r"(\d{4}\-\d\d\-\d\d\s\d\d:\d\d:\d\d[\,\d]*[\s\w]*)"
    match = re.search(rex, line)
    if match:
        return match.group(1)
    return ""
