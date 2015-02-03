#use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use CGI;
use strict;
use DFconfig;

my %config = DFconfig::get_config();
my $cgi = CGI->new();
open(LOG, ">>$config{log_dir}");
my $courseids = $cgi->param('id');
$courseids =~ s/default//ig; # cut off 'default' that is appended by LON CAPA
my @courses = split(/,/,$courseids);

print LOG "Received request for $courseids\n";

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

my $output = "";
my $total = 0;

my %enrollment = readfile("$config{export_dir}enrollments.csv");
my $enrollments = scalar(@{$enrollment{'course_id'}});
for (my $i = 0; $i < $enrollments; $i++) {
	my $courseid = @{$enrollment{'course_id'}}[$i];
	my $role = @{$enrollment{'role'}}[$i];
	if ( $role eq "student" && $courseid ~~ @courses ) {
		$total++;
		my $canvas_id = @{$enrollment{'canvas_user_id'}}[$i];
		my $studentid = @{$users{'login_id'}}[$users_index{$canvas_id}];
		$output .= "\t<student username=\"$studentid\">\n";
		$output .= "\t\t<autharg></autharg>\n";
		$output .= "\t\t<authtype>localauth</authtype>\n";
		$output .= "\t\t<email>" . @{$users{'email'}}[$users_index{$canvas_id}] . "</email>\n";
		$output .= "\t\t<enddate></enddate>\n";
		$output .= "\t\t<firstname>" . @{$users{'first_name'}}[$users_index{$canvas_id}] . "</firstname>\n";
		$output .= "\t\t<groupID>$courseid</groupID>\n";
		$output .= "\t\t<lastname>" . @{$users{'last_name'}}[$users_index{$canvas_id}] . "</lastname>\n";		
		$output .= "\t\t<middlename></middlename>\n";
		$output .= "\t\t<startdate></startdate>\n";
		$output .= "\t\t<studentID>$studentid</studentID>\n";
		$output .= "\t</student>\n";
	}
}

print "X-Enrollment-count: $total\n";
print "Content-type: text/plain\n\n";
print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
print "<!DOCTYPE text>\n";
print "<students>\n";
print $output;
print "</students>\n";

print LOG "returned $total enrollments\n";

close LOG;



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
