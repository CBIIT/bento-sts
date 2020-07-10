package Bento::STS::Datastore;

use FindBin qw($Bin);
use lib "$Bin";
use Neo4j::Bolt;

use Bento::STS::CypherQueries qw( %queries );

use Exporter qw(import);
our @EXPORT= qw(setup_mdb);

sub setup_mdb {
    my ($self) = @_;

    # TODO: better, explicit error if these are empty
    # Grab AWS credentials from environment
    my $neo4j_user = $ENV{NEO4J_MDB_USER};
    my $neo4j_pass = $ENV{NEO4J_MDB_PASS};
    my $neo4j_ip = $self->config->{neo4j_mdb_ip};

    # Construct MDB access url
    my $NEO4J_URL = 'bolt://' . $neo4j_user . ':' . $neo4j_pass . '@' . $neo4j_ip . ':7687';

    my $mdbh = Neo4j::Bolt->connect($NEO4J_URL);
    my $conn = $mdbh->connected;
    die "No connection to neo4j: " . $mdbh->errmsg unless $conn;
 
    # construct anonymouns subs for each queries as needed in routes above
    while ((my $queryname, my $cypherquery) = each (%queries)) { 
        eval "\$self->helper( ${queryname}_sref => sub { 
            return sub {
                my (\$param_href) = \@_;
                \$mdbh->run_query( \$cypherquery, \$param_href ) 
            }
        } )";
    }
}


1;

__END__

=head1 NAME

sts::datastore - A simple module for accessing datastores (sqlite, neo4j mdb)

=cut


