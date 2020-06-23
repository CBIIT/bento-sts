# WWW::OpenAPIClient::DefaultApi

## Load the API package
```perl
use WWW::OpenAPIClient::Object::DefaultApi;
```

All URIs are relative to *http://petstore.swagger.io/v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_node_by_id**](DefaultApi.md#get_node_by_id) | **GET** /nodes/{nodeId} | Find node by ID


# **get_node_by_id**
> Node get_node_by_id(node_id => $node_id)

Find node by ID

Returns a single node

### Example 
```perl
use Data::Dumper;
use WWW::OpenAPIClient::DefaultApi;
my $api_instance = WWW::OpenAPIClient::DefaultApi->new(
);

my $node_id = 789; # int | ID of node to return

eval { 
    my $result = $api_instance->get_node_by_id(node_id => $node_id);
    print Dumper($result);
};
if ($@) {
    warn "Exception when calling DefaultApi->get_node_by_id: $@\n";
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **node_id** | **int**| ID of node to return | 

### Return type

[**Node**](Node.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, text/plain

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

