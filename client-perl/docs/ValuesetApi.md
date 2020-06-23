# WWW::OpenAPIClient::ValuesetApi

## Load the API package
```perl
use WWW::OpenAPIClient::Object::ValuesetApi;
```

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
```perl
use Data::Dumper;
use WWW::OpenAPIClient::ValuesetApi;
my $api_instance = WWW::OpenAPIClient::ValuesetApi->new(
);


eval { 
    my $result = $api_instance->get_list_of_value_sets();
    print Dumper($result);
};
if ($@) {
    warn "Exception when calling ValuesetApi->get_list_of_value_sets: $@\n";
}
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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_value_set_by_id**
> Term get_value_set_by_id(valueset_id => $valueset_id)

Get a value set using ID

Returns a single value set

### Example 
```perl
use Data::Dumper;
use WWW::OpenAPIClient::ValuesetApi;
my $api_instance = WWW::OpenAPIClient::ValuesetApi->new(
);

my $valueset_id = "valueset_id_example"; # string | ID of value set to return

eval { 
    my $result = $api_instance->get_value_set_by_id(valueset_id => $valueset_id);
    print Dumper($result);
};
if ($@) {
    warn "Exception when calling ValuesetApi->get_value_set_by_id: $@\n";
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **valueset_id** | **string**| ID of value set to return | 

### Return type

[**Term**](Term.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

