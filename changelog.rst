2015.2.08
=========

* Feature: Add argument '-output' to the application
* Feature: Add setup.py
* Rename 'htmldiff' to 'htmldiff.py' because 'py_module' argument in 'setup.py' require extension

2015.2.07
=========

* Feature: Add parameter 'notags=True'
* Add param 'self' to method html_encode.
* Tests working again.
* Improvement and extension passing arguments to the application.

2015.2.06
=========

* Feature: modified method to compare url content.
* Accomplish the PEP8 naming conventions.
* Removed stopword. No sense because HTML could contain any language.
* Convert def isJunk(x) to lambda expression.
* Moved re.compile sentences within the class.

2014.5.26
=========

* Initial release.
* forked from github.com/edsu/htmldiff