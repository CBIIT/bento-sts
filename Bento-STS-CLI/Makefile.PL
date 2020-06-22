use strict;
use warnings;
use ExtUtils::MakeMaker;

WriteMakefile(
    NAME                => 'Bento::STS::CLI',
    AUTHOR              => 'Mark Benson <bensonml>',
    VERSION_FROM        => 'lib/Bento/STS/CLI.pm',
    ABSTRACT_FROM       => 'lib/Bento/STS/CLI.pm',
    PL_FILES            => {},
    PREREQ_PM => {
        'Test::More' => 0,
        'version'    => 0,
    },
    dist                => { COMPRESS => 'gzip -9f', SUFFIX => 'gz', },
    clean               => { FILES => 'Bento-STS-CLI-*' },
);
