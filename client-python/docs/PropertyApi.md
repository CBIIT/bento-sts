# openapi_client.PropertyApi

All URIs are relative to *http://petstore.swagger.io/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_list_of_properties**](PropertyApi.md#get_list_of_properties) | **GET** /properties | List all properties
[**get_property_by_id**](PropertyApi.md#get_property_by_id) | **GET** /properties/{propertyId} | Get a property using ID


# **get_list_of_properties**
> ModelProperty get_list_of_properties()

List all properties

Returns a collection of properties 

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
    api_instance = openapi_client.PropertyApi(api_client)
    
    try:
        # List all properties
        api_response = api_instance.get_list_of_properties()
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling PropertyApi->get_list_of_properties: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ModelProperty**](ModelProperty.md)

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

# **get_property_by_id**
> ModelProperty get_property_by_id(property_id)

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
    api_instance = openapi_client.PropertyApi(api_client)
    property_id = 'property_id_example' # str | ID of property to return

    try:
        # Get a property using ID
        api_response = api_instance.get_property_by_id(property_id)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling PropertyApi->get_property_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **property_id** | **str**| ID of property to return | 

### Return type

[**ModelProperty**](ModelProperty.md)

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
**404** | Property not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

