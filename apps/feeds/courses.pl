#use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use CGI;
use strict;
use warnings;
use DFconfig;
my %config = DFconfig::get_config();

my $cgi = CGI->new();

my $semester = $cgi->param('sem') || 'Spring Semester 2015';

if ($semester =~ /(SP|SM|FA)[0-9][0-9]/) {
	my %termname = (
		SP => 'Spring Semester 20',
		SM => 'Summer Session 20',
		FA => 'Fall Semester 20',
	);
	$semester =~ s!(SP|SM|FA)!$termname{$1} || $1!e;
	}

my %terms = readfile("$config{export_dir}terms.csv");
my @terms;
my $sem;

my $termcount = scalar(@{$terms{'term_id'}});
for (my $i = 0; $i < $termcount; $i++) {
	my $id = @{$terms{'term_id'}}[$i];
	my $name = @{$terms{'name'}}[$i];
	if ($name ne "Default Term" && $name eq $semester) {
		$sem = $id;
	}
}

my %courses = readfile("$config{export_dir}courses.csv");

my @xlist;
my %xlist = readfile("$config{export_dir}xlist.csv");
my $xlist_count = scalar(@{$xlist{'xlist_course_id'}});
my %xlist_index;
for (my $i = 0; $i < $xlist_count; $i++) {
	my $sectionid = @{$xlist{'section_id'}}[$i];
	push (@xlist, $sectionid);

}

my @output;

my $count = scalar(@{$courses{'course_id'}});
for (my $i = 0; $i < $count; $i++) {
	my $id = @{$courses{'course_id'}}[$i];
	my $name = @{$courses{'long_name'}}[$i];
	my $term = @{$courses{'term_id'}}[$i];
	if (length $id > 0 && length $name > 0 && $id !~ /_draft/ && $term eq $sem && !($id ~~ @xlist)) {
		push (@output, "$id $name\n");
	}
}

print "Content-type: text/plain\n\n";

@output = sort @output;
foreach (@output) {
	print $_;
}

sub readfile
{
	my $filename = $_[0];
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
