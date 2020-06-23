package Bento::STS;
use Mojo::Base 'Mojolicious';

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
  $r->get('/')->to('example#welcome');
}

1;
