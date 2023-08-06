==========================
Hyper: HTTP/2.0 for Python
==========================

.. image:: https://travis-ci.org/Lukasa/hyper.png?branch=master
    :target: https://travis-ci.org/Lukasa/hyper

HTTP is changing under our feet. HTTP/1.1, our old friend, is being
supplemented by the brand new HTTP/2.0 standard. HTTP/2.0 provides many
benefits: improved speed, lower bandwidth usage, better connection management,
and more.

``hyper`` provides these benefits to your Python code. How? Like this::

    from hyper import HTTP20Connection

    conn = HTTP20Connection('twitter.com:443')
    conn.request('GET', '/')
    resp = conn.getresponse()

    print(resp.read())

Simple.

Caveat Emptor!
==============

Please be warned: ``hyper`` is in a very early alpha. You *will* encounter bugs
when using it. In addition, there are very many rough edges. With that said,
please try it out in your applications: I need your feedback to fix the bugs
and file down the rough edges.

Versions
========

``hyper`` provides support for draft 9 of the HTTP/2.0 draft specification and
draft 5 of the HPACK draft specification. As further drafts are released,
``hyper`` will be updated to support them.

Compatibility
=============

``hyper`` is intended to be a drop-in replacement for ``http.client``, with a
similar API. However, ``hyper`` intentionally does not name its classes the
same way ``http.client`` does. This is because most servers do not support
HTTP/2.0 at this time: I don't want you accidentally using ``hyper`` when you
wanted ``http.client``.

Contributing
============

``hyper`` welcomes contributions from anyone! Unlike many other projects we are
happy to accept cosmetic contributions and small contributions, in addition to
large feature requests and changes.

Before you contribute (either by opening an issue or filing a pull request),
please read the following guidelines:

1. Check for issues, *both open and closed*, before raising a new one. It's
   possible your idea or problem has been discussed before. GitHub has a very
   useful search feature: I recommend using that for a few minutes.
2. Fork the repository on GitHub.
3. Run the tests to confirm that they all pass on your system. If they don't,
   you will need to investigate why they fail. ``hyper`` has a substantial
   suite of tests which should cover most failures.
4. Write tests that demonstrate your bug or feature. Ensure that they all fail.
5. Make your change.
6. Run the entire test suite again, confirming that all tests pass including
   the ones you just added.
7. Send a pull request to the ``development`` branch. GitHub pull requests are
   the expected method of collaborating on this project. The `master` branch
   is where all the documentation and releases are built from, and so is
   required to be known-good at all times.

If for whatever reason you strongly object to the GitHub workflow, email the
maintainer with a patch.

License
=======

``hyper`` is made available under the MIT License. For more details, see the
``LICENSE`` file in the repository.

Authors
=======

``hyper`` is maintained by Cory Benfield, with contributions from others. For
more details about the contributors, please see ``CONTRIBUTORS.rst``.


Release History
===============

0.0.4 (2014-03-08)
------------------

- Add logic for pluggable objects to manage the flow-control window for both
  connections and streams.
- Raise new ``HPACKDecodingError`` when we're unable to validly map a
  Huffman-encoded string.
- Correctly respect the HPACK EOS character.

0.0.3 (2014-02-26)
------------------

- Use bundled SSL certificates in addition to the OS ones, which have limited
  platform availability. (`Issue #9`_)
- Connection objects reset to their basic state when they're closed, enabling
  them to be reused. Note that they may not be reused if exceptions are thrown
  when they're in use: you must open a new connection in that situation.
- Connection objects are now context managers. (`Issue #13`_)
- The ``HTTP20Adapter`` correctly reuses connections.
- Stop sending WINDOWUPDATE frames with a zero-size window increment.
- Provide basic functionality for gracelessly closing streams.
- Exhausted streams are now disposed of. (`Issue #14`_)

.. _Issue #9: https://github.com/Lukasa/hyper/issues/9
.. _Issue #13: https://github.com/Lukasa/hyper/issues/13
.. _Issue #14: https://github.com/Lukasa/hyper/issues/14

0.0.2 (2014-02-20)
------------------

- Implemented logging. (`Issue #12`_)
- Stopped HTTP/2.0 special headers appearing in the response headers.
  (`Issue #16`_)
- `HTTP20Connection` objects are now context managers. (`Issue #13`_)
- Response bodies are automatically decompressed. (`Issue #20`_)
- Provide a requests transport adapter. (`Issue #19`_)
- Fix the build status indicator. (`Issue #22`_)


.. _Issue #12: https://github.com/Lukasa/hyper/issues/12
.. _Issue #16: https://github.com/Lukasa/hyper/issues/16
.. _Issue #13: https://github.com/Lukasa/hyper/issues/13
.. _Issue #20: https://github.com/Lukasa/hyper/issues/20
.. _Issue #19: https://github.com/Lukasa/hyper/issues/19
.. _Issue #22: https://github.com/Lukasa/hyper/issues/22

0.0.1 (2014-02-11)
------------------

- Initial Release
- Support for HTTP/2.0 draft 09.
- Support for HPACK draft 05.
- Support for HTTP/2.0 flow control.
- Verifies TLS certificates.
- Support for streaming uploads.
- Support for streaming downloads.


