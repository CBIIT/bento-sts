# WWW::OpenAPIClient::NodeApi

## Load the API package
```perl
use WWW::OpenAPIClient::Object::NodeApi;
```

All URIs are relative to *http://petstore.swagger.io/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_list_of_nodes**](NodeApi.md#get_list_of_nodes) | **GET** /nodes | List all nodes 


# **get_list_of_nodes**
> Node get_list_of_nodes(model_id => $model_id)

List all nodes 

Returns a collection of nodes

### Example 
```perl
use Data::Dumper;
use WWW::OpenAPIClient::NodeApi;
my $api_instance = WWW::OpenAPIClient::NodeApi->new(
);

my $model_id = "model_id_example"; # string | limit to nodes belonging to this model 

eval { 
    my $result = $api_instance->get_list_of_nodes(model_id => $model_id);
    print Dumper($result);
};
if ($@) {
    warn "Exception when calling NodeApi->get_list_of_nodes: $@\n";
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_id** | **string**| limit to nodes belonging to this model  | [optional] 

### Return type

[**Node**](Node.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, text/plain

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

