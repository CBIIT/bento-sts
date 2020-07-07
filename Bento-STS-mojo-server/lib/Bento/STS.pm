package Bento::STS;
use Mojo::Base 'Mojolicious';
use Bento::STS::Datastore qw(setup_mdb);
use Bento::STS::helpers qw(setup_sanitizer);

our $VERSION = '0.3.0';

# This method will run once at server start
sub startup {
  my $self = shift;

  # Load configuration from hash returned by config file
  #my $config = $self->plugin('Config');
  my $config = $self->plugin('Config' => {file => 'bento-sts.conf'});

  # Configure the application
  $self->secrets($config->{secrets});

  # Router
  my $r = $self->routes;

  # Normal route to controller
  $r->get('/')->to('Actions#welcome');
  $r->get('/about')->to('Actions#about');
  #$r->get('/healthcheck')->to('actions#healthcheck');

  $r->get('/models')->to('Actions#getListOfModels');
  $r->get('/models/:modelName')->to('Actions#getModelByName');

  $r->get('/nodes')->to('Actions#getListOfNodes');
  $r->get('/nodes/:nodeId')->to('Actions#getNodeById');

  $r->get('/properties')->to('Actions#getListOfProperties');
  $r->get('/properties/:propertyId')->to('Actions#getPropertyById');
  
  $r->get('/valuesets')->to('Actions#getListOfValuesets');
  $r->get('/valuesets/:valuesetId')->to('Actions#getValuesetById');

  $r->get('/terms')->to('Actions#getListOfTerms');
  $r->get('/terms/:termId')->to('Actions#getTermById');

  #$r->get('/origin')->to('getListOfOrigins"');
  #$r->get('/origin/:originId')->to('getOriginById');
  
  ## initial simple sanitization helper (sanitize_input)
  setup_sanitizer($self);

  # setup db interface
  setup_mdb($self);

}

1;
