# WWW::OpenAPIClient::TermApi

## Load the API package
```perl
use WWW::OpenAPIClient::Object::TermApi;
```

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
```perl
use Data::Dumper;
use WWW::OpenAPIClient::TermApi;
my $api_instance = WWW::OpenAPIClient::TermApi->new(
);


eval { 
    my $result = $api_instance->get_list_of_terms();
    print Dumper($result);
};
if ($@) {
    warn "Exception when calling TermApi->get_list_of_terms: $@\n";
}
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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_termy_by_id**
> InlineResponse2001 get_termy_by_id(term_id => $term_id)

Get a property using ID

Returns a single property

### Example 
```perl
use Data::Dumper;
use WWW::OpenAPIClient::TermApi;
my $api_instance = WWW::OpenAPIClient::TermApi->new(
);

my $term_id = "term_id_example"; # string | ID of term to return

eval { 
    my $result = $api_instance->get_termy_by_id(term_id => $term_id);
    print Dumper($result);
};
if ($@) {
    warn "Exception when calling TermApi->get_termy_by_id: $@\n";
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **term_id** | **string**| ID of term to return | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, text/plain

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

