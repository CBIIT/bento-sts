#!/usr/bin/env perl
use strict;
use warnings;
no warnings qw( regexp deprecated );
use Data::Dumper;
use DateTime;
use FindBin qw( $Bin $Script $RealBin $RealScript);
use Getopt::Long qw(GetOptions);

use lib "$Bin/../lib";
use Bento::STS::CLI;

#-----------------------------------------------------------------------------
# Check on Bento::STS::CLI
# do a simple check on MDB connection 
#-----------------------------------------------------------------------------
my $usage = '$> perl demo.pl [ -mdb DEV|STAGE|PROD ] [ -dev P|Y|D ] [ -v | -verbose] [ -debug=# ]';

#-----------------------------------------------------------------------------
# Simple Global Settings
#-----------------------------------------------------------------------------
my $pid = $$;
my $start_time = DateTime->now(time_zone=>'local');

## default Options
my $mdb       = 'DEV';
my $mdb_bolt_url;
my $dev       = 'D';        # N = Production, Y|D = Development
my $verbose   = 0 ;         # 0 = no debug messages
my $vrsn;
my $config    = '';
my $help;

my %mdb_server_ip = ( 'LOCAL'   => '127.0.0.1',
                      'TEANCUM' => '192.168.0.115',
                      'DEV'     => '54.91.213.206',
                      'STAGE'   => '3.210.7.218',
                      'PROD'    => '34.233.99.234');

GetOptions(
            # what mdb instance to run against
            'mdb=s{1,1}'  => \$mdb,

            # production / dev mode options
            'dev=s{1,1}'  => \$dev,
            'P'           => sub { $dev = 'P'; },   # production
            'Y'           => sub { $dev = 'Y'; },   # development
            'D'           => sub { $dev = 'D'; },   # development

            # print / verbose options
            'verbose|debug:1'   => \$verbose,
            'quiet'             => sub { $verbose=0; },

            # version
            'version|v'   => \$vrsn,

            'config'      => \$config,
            'help'        => \$help
          ) or die "Incorrect usage!\nUSAGE: $usage";

unless (exists $mdb_server_ip{$mdb}) {
    die "Error! Unknown MDB Server!\n";
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

    print_settings() if $verbose;
    
    #print_header() if $verbose;

    # main call
    my $bolt_url = get_bolt_url($mdb);

    ## example 1
    print "Example 1\n";
    my @handles = Bento::STS::CLI::get_model_handles($bolt_url);
    print "model handles found: @handles\n";

    ## example 2
    print "\n\nExample 2\n";
    my $icdc_model = Bento::STS::CLI::get_icdc_model();
    print Dumper ($icdc_model);
    
    
    print_footer();
}

sub get_bolt_url {
    my ($mdb) = @_;

    my $ip = $mdb_server_ip{$mdb};
    #my $neo4j_user = 'neo4j'; #$ENV{'NEO4J_USER'};
    my $neo4j_user = $ENV{'NEO4J_USER'};
    my $neo4j_pass = $ENV{'NEO4J_PASS'};
    my $port = 7687;
    
    print "port is $port - u: $neo4j_user - p: $neo4j_pass\n" if ($verbose > 10);
    
    my $url = 'bolt://' . $neo4j_user . ':' . $neo4j_pass . '@' . $ip . ':' . $port; 
}

#-----------------------------------------------------------------------------
# sub: print_settings     -- prints global settings --
#-----------------------------------------------------------------------------
sub print_settings {
    print "\n","="x80,"\n";
    print "SETTINGS\n";
    print "  mdb     is : $mdb\n";
    print "  dev     is : $dev\n";
    print "  verbose is : $verbose\n";
    print "  config  is : $config\n";
}

#-----------------------------------------------------------------------------
# sub: print_header     -- prints script header --
#-----------------------------------------------------------------------------
sub print_header {
    print "\n","="x80,"\n";
    print "COMMAND     : ", `ps -o cmd --no-headers -p $pid`;
    print "START TIME  : $start_time\n";
    print "-"x80,"\n";
}


#-----------------------------------------------------------------------------
# sub: print_footer    -- prints a simple script footer --
#-----------------------------------------------------------------------------
sub print_footer {
    print "="x80,"\n";
    print "SCRIPT PATH : $RealBin\n";
    print "SCRIPT      : $RealScript\n";
    print "COMMAND     : ", `ps -o 'command=' -p $pid`;
    print "PERL VER    : $]\n";
    print "HOSTNAME    : ", `hostname -s`;
    print "USER        : ", `ps -o 'user=' -p $pid`;
    print "START TIME  : $start_time\n";
    print "END TIME    : ", DateTime->now(time_zone=>'local'), "\n";
    print "-"x80,"\n";
    print `ps -o user,pmem,pcpu,lstart,etime,cputime,command -p $pid`;
    print "="x80,"\n\n";
}



#-----------------------------------------------------------------------------
1;
