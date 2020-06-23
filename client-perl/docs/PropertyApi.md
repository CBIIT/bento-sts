# WWW::OpenAPIClient::PropertyApi

## Load the API package
```perl
use WWW::OpenAPIClient::Object::PropertyApi;
```

All URIs are relative to *http://petstore.swagger.io/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_list_of_properties**](PropertyApi.md#get_list_of_properties) | **GET** /properties | List all properties
[**get_property_by_id**](PropertyApi.md#get_property_by_id) | **GET** /properties/{propertyId} | Get a property using ID


# **get_list_of_properties**
> Property get_list_of_properties()

List all properties

Returns a collection of properties 

### Example 
```perl
use Data::Dumper;
use WWW::OpenAPIClient::PropertyApi;
my $api_instance = WWW::OpenAPIClient::PropertyApi->new(
);


eval { 
    my $result = $api_instance->get_list_of_properties();
    print Dumper($result);
};
if ($@) {
    warn "Exception when calling PropertyApi->get_list_of_properties: $@\n";
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Property**](Property.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, text/plain

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_property_by_id**
> Property get_property_by_id(property_id => $property_id)

Get a property using ID

Returns a single property

### Example 
```perl
use Data::Dumper;
use WWW::OpenAPIClient::PropertyApi;
my $api_instance = WWW::OpenAPIClient::PropertyApi->new(
);

my $property_id = "property_id_example"; # string | ID of property to return

eval { 
    my $result = $api_instance->get_property_by_id(property_id => $property_id);
    print Dumper($result);
};
if ($@) {
    warn "Exception when calling PropertyApi->get_property_by_id: $@\n";
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **property_id** | **string**| ID of property to return | 

### Return type

[**Property**](Property.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, text/plain

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

