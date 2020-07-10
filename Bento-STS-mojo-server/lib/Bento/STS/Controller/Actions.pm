package Bento::STS::Controller::Actions;
use Mojo::Base 'Mojolicious::Controller';

# This action will render a template
sub welcome {
  my $self = shift;

  # Render template "example/welcome.html.ep" with message
  #$self->render(template => 'index', msg => 'Welcome to the Mojolicious real-time web framework!');
  $self->stash(msg => 'Welcome to the Simple Terminology Service (STS)', header => 'STS');
  $self->render(template => 'index');
}

sub about {
  my $self = shift;

  $self->render(msg =>  "Simple Terminology Service (STS) - verstion: 0.3.0");
}

############################################################
sub healthcheck {
  my $self = shift;

  # ----------------------------------------------
  # Part 1:
  # See if the Meta database is up by querying the neo4j version
  # we don't need to look at actual data, just check
  # if expected headers were returned
  
  # get subroutine_ref to exec Neo4j::Bolt's `run_query` (defined in sts.pm)
  # $h is anon hash, used for [$param_hash] in Neo4j::Bolt::Cxn
  # $h is empty (no parameters is being passed)
  my $h = {};
  my $run_query_sref = $self->get_database_version_sref;
  my $stream = $run_query_sref->($h);
 
  # check returned version (in headers)
  my $mdb_connection = 'fail';
  my @names = $stream->field_names;
  if (
    $names[0] eq 'name'
    && $names[1] eq 'version'
    && $names[2] eq 'edition'
  ) {
      $mdb_connection = 'ok';
  };

  # ----------------------------------------------
  # Part 2:
  # see if some data exists in MDB by simply counting nodes

  # get subroutine_ref to exec Neo4j::Bolt's `run_query` (defined in sts.pm)
  $run_query_sref = $self->get_database_node_count_sref;
  $stream = $run_query_sref->($h);

  # count nodes
  my $mdb_node_count;
  while ( my @row = $stream->fetch_next ) {
      $mdb_node_count = $row[0];
  }

  # ----------------------------------------------
  # done - now return
  my $healthcheck_response = {'MDB_CONNECTION' => $mdb_connection,
                              'MDB_NODE_COUNT' => $mdb_node_count };
  $self->render( json => $healthcheck_response );

}

sub getListOfModels {
  my $self = shift;

  # get subroutine_ref to exec Neo4j::Bolt's `run_query` (defined in sts.pm)
  # $h is anon hash, used for [$param_hash] in Neo4j::Bolt::Cxn
  # $h is empty (no parameters is being passed)
  my $h = {};
  my $run_query_sref = $self->get_list_of_models_sref;
  my $stream = $run_query_sref->($h);

  # now handle the query result
  my @data_ = ();
  while ( my @row = $stream->fetch_next ) {
    # no formatting right now, thank you
    push @data_, "$row[0]";
    print "found $row[0] \n";
  }


  # done - now return
  #$self->stash(list => ['ICDC', 'CTDC']);
  $self->stash(list => \@data_);
  $self->stash(header => 'MODELS');
  $self->stash(msg => 'List of All Models');
  $self->render(template => 'index');

}

sub getModelByName {
  my $self = shift;

  my $modelName = $self->stash('modelName');
  my $sanitizer = $self->sanitize_input_sref;
  $modelName = $sanitizer->($modelName); # simple sanitization
  $self->app->log->info("using model name  >$modelName<");

  # just make sure we have term to proceed, else return error 400
  unless ($modelName) {
     $self->render(json => { errmsg => "Missing or non-existent model name"},
                   status => 400);
     return;
  }

  # $h is anon hash, used for [$param_hash] in Neo4j::Bolt::Cxn
  my $h = { param => $modelName };
  
  # get subroutine_ref to exec Neo4j::Bolt's `run_query` (defined in sts.pm)
  my $run_query_sref = $self->get_model_by_name_sref;
  my $stream = $run_query_sref->($h);

  # now handle the query result
  my $model = '';
  while ( my @row = $stream->fetch_next ) {
    # no formatting right now, thank you
    $model = $row[0];
  }

  my $msg;
  if ($model) { 
      $msg = 'Single Model';
  } else {
      $msg = 'Model Not Found';
  }

  # done - now return
  $self->stash(list => [$model] );
  $self->stash(header => 'MODEL');
  $self->stash(msg => $msg);
  $self->render(template => 'index');

}

