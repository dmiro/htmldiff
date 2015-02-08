# htmldiff.py

[![Build Status](https://secure.travis-ci.org/edsu/htmldiff.png)](http://travis-ci.org/edsu/htmldiff)


```
usage: htmldiff [-h] [-test] [-ta] [-ss] [-sh] resource1 resource2

outputs HTML that shows the differences in text between two versions of an
HTML document. Differences in markup are not shown.

positional arguments:
  resource1          File or URL to diff from
  resource2          File or URL to diff against

optional arguments:
  -h, --help         show this help message and exit
  -test              Test
  -ta, --tags        Also compares the differences in tags
  -ss, --stylesheet  Insert stylesheet to result
  -sh, --simplehtml  Mostly for testing
```

htmldiff outputs HTML that shows the differences in text between
two versions of an HTML document. Differences in markup are not
shown.

Original version is from [Ian Bicking](https://github.com/ianb)
with changes from [Richard Cyganiak](https://github.com/cygri).

## Requirements

* Python 2.7

## Using with Mercurial

Put `htmldiff` on the path, and add the following to `~/.hgrc`:

    [extensions]
    hgext.extdiff =

    [extdiff]
    cmd.htmldiff = htmldiff

Then you can do: `hg htmldiff index.html > diff.html`

## Limitations

This uses Python's `SequenceMatcher`, which is generally a bit crap
and sometimes misses long possible matches, especially if the long
match is punctuated by short non-matches, which happens easily for
example if markup is systematically changed. You can try uncommenting
the simpler version of the `isJunk` function in the source to make
this slightly better, at the price of less speed and more noise.

## Ideas for future improvements

* Add flag for "accurate" versus "risky" mode, see Limitations above
* Allow diffing only of a given section by specifying an `id`
* Make a web service

## License

MIT License, see `LICENSE.txt`.
