"""Utilities for logfile handling with pandas."""

from datetime import datetime
import pandas as pd


def read_logfile(log_file):
    """Read given logfile into a pandas DataFrame.

    :param log_file: path to logfile.
    :type log_file: str
    :return: dataframe with one record per log line.
    :rtype: pd.DataFrame
    """
    with open(log_file, "r") as lf:
        content = [{"message": line} for line in lf.readlines()]
    df = pd.DataFrame.from_dict(content)
    df.message = df.message.astype("string").str.strip()

    # Filter for lines with timestamp.
    df = df[df.message.str.match(r"^\d{4}")]

    # New data frame for parsed log items.
    df_log = pd.DataFrame()

    # Get timestamp left of thread.
    df1 = df.message.str.split("[", expand=True, n=1)
    df1.columns = ["datetime", "message"]
    df1["timestamp"] = [pd.Timestamp(ts) for ts in df1.datetime]
    df_log["timestamp"] = df1.timestamp
    # Extract thread - may include blanks.
    df2 = df1.message.str.split("] ", expand=True, n=1)
    df2.columns = ["thread", "message"]
    df_log["thread"] = df2.thread.str.replace(r"(?P<ident>.*-)(\d+)", unify_numbered)
    # Extract severity and file, leaving message.
    df3 = df2.message.str.strip().str.split(" ", expand=True, n=2)
    df3.columns = ["severity", "file", "message"]
    df_log["severity"] = df3.severity
    df_log["file"] = df3.file.str.replace(r":\?$", "")
    df_log["message"] = df3.message

    df_log.message = df_log.message.str.replace("^ *-", "")
    df_log.message = df_log.message.str.strip()
    return df_log


def make_datetime(timestamp: str, format=None):
    """Make a datetime object from a timestamp string.

    :param timestamp: the timestamp as string.
    :param format: the format string for the timestamp. Default: '%Y-%m-%d %H:%M:%S,%f %Z'
    :return: timestamp as datetime object
    :rtype: datetime.datetime
    """
    if format is None:
        format = "%Y-%m-%d %H:%M:%S,%f %Z"
    return datetime.strptime(timestamp, format)


def unify_numbered(match_object):
    """Take the match object and return unnumbered identifier.
    E.g. makes worker-XX from worker-12.
    """
    return match_object.groups()[0] + "XX"