sub getListOfNodes {
  my $self = shift;

  # get subroutine_ref to exec Neo4j::Bolt's `run_query` (defined in sts.pm)
  # $h is anon hash, used for [$param_hash] in Neo4j::Bolt::Cxn
  # $h is empty (no parameters is being passed)
  
  my $h = {};
  my $run_query_sref = $self->get_list_of_nodes_sref;
  my $stream = $run_query_sref->($h);

  ## now handle the query result
  my @data_ = ();
  my $organized_nodes = {};
  while ( my @row = $stream->fetch_next ) {
    # no formatting right now, thank you

    my $id = $row[0];
    my $handle = $row[1];
    my $model = $row[2]; 
   
    ## approach 2: refactoring attempt (to organize by model)
    unless ( exists $organized_nodes->{ $model } ) {
        $organized_nodes->{$model} = [];
    }
    push @{$organized_nodes->{$model}}, [$id, $handle];

    ## approach 1: original basic list...
    my $set = [$row[0], $row[1], $row[2]];
    push @data_, $set;
  }

  ## approach 1: (will need to modulate return by return format requested)
  #$self->stash(nodes => \@data_);
  #$self->stash(header => 'nodes');
  #$self->stash(msg => 'List of Nodes');
  #$self->render(template => 'index');

  ## approach 2:
  # sort the results?
  foreach my $m (keys %{$organized_nodes}){
      my @unsorted = @{$organized_nodes->{$m}};
      my @sorted = sort { $a->[1] cmp $b->[1] } @unsorted;
      $organized_nodes->{$m} = \@sorted;
  }
  
  $self->stash(nodes => $organized_nodes);
  $self->stash(header => 'NODES');
  $self->stash(msg => 'List of All Nodes by Model');
  $self->render(template => 'index');


}

