/*
 * $Id: dave_mpl.1_channel.c,v 1.1 2010/10/19 11:28:17 dturner Exp $
 *
 * Abstract: this code is a template to read the raw MPL datafiles that were
 * 	created by the MPL at RHUBC-II in Chile.  I have used code provided
 * 	by Rich Coulter as the template for this routine.  This is for a single
 *	channel MPL with no polarization sensitivity!  We also (apparently) ran
 *	this system with a relatively small range of heights (from 0 to 15 km)
 *	with no profiles extending below or above this altitude; this makes the
 *	verification of the background extremely difficult.  Oh well.
 *
 * 		gcc -o dmpl -m32 dave_mpl.c -lm
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <glob.h>
#include "netcdf.h"

#define DEBUG 0
#define doswap 1
#define MAXSTRING 256
#define MAXHTS 4001
#define SOL 299792458		/* Speed of light (m / s) */
#define CALLOC(n,t)  (t*)calloc(n, sizeof(t))


        /* This structure is ideal for holding arrays of strings */
struct filelist {
  long nfiles;
  char **files;
};
typedef struct filelist filelist;

char *rcsversion = "$Id: dave_mpl.1_channel.c,v 1.1 2010/10/19 11:28:17 dturner Exp $";
int exitcode = -1;

  void swap2(char *,int);
  void swap4(char *,int);
  void swap8(char *,int);

/**********************************************************************************/
/* Gracefully opens a file                                                        */
/**********************************************************************************/
FILE *gopen(char *filename, char *mode)
{
  FILE *fp;

  fp = fopen(filename, mode);
  if(fp == NULL)
  {
    fprintf(stderr, "ERROR: Unable to open the file %s - aborting\n\n", filename);
    exit(exitcode);
  }
  return(fp);
}

/***********************************************************************************/
int readmplheader(FILE *fh,
		float *rng, 
		short *un,
		short *y,
		short *m,
		short *d,
		short *h,
		short *min,
		short *s,
		short *ds,
		long *nshot,
		long *prf,
		long *emon,
		long temp[5],
		long ad[4],
  		float *bck,
		long *nb,
		float *btim,
		float *zmax,
		short *dtimflg,
		float *cldbs)
{
  char bary[24], cary[24];
  short int i, iary[24];
  int hary[24];
  long int lary[24];
  float fary[24];

  if(DEBUG) printf("HEADER\n");
  if(fread(bary,1,8,fh) < 8) return(-1);
  *un = bary[0]; 			/* Unit number */
  *y = bary[1]; *m = bary[2]; *d = bary[3];
  *h = bary[4]; *min = bary[5]; *s = bary[6];
  *ds = bary[7];
  if(*y >= 100) *y = (*y-100)+2000; else *y = *y + 1900;

  if(fread(lary,sizeof(long),1,fh) < 1) return(-1);
  if(doswap) swap4(lary,1);
  *nshot = lary[0];

  if(fread(iary,sizeof(short),10,fh) < 10) return(-1);
  if(doswap) swap2(iary,10);
  *prf = iary[0]; 		/* pulse rep rate */
  *emon = iary[1];		/* energy monitor */
  		/* Store detector temp, telescope temp, dummy, laser temp, dummy */
  for(i = 2; i < 6; i++) temp[i-2] = (long)iary[i];
  		/* Choosing not to read in the a to d readings */
  *cldbs = (float)iary[9];			/* cloud base height */

  if(fread(lary,sizeof(long),2,fh) < 2) return(-1);
  if(doswap) swap4(lary,2);
  *bck = (float)lary[0] / 100000000;	/* Background counts */
  *btim = (float)lary[1];		/* Number of seconds per bin average */

  if(fread(iary,sizeof(short),2,fh) < 2) return(-1);
  if(doswap) swap2(iary,2);
  *zmax = (float)iary[0];		/* Maximum range */
  *dtimflg = iary[1];			/* dea time cor flag (??) */

  *rng = 0.0005 * SOL * (*btim) * 1.0e-9;	/* Range gate altitude [m] */

  *nb = (long)(*zmax / *rng + 0.5);		/* Number of bins per channel */

  if(DEBUG)
  {
    printf("  Date          : %4hd%02hd%02hd %02hd%02hd%02hd\n", *y,*m,*d,*h,*min,*s);
    printf("  Unit number   : %6hd\n", *un);
    printf("  Nshots        : %ld\n", *nshot);
    printf("  Laser Prate   : %ld\n", *prf);
    printf("  Laser energy  : %ld\n", *emon);
    printf("  Detector temp : %6ld\n", temp[0]);
    printf("  Dummy temp 1  : %6ld\n", temp[1]);
    printf("  Telescope temp: %6ld\n", temp[2]);
    printf("  Laser temp    : %6ld\n", temp[3]);
    printf("  Dummy temp 2  : %6ld\n", temp[4]);
    printf("  Number of bins: %ld\n", *nb);
    printf("  Time / bin    : %e\n", *btim);
    printf("  Vertical res  : %f\n", *rng);
    printf("  Max range     : %f\n", *zmax);
    printf("  Background    : %ld\n", *bck);
    printf("  Cloud base    : %f\n", *cldbs);
  }
  return(0);
} 

