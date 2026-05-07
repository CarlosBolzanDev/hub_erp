"""Controlled Flask facade prepared for VoltPy web apps."""

from voltpy.importing.hook import import_real_module

_flask = import_real_module("flask")

Flask = _flask.Flask
Blueprint = _flask.Blueprint
jsonify = _flask.jsonify
request = _flask.request

__all__ = ["Flask", "Blueprint", "jsonify", "request"]
