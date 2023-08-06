Changelog
=========

1.3.0
-----
    - Changed internal way of handling AMQP communication. This shouldn't change user API.
    - Documentation updated to reflect changes in internal API. Added UML diagrams.

1.2.2
-----
    - Documentation updated. Added intersphinx links to edeposit.amqp.serializers.

1.2.1
-----
    - edeposit.amqp.serializers API changed, so this module needed to be adjusted.

1.2.0
-----
    - Serialization is now handled (but not stored) in this module, instead of aleph. It will be used in other modules too.
    - Added dependency to edeposit.amqp.serializers.

1.1.6
-----
    - Documentation is now even for settings.py's attributes.
    - User defined JSON configuration is now supported.

1.1.5
-----
    - Added autogeneration of documentation to the package generator (setup.py).

1.1.0
-----
    - Project released at PYPI

1.0 (unreleased)
----------------
    - alephdaemon is working correctly, other classes are in release state too