/*************************************************************************************/
/* This function was written to make the addition of data to the netCDF file easier  */
/* and more like it is in IDL.  Basically, I won't have to remember the field ids    */
/*************************************************************************************/
void ncdf_slabput(int fid, char *field, long *start, long *count, void *data)
{
  int vid;

        /* First step: get the variable's id from its name */
  vid = ncvarid(fid, field);

        /* If the id is negative, either the field did not exist     */
        /* or the file was closed.  In either case, abort gracefully */
  if(vid < 0)
  {
    fprintf(stdout, "Error: Unable to find the field %s in the netCDF file\n");
    exit(exitcode);
  }

        /* We have a valid field, so let's stuff the data in.        */
        /* Note that this assumes that the field is a 1-D field only */
  ncvarput(fid, vid, start, count, data);

  return;
}

/*************************************************************************************/
/* This function was written to make the addition of data to the netCDF file easier  */
/* and more like it is in IDL.  Basically, I won't have to remember the field ids    */
/*************************************************************************************/
void ncdf_varput1(int fid, char *field, long index, void *data)
{
  int vid;

        /* First step: get the variable's id from its name */
  vid = ncvarid(fid, field);

        /* If the id is negative, either the field did not exist     */
        /* or the file was closed.  In either case, abort gracefully */
  if(vid < 0)
  {
    fprintf(stdout, "Error: Unable to find the field %s in the netCDF file\n");
    exit(exitcode);
  }

        /* We have a valid field, so let's stuff the data in.        */
        /* Note that this assumes that the field is a 1-D field only */
  ncvarput1(fid, vid, &index, data);

  return;
}

/**********************************************************************************/
/* This function uses the glob() to find files and/or directories where the exact */
/* name is not know beforehand.  This is very similar to the routine findfile in  */
/* IDL.  To find only directories, the second argument should be set to true.     */
/**********************************************************************************/
filelist findfile(char *filename, int directory)
{
  int i;
  filelist list;
  static glob_t globbuf;
  static int globbuf_set = 0;
  
  if(!globbuf_set) globbuf_set = 1;
  else
  {
    /*  
    printf("Freeing globbuf\n");
     */ 
    globfree(&globbuf);
  }
    
  globbuf.gl_offs = 0;
  if(directory)
      i = glob(filename, GLOB_DOOFFS | GLOB_BRACE | GLOB_TILDE | GLOB_ONLYDIR,
                NULL, &globbuf);
  else i = glob(filename, GLOB_DOOFFS | GLOB_BRACE | GLOB_TILDE, NULL, &globbuf);
  if(i == 0)
  {
    list.nfiles = globbuf.gl_pathc;
    list.files  = globbuf.gl_pathv;
  }
  else if(i == GLOB_NOMATCH)
    list.nfiles = 0;
  else if(i == GLOB_ABORTED)
  {
    fprintf(stderr, "WARNING: Read error problem in findfile() - check permissions\n");
    list.nfiles = 0;
  }
  else
  {
    fprintf(stderr, "ERROR findfile() - aborting\n");
    exit(exitcode);
  }

  return(list);
}

/***********************************************************************************/
/* This routine checks to see if a file already exists for this day.		   */
/***********************************************************************************/
int netcdf_file_exist(short y, short m, short d)
{
  char filename[MAXSTRING], string[MAXSTRING];
  filelist flist;

  filelist findfile(char *, int);

  sprintf(filename,"cjcmplM1.a1.%04hd%02hd%02hd.%02hd%02hd%02hd.cdf", y,m,d,0,0,0);
  flist = findfile(filename, 0);
  if(flist.nfiles == 0) return(0); 
  else return(1);
}

/***********************************************************************************/
/* This function opens the file, performs some basic checks to make sure the fixed */
/* information is unchanged, and makes ready to append to the file.		   */
/***********************************************************************************/
int open_check_netcdf_file(short y, short m, short d, 
	long nb, float rng, long *sample, float *last_hour)
{
  int i, j, fid, did, vid;
  long nhts, nsamples, count, start;
  float ht0, ht1;
  char filename[MAXSTRING], string[MAXSTRING];

  sprintf(filename,"cjcmplM1.a1.%04hd%02hd%02hd.%02hd%02hd%02hd.cdf", y,m,d,0,0,0);
  fid = ncopen(filename, NC_WRITE);
  	
	/* Check the height dimension */
  did = ncdimid(fid,"height");
  i = ncdiminq(fid, did, (char *)0, &nhts);
  if(nhts != nb) 
  {
    fprintf(stderr,"Error: the height dimension changed on this "
    		"day (%04hd%02hd%02hd)\n", y, m, d);
    exit(exitcode);
  }

	/* Get the time dimension, so I know how many samples have been added */
  did = ncdimid(fid,"time");
  i = ncdiminq(fid, did, (char *)0, &nsamples);
  
	/* Get the hour variable, and in particular, capture the time of the last */
	/* sample.  This is done to prevent appending data we have already added  */
  vid = ncvarid(fid,"hour");
  start = nsamples-1; count = 1;
  i = ncvarget(fid,vid,&start,&count,last_hour);
  if(DEBUG) printf("  The last time sample in this file is %f\n", *last_hour);

	/* Check the height resolution of the data in the file to what I have now */
  vid = ncvarid(fid,"height");
  start = 0; count = 1;
  i = ncvarget(fid,vid,&start,&count,&ht0);
  start = 1; count = 1;
  i = ncvarget(fid,vid,&start,&count,&ht1);
  if(abs(1000*(ht1-ht0) - 1000*rng) > 1) 
  {
    fprintf(stderr,"Error: It appears that the vertical resolution changed "
    		"on this day (%04hd%02hd%02hd)\n",y,m,d);
    fprintf(stderr,"\tResolution in file : %f\n", 1000*(ht1-ht0));
    fprintf(stderr,"\tResolution in array: %f\n", 1000*rng);
    exit(exitcode);
  }

  	/* Pass the needed information back to the calling routine */
  *sample = nsamples;	
  return(fid);
}

/***********************************************************************************/
/* This routine creates the netCDF file with all of its attributes		   */
/***********************************************************************************/
int create_netcdf_file(short y, short m, short d, short h, short min, short s, 
		long nhts, float *ht, short unitnumber)
{
  char filename[MAXSTRING], string[MAXSTRING];
  int fid, vid, tdim, hdim, *dimsarray;
  float lat, lon, alt;
  time_t now;
  struct tm t;
  long bt, start, count;

  void ncdf_varput1(int, char *, long, void *);
  void ncdf_slabput(int, char *, long *, long *, void *);

  	/* Open the file */
  		/* This ingest is designed for RHUBC-II site in Chile */
  lat = -22.957;
  lon = -67.771;
  alt = 5322;
  now = time(NULL);
  sprintf(filename,"cjcmplM1.a1.%04hd%02hd%02hd.%02hd%02hd%02hd.cdf", y,m,d,0,0,0);
  fid = nccreate(filename, NC_CLOBBER);
  printf("\tCreated the file %s\n", filename);

	/* Create the dimensions */
  tdim = ncdimdef(fid, "time", NC_UNLIMITED);
  hdim = ncdimdef(fid, "height", nhts);

  	/* Create the fields, adding attributes as we go along */
  vid = ncvardef(fid, "base_time", NC_LONG, 0, NULL);
    sprintf(string, "Base time in Epoch");
    ncattput(fid, vid, "long_name", NC_CHAR, strlen(string)+1, string);
    sprintf(string, "seconds since 1970-1-1 0:00:00 0:00");
    ncattput(fid, vid, "units", NC_CHAR, strlen(string)+1, string);
  vid = ncvardef(fid, "time_offset", NC_DOUBLE, 1, &tdim);
    sprintf(string, "Time offset from base_time");
    ncattput(fid, vid, "long_name", NC_CHAR, strlen(string)+1, string);
    sprintf(string, "seconds");
    ncattput(fid, vid, "units", NC_CHAR, strlen(string)+1, string);
  vid = ncvardef(fid, "hour", NC_FLOAT, 1, &tdim);
    sprintf(string, "Hour of the day");
    ncattput(fid, vid, "long_name", NC_CHAR, strlen(string)+1, string);
    sprintf(string, "UTC");
    ncattput(fid, vid, "units", NC_CHAR, strlen(string)+1, string);
  vid = ncvardef(fid, "height", NC_FLOAT, 1, &hdim);
    sprintf(string, "height");
    ncattput(fid, vid, "long_name", NC_CHAR, strlen(string)+1, string);
    sprintf(string, "km AGL");
    ncattput(fid, vid, "units", NC_CHAR, strlen(string)+1, string);
  vid = ncvardef(fid, "nshots", NC_LONG, 1, &tdim);
    sprintf(string, "number of laser shots");
    ncattput(fid, vid, "long_name", NC_CHAR, strlen(string)+1, string);
    sprintf(string, "unitless");
    ncattput(fid, vid, "units", NC_CHAR, strlen(string)+1, string);
  vid = ncvardef(fid, "rep_rate", NC_LONG, 1, &tdim);
    sprintf(string, "laser pulse repetition frequency");
    ncattput(fid, vid, "long_name", NC_CHAR, strlen(string)+1, string);
    sprintf(string, "Hz");
    ncattput(fid, vid, "units", NC_CHAR, strlen(string)+1, string);
  vid = ncvardef(fid, "energy", NC_FLOAT, 1, &tdim);
    sprintf(string, "laser energy");
    ncattput(fid, vid, "long_name", NC_CHAR, strlen(string)+1, string);
    sprintf(string, "microJoules");
    ncattput(fid, vid, "units", NC_CHAR, strlen(string)+1, string);
  vid = ncvardef(fid, "temp_detector", NC_FLOAT, 1, &tdim);
    sprintf(string, "detector temperature");
    ncattput(fid, vid, "long_name", NC_CHAR, strlen(string)+1, string);
    sprintf(string, "C");
    ncattput(fid, vid, "units", NC_CHAR, strlen(string)+1, string);
  vid = ncvardef(fid, "temp_telescope", NC_FLOAT, 1, &tdim);
    sprintf(string, "telescope temperature");
    ncattput(fid, vid, "long_name", NC_CHAR, strlen(string)+1, string);
    sprintf(string, "C");
    ncattput(fid, vid, "units", NC_CHAR, strlen(string)+1, string);
  vid = ncvardef(fid, "temp_laser", NC_FLOAT, 1, &tdim);
    sprintf(string, "laser temperature");
    ncattput(fid, vid, "long_name", NC_CHAR, strlen(string)+1, string);
    sprintf(string, "C");
    ncattput(fid, vid, "units", NC_CHAR, strlen(string)+1, string);
  vid = ncvardef(fid, "background", NC_FLOAT, 1, &tdim);
    sprintf(string, "mean background");
    ncattput(fid, vid, "long_name", NC_CHAR, strlen(string)+1, string);
    sprintf(string, "counts / microsecond");
    ncattput(fid, vid, "units", NC_CHAR, strlen(string)+1, string);
  vid = ncvardef(fid, "initial_cbh", NC_FLOAT, 1, &tdim);
    sprintf(string, "initial cloud base height from MPL software");
    ncattput(fid, vid, "long_name", NC_CHAR, strlen(string)+1, string);
    sprintf(string, "km AGL");
    ncattput(fid, vid, "units", NC_CHAR, strlen(string)+1, string);

  dimsarray = CALLOC(2, int);
  dimsarray[0] = tdim; dimsarray[1] = hdim;
  vid = ncvardef(fid, "backscatter", NC_FLOAT, 2, dimsarray);
    sprintf(string, "attenuated backscatter");
    ncattput(fid, vid, "long_name", NC_CHAR, strlen(string)+1, string);
    sprintf(string, "counts / microsecond");
    ncattput(fid, vid, "units", NC_CHAR, strlen(string)+1, string);
    sprintf(string, "This field literally contains the counts detected by the detector for each range bin.  No corrections of any kind have been applied to this field.  In order to make proper use of the data, one should correct for detector non-linearity, subtract the afterpulse, subtract background counts, apply a range-squared correction, and correct for optical overlap and collimation effects");
    ncattput(fid, vid, "comment", NC_CHAR, strlen(string)+1, string);
  free(dimsarray);

  vid = ncvardef(fid, "lat", NC_FLOAT, 0, NULL);
    sprintf(string, "north latitude");
    ncattput(fid, vid, "long_name", NC_CHAR, strlen(string)+1, string);
    sprintf(string, "deg");
    ncattput(fid, vid, "units", NC_CHAR, strlen(string)+1, string);
  vid = ncvardef(fid, "lon", NC_FLOAT, 0, NULL);
    sprintf(string, "east longitude");
    ncattput(fid, vid, "long_name", NC_CHAR, strlen(string)+1, string);
    sprintf(string, "deg");
    ncattput(fid, vid, "units", NC_CHAR, strlen(string)+1, string);
  vid = ncvardef(fid, "alt", NC_FLOAT, 0, NULL);
    sprintf(string, "altitude");
    ncattput(fid, vid, "long_name", NC_CHAR, strlen(string)+1, string);
    sprintf(string, "m MSL");
    ncattput(fid, vid, "units", NC_CHAR, strlen(string)+1, string);

		/* Global attributes */
  strftime(string, 124, "%a %b %d %H:%M:%S %Y %Z", localtime(&now));
  ncattput(fid, NC_GLOBAL, "Date_created", NC_CHAR, strlen(string)+1, string);
  ncattput(fid, NC_GLOBAL, "Ingest_version", NC_CHAR, strlen(rcsversion)+1,rcsversion);
  sprintf(string, "DOE Atmospheric Radiation Measurement (ARM) Micropulse Lidar (MPL) "
  	"deployed to Cerro Toco, Chile, as part of the ARM-funded RHUBC-II project");
  ncattput(fid, NC_GLOBAL, "comment", NC_CHAR, strlen(string)+1, string);
  sprintf(string, "Dave Turner, NOAA National Severe Storms Laboratory, "
                "dave.turner@noaa.gov");
  ncattput(fid, NC_GLOBAL, "Author", NC_CHAR, strlen(string)+1, string);
  sprintf(string, "%hd", unitnumber);
  ncattput(fid, NC_GLOBAL, "instrument_serial_number", NC_CHAR, strlen(string)+1, string);

  		/* Take the file out of "define" mode */
  ncendef(fid);

		/* Compute the epoch time for this sample */
  t.tm_year = y - 1900;		/* Years after 1900 */
  t.tm_mon  = m-1;		/* January is 0, Dec is 11 */
  t.tm_mday = d;
  t.tm_hour = h;
  t.tm_min = min;
  t.tm_sec = s;
  t.tm_zone = (char *)0;
  t.tm_wday = t.tm_isdst = t.tm_yday = 0;
  bt = (long)timegm(&t);

  		/* Store some of the base fields */
  ncdf_varput1(fid, "base_time", 0, (void *)(&bt));
  start = 0; count = nhts;
  ncdf_slabput(fid, "height", &start, &count, (void *)ht);
  ncdf_varput1(fid, "lat", 0, (void *)(&lat));
  ncdf_varput1(fid, "lon", 0, (void *)(&lon));
  ncdf_varput1(fid, "alt", 0, (void *)(&alt));
	
		/* Flush the buffer to get the data out there */
  nc_sync(fid);

  		/* Return the file pointer.  Note that the file is still */
		/* open as the other fields will be stored later...      */
  return(fid);
}

