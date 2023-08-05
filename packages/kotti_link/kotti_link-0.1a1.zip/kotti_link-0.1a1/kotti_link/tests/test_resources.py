from kotti.resources import get_root
from kotti.testing import DummyRequest

from kotti_link.resources import Link


def test_link(db_session, config):

    root = get_root()
    content = Link(link='')
    # assert content.type_info.addable(content, DummyRequest()) is True
    root['content'] = content
