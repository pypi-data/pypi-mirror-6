#!/usr/bin/perl 
#********************************************************
#
# runadipls.pl
#
#********************************************************

$script_name="runadipls.pl";

if (  scalar(@ARGV) < 2 ) {
    print "\n";
    print ">>>>>>>>>>>>>>>>>>>\n";
    print "$script_name needs 2 arguments !\n";
    print ">>>>>>>>>>>>>>>>>>>\n";
    print "\n";
    &usage();
    exit(0);
}

#-------------------------------------
$FILEPAR= $ARGV[1];
$template="TEMPLATE";
#print "cp $FILEPAR $template";
system("cp $FILEPAR $template");

$FILEPAR=substr( $FILEPAR , rindex(  $FILEPAR   , "/")+1 )  ; # détermination du nom du fichier (le nom sans le path).
$FILEPAR=substr( $FILEPAR , 0,  rindex(  $FILEPAR , ".") ); # suppression de son éventuel suffixe 

$subname = "" ;
$version = "4" ;

$ii=0;
foreach $s(@ARGV) 
{
if( $s=~m/^-subname/) {
	$subname=".".$ARGV[$ii+1];
    }
if( $s=~m/^-cesam/) {
	$version="$ARGV[$ii+1]";
    }
    $ii=$ii+1
}


# On chercher dans le répertoire courant 
# 


@fich =`ls ./$ARGV[0]` ;


print " \n";
print "===========================================\n";
print "===============  DEBUT  ===================\n";

foreach $fich(@fich)  {
    $fich =~ s/^\s//;
    $fich =~ s/\n// ; 
}






foreach $fich(@fich)  {    

    if(  $fich =~ /\.gz$/ ) {
	print "gunzip -f "  .$fich. "\n";
	system("gunzip -f "  .$fich  );	
	$fich =~ s/\.gz$//;
    }
    print "**************************\n";
    print "on traite le fichier:\n";
    print $fich;    
    print "\n**************************\n";

    if( $fich =~ /.oscb|.osc/) { # il s'agit d'un fichier .osc

    $fichosc = $fich ;
    $str = $fich ;
    $str =~ s/.oscb|.osc// ;
    $fichjcd =$str . ".jcdb" ;
    if(-e $fichjcd) { system("rm -f $fichjcd") ;}
    print "-------------------------------------------------\n";
    print " conversion de $fichosc en $fichjcd à l\'aide de INTERF5\n" ;
    print "-------------------------------------------------\n";
    open (INTERF,"|interf5") ;
    print INTERF  "$fichosc\n" ;    
    print INTERF  "$version\n" ;
    print INTERF  "$fichjcd\n" ;    
    print INTERF  "0\n" ;    
    close (INTERF); 
 
    } else { 
	$fichjcd=$fich  ;
	$str = $fich ;
	$str =~ s/.jcdb|.bin|.amdl// ;	
    }
    print "$str\n";
	open (PARIN,"<$template") ;
#	$str= "." . $FILEPAR if (length($FILEPAR) >0) ;
	$str=$str . $subname ;
	$parout =  $str  .  ".par";
	print "$parout\n";
	open (PAROUT,">$parout") ;
	while ( ($ligne =<PARIN>)  )
	{
	    
	    if (!($ligne=~/^\s{0,}-1/) &&  $ligne=~ /\d{1,} {1,}\'/ && ! ($ligne=~ /\d{1,} {1,}\'\'/ )  ) # 
	    {
		$ligne =~ s/ {1,}\'/ \'/; # suppression des blancs inutiles
		print PAROUT  "2 \'" .  $fichjcd . "\'@\n"  if ($ligne =~/^2 \'/) ;
		print PAROUT  "9 \'" .   $str . ".alog\'@\n"  if ($ligne =~/^9 \'/) ;
  		print PAROUT  "10 \''\n"  if ($ligne =~/^10 \'/) ;
   		print PAROUT  "11 \'" .  $str . ".gsm\'@\n"  if ($ligne =~/^11 \'/) ;
   		print PAROUT  "15 \'" .   $str . ".ssm\'@\n"  if ($ligne =~/^15 \'/) ;
   		print PAROUT  "16 \'" .   $str . ".fsm\'@\n"  if ($ligne =~/^16 \'/) ;
   		print PAROUT  "4 \'" . $str . ".ef\'@\n"  if ($ligne =~/^11 \'/) ;
	    }
	    else  {
		print PAROUT $ligne;
	    }
	}
	close(PARIN) ;    
  	close(PAROUT) ;    
	print "-------------------------------------------------\n";
	print " lancement de adipls\n";
	print "-------------------------------------------------\n";
    print "adipls.c.d $parout";
	system("adipls.c.d $parout");
#	system("rm -f $m_out");	
	system("rm -f ". $str . ".ssm");
#	system("gzip -f " .  $str . ".eigf.bin");    

    
        
    
} # end foreach $fich(@fich)

    system("rm -f $template");








#*************************************************
sub usage {
    print "*************************************************************\n";
    print "$script_name  fmodels  fparam [-subname XX][-cesam V]\n";
    print "\nComputes with ADIPLS the  eigenfunctions and eigenfrequencies\n";
    print "for one or a set of 1D models.\n";
    print "The model can be either a CESAM .osc file\n";
    print "or a binary model compatible with ADIPLS.\n";
    print "In the latter case the file must have the sufix '.jcdb' or '.bin'.\n";
    print "When the file is a CESAM model, it is first converted \n";
    print "into a binary file compatible with ADIPLS using INTERF5\n";
    print "All the models must be in the current directory\n";
    print "INPUTS:\n";
    print "fmodels : the 1D model (e.g.: '*01*.osc' or '*01*.bin')  \n";
    print "fparam : the file contening the parameters for the adipls code\n";
    print "-subname : the subname 'XX' will be added in each of the \n";
    print "output files before the sufix (e.g.  *.XX.ef) \n";
    print "-cesam V : we assume version V of CESAM (see interf5).  \n";
    print "-By default V=4  \n";
    print "\n" ;
    print "Reza Samadi, 02.12.2002, updated 13.03.2008\n" ;
    print "*************************************************************\n";
    return;
}
   