/***********************************************************************************/
/* This routine adds a time sample to the already created (and open) data file     */
/***********************************************************************************/
void add_netcdf_sample(int fid, long sample, long nb, float rng, 
	short un, short y, short m, short d, short h, short min, short s, 
	long nshot, long prf, long emon, long *temp, float bck, 
	float cbh, float *data)
{
  int i, vid;
  long *start, *count, obt, bt;
  struct tm t;
  float ht0, ht1, hour, tmp;
  double timeoffset;

  void ncdf_varput1(int, char *, long, void *);
  void ncdf_slabput(int, char *, long *, long *, void *);

		/* Compute the epoch time for this sample */
  t.tm_year = y - 1900;		/* Years after 1900 */
  t.tm_mon  = m-1;		/* January is 0, Dec is 11 */
  t.tm_mday = d;
  t.tm_hour = h;
  t.tm_min = min;
  t.tm_sec = s;
  t.tm_zone = (char *)0;
  t.tm_wday = t.tm_isdst = t.tm_yday = 0;
  bt = (long)timegm(&t);
  hour = h + min/60. + s/3600.;

  	/* Do some quick QC to ensure that the "fixed" information is indeed */
	/* the same and that we can safely append to this datafile....	     */
  start = CALLOC(1,long);
  count = CALLOC(1,long);
  start[0] = 0; count[0] = 1;
  vid = ncvarid(fid,"base_time");
  i = ncvarget(fid,vid,start,count,&obt);

  vid = ncvarid(fid,"height");
  start[0] = 0; count[0] = 1;
  i = ncvarget(fid,vid,start,count,&ht0);
  start[0] = 1; count[0] = 1;
  i = ncvarget(fid,vid,start,count,&ht1);
  if(abs(1000*(ht1-ht0) - 1000*rng) > 1) 
  {
    fprintf(stderr,"Error: It appears that the vertical resolution changed "
    		"on this day (%04hd%02hd%02hd)\n",y,m,d);
    fprintf(stderr,"\tResolution in file : %f\n", 1000*(ht1-ht0));
    fprintf(stderr,"\tResolution in array: %f\n", 1000*rng);
    exit(exitcode);
  }
  
  	/* Add the fields to the datafile */
  timeoffset = bt - obt;		/* This is the time_offset */
  ncdf_varput1(fid,"time_offset",sample,(void *)(&timeoffset));
  ncdf_varput1(fid,"hour",sample,(void *)(&hour));
  ncdf_varput1(fid,"nshots",sample,(void *)(&nshot));
  ncdf_varput1(fid,"rep_rate",sample,(void *)(&prf));
  tmp = emon / 1000.;			
  ncdf_varput1(fid,"energy",sample,(void *)(&tmp));
  tmp = temp[0]/100.;
  ncdf_varput1(fid,"temp_detector",sample,(void *)(&tmp));
  tmp = temp[2]/100.;
  ncdf_varput1(fid,"temp_telescope",sample,(void *)(&tmp));
  tmp = temp[3]/100.;
  ncdf_varput1(fid,"temp_laser",sample,(void *)(&tmp));
  ncdf_varput1(fid,"background",sample,(void *)(&bck));
  ncdf_varput1(fid,"initial_cbh",sample,(void *)(&cbh));

  free(count); free(start);
  start = CALLOC(2,long);
  count = CALLOC(2,long);
  start[0] = sample;
  start[1] = 0;
  count[0] = 1;
  count[1] = nb;
  ncdf_slabput(fid,"backscatter",start,count,(void *)data);
  
		/* Flush the buffer to get the data out there */
  nc_sync(fid);

  return;
}