sub getNodeById {
  my $self = shift;

  my $nodeId = $self->stash('nodeId');
  my $sanitizer = $self->sanitize_input_sref;
  $nodeId = $sanitizer->($nodeId); # simple sanitization
  $self->app->log->info("using node id  >$nodeId<");

  # just make sure we have term to proceed, else return error 400
  unless ($nodeId) {
     $self->render(json => { errmsg => "Missing or non-existent node Id"},
                   status => 400);
     return;
  }

  # $h is anon hash, used for [$param_hash] in Neo4j::Bolt::Cxn
  my $h = { param => $nodeId };
  
  # get subroutine_ref to exec Neo4j::Bolt's `run_query` (defined in sts.pm)
  my $run_query_sref = $self->get_node_by_id_sref;
  my $stream = $run_query_sref->($h);

  # now handle the query result
  my $node = {};
  while ( my @row = $stream->fetch_next ) {
    # no formatting right now, thank you

        # see if we want from and to nodes handled
        # need to see if the exist before we can test
        my $from_node_exists = 0;
        if ( defined ($row[8])) {             # look at r2.nanoid6
                $from_node_exists = $row[7];  # add r12.handle
        }
        my $to_node_exists = 0;
        if ( defined ($row[4])) {             # look at r3.nanoid
                $to_node_exists = $row[3];    # add r31.handle
        }
        my $property_exists = 0;
        if ( defined ($row[11])) {
                $property_exists = 1;
        }

        unless (exists $node->{'node'}) {
            $node = { 'node' => { 'node-id'  => $row[0],
                                  'node-handle' => $row[1],
                                  'node-model' => $row[2] ,
                                  'has-concept' => {
                                          'concept-id' => $row[15] ,
                                          'represented-by' => {
                                              'term-id' => $row[16],
                                              'term-value' => $row[17],
                                              'term-origin_id' => $row[18],
                                              'term-origin_definition' => $row[19],
                                              'term-comments' => $row[20],
                                              'term-notes' => $row[21],
                                              'term-origin' => $row[22]
                                          }
                                    }
                                }
                    }
        };

        #  # only add if the X were found
          if ($from_node_exists) {
                
                # for the sake of ease of working in html/template land...
                ## if the list of from relationships array hasn't been started yet, 
                ## then make it an anon array to hold list of from_node_relationships
                unless ( exists $node->{'node'}->{'from_node_relationships'} ){
                    $node->{'node'}->{'from_node_relationships'} = [];
                }
                ## make a list of those 'from_node_relationships' that I have, to see
                ## if I need to add it...
                my %from_rels = map { $_ => 1 } @{$node->{'node'}->{'from_node_relationships'}};
                unless ( exists $from_rels{ $from_node_exists } ){
                    push @{$node->{'node'}->{'from_node_relationships'}} , $from_node_exists ;
                }
               
                # add to 'json' stuff for 'json-based-structure'
                unless ( exists $node->{'node'}->{$from_node_exists} ) {
                    $node->{'node'}->{$from_node_exists} = {
                                    'node-id'  => $row[8],
                                    'node-handle' => $row[9],
                                    'node-model' => $row[10] };
                }
            }


            if ($to_node_exists){
                
                # for the sake of ease of working in html/template land...
                ## if the list of to relationships array hasn't been started yet, 
                ## then make it an anon array to hold list of to_node_relationships
                unless ( exists $node->{'node'}->{'to_node_relationships'} ){
                    $node->{'node'}->{'to_node_relationships'} = [];
                }
                ## make a list of those 'to_node_relationships' that I have, to see
                ## if I need to add it...
                my %from_rels = map { $_ => 1 } @{$node->{'node'}->{'to_node_relationships'}};
                unless ( exists $from_rels{ $to_node_exists } ){
                    push @{$node->{'node'}->{'to_node_relationships'}}, $to_node_exists ;
                }

                # add to 'json' stuff for 'json-based-structure'
                unless (exists $node->{'node'}->{$to_node_exists} ) {
                  $node->{'node'}->{$to_node_exists} = {
                                    'node-id'  => $row[4],
                                    'node-handle' => $row[5],
                                    'node-model' => $row[6]};
                }
            }


            # property
            if ($property_exists) {
                unless (exists $node->{'node'}->{'has-property'}) {
                        $node->{'node'}->{'has-property'} = [];
                        $node->{'node'}->{'_seen-property'} = [];
                }
              # only add unique props
              my %seen = map { $_ => 1 } @{$node->{'node'}->{'_seen-property'}};
              unless (exists $seen{$row[11]} ) {
                  push @{$node->{'node'}->{'_seen-property'}}, $row[11];
                  my $prop = {'property-id' => $row[11],
                              'property-handle' => $row[12],
                              'property-value_domain' => $row[13],
                              'property-model' => $row[14] };
                  push @{$node->{'node'}->{'has-property'}}, $prop;
              }
            }



    print "\n\n\nnode is $row[0] ";
    print "\n\t1  n1.handle is " . $row[1] || "n/a";
    print "\n\t2  n1.model " . $row[2] || 'n/a';
    print "\n\t3  r12.handle as `to-relationship` " . ($row[3] || 'n/a');
    print "\n\t4  n2.nanoid6 as `to-node`" . ( $row[4] || 'n/a');
    print "\n\t5  n2.handle " . ( $row[5] || 'n/a');
    print "\n\t6  n2.model " .  ( $row[6] || 'n/a');
    print "\n\t7  r31.handle " . ( $row[7] || 'n/a') ;
    print "\n\t8  n3.nanoid6 " . ( $row[8] || 'n/a');
    print "\n\t9  n3.handle  " . ($row[9] || 'n/a');
    print "\n\t10 n3.model   " . ($row[10] || 'n/a');
    print "\n\t11 p1.nanoid6 " . ($row[11] || 'n/a');
    print "\n\t12 p1.handle  " . ($row[12] || 'n/a');
    print "\n\t13 p1.value_domain " . ( $row[13] || 'n/a');
    print "\n\t14 p1.model " . ( $row[14] || 'n/a');
    print "\n\t15 c1 .id " . ($row[15] || 'n/a');
    print "\n\t16 ct.nanoid6 " . ( $row[16] || 'n/a');
    print "\n\t17 ct.value " . ($row[17] || 'n/a') ;
    print "\n\t18 ct.origin_id " . ( $row[18] || 'n/a') ;
    print "\n\t19 ct.origin_definition " . ( $row[19] || 'n/a' );
    print "\n\t20 ct.comments " . ( $row[20] || 'n/a' ) ;
    print "\n\t21 ct.notes " . ( $row[21] || 'n/a' ) ;
    print "\n\t22 o.name " .  ( $row[22] || 'n/a' ) ;
  }

                  print "\n\n yes! \n\n";
                  use Data::Dumper;
                  print Dumper($node->{'node'}->{'has-property'});

  my $msg;
  if ($node) { 
      $msg = 'Details for a Single Node';
  } else {
      $msg = 'Node Not Found';
  }

  # done - now return
  $self->stash(list => $node );
  $self->stash(header => 'NODE');
  $self->stash(msg => $msg);
  $self->render(template => 'nodes');

}


