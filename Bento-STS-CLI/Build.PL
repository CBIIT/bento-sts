use strict;
use warnings;
use Module::Build;

my $builder = Module::Build->new(
    module_name         => 'Bento::STS::CLI',
    license             => 'artistic2',
    dist_author         => 'Mark Benson <bensonml>',
    dist_version_from   => 'lib/Bento/STS/CLI.pm',
    requires => {
        'Test::More' => 0,
        'version'    => 0,
    },
    add_to_cleanup      => [ 'Bento-STS-CLI-*' ],
);

$builder->create_build_script();
