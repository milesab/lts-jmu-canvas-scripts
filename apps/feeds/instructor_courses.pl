#use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use CGI;
use strict;
use DFconfig;
my %config = DFconfig::get_config();

my $cgi = CGI->new();
my $instructors = $cgi->param('id');
my @instructors = split(/,/,$instructors);

my @output;

my %enrollment = readfile("$config{export_dir}enrollments.csv");
my $enrollments = scalar(@{$enrollment{'course_id'}});
for (my $i = 0; $i < $enrollments; $i++) {
	my $userid = @{$enrollment{'user_id'}}[$i];
	my $role = @{$enrollment{'role'}}[$i];
	if ( $role eq "teacher" && $userid ~~ @instructors ) {
		my $instructor = @{$enrollment{'user_id'}}[$i];
		my $courseid = @{$enrollment{'course_id'}}[$i];
		my $ccid = @{$enrollment{'canvas_course_id'}}[$i];
		push (@output, "$instructor,$ccid\t$courseid\n");
	}
}


print "Content-type: text/plain\n\n";
@output = reverse sort @output;
foreach (@output) {
	print $_;
}



sub readfile
{
	my $filename = @_[0];
	open(FILE, $filename) or die "Could not open $filename";
	my %data;
	my $line = <FILE>;
	chomp $line;
	my @columns = split(/\,/, $line);
	while ($line = <FILE>)
	{
		chomp $line;
		my @fields = split(/\,/, $line);
		for (my $index = 0; $index < scalar(@columns); $index++)
		{
			push(@{$data{$columns[$index]}}, $fields[$index]);
		}
	}	
	close(FILE);
	return %data;
}