sub getListOfValuesets {
  my $self = shift;

  # get subroutine_ref to exec Neo4j::Bolt's `run_query` (defined in sts.pm)
  # $h is anon hash, used for [$param_hash] in Neo4j::Bolt::Cxn
  # $h is empty (no parameters is being passed)
  my $h = {};
  my $run_query_sref = $self->get_list_of_valuesets_sref;
  my $stream = $run_query_sref->($h);

  # handle returned data
  my $results = [];
  my %list_of_seen_vs = ();
  while ( my @row = $stream->fetch_next ) {

    # see if we want terms handled
    # need to see if the exist before we can test
    my $terms_exist = -1;
    if ( defined ($row[5]) || defined ($row[6]) ) {
            $terms_exist = 1;
    }else{
        $terms_exist = 0;
    }

    # capture basic value_set data
    my $vs = { 'value_set' => { 'id'  => $row[3],
                                'url' => $row[4] },
               'property-id' => $row[0],
               'property-handle' => $row[1],
               'property-model'  => $row[2] };
    # only add the 'terms' if terms were found
    if ($terms_exist){
        $vs->{'terms'} = [];
    }

    # check to see if this is a new value set or not
    unless ( exists ($list_of_seen_vs{$row[3]})) {
        push @$results, $vs;
        $list_of_seen_vs{$row[3]} = 1;
    }

    # now only if there are terms, add them under the 'terms' array
    # for the appropriate vs
    if ($terms_exist) {
        my $term_ = { 'term' => {'id' => $row[5], 'value' => $row[6]} };

        ## find which element in big data array has value set
        ## and add the term to it
        my $id_ = $row[3];          # this is the current rows id
        my $size = scalar (@$results); # how many rows in data it iterate over
        my $i = 0;
        for (0..$size-1) {
            if ( $results->[$i]->{'value_set'}->{'id'} eq $id_) {
                # ah-ha, now I know which one to add to...
                push @{$results->[$i]->{'terms'}}, $term_;
                last; # all done, stop loop
            }
            $i++;
        }
    }


  }

  if (0) {
      # JSON
      $self->render( json => $results );
  }
  elsif (1) {
     
     # HTML 

      my $msg;
      if ($results) {
          $msg = 'List of All Value Sets';
      } else {
          $msg = 'Value Sets Not Found';
      } 

      $self->stash(list => $results );
      $self->stash(header => 'VALUE SETS');
      $self->stash(msg => $msg);
      $self->render(template => 'valuesets');
    }
}


