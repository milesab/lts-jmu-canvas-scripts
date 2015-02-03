#use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use CGI;
use strict;
use DFconfig;

my %config = DFconfig::get_config();
my $cgi = CGI->new();
my $courseids = $cgi->param('id');
$courseids =~ s/default//ig; # cut off 'default' string appended by LON CAPA
my @courses = split(/,/,$courseids);

my %users = readfile("$config{export_dir}users.csv");
my $users_count = scalar(@{$users{'canvas_user_id'}});
my %users_index;
for (my $i = 0; $i < $users_count; $i++) {
	$users_index{@{$users{'canvas_user_id'}}[$i]} = $i;
}

my %xlist = readfile("$config{export_dir}xlist.csv");
my $xlist_count = scalar(@{$xlist{'xlist_course_id'}});
my %xlist_index;
for (my $i = 0; $i < $xlist_count; $i++) {
	my $courseid = @{$xlist{'xlist_course_id'}}[$i];
	my $sectionid = @{$xlist{'section_id'}}[$i];
	if ( $courseid ~~ @courses && !($sectionid ~~ @courses) ) {
		push (@courses, $sectionid);
	}

}

my @output;

my %enrollment = readfile("$config{export_dir}enrollments.csv");
my $enrollments = scalar(@{$enrollment{'course_id'}});
for (my $i = 0; $i < $enrollments; $i++) {
	my $courseid = @{$enrollment{'course_id'}}[$i];
	my $role = @{$enrollment{'role'}}[$i];
	if ( $role eq "teacher" && $courseid ~~ @courses ) {
		my $canvas_id = @{$enrollment{'canvas_user_id'}}[$i];
		my $instructor = @{$users{'login_id'}}[$users_index{$canvas_id}];
		my $email = @{$users{'email'}}[$users_index{$canvas_id}];
		my $first = @{$users{'first_name'}}[$users_index{$canvas_id}];
		my $last = @{$users{'last_name'}}[$users_index{$canvas_id}];
		push (@output, "instructor\t$instructor\t$email\t$first\t$last\n");
		
	}
	elsif ( $role eq "student" && $courseid ~~ @courses ) {
		my $canvas_id = @{$enrollment{'canvas_user_id'}}[$i];
		my $studentid = @{$users{'login_id'}}[$users_index{$canvas_id}];
		my $email = @{$users{'email'}}[$users_index{$canvas_id}];
		my $first = @{$users{'first_name'}}[$users_index{$canvas_id}];
		my $last = @{$users{'last_name'}}[$users_index{$canvas_id}];
		push (@output, "student\t$studentid\t$email\t$first\t$last\n");
	}
}

print "Content-type: text/plain\n\n";
@output = uniq(@output);
@output = sort @output;
foreach (@output) {
	print $_;
}


sub uniq {
	my %seen;
	grep !$seen{$_}++, @_;
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
