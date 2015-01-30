package DFconfig;
require Exporter;
use strict;

our @ISA    = qw(Exporter);
our @EXPORT = qw( getconfig );

my %config = (
    dir => '/Path/To/Export/Data/',
    log => '/Path/To/Log/File/',
    );

sub getconfig {
    return %config;
    }
1;
