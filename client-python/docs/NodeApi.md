# openapi_client.NodeApi

All URIs are relative to *http://petstore.swagger.io/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_list_of_nodes**](NodeApi.md#get_list_of_nodes) | **GET** /nodes | List all nodes 


# **get_list_of_nodes**
> Node get_list_of_nodes(model_id=model_id)

List all nodes 

Returns a collection of nodes

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
    api_instance = openapi_client.NodeApi(api_client)
    model_id = 'model_id_example' # str | limit to nodes belonging to this model  (optional)

    try:
        # List all nodes 
        api_response = api_instance.get_list_of_nodes(model_id=model_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling NodeApi->get_list_of_nodes: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**| limit to nodes belonging to this model  | [optional] 

### Return type

[**Node**](Node.md)

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

