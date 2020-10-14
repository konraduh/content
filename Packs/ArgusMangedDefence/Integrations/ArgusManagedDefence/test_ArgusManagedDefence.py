BASE_URL = "https://api.mnemonic.no"
case_id = 1337


def test_is_valid_service():
    from ArgusManagedDefence import is_valid_service
    assert is_valid_service("ids")
    assert is_valid_service("support")
    assert is_valid_service("administrative")
    assert is_valid_service("advisory")
    assert is_valid_service("vulnscan")
    assert not is_valid_service("not_a_service")


def test_is_valid_case_type():
    from ArgusManagedDefence import is_valid_case_type
    assert is_valid_case_type("ids", "change")
    assert not is_valid_case_type("not_a_service", "change")
    assert not is_valid_case_type("ids", "not_a_type")


def test_add_case_tag(requests_mock):
    from ArgusManagedDefence import add_case_tag_command
    from argus_json import argus_case_data

    method_url = f"/cases/v2/case/{case_id}/tags"

    requests_mock.post(f"{BASE_URL}{method_url}", json=argus_case_data.ARGUS_CASE_TAGS)
    args = {"case_id": case_id, "key": "test_key", "value": "test_value"}
    result = add_case_tag_command(args)
    assert result.raw_response == argus_case_data.ARGUS_CASE_TAGS


def test_add_comment(requests_mock):
    from ArgusManagedDefence import add_comment_command
    from argus_json import argus_case_data

    method_url = f"/cases/v2/case/{case_id}/comments"

    requests_mock.post(f"{BASE_URL}{method_url}", json=argus_case_data.ARGUS_CASE_COMMENT)
    args = {"case_id": case_id, "comment": "test_comment"}
    result = add_comment_command(args)
    assert result.raw_response == argus_case_data.ARGUS_CASE_COMMENT


def test_advanced_case_search(requests_mock):
    from ArgusManagedDefence import advanced_case_search_command
    from argus_json import argus_case_data

    method_url = f"/cases/v2/case/search"

    requests_mock.post(f"{BASE_URL}{method_url}", json=argus_case_data.ARGUS_CASE_SEARCH_RESULT)
    result = advanced_case_search_command({})
    assert result.raw_response == argus_case_data.ARGUS_CASE_SEARCH_RESULT


def test_close_case(requests_mock):
    from ArgusManagedDefence import close_case_command
    from argus_json import argus_case_data

    method_url = f"/cases/v2/case/{case_id}/close"
    requests_mock.put(f"{BASE_URL}{method_url}", json=argus_case_data.ARGUS_CASE_METADATA)
    args = {"case_id": case_id}
    result = close_case_command(args)
    assert result.raw_response == argus_case_data.ARGUS_CASE_METADATA


def test_create_case(requests_mock):
    from ArgusManagedDefence import create_case_command
    from argus_json import argus_case_data

    method_url = f"/cases/v2/case/"

    requests_mock.post(f"{BASE_URL}{method_url}", json=argus_case_data.ARGUS_CASE_METADATA)
    args = {"case_id": case_id}
    result = create_case_command(args)
    assert result.raw_response == argus_case_data.ARGUS_CASE_METADATA


def test_delete_case(requests_mock):
    raise NotImplementedError


def test_delete_comment(requests_mock):
    raise NotImplementedError


def test_download_attachment(requests_mock):
    raise NotImplementedError


def test_edit_comment(requests_mock):
    raise NotImplementedError


def test_get_attachment(requests_mock):
    raise NotImplementedError


def test_get_case_metadata_by_id(requests_mock):
    raise NotImplementedError


def test_list_case_attachments(requests_mock):
    raise NotImplementedError


def test_list_case_tags(requests_mock):
    from ArgusManagedDefence import list_case_tags_command
    from argus_json import argus_case_data

    method_url = f"/cases/v2/case/{case_id}/tags"

    requests_mock.get(f"{BASE_URL}{method_url}", json=argus_case_data.ARGUS_CASE_TAGS)
    args = {"case_id": case_id}
    result = list_case_tags_command(args)
    assert result.raw_response == argus_case_data.ARGUS_CASE_TAGS


def test_list_case_comments(requests_mock):
    from ArgusManagedDefence import list_case_comments_command
    from argus_json import argus_case_data

    method_url = f"/cases/v2/case/{case_id}/comments"

    requests_mock.get(f"{BASE_URL}{method_url}", json=argus_case_data.ARGUS_CASE_COMMENTS_LIST)
    args = {"case_id": case_id}
    result = list_case_comments_command(args)
    assert result.raw_response == argus_case_data.ARGUS_CASE_COMMENTS_LIST


def test_remove_case_tag_by_key_value(requests_mock):
    raise NotImplementedError


def test_update_case(requests_mock):
    raise NotImplementedError


def test_get_events_for_case(requests_mock):
    raise NotImplementedError


def test_list_aggregated_events(requests_mock):
    raise NotImplementedError


def test_get_payload(requests_mock):
    raise NotImplementedError


def test_get_pcap(requests_mock):
    raise NotImplementedError


def test_search_records(requests_mock):
    raise NotImplementedError


def test_fetch_observations_for_domain(requests_mock):
    raise NotImplementedError


def test_fetch_observations_for_i_p(requests_mock):
    raise NotImplementedError

