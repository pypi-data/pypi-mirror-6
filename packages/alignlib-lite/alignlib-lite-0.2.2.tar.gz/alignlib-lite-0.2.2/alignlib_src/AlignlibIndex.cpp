#include <iostream>
#include <map>
#include "AlignlibDebug.h"
#include "AlignlibException.h"
#include "AlignlibIndex.h"


namespace alignlib
{

//--------------------------------------------------------------------------------------------
bool fileExists (const std::string & filename)
{
	debug_func_cerr( 5 );
	FILE * infile = fopen(filename.c_str(), "r");
	if (infile != NULL)
	{
		fclose(infile);
		return true;
	}
	else
	{
		return false;
	}
}

//--------------------------------------------------------------------------------------------
FILE * openFileForWrite( const std::string & filename )
{
	debug_func_cerr( 5 );
	if (fileExists(filename))
	{
		std::cerr << "# file " << filename << " already exists, aborting." << std::endl;
		exit(EXIT_FAILURE);
	}

	FILE * file = fopen( filename.c_str(), "w");

	if (file == NULL)
	{
		std::cerr << "# error while opening " << filename << " for writing." << std::endl;
		exit(EXIT_FAILURE);
	}

	return file;
}

//--------------------------------------------------------------------------------------------
FILE * openFileForRead( const std::string & filename )
{
	debug_func_cerr( 5 );
	FILE * file = fopen( filename.c_str(), "r");
	if (file == NULL)
	{
		std::cerr << "# file " << filename << " could not be opened for reading." << std::endl;
		exit(EXIT_FAILURE);
	}

	return file;
}


}

/* 
 {
 int x = fread(&nid,sizeof(Nid), 1, outfile);
 if (x != 1) return 0;
 }
 if (feof(outfile)) break;
 {
 int x = fread(&index, sizeof(FileIndex), 1, outfile);
 if (x != 1) return 0;
 }

 if (param_loglevel >= 2) 
 {
 if (!(iteration % param_report_step)) 
 {
 std::cout << "# line=" << iteration << " nid=" << nid << std::endl;
 }
 }

 Nid check_nid;
 fsetpos( infile, &index );
 {
 char * x = fgets( buffer, MAX_LINE_LENGTH, infile );
 if (x == NULL)
 {
 std::cerr << "error for nid " << nid << ": could not position"
 << std::endl;
 return 1;
 }
 }

 if (sscanf(buffer, "%ld", &check_nid) != 1) 
 {
 std::cerr << "error for nid " << nid << ": could not parse from line:" << buffer
 << std::endl;

 return 1;
 }
 
 if (nid != check_nid)
 {
 std::cerr << "error for nid " << nid << ": incorrect file position gives " 
 << check_nid << " at line :" << buffer << std::endl;
 return 1;
 }
 }
 
 fclose(infile);  
 fclose(outfile);  
 return 0;
 }

 */