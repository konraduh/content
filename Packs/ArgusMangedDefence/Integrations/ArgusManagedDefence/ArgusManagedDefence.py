import demistomock as demisto
from CommonServerPython import *

import json
import urllib3
import dateparser
import traceback
from typing import Any, Dict, Tuple, List, Optional, Union, cast

from argus_cli.utils import formatting  # Common helper for creating nice outputs
from argus_cli.settings import settings

from argus_api.api.currentuser.v1.user import get_current_user

from argus_api.api.cases.v2.case import (
    add_case_tag,
    add_comment,
    advanced_case_search,
    close_case,
    create_case,
    delete_case,
    delete_comment,
    download_attachment,
    edit_comment,
    get_attachment,
    get_case_metadata_by_id,
    list_case_attachments,
    list_case_tags,
    list_case_comments,
    remove_case_tag_by_key_value,
    update_case,
)

from argus_api.api.events.v1.case.case import get_events_for_case
from argus_api.api.events.v1.aggregated import list_aggregated_events
from argus_api.api.events.v1.payload import get_payload
from argus_api.api.events.v1.pcap import get_pcap

from argus_api.api.pdns.v3.search import search_records

from argus_api.api.reputation.v1.observation import (
    fetch_observations_for_domain,
    fetch_observations_for_i_p,
)


# Disable insecure warnings
urllib3.disable_warnings()


""" CONSTANTS """


DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
MAX_INCIDENTS_TO_FETCH = 50
FETCH_TAG = demisto.params().get("fetch_tag")

""" CLIENT CLASS """


""" HELPER FUNCTIONS """


def set_argus_settings(api_key, api_url):
    settings["api"]["api_key"] = api_key
    settings["api"]["api_url"] = api_url


def argus_priority_to_demisto_severity(priority: str) -> int:
    mapping = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    return mapping.get(priority, 0)


def argus_status_to_demisto_status(status: str) -> int:
    mapping = {
        "pendingCustomer": 0,
        "pendingSoc": 0,
        "pendingVendor": 0,
        "pendingClose": 0,
        "workingSoc": 1,
        "workingCustomer": 1,
        "closed": 2,
    }
    return mapping.get(status, 0)


""" COMMAND FUNCTIONS """


def test_module_command() -> str:
    response = get_current_user()
    if response["responseCode"] == 200:
        return "ok"
    else:
        return_error(
            "Unable to communicate with Argus API", response["responseCode"], response
        )


def fetch_incidents(last_run: dict, first_fetch_period: str):
    raise NotImplementedError


def add_case_tag_command(args: Dict[str, Any]) -> CommandResults:
    case_id = args.get("case_id", None)
    key = args.get("key", None)
    value = args.get("value", None)
    if not case_id:
        raise ValueError("case_id not specified")
    if not key:
        raise ValueError("key not specified")
    if not value:
        raise ValueError("value not specified")
    tag = {"key": key, "value": value}
    result = add_case_tag(caseID=case_id, tags=tag)
    # tags = {key: result['data'][0][key] for key in result['data'][0].keys() & {'key', 'value', 'addedTimestamp'}}
    headers = ["key", "value", "addedTime"]
    readable_output = tableToMarkdown(
        f"#{case_id}: Tags", result["data"], headers=headers
    )

    return CommandResults(readable_output=readable_output, outputs=result)


def add_comment_command(args: Dict[str, Any]) -> CommandResults:
    case_id = args.get("case_id", None)
    comment = args.get("comment", None)
    as_reply_to = args.get("as_reply_to", None)
    internal = args.get("internal", None)
    origin_email_address = args.get("origin_email_address", None)
    associated_attachment_id = args.get("associated_attachement_id", None)
    if not case_id:
        raise ValueError("case_id not specified")
    if not comment:
        raise ValueError("comment not specified")
    result = add_comment(
        caseID=case_id,
        comment=comment,
        asReplyTo=as_reply_to,
        internal=internal,
        originEmailAddress=origin_email_address,
        associatedAttachmentID=associated_attachment_id,
    )
    readable_output = f"# #{case_id}: Added comment\n"
    readable_output += f"#### *{result['data']['addedByUser']['userName']} - {result['data']['addedTime']}*\n"
    readable_output += f"{result['data']['comment']}"

    return CommandResults(readable_output=readable_output, outputs=result)


