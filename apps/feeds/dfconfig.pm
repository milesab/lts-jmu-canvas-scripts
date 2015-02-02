package DFconfig;
use strict;

open my $cf, '<', '../../conf/settings.conf' or die "Unable to open file:$!\n";
my %config = map { s/#.*//; s/^\s+//; s/\s+$//; split /=|\s+/; } <$cf>;
close $cf;

sub get_config { return %config; }
1;