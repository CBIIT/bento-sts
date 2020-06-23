# WWW::OpenAPIClient::ModelApi

## Load the API package
```perl
use WWW::OpenAPIClient::Object::ModelApi;
```

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
```perl
use Data::Dumper;
use WWW::OpenAPIClient::ModelApi;
my $api_instance = WWW::OpenAPIClient::ModelApi->new(
);


eval { 
    my $result = $api_instance->get_list_of_models();
    print Dumper($result);
};
if ($@) {
    warn "Exception when calling ModelApi->get_list_of_models: $@\n";
}
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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_model_by_id**
> InlineResponse200 get_model_by_id(model_id => $model_id)

find model by ID

Returns a single model

### Example 
```perl
use Data::Dumper;
use WWW::OpenAPIClient::ModelApi;
my $api_instance = WWW::OpenAPIClient::ModelApi->new(
);

my $model_id = "model_id_example"; # string | 

eval { 
    my $result = $api_instance->get_model_by_id(model_id => $model_id);
    print Dumper($result);
};
if ($@) {
    warn "Exception when calling ModelApi->get_model_by_id: $@\n";
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **string**|  | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, text/plain

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

