.. :changelog:

Changelog for diagnostics module
================================
0.2.4 (2014-04-14)
------------------
- *BUG FIX:* Correctly logged traceback if no exception occured.

0.2.3 (2013-11-15)
------------------
- *BUG FIX:* Context code is rendered with correct line number even
  when exception is raised from with-statement block.
- *BUG FIX:* Added time and logging level name into log messages.

0.2.2 (2013-10-05)
------------------
- *BUG FIX:* Fixed usage in terminal.
- *BUG FIX:* Fixed reading of JS/CSS file in Python 3. HTML traceback
  is properly rendered.

0.2.1 (2013-10-04)
------------------
- *FEATURE:* Removed empty trailing lines from context code.
- *BUG FIX:* Removed duplicated global variables from list of local variables.
- *BUG FIX:* Don't show types/modules/functions in list of local variables.

0.2.0 (2013-06-22)
------------------
- *BUG FIX:* Removed class types, modules and other crap from
  list of global variables.
- *BUG FIX:* Function/method variables are ordered according
  to function/method signature.
- *FEATURE:* The same exceptions are stored only once
  (according to their hash).
- *BUG FIX:* Recover when converting object to unicode raises
  exception (e.g. BeautifulSoup).
- *BUG FIX:* Format code context even if code is in binary form
  (e.g. lxml).
- *BUG FIX:* Use `repr` function when instance can't be de/en-coded
  to the unicode/bytes.
- *BUG FIX:* Tracebacks with the same type of exception and timestamp
  are stored to different files.
- *FEATURE:* Added support for with statement.
- *FEATURE:* Added logging support.

0.1.0 (2013-02-13)
------------------
- First public release.