def advanced_case_search_command(args: Dict[str, Any]) -> CommandResults:
    start_timestamp = args.get("start_timestamp", None)
    end_timestamp = args.get("end_timestamp", None)
    limit = args.get("limit", None)
    offset = args.get("offset", None)
    include_deleted = args.get("include_deleted", None)
    sub_criteria = args.get("sub_criteria", None)
    exclude = args.get("exclude", None)
    required = args.get("required", None)
    customer_id = args.get("customer_id", None)
    case_id = args.get("case_id", None)
    customer = args.get("customer", None)
    case_type = args.get("type", None)
    service = args.get("service", None)
    category = args.get("category", None)
    status = args.get("status", None)
    priority = args.get("priority", None)
    asset_id = args.get("asset_id", None)
    tag = args.get("tag", None)
    workflow = args.get("workflow", None)
    field = args.get("field", None)
    keywords = args.get("keywords", None)
    time_field_strategy = args.get("time_field_strategy", None)
    time_match_strategy = args.get("time_match_strategy", None)
    keyword_field_strategy = args.get("keyword_field_strategy", None)
    keyword_match_strategy = args.get("keyword_match_strategy", None)
    user = args.get("user", None)
    user_field_strategy = args.get("user_field_strategy", None)
    user_assigned = args.get("user_assigned", None)
    tech_assigned = args.get("tech_assigned", None)
    include_workflows = args.get("include_workflows", None)
    include_description = args.get("include_description", None)
    access_mode = args.get("access_mode", None)
    explicit_access = args.get("explicit_access", None)
    sort_by = args.get("sort_by", None)
    include_flags = args.get("include_flags", None)
    exclude_flags = args.get("exclude_flags", None)

    result = advanced_case_search(
        startTimestamp=start_timestamp,
        endTimestamp=end_timestamp,
        limit=limit,
        offset=offset,
        includeDeleted=include_deleted,
        subCriteria=sub_criteria,
        exclude=exclude,
        required=required,
        customerID=customer_id,
        caseID=case_id,
        customer=customer,
        type=case_type,
        service=service,
        category=category,
        status=status,
        priority=priority,
        assetID=asset_id,
        tag=tag,
        workflow=workflow,
        field=field,
        keywords=keywords,
        timeFieldStrategy=time_field_strategy,
        timeMatchStrategy=time_match_strategy,
        keywordFieldStrategy=keyword_field_strategy,
        keywordMatchStrategy=keyword_match_strategy,
        user=user,
        userFieldStrategy=user_field_strategy,
        userAssigned=user_assigned,
        techAssigned=tech_assigned,
        includeWorkflows=include_workflows,
        includeDescription=include_description,
        accessMode=access_mode,
        explicitAccess=explicit_access,
        sortBy=sort_by,
        includeFlags=include_flags,
        excludeFlags=exclude_flags,
    )
    return CommandResults(readable_output=tableToMarkdown("Result", result["data"]), outputs=result)


def close_case_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


def create_case_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


def delete_case_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


def delete_comment_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


def download_attachment_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


def edit_comment_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


def get_attachment_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


def get_case_metadata_by_id_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


def list_case_attachments_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


def list_case_tags_command(args: Dict[str, Any]) -> CommandResults:
    case_id = args.get("case_id", None)
    limit = args.get("limit", None)
    offset = args.get("offset", None)
    if not case_id:
        raise ValueError("case_id not specified")
    result = list_case_tags(caseID=case_id, limit=limit, offset=offset)
    headers = ["key", "value", "addedTime"]
    readable_output = tableToMarkdown(
        f"#{case_id}: Tags", result["data"], headers=headers
    )
    return CommandResults(readable_output=readable_output, outputs=result)


def list_case_comments_command(args: Dict[str, Any]) -> CommandResults:
    case_id = args.get("case_id", None)
    before_comment = args.get("before_comment", None)
    after_comment = args.get("after_comment", None)
    offset = args.get("offset", None)
    limit = args.get("limit", None)
    sort_by = args.get("sort_by", None)
    if not case_id:
        raise ValueError("case_id not specified")
    if sort_by:
        sort_by = ["addedTimestamp"] if sort_by == "ascending" else ["-addedTimestamp"]
    result = list_case_comments(
        caseID=case_id,
        beforeComment=before_comment,
        afterComment=after_comment,
        offset=offset,
        limit=limit,
        sortBy=sort_by,
    )
    readable_output = f"# #{case_id}: Comments\n"
    for comment in result["data"]:
        readable_output += f"#### *{comment['addedByUser']['userName']} - {comment['addedTime']}*\n"
        readable_output += f"{comment['comment']}\n\n"

    return CommandResults(readable_output=readable_output, outputs=result)


