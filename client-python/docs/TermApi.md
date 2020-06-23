# openapi_client.TermApi

All URIs are relative to *http://petstore.swagger.io/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_list_of_terms**](TermApi.md#get_list_of_terms) | **GET** /terms | List all terms
[**get_termy_by_id**](TermApi.md#get_termy_by_id) | **GET** /terms/{termId} | Get a property using ID


# **get_list_of_terms**
> Term get_list_of_terms()

List all terms

Returns a collection of terms

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
    api_instance = openapi_client.TermApi(api_client)
    
    try:
        # List all terms
        api_response = api_instance.get_list_of_terms()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling TermApi->get_list_of_terms: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Term**](Term.md)

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

# **get_termy_by_id**
> InlineResponse2001 get_termy_by_id(term_id)

Get a property using ID

Returns a single property

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
    api_instance = openapi_client.TermApi(api_client)
    term_id = 'term_id_example' # str | ID of term to return

    try:
        # Get a property using ID
        api_response = api_instance.get_termy_by_id(term_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling TermApi->get_termy_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **term_id** | **str**| ID of term to return | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, text/plain

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | successful operation |  -  |
**400** | Invalid ID supplied |  -  |
**404** | Term not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

