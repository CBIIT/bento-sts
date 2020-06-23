# openapi_client.ModelApi

All URIs are relative to *http://petstore.swagger.io/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_list_of_models**](ModelApi.md#get_list_of_models) | **GET** /models | List all models
[**get_model_by_id**](ModelApi.md#get_model_by_id) | **GET** /models/{modelId} | find model by ID


# **get_list_of_models**
> Model get_list_of_models()

List all models

Returns a collection of models 

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
    api_instance = openapi_client.ModelApi(api_client)
    
    try:
        # List all models
        api_response = api_instance.get_list_of_models()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ModelApi->get_list_of_models: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Model**](Model.md)

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

# **get_model_by_id**
> InlineResponse200 get_model_by_id(model_id)

find model by ID

Returns a single model

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
    api_instance = openapi_client.ModelApi(api_client)
    model_id = 'model_id_example' # str | 

    try:
        # find model by ID
        api_response = api_instance.get_model_by_id(model_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ModelApi->get_model_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **str**|  | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

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
**404** | Model not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