def remove_case_tag_by_key_value_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


def update_case_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


def get_events_for_case_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


def list_aggregated_events_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


def get_payload_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


def get_pcap_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


def search_records_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


def fetch_observations_for_domain_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


def fetch_observations_for_i_p_command(args: Dict[str, Any]) -> CommandResults:
    raise NotImplementedError


""" MAIN FUNCTION """


def main() -> None:
    # TODO test argus-cli
    verify_certificate = not demisto.params().get("insecure", False)
    proxy = demisto.params().get("proxy", False)

    first_fetch_period = demisto.params().get("first_fetch_period", "1 day")

    demisto.debug(f"Command being called is {demisto.command()}")
    try:

        set_argus_settings(
            demisto.params().get("api_key"), demisto.params().get("api_url")
        )

        if demisto.command() == "test-module":
            # This is the call made when pressing the integration Test button.
            return_results(test_module_command())

        elif demisto.command() == "fetch-incidents":
            # Set and define the fetch incidents command to run after activated via integration settings.
            next_run, incidents = fetch_incidents(
                last_run=demisto.getLastRun(),
                first_fetch_period=first_fetch_period,
            )

            demisto.setLastRun(next_run)
            demisto.incidents(incidents)

        elif demisto.command() == "argus_add_case_tag":
            return_results(add_case_tag_command(demisto.args()))

        elif demisto.command() == "argus_add_comment":
            return_results(add_comment_command(demisto.args()))

        elif demisto.command() == "argus_advanced_case_search":
            return_results(advanced_case_search_command(demisto.args()))

        elif demisto.command() == "argus_close_case":
            return_results(close_case_command(demisto.args()))

        elif demisto.command() == "argus_create_case":
            return_results(create_case_command(demisto.args()))

        elif demisto.command() == "argus_delete_case":
            return_results(delete_case_command(demisto.args()))

        elif demisto.command() == "argus_delete_comment":
            return_results(delete_comment_command(demisto.args()))

        elif demisto.command() == "argus_download_attachment":
            return_results(download_attachment_command(demisto.args()))

        elif demisto.command() == "argus_edit_comment":
            return_results(edit_comment_command(demisto.args()))

        elif demisto.command() == "argus_get_attachment":
            return_results(get_attachment_command(demisto.args()))

        elif demisto.command() == "argus_get_case_metadata_by_id":
            return_results(get_case_metadata_by_id_command(demisto.args()))

        elif demisto.command() == "argus_list_case_attachments":
            return_results(list_case_attachments_command(demisto.args()))

        elif demisto.command() == "argus_list_case_tags":
            return_results(list_case_tags_command(demisto.args()))

        elif demisto.command() == "argus_list_case_comments":
            return_results(list_case_comments_command(demisto.args()))

        elif demisto.command() == "argus_remove_case_tag_by_key_value":
            return_results(remove_case_tag_by_key_value_command(demisto.args()))

        elif demisto.command() == "argus_update_case":
            return_results(update_case_command(demisto.args()))

        elif demisto.command() == "argus_get_events_for_case":
            return_results(get_events_for_case_command(demisto.args()))

        elif demisto.command() == "argus_list_aggregated_events":
            return_results(list_aggregated_events_command(demisto.args()))

        elif demisto.command() == "argus_get_payload":
            return_results(get_payload_command(demisto.args()))

        elif demisto.command() == "argus_get_pcap":
            return_results(get_pcap_command(demisto.args()))

        elif demisto.command() == "argus_search_records":
            return_results(search_records_command(demisto.args()))

        elif demisto.command() == "argus_fetch_observations_for_domain ":
            return_results(fetch_observations_for_domain_command(demisto.args()))

        elif demisto.command() == "argus_fetch_observations_for_i_p":
            return_results(fetch_observations_for_i_p_command(demisto.args()))

    # Log exceptions and return errors
    except Exception as e:
        demisto.error(traceback.format_exc())  # print the traceback
        return_error(
            f"Failed to execute {demisto.command()} command.\nError:\n{str(e)}"
        )


""" ENTRY POINT """


if __name__ in ("__main__", "__builtin__", "builtins"):
    main()