sub getValuesetById {
  my $self = shift;

  my $vs_id = $self->stash('valuesetId');
  my $sanitizer = $self->sanitize_input_sref;
  $vs_id = $sanitizer->($vs_id); # simple sanitization
  $self->app->log->info("using value_set >$vs_id<");

  # just make sure we have term to proceed, else return error 400
  unless ($vs_id) {
     $self->render(json => { errmsg => "Missing or non-existent value_set id"},
                   status => 400);
     return;
  }

  # $h is anon hash, used for [$param_hash] in Neo4j::Bolt::Cxn
  my $h = { param => $vs_id };

  # get subroutine_ref to exec Neo4j::Bolt's `run_query` (defined in sts.pm)
  my $run_query_sref = $self->get_valueset_by_id_sref;
  my $stream = $run_query_sref->($h);

  # handle returned data -- single hash here
  my $results = [];
  my %list_of_seen_vs = ();
  while ( my @row = $stream->fetch_next ) {
    # now format

    # see if we want terms handled
    # need to see if the exist before we can test
    my $terms_exist = -1;
    if ( defined ($row[5]) || defined ($row[6]) ) {
            $terms_exist = 1;
    }else{
        $terms_exist = 0;
    }

    # capture basic value_set data
    my $vs = { 'value_set' => { 'id'  => $row[3],
                                    'url' => $row[4] },
                   'property-id' => $row[0],
                   'property-handle' => $row[1],
                   'property-model'  => $row[2]
    };
    # only add the 'terms' if terms were found
    if ($terms_exist){
         $vs->{'terms'} = [];
    }

    # check to see if this is a new value set or not
    unless ( exists ($list_of_seen_vs{$row[3]})) {
        push @$results, $vs;
        $list_of_seen_vs{$row[3]} = 1;
    }

    # now only if there are terms, add them under the 'terms' array
    # for the appropriate vs
    if ($terms_exist) {
        my $term_ = { 'term' => {'id' => $row[5], 'value' => $row[6]} };

        ## find which element in big data array has value set
        ## and add the term to it
        my $id_ = $row[3];          # this is the current rows id
        my $size = scalar (@$results); # how many rows in data it iterate over
        my $i = 0;
        for (0..$size-1) {
            if ( $results->[$i]->{'value_set'}->{'id'} eq $id_) {
                # ah-ha, now I know which one to add to...
                push @{$results->[$i]->{'terms'}}, $term_;
                last; # all done, stop loop
            }
            $i++;
        }
    }

  } # end while

  if (0) {
    # done - now return
    $self->render( json => $results );
  }
  elsif (1) {
     # HTML 
      my $msg;
      if ($results) {
          $msg = 'Details of a Value Set';
      } else {
          $msg = 'Value Sets Not Found';
      } 

      $self->stash(list => $results );
      $self->stash(header => 'VALUE SET');
      $self->stash(msg => $msg);
      $self->render(template => 'valuesets');
    }

}


sub getPropertyById {
  my $self = shift;

  my $propertyId = $self->stash('propertyId');
  my $sanitizer = $self->sanitize_input_sref;
  $propertyId = $sanitizer->($propertyId); # simple sanitization
  $self->app->log->info("using property id  >$propertyId<");

  # just make sure we have term to proceed, else return error 400
  unless ($propertyId) {
     $self->render(json => { errmsg => "Missing or non-existent property Id"},
                   status => 400);
     return;
  }

  # $h is anon hash, used for [$param_hash] in Neo4j::Bolt::Cxn
  my $h = { param => $propertyId };

  # get subroutine_ref to exec Neo4j::Bolt's `run_query` (defined in sts.pm)
  # $h is anon hash, used for [$param_hash] in Neo4j::Bolt::Cxn
  # $h is empty (no parameters is being passed)
  my $run_query_sref = $self->get_property_by_id_sref;
  my $stream = $run_query_sref->($h);

  # handle query result data
  my $result = {};
  while ( my @row = $stream->fetch_next ) {

    # now format
    $result = { 'property' => { 'property-id'           => $row[0], 
                              'property-handle'       => $row[1],
                              'property-model'        => $row[2],
                              'property-value_domain' => $row[3],
                              'property-is_required'  => $row[4],
                              'value_set-id' => $row[5],
                              'value_set-url' => $row[6],
                              'value_set-size' => $row[7]
                          } };
  }

  my $msg;
  if ($result) {
      $msg = 'Details for a Single Property';
  } else {
      $msg = 'Property Not Found';
  }

  if (0) {
  # done - now return
  #$self->render( json => $data );
  }
  elsif (1) {
    # html return
    $self->stash(list => $result );
    $self->stash(header => 'PROPERTY');
    $self->stash(msg => $msg);
    $self->render(template => 'properties');
  }
}

