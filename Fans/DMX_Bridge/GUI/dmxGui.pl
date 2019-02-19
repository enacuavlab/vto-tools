#!/usr/bin/perl 

use strict;
use warnings;
use feature ':5.22';

use Ivy;
use Getopt::Long;

use Tk;
use Tk::ProgressBar;

sub generateGui ();
sub generateLeftPanel ();
sub generateRightPanel ();
sub generateOneServoFrame ($);
sub labelEntryFrame ($$$$;$) ;
sub statusFunc ($$);
sub geneDmxMsgsCB ();
sub geneDmxMsgsChannel ($$);

my $mw;
my $mwf;

my %options;
my %tkObject = (
    dmxMaxScale => [0,0,0,0,0],
    dmwMinScale => [0,0,0,0,0],
    );

END {Ivy::stop ();}

GetOptions (\%options,  "bus:s", "nb:i");

$options{nb} //= 1;

Ivy->init (-loopMode => 'TK',
           -appName =>  'DMX_GUI',
           -ivyBus => $options{bus},
	  ) ;

my $bus = Ivy->new (-statusFunc => \&statusFunc,
		    -blockOnSlowAgent => 0,
		    -neededApp =>   ["Dmx_FAN"]);

generateGui();
$bus->start ();
Tk::MainLoop;



sub generateGui()
{
    $mw = MainWindow->new;
    $mw->wm (title => $0);
    my $w = $mw->screenwidth;
    my $h = $mw->screenheight;

    $mw->MoveToplevelWindow (0,0);

    $mwf =  $mw->Frame ()->pack(-side => 'left', -anchor => 'w');
    generatePanel ();
    $mw->repeat (1000, \&geneDmxMsgsCB);
}



sub generatePanel ()
{
    my $outerFrame = $mwf->Frame ();
    $outerFrame->pack(-side => 'left', -anchor => 'w');
    
    my $entriesFrame = $mwf->Frame ();
    $entriesFrame->pack(-side => 'left', -anchor => 'w');

#  __    __   __   ____    _____   _____   ______   _____          
# |  |/\|  | |  | |    \  /  ___\ |  ___| |_    _| /  ___>         
# |        | |  | |  |  | |  \_ \ |  ___|   |  |   \___  \         
#  \__/\__/  |__| |____/  \_____/ |_____|   |__|   <_____/         
    my $dmxsFrame = $mwf->Frame ();
    $dmxsFrame->pack(-side => 'left', -anchor => 'w');

    foreach my $nbi (1 .. $options{nb}) {
    geneDmxFrame($dmxsFrame, $nbi);
    }
}