/***********************************************************************************/
int main(int argc, char *argv[])
{
  FILE *fp;
  long ldata[MAXHTS];
  float fdata[MAXHTS];
  long nelem;
  int i, j, k, firstwhile;
  short un,y,m,d,h,min,s,ds,dtimflg;
  long nshot,prf,emon,nb,maxbn;
  long temp[5],ad[4];
  float rng,bck,btim,zmax,el,cldbs;
  float last_hour=-1.;
  long sample=0;	/* The number of samples written to the output netcdf file */
  int nid;		/* The netcdf file id number */
  float *hts;		/* This is the height array of the data */

  int readmplheader(FILE *, float *, short *, short *, short *, short *, short *, 
  	short *, short *, short *, long *, long *, long *, long *, long *, float *, 
	long *, float *, float *, short *, float *);

  FILE *gopen(char *, char *);
  int netcdf_file_exist(short, short, short);
  int open_check_netcdf_file(short, short, short, long, float, long *, float *);
  int create_netcdf_file(short, short, short, short, short, short, long, 
  		float *, short);
  void add_netcdf_sample(int, long, long, float, short, short, short, short, 
  	short, short, short, long, long, long, long *, float, float, float *);

  if(argc < 2)
  {
    fprintf(stderr, "Usage: %s infile <infile2 infile3 infile4 ...>\n", argv[0]);
    fprintf(stderr, "\twhere infile is the input MPL raw datafile and there may "
    			"be may infiles\n\n");
    exit(exitcode);
  }
  for(k = 0; k < argc-1; k++)
  {
    printf("  Ingesting %s\n", argv[k+1]);

    fp = gopen(argv[k+1],"r");
    firstwhile = 1;
    while(readmplheader(fp,&rng,&un,&y,&m,&d,&h,&min,&s,&ds,&nshot,&prf,&emon,
		temp,ad,&bck,&nb,&btim,&zmax,&dtimflg,&cldbs) != -1)
    {
    	/* Read in the data lines */
      if(nelem = fread(ldata,sizeof(long),nb,fp) <= 0)
      {
        fprintf(stderr, "Error reading channel data\n");
	fprintf(stderr, "There were %ld bytes read\n", nelem);
        exit(exitcode);
      }
      if(doswap) swap4(ldata,nb);
      for(j = 0; j < nb; j++) fdata[j] = ldata[j] / 100000000.;

      		/* Determine the number of bins under the max altitude I desire */
      hts = CALLOC(nb, float);
      for(maxbn = -1, i = 0; i < nb; i++) 
      {
	hts[i] = i*rng;
	if(hts[i] <= 16.) maxbn = i;
      }
      maxbn += 1;
      if(DEBUG) for(j=0; j < maxbn; j++) 
      	printf("%2d  %7.3f  %8.5f\n", j, hts[j], fdata[j]);

      		/* Determine if another file with this date already exists */
      if(firstwhile)
      {
        j = netcdf_file_exist(y,m,d);
        if(j == 0) 
        {
			/* No file exists, so create a new file */
          nid = create_netcdf_file(y,m,d,h,min,s,maxbn,hts,un);
	  sample = 0;
        }
        else 
        {
      			/* A file exists.  Open it, make sure that it has the    */
			/* same "fixed" information as we are currently reading, */
			/* and then get ready to append to it again.		 */
          nid = open_check_netcdf_file(y,m,d,maxbn,rng,&sample,&last_hour);
        }
      }

    		/* Add this sample to the file if it is   */
		/* after the last sample time in the file */
      if(h+min/60+s/3600. > last_hour)
        add_netcdf_sample(nid,sample,maxbn,rng,un,y,m,d,h,min,s,nshot,prf,emon,
    		temp,bck,cldbs,fdata);

      		/* Free up the memory */
      free(hts);

		/* Advance the pointer */
      sample++;
      		/* Change the boolean */
      firstwhile = 0;
    }

    if(!firstwhile) 
    {
      		/* If this happens, then there were data in the raw file   */
		/* which means the netCDF output file was actually openned */
      ncclose(nid);
    }
    fclose(fp);
    fflush(stderr);
    fflush(stdout);
    if(exitcode < 0) exitcode = 1; else exitcode++;
  } 
  exit(0);
}
