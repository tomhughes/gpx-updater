#!/usr/bin/perl

use Cache::Memcached;

$memd = new Cache::Memcached {
	'servers' => [ "localhost:11211" ],
};

@vars = split(/&/, $ENV{'QUERY_STRING'});

for $v (@vars) {
	($key, $val) = split(/=/, $v, 2);
	$val =~ s/[^0-9]//g;
	$var{$key} = $val;
}

if ($ENV{'PATH_INFO'} =~ /^\/([0-9]+)\/([0-9]+)\/([0-9]+)/) {
	$var{'z'} = $1;
	$var{'x'} = $2;
	$var{'y'} = $3;
}

unless ($var{'z'} =~ /^[0-9]+$/ &&
        $var{'x'} =~ /^[0-9]+$/ &&
        $var{'y'} =~ /^[0-9]+$/) {
	print "Content-type: text/html\n\nUnrecognized tile specification\n";
	exit 0;
}

print "Content-type: image/png\n\n";

$cache = "/tmp/tile";
$cachefile = "$cache/$var{'z'}/$var{'x'}/$var{'y'}.png";

$cached = $memd->get($cachefile);
if ($cached) {
	print $cached;
	exit 0;
}

$data = "";
open(IN, "/home/enf/datamaps/render -f /home/enf/shapes/lines-directional.dm -t 0 -g -C 256 /home/enf/shapes/current $var{'z'} $var{'x'} $var{'y'} | pngquant 64 |");
while (<IN>) {
	$data .= $_;
}
close(IN);

$memd->set($cachefile, $data);
print $data;
exit 0;
