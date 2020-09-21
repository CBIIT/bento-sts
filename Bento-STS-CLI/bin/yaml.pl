#!/usr/bin/env perl
use strict;
use warnings;
use Data::Dumper;
use DateTime;
use FindBin qw( $Bin $Script $RealBin $RealScript);
use Getopt::Long qw(GetOptions);

use lib "$Bin/../lib";
use Bento::STS::CLI;
use Bento::STS::CLI::Yaml;

#-----------------------------------------------------------------------------
# make a simple yaml 
#-----------------------------------------------------------------------------
my $usage = '$> perl -X yaml.pl  -model "ICDC"|"CTDC" [ -v | -verbose] [ -debug=# ]';

#-----------------------------------------------------------------------------
# Simple Global Settings
#-----------------------------------------------------------------------------
my $pid = $$;
my $start_time = DateTime->now(time_zone=>'local');

## default Options
my $model     = '';
my $verbose   = 0 ;         # 0 = no debug messages
my $vrsn;
my $config    = '';
my $help;

GetOptions(

            # model
            'model=s'    => \$model,

            # print / verbose options
            'verbose|debug:1'   => \$verbose,
            'quiet'             => sub { $verbose=0; },

            # version
            'version|v'   => \$vrsn,

            'config'      => \$config,
            'help'        => \$help
          ) or die "Incorrect usage!\nUSAGE: $usage";

unless ($model) {
    die "Error! Unknown Model!\n";
}

if ( $vrsn ) {
    print "$Bento::STS::CLI::VERSION\n";
}

if( $help ) {
    print "$usage\n";
}

if ( $vrsn || $help ) {
    exit;
}


#-----------------------------------------------------------------------------
#  MAIN
#-----------------------------------------------------------------------------
run() unless caller();


#-----------------------------------------------------------------------------
# sub: run
#-----------------------------------------------------------------------------
sub run {

    # main call
    my $bolt_url = get_bolt_url();

    my $model_ = Bento::STS::CLI::get_model($bolt_url, $model);
    my $yaml = Bento::STS::CLI::Yaml::get_model_yaml($model_);

    print "$yaml\n";

}

sub get_bolt_url {

    my $ip = '127.0.0.1';
    my $bolt_url = $ENV{'NEO4J_MDB_URI'};
    my $neo4j_user = $ENV{'NEO4J_MDB_USER'};
    my $neo4j_pass = $ENV{'NEO4J_MDB_PASS'};
    my $port = 7687;

    if ($bolt_url =~ /bolt:\/\/(\d*\.\d*\.\d*\.\d*):$port/){
            $ip = $1;
    }

    print "port is $port - u: $neo4j_user - p: $neo4j_pass\n" if $verbose;

    my $url = 'bolt://' . $neo4j_user . ':' . $neo4j_pass . '@' . $ip . ':' . $port; 
}



#-----------------------------------------------------------------------------
1;