sub getListOfTerms {
  my $self = shift;

  $self->app->log->info("getting list of all terms");

  # get subroutine_ref to exec Neo4j::Bolt's `run_query` (defined in sts.pm)
  # $h is anon hash, used for [$param_hash] in Neo4j::Bolt::Cxn
  # $h is empty (no parameters is being passed)
  my $h = {};
  my $run_query_sref = $self->get_list_of_terms_sref;
  my $stream = $run_query_sref->($h);

  # handle query result data
  my $result = [];
  while ( my @row = $stream->fetch_next ) {
    # now format
    my $t = { 'term' => { 'value'  => $row[0],
                          'id'   => $row[1] },
              'term-origin' => $row[2] };

    push @$result, $t;
  }

  if (0) {
    # done, now return
    $self->render( json => $result );
  }
  elsif (1) {
    # html return
    my $msg;
      if ($result) {
          $msg = 'List of all Terms';
      } else {
          $msg = 'Term Not Found';
      }
    $self->stash(list => $result );
    $self->stash(header => 'TERMS');
    $self->stash(msg => $msg);
    $self->render(template => 'terms');
  }
}

sub getTermById {
  my $self = shift;

  my $term = $self->stash('termId');
  $self->app->log->info("using term $term");

  # just make sure we have term to proceed, else return error 400
  unless ($term) {
     $self->render(json => { errmsg => "Missing or non-existent term id"},
                   status => 400);
     return;
  }

  # $h is anon hash, used for [$param_hash] in Neo4j::Bolt::Cxn
  my $h = { param => $term };

  # get subroutine_ref to exec Neo4j::Bolt's `run_query` (defined in sts.pm)
  my $run_query_sref = $self->get_term_by_id_sref;
  my $stream = $run_query_sref->($h);

  # capture data back from Neo4j::Bolt::ResultStream
  my $result = [];
  while ( my @row = $stream->fetch_next ) {
    # now format
    my $t = { 'term' => { 'value'  => $row[0],
                          'id'   => $row[1] },
              'term-origin' => $row[2] };

    push @$result, $t;
  }

  unless (scalar @$result) {
     $self->render(json => { errmsg => "Missing or non-existent term"},
                   status => 400);
     return;
  }

  if (0) {
    # now return result
    $self->render( json => $result );
  }
  elsif (1) {
    # html return
    my $msg;
      if ($result) {
          $msg = 'List of all Terms';
      } else {
          $msg = 'Term Not Found';
      }
    $self->stash(list => $result );
    $self->stash(header => 'TERMS');
    $self->stash(msg => $msg);
    $self->render(template => 'terms');
  }
}

sub getTermByName {
  my $self = shift;

  my $term = $self->stash('term');
  $self->app->log->info("using term $term");

  # just make sure we have term to proceed, else return error 400
  unless ($term) {
     $self->render(json => { errmsg => "Missing or non-existent term"},
                   status => 400);
     return;
  }

  # $h is anon hash, used for [$param_hash] in Neo4j::Bolt::Cxn
  my $h = { param => $term };

  # get subroutine_ref to exec Neo4j::Bolt's `run_query` (defined in sts.pm)
  my $run_query_sref = $self->get_term_detail_sref;
  my $stream = $run_query_sref->($h);

  # capture data back from Neo4j::Bolt::ResultStream
  my $result = [];
  while ( my @row = $stream->fetch_next ) {
    # now format
    my $t = { 'term' => { 'value'  => $row[0],
                          'id'   => $row[1] },
              'term-origin' => $row[2] };

    push @$result, $t;
  }

  unless (scalar @$result) {
     $self->render(json => { errmsg => "Missing or non-existent term"},
                   status => 400);
     return;
  }

  if(0) {
    # now return result
    $self->render( json => $result );
  } 
  elsif (1) {
    # html return
    my $msg;
      if ($result) {
          $msg = 'List of all Terms';
      } else {
          $msg = 'Term Not Found';
      }
    $self->stash(list => $result );
    $self->stash(header => 'TERMS');
    $self->stash(msg => $msg);
    $self->render(template => 'terms');
  }
}

1;
