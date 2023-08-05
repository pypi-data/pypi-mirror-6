=========
zosftplib
=========        

**A FTP subclass which adds some Mainframe z/OS features like job submission, execution of sql/DB2 queries, ...**
   
Usage
===== 

  .. sourcecode :: python

	   import zosftplib
	   Myzftp = zosftplib.Zftp(mvshost, mvsuser, passwd,
                                   timeout=500.0, sbdataconn='(ibm-1147,iso8859-1)')

Features
========


submitting sql/DB2 queries and retrieving their outputs 
-------------------------------------------------------

  .. sourcecode :: python

	   with open('/tmp/systables.csv', 'w') as outfile:
	       for line in Myzftp.exec_sql("SELECT * FROM SYSIBM.SYSTABLES WITH UR"):
		   outfile.write(';'.join(line.split()) + '\n')



submitting batch jobs, pending their outputs 
--------------------------------------------

  .. sourcecode :: python

            # easy job for zos:
            job = Myzftp.submit_wait_job('//IBMUSERX JOB MSGLEVEL(1,1)\n'
                                         '//STEP001 EXEC PGM=IEFBR14',
                                          purge=True)
            print "rc:", job["rc"], "Jes status:", job["status"]
            for line in job["output"]:
                print line


  This produces the following output::
 
    rc: RC=0000 Jes status: OUTPUT (job purged)
    1                         J E S 2  J O B  L O G  --  S Y S T E M  S Y S 1  --  N O D E  N 1              
    0 
     17.49.35 JOB03914 ---- WEDNESDAY, 27 NOV 2013 ----
     17.49.35 JOB03914  IRR010I  USERID IBMUSER  IS ASSIGNED TO THIS JOB.
     17.49.35 JOB03914  ICH70001I IBMUSER  LAST ACCESS AT 17:47:56 ON WEDNESDAY, NOVEMBER 27, 2013
     17.49.35 JOB03914  $HASP373 IBMUSERX STARTED - INIT 1    - CLASS A - SYS SYS1
     17.49.35 JOB03914  IEF403I IBMUSERX - STARTED - TIME=17.49.35
     17.49.35 JOB03914  IEF404I IBMUSERX - ENDED - TIME=17.49.35
     17.49.35 JOB03914  $HASP395 IBMUSERX ENDED
    0------ JES2 JOB STATISTICS ------                                                                                                   
    -  27 NOV 2013 JOB EXECUTION DATE                                                                                                    
    -            2 CARDS READ                                                                                                            
    -           24 SYSOUT PRINT RECORDS                                                                                                  
    -            0 SYSOUT PUNCH RECORDS                                                                                                  
    -            1 SYSOUT SPOOL KBYTES                                                                                                   
    -         0.00 MINUTES EXECUTION TIME                                                                                                
      END OF JES SPOOL FILE 
            1 //IBMUSERX JOB MSGLEVEL(1,1)                                            JOB03914
            2 //STEP001 EXEC PGM=IEFBR14                                                      
      END OF JES SPOOL FILE 
     ICH70001I IBMUSER  LAST ACCESS AT 17:47:56 ON WEDNESDAY, NOVEMBER 27, 2013
     IEF142I IBMUSERX STEP001 - STEP WAS EXECUTED - COND CODE 0000
     IEF373I STEP/STEP001 /START 2013331.1749
     IEF374I STEP/STEP001 /STOP  2013331.1749 CPU    0MIN 00.01SEC SRB    0MIN 00.00SEC VIRT     4K SYS   232K EXT       0K SYS   10780K
     IEF375I  JOB/IBMUSERX/START 2013331.1749
     IEF376I  JOB/IBMUSERX/STOP  2013331.1749 CPU    0MIN 00.01SEC SRB    0MIN 00.00SEC
 

z/OS Catalog and JES spool informations 
---------------------------------------

  .. sourcecode :: python
            
            for x in Myzftp.list_catalog('SYS1.*'): 
                print x["Dsname"], x["Dsorg"], x["Used"], "tracks"
            
            # print all "ACTIVE" jobs:
            for job in Myzftp.list_jes_spool('', '', 'ACTIVE'):
	        print job

  This produces the following output::

    JOBNAME  JOBID    OWNER    STATUS CLASS
    BPXAS    STC04218 START2   ACTIVE STC      
    PORTMAP  STC04182 START2   ACTIVE STC      
    BPXAS    STC04179 START2   ACTIVE STC          
    NFSC     STC04171 START2   ACTIVE STC      
    CICSA    STC04170 START2   ACTIVE STC          
    TCPIP    STC04162 TCPIP    ACTIVE STC      
    TN3270   STC04163 START2   ACTIVE STC      
    SDSF     STC04160 START2   ACTIVE STC      1 spool files 
    TSO      STC04158 START1   ACTIVE STC      1 spool files 
    INIT     STC04157 START2   ACTIVE STC      
    TCPIP    STC04162 TCPIP    ACTIVE STC      
    VTAM     STC04147 START1   ACTIVE STC      
    RACF     STC04164 START2   ACTIVE STC      
    ...

Retrieve thousands of members
-----------------------------

  .. sourcecode :: python

            Myzftp.get_members('SYS1.PARMLIB', '/tmp/parmlib/')

            Myzftp.get_members('SYS1.LINKLIB', '/tmp/linklib/',
                               members='*', retr='binary', ftp_threads=10)


Get/put sequential text/binary z/OS file 
----------------------------------------

  .. sourcecode :: python

	    Myzftp.download_binary('SYS1.MAN1', '/tmp/smf.bin')
 
            Myzftp.upload_text('/tmp/bigdata.txt', 'IBMUSER.BIGDATA',
                               sitecmd='lrecl=1024 cyl pri=500 sec=100')


Installation
============ 

The package is available as a Pip package:
    
``$ sudo pip install zosftplib``

Or using easy_install:

``$ sudo easy_install zosftplib``
        

Changelog
=========

 1.0 - (2013-11-25) 
 Initial release.

