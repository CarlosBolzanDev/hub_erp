"""VoltPy HTTP facade wrapping requests."""

from importing.hook import import_real_module

_requests = import_real_module("requests")

get = _requests.get
post = _requests.post
put = _requests.put
delete = _requests.delete
Session = _requests.Session

__all__ = ["get", "post", "put", "delete", "Session"]
