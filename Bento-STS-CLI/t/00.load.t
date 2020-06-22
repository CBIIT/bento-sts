use strict;
use warnings FATAL => 'all';
use Test::More tests => 1;

use lib 'lib';

BEGIN {
    use_ok( 'Bento::STS::CLI' ) || print "Bail out!\n";;
}

diag( "Testing Bento::STS::CLI $Bento::STS::CLI::VERSION, Perl $], $^X" );
