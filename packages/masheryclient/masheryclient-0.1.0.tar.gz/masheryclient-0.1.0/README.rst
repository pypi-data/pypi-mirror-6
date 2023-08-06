==========================
Mashery API Client Library
==========================

A simple Python client library for the `Mashery API <http://support.mashery.com/docs/read/mashery_api>`_.


Example
=======

Query recently created apps:

.. code:: python

    from masheryclient.jsonrpc import MasheryJsonRpcApi

    json_rpc_api_client = MasheryJsonRpcApi(
        MASHERY_SITE_ID,
        MASHERY_SERVICE_KEY,
        MASHERY_API_KEY,
        MASHERY_API_SECRET
    )

    mashery_query = 'SELECT * FROM applications ORDER BY created DESC ITEMS 10'
    r = json_rpc_api_client.query(mashery_query)['items']

    for app in r:
        print app['name']

Top API callers within the specified time period:

.. code:: python

    reporting_client = MasheryReportingApi(
        MASHERY_SITE_ID,
        MASHERY_SERVICE_KEY,
        MASHERY_API_KEY,
        MASHERY_API_SECRET,
    )

    r = reporting_client.developer_activity_for_service(start_date_str, end_date_str, limit)

    app_list = []
    for app in r:
        api_key = app['serviceDevKey']
        call_count_success = app['callStatusSuccessful']
        call_count_blocked = app['callStatusBlocked']
        call_count_other = app['callStatusOther']