sub geneDmxFrame ($$) {
    my ($frame, $dmxIdx) =@_;
 
    my $dmxFrame = $frame->Frame (-bd => '1m', -relief => 'sunken');
    $dmxFrame->pack(-side => 'left', -anchor => 'w');
  
    my $scalabframe1 = $dmxFrame->Frame()->pack(-side => 'left', -anchor => 'w') ;
    $scalabframe1->Label ('-text' => "DMX $dmxIdx")->
	pack (-side => 'top', -anchor => 'n');

    $scalabframe1->Checkbutton(
        -text     => 'On',
	#	-state => 'disabled',
        -variable => \ ($tkObject{"dmxOn${dmxIdx}"}),
	-relief   => 'flat')->pack (-side => 'left', -anchor => 'n') ;
    $tkObject{"dmxOn${dmxIdx}"} = 0;
    
    $tkObject{"dmx${dmxIdx}Scale"} = $scalabframe1->Scale (
	'-orient' => 'vertical', '-length' => 600, 
	'-from' => 255, '-to' => 0,
	'-resolution' => 5,
	'-variable' => \ ($tkObject{"dmx${dmxIdx}"}),
	'-background' => 'lightgreen',
	'-sliderlength' => 20,
	'-sliderrelief' => 'solid');

    $tkObject{"dmx${dmxIdx}Scale"}->pack (-side => 'top', -anchor => 'n') ;
    $tkObject{"dmx${dmxIdx}"}=255;

    my $scalabframe2 = $dmxFrame->Frame()->pack(-side => 'left', -anchor => 'w') ;
    $scalabframe2->Label ('-text' => "DMX $dmxIdx On")->
	pack (-side => 'top', -anchor => 'n');
   
    
    $tkObject{"dmxOnDuration${dmxIdx}Scale"} = $scalabframe2->Scale (
	'-orient' => 'vertical', '-length' => 600, 
	'-from' => 20, '-to' => 0,
	'-resolution' => 1,
	'-variable' => \ ($tkObject{"onDuration${dmxIdx}"}),
	'-background' => 'lightgreen',
	'-sliderlength' => 20,
	'-sliderrelief' => 'solid');

    $tkObject{"dmxOnDuration${dmxIdx}Scale"}->pack (-side => 'top', -anchor => 'n') ;

    my $scalabframe3 = $dmxFrame->Frame()->pack(-side => 'left', -anchor => 'w') ;
    $scalabframe3->Label ('-text' => "DMX $dmxIdx Off")->
	pack (-side => 'top', -anchor => 'n');
    
    
    $tkObject{"dmxOffDuration${dmxIdx}Scale"} = $scalabframe3->Scale (
	'-orient' => 'vertical', '-length' => 600, 
	'-from' => 20, '-to' => 0,
	'-resolution' => 1,
	'-variable' => \ ($tkObject{"offDuration${dmxIdx}"}),
	'-background' => 'lightgreen',
	'-sliderlength' => 20,
	'-sliderrelief' => 'solid');

    $tkObject{"dmxOffDuration${dmxIdx}Scale"}->pack (-side => 'top', -anchor => 'n') ;
}


sub labelEntryFrame ($$$$;$)
{
    my ($ef, $labelText, $textVar, $packDir, $width) = @_ ;
    
    my (
	$label,
	$entry,
	$frame,
	$frameDir
	) = ();
    
    $frameDir = ($packDir eq 'top') ? 'left' : 'top' ; 
    
    $width = 15 unless defined $width ;
    $frame = $ef->Frame ();
    $frame->pack (-side => $frameDir, -pady => '2m', -padx => '0m', 
		  -fill => 'y', -anchor => 'w');
    
    $label = $frame->Label (-text => $labelText);
    $label->pack (-side =>$packDir, -padx => '0m', -fill => 'y');
    
    $entry = $frame->Entry (-width => $width, -relief => 'sunken',
			    -bd => 2, -textvariable => $textVar,
			    -font => "-adobe-courier-medium-r-*-*-14-*-*-*-*-*-iso8859-15",
			    -exportselection => 'false') ;
    
    $entry->pack (-side =>$packDir, -padx => '0m', -anchor => 'w');
    
    return $entry ;
}


sub statusFunc ($$)
{
  my ($ready, $notReady) = @_;

  if (@{$notReady})  {
    printf "appli manquantes : %s\n", join (' ', @{$notReady});
  } else {
    printf ("Toutes applis OK !!\n");
  }
}

sub geneDmxMsgsCB ()
{
   state $count=0; 
   $count++;

   foreach my $nbi (1 .. $options{nb}) {
       geneDmxMsgsChannel ($nbi, $count);
   }
}

sub geneDmxMsgsChannel ($$)
{
    state @dmxState;
    my ($dmxIdx, $count) = @_;
    my $dmxVal = 0;

    if ($tkObject{"dmxOn${dmxIdx}"}) {
	my $onDur = $tkObject{"onDuration${dmxIdx}"};
	my $offDur = $tkObject{"offDuration${dmxIdx}"};
	$dmxVal = $tkObject{"dmx${dmxIdx}"};

	if ($onDur && $offDur) {
	    my $period = $onDur + $offDur;
	    $dmxVal = 0 if ($count % $period) >= $onDur;
	}
    }

    $dmxState[$dmxIdx] //= -1;
    if ($dmxVal != $dmxState[$dmxIdx]) {
	$dmxState[$dmxIdx] = $dmxVal; 
	$bus->sendMsgs ("Dmx_FAN channel${dmxIdx}=${dmxVal}");
    }
}
