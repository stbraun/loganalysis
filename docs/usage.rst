=====
Usage
=====

`loganalysis` is primarily meant to be used within a jupyter notebook. But it can also be used with a script if the output shall be streamed into another process for further evaluation.

Be aware that the functions in this package are asynchronous. That means you must put `await` in front of each call.

To use `loganalysis` in a project::

    import loganalysis as la

If the log file has an encoding other than utf-8 specify the correct encoding before accessing the file, for example to `latin1`:::

    la.encoding = 'latin1'

Printing call stacks
--------------------
This is useful to pull all Java stack traces out of a log file. If the same stack trace appears multiple times it is printed only once with a count of `n`:::

    la.print_stacks(log_file)

If you only want to retrieve the stacks for further processing, call::

    la.extract_stacks(log_file)


Printing Exceptions
-------------------
Will print all lines matching `Exception`. The output can be sorted and same exceptions bundled into a single output:::

    la.print_exception(log_file, sort=False, unique=False)


Printing Error logs
-------------------
Will print all logs with level `ERROR`. You can specify to include the thread where the log was written:::

    la.print_errors(log_file, include_thread=False)


Printing specified matches
--------------------------
You can specify a regular expression to match log lines against. For output you can decide to include log timestamp or not. If a group is specified in the regular expression, only the group is extracted. This can be overwritten:::

    la.extract_matches(log_file, regex, with_timestamp=False, ignore_groups=False)


Printing Log info
-----------------
When working at a project over a longer period, log files may have been recorded in varying situations. Then it is helpful to add some information describung the circumstances into the logfile for later reference.
If you add such text with prefix characters `###` at the beginning of each line, you can extract it easily with the following call:::

    la.print_info(log_file)

There is also a function to just extract the information:::

    la.extract_info(log_file)


