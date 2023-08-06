import requests


def test_pagination(webapp, page_size):
    object_ids = [obj["id"] for obj in webapp.get_all_paged(page_size)]
    assert object_ids == list(range(1, webapp.num_objects + 1))

def test_pagination_different_renderer(webapp, page_size):
    assert webapp.get_all_paged(page_size, path="objects_different_renderer") == [{"id_value": i} for i in range(1, webapp.num_objects + 1)]

def test_pagination_max_page_size(webapp):
    resp = requests.get(webapp.url.add_path("objects_limited_page_size").set_query_param("page_size", "11"))
    assert resp.status_code == requests.codes.bad_request

def test_pagination_default_page_size(webapp):
    resp = requests.get(webapp.url.add_path("objects_limited_page_size"))
    resp.raise_for_status()
    assert len(resp.json()["result"]) == 5
