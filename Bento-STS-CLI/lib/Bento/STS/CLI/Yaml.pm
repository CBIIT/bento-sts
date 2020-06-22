package Bento::STS::CLI::Yaml;

use warnings;
no warnings qw(regexp deprecated);
use strict;
use Carp;
use List::MoreUtils qw(uniq);

use lib '/Users/bensonml/0_SRC/bento-meta/perl/lib';
use Bento::Meta;
use Bento::Meta::Model;


sub get_yaml_node_section{
    my ($model) =@_ ;
  
    # return this string;
    my $yaml_node_section = "\nNodes:";

    ### internal data structures
    # -  @nodehandles_unsorted is self explanatory
    # and for easier manipulation: (using nodehandle as key for each hash)
    # -  %props_for_node will hold all of the prop data
    # -  %cat_for_node will hold all of the cat data
    
    ## Get data
    # 1. get data, load into above structures
    # 2. sort the nodes by handle, 
    ## Format
    # 3. then use the sorted nodes, 
    # 4. to get sorted props for each node 
    # 5. to get categories
    my @nodehandles_unsorted = ();
    my %props_for_node = ();
    my %cat_for_node   = ();

    ## Get data (1,2)
    # get data for nodes, and load the contents into %props_for_node
    my @model_nodes = $model->nodes();
    foreach my $node (@model_nodes) {
        # get node.handle
        my $node_handle = $node->handle();
        push @nodehandles_unsorted, $node_handle;
       
        # get node.category
        my $node_category = $node->category();
        if ($node_category) {
            $cat_for_node{$node_handle} = $node_category;
        }

        # get node -> props
        my @prop_handles_unsorted = ();
        my @props = $node->props();
        foreach my $prop (@props){
            push @prop_handles_unsorted, $prop->handle();
        }
        $props_for_node{$node_handle} = [ sort @prop_handles_unsorted ]; 
    }

    ## Format (3,4,5)
    # now order the nodes by handle, and get their props
    foreach my $nodehandle (sort @nodehandles_unsorted) {
        # add node
        $yaml_node_section .= "\n  $nodehandle:";
       
        # add category
        if (exists ($cat_for_node{$nodehandle})) {
            $yaml_node_section .= "\n    Category: ";
            $yaml_node_section .= $cat_for_node{$nodehandle};
        }

        # add prop
        $yaml_node_section .= "\n    Props:";
        if (scalar ( @{$props_for_node{$nodehandle}} ) ){
            foreach my $prop ( @{$props_for_node{$nodehandle}} ){
                # add prop
                $yaml_node_section .= "\n      - $prop";
            }
        }else{
            # handle case where no properties were found...
            $yaml_node_section .= " null";
        }
    }

    return $yaml_node_section;
}

sub get_yaml_relationship_section{
    my ($model) =@_ ;
  
    # return this string;
    my $yaml_rel_section = "\nRelationships:";

    ### internal data structures
    # -  @rel_unsorted is self explanatory
    # and for easier manipulation: (using rel as key for each hash)
    # -  %ends_for_rel will hold all of the ends (src/dst) data
    # -  %mul_for_rel will hold all of the multiplicity data
    
    ## Get data
    # 1. get data, load into above structures
    # 2. sort the rels by handle, 
    ## Format
    # 3. then use the sorted rel, 
    # 4. to get sorted ends for each rel 
    # 5. to get multiplicity
    my @relhandles_unsorted = ();
    my %ends_for_rel = ();
    my %props_for_rel = ();
    my %mult_for_rel = ();

    ## Get data (1,2)
    # get data for nodes, and load the contents into %props_for_node
    my @model_relationships = $model->edges();
    foreach my $relationship (@model_relationships) {
        # get rel.handle
        my $relationship_handle = $relationship->handle();
        push @relhandles_unsorted, $relationship_handle;
       
        # get rel.multiplicity
        my $relationship_multiplicity = $relationship->multiplicity();
        if ($relationship_multiplicity) {
            $mult_for_rel{$relationship_handle} = $relationship_multiplicity;
        }

        ## get rel -> src node and dst node
        my $src = $relationship->src()->handle();
        my $dst = $relationship->dst()->handle();
        my $end_parts_href = { src => $src, dst => $dst }; 

        unless (defined  ($ends_for_rel{$relationship_handle})){
              $ends_for_rel{$relationship_handle} = [];
        }
        push @{$ends_for_rel{$relationship_handle}}, $end_parts_href;

        # get rel -> props
        my @prop_handles_unsorted = ();
        my @props = $relationship->props();
        foreach my $prop (@props){
            push @prop_handles_unsorted, $prop->handle();
        }
        $props_for_rel{$relationship_handle} = [ sort @prop_handles_unsorted ]; 


    }

    ## Format (3,4,5)
    # now order the relationships by handle, and get their mult and ends
    my @relhandles_sortedwdupes = sort(@relhandles_unsorted);
    my @relhandles = uniq(@relhandles_sortedwdupes);
    foreach my $relhandle (@relhandles) {
        # add rel
        $yaml_rel_section .= "\n  $relhandle:";
       
        # add multiplicity
        if (exists ($mult_for_rel{$relhandle})) {
            $yaml_rel_section .= "\n    Mul: ";
            $yaml_rel_section .= $mult_for_rel{$relhandle};
        }

        ## add ends
        $yaml_rel_section .= "\n    Ends: ";
        foreach my $end_href ( @{$ends_for_rel{$relhandle}} ) {
            $yaml_rel_section .= "\n      - Src: " . $end_href->{'src'};
            $yaml_rel_section .= "\n        Dst: " . $end_href->{'dst'};
        }
        
        # add prop
        $yaml_rel_section .= "\n    Props:";
        if (scalar ( @{$props_for_rel{$relhandle}} ) ){
            foreach my $prop ( @{$props_for_rel{$relhandle}} ){
                # add prop
                $yaml_rel_section .= "\n      - $prop";
            }
        }else{
            # handle case where no properties were found...
            $yaml_rel_section .= " null";
        }

    }

    return $yaml_rel_section;
}



sub get_model_yaml {
    my ($model) = @_;

    my $yaml;

    # construct yaml
    $yaml .= get_yaml_header($model);
    $yaml .= get_yaml_node_section($model);
    $yaml .= get_yaml_relationship_section($model);

    return $yaml;
}

sub get_yaml_header {
    my ($model) = @_;

    my $model_handle = $model->handle();
    my $header = '# ' . $model_handle ;
    return $header;
}


1; # Magic true value required at end of module
__END__

=head1 NAME

Bento::STS::CLI - [One line description of module's purpose here]
