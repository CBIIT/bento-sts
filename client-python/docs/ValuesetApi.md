# openapi_client.ValuesetApi

All URIs are relative to *http://petstore.swagger.io/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_list_of_value_sets**](ValuesetApi.md#get_list_of_value_sets) | **GET** /valuesets | List all Value Sets
[**get_value_set_by_id**](ValuesetApi.md#get_value_set_by_id) | **GET** /valuesets/{valuesetId} | Get a value set using ID


# **get_list_of_value_sets**
> ValueSet get_list_of_value_sets()

List all Value Sets

Returns a collection of value sets

### Example

```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://petstore.swagger.io/v2
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://petstore.swagger.io/v2"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ValuesetApi(api_client)
    
    try:
        # List all Value Sets
        api_response = api_instance.get_list_of_value_sets()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ValuesetApi->get_list_of_value_sets: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ValueSet**](ValueSet.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, text/plain

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | successful operation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_value_set_by_id**
> Term get_value_set_by_id(valueset_id)

Get a value set using ID

Returns a single value set

### Example

```python
from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint
# Defining the host is optional and defaults to http://petstore.swagger.io/v2
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://petstore.swagger.io/v2"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.ValuesetApi(api_client)
    valueset_id = 'valueset_id_example' # str | ID of value set to return

    try:
        # Get a value set using ID
        api_response = api_instance.get_value_set_by_id(valueset_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ValuesetApi->get_value_set_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **valueset_id** | **str**| ID of value set to return | 

### Return type

[**Term**](Term.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | successful operation |  -  |
**400** | Invalid ID supplied |  -  |
**404** | Value set not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

