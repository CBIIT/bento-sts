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
  }


  # done - now return
  $self->stash(list => ['ICDC', 'CTDC']);
  $self->stash(header => 'Models');
  $self->stash(msg => 'List of Models');
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
      $msg = 'Model Verified';
  } else {
      $msg = 'Model Not Found';
  }

  # done - now return
  $self->stash(list => [$model] );
  $self->stash(header => 'Models');
  $self->stash(msg => $msg);
  $self->render(template => 'index');

}
1;

1;
