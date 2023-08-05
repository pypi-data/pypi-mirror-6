# -*- coding: utf-8 -*-
'''
A FTP subclass which adds some Mainframe z/OS ftp features
==========================================================

    class zosftplib.Zftp(host[, user[, passwd[, acct[, timeout, sbdataconn]]]])

    * Allows submitting a job and automatically receiving the output :
    * Allows submitting DB2 queries and retrieving their output
    * PDS directory exploration
    * Retrieve a large amount of members from a PDS in parallel:
    * Catalog/Jes spool exploration


    get_pds_directory(pdsname, attrs=False, samples=None)

         -> returns a dictionary of members:attrs from a PDS directory
    
    exec_sql([query='', cntlfile='', db2id='', spread='')
     
         -> returns the resultset of a Db2/sql query
    
    submit_job(jcl, jobname='', retry_info=3)
     
         -> submits a job and returns its jobid
      
    submit_wait_job(jcl, jobname='', cntlfile='', spoolback=None,
                        purge = False, timeout=None)
                        
         -> submits a job, waits and returns its outputs  

    get_job_infos(jobid, jobmask='*')

         -> returns job status, returncode and other JES infos

    get_members(pdsname, local_dir, lmembers='*', retr='',
                   callback=None, ftp_threads=1, samples=None, fmback=None)

         -> gets all members (or a list) from a PDS (can be parallelized)
    
    list_catalog(mask)

         -> returns a list of dsnames and their attributes (dictionaries)
    
    list_jes_spool(jobmask='', owner='', status='ALL')

         -> returns a list of jobname/status (dictionaries)

    download_text(mvsname, localpath)
     
    download_binary(mvsname, localpath)

    upload_text(localpath, mvsname, sitecmd='')

    upload_binary(localpath, mvsname, sitecmd='')

'''

import re
import os.path
import subprocess
import ftplib

def test_hostname_alive(host):
    "ping a host"
    # $TODO : test under "windows"
    ping = subprocess.Popen("ping -q -c2 -W 2 " + host, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    exitcode = ping.wait()
    response = ping.stdout.read()
    errors   = ping.stderr.read()
    if exitcode in (0, 1):
        life = re.search(r"(\d) received", response)
        if life and life.group(1) == '0':  # 1 packets transmitted, 0 received,
            raise ZftpError("Unknown hostname %s (if ICMP ping is blocked"
                            ", try this: Zftp(..,noping=1) )"%host)
    else:
        if 'unknown host' in errors:
            raise ZftpError("Unknown hostname %s (%s)"%(host, errors))
        else:
            raise ZftpError("Ping hostname %s error (%s)"%(host, errors))

    
def ensure_cntlfile(file_or_text, jobcontrol=None):
    """
    To check if the JCL or SQL input 'ctnl file' is correct (80 columns
    max line length). Returns an file object
    - file_or_text: can be pathname (whose existence was previously tested),
      a string or a file object
    - control: test if jobcard 'JOBNAME' value in jcl is conform to the JOBNAME
    parameter. This is necessary for the list_jes_spool method to find JOBNAME
    (with jes 'JESJOBNAME' subcommand)
    """

    if isinstance(file_or_text, file):
        fout = file_or_text
        text = fout.read()
        fout.seek(0) # at beginning
    elif isinstance(file_or_text, basestring):
        if os.path.isfile(file_or_text):
            fout = open(file_or_text, 'r')
            text = fout.read()
            fout.seek(0) # at beginning
        else: 
            import cStringIO
            text = file_or_text
            fout = cStringIO.StringIO(text)
    else:
        raise CntlError("invalid cntlfile type: %s"
                        %(file_or_text,))
    lines_error = [l for l in text.splitlines() if len(l.rstrip()) > 80]
    if lines_error:
        raise CntlError("invalid cntlfile record length: %s (should be <=80)"
                        " %s"%(len(lines_error[0]),lines_error[0]))
    if jobcontrol:
        job_re = re.compile(r"^[\n]?//(\S+)\s+JOB\s+", flags=re.MULTILINE)
        sx0 = re.search(job_re, text)
        if not sx0:
            raise JobnameError("invalid jobcard: '%s' in JCL file "
                               % (text[:80].strip(),))           
        if not sx0.group(1).startswith(jobcontrol):
            raise JobnameError("invalid jobname %s parameter in JCL file "
                                "(JESJOBNAME= %s)"% 
                                (sx0.group(1), jobcontrol))
    return fout

def sanitize_mvsname(name):
    " sanitize mvs dataset name "
    if name:
        return "'" + name.strip().replace("'","").replace('"','') + "'"
    else:
        return name

 
class ZftpError( Exception ):
    """ZosFtp error."""
    def __init__(self, value):
        super(ZftpError, self).__init__(value)
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class JobnameError(ZftpError):
    " jobname parameter error"
    pass

class JclError(ZftpError):
    """ jcl error "
    IEF212I <jobname> stepname ddname> - DATA SET NOT FOUND
    IEFC452I INVALID - JOB NOT RUN - JCL ERROR  848
    IEFC452I <jobname> - JOB NOT RUN - JCL ERROR  858
    IEFC605I UNIDENTIFIED OPERATION FIELD
    IEF643I UNIDENTIFIED POSITIONAL PARAMETER IN THE DISP FIELD
    IEFC662I INVALID LABEL
    """
    pass

class CntlError(ZftpError):
    " cntl file lrecl error "
    pass

class Zftp(ftplib.FTP):
    """
       MVS z/OS FTP subclass
    """
    # To parse nlst() output :
    CATALOG_OFS = (('Volume', 0, 6), ('Unit', 7, 14), ('Referred', 14, 24),
                   ('Ext', 24, 27), ('Used', 27, 32), ('Recfm', 34, 39),
                   ('Lrecl', 39, 44), ('BlkSz', 45, 50), ('Dsorg', 51, 55),
                   ('Dsname', 56, 100))
    PDSLOAD_OFS = (('Size', 10, 16), ('TTR', 17, 23), ('Alias-of', 24, 32),
                   ('AC', 33, 35), ('Attributes', 36, 66), ('Amode', 68, 71),
                   ('Rmode', 74, 77))
    PDSTXT_OFS  = (('VV.MM', 10, 15), ('Created', 16, 26), ('Changed', 27, 37),
                  ('Heure', 38, 43), ('Size', 44, 49), ('Init', 50, 79),
                  ('Size', 44, 79), ('Id', 44, 79))
 
    def __init__(self, host='', user='', passwd='', acct='', timeout=600.0,
                 sbdataconn='', **kwargs):

        self.__ping = kwargs.get('ping', False)
        if self.__ping:                 # caution: a host can be configured 
            test_hostname_alive(host)   # to block icmp pings

        self.__kwargs = kwargs
        try:
            ftplib.FTP.__init__(self, host, user, passwd, acct, timeout)
        except TypeError: # timeout not supported ?
            ftplib.FTP.__init__(self, host, user, passwd, acct)
            self.timeout = None
        syst = self.sendcmd('SYST')    
        if not 'z/OS' in syst:
            raise ZftpError("host %s is not a MVS or z/OS platform: %s"
                            %(host, syst))
        if sbdataconn:
            self.sendcmd('SITE sbdataconn=' + sbdataconn)
        self.sbdataconn = sbdataconn
        self.stats  = self.sendcmd('STAT')
        self.stats  = self.sendcmd('STAT')
        pos_ftyp    = self.stats.find('211-FileType') + 12
        pos_jesint  = self.stats.find('211-JESINTERFACELEVEL') + 25
        self.filetype = self.stats[pos_ftyp :pos_ftyp + 3]
        self.__jesinterfacelevel = self.stats[pos_jesint :pos_jesint + 1]
        self.__offsets = None
        self.__processed_members = 0 
        self.__jobid = None

    def login(self, user = '', passwd = '', acct = ''):
        self.user   = user
        self.passwd = passwd
        self.acct   = acct
        ftplib.FTP.login(self, user, passwd, acct)

        
    def _setfiletype(self, filetype='SEQ'):
        """Switch z/OS FTP filetype parameter : SEQ, JES, DB2
        """
        if not self.filetype == filetype:
            self.sendcmd('SITE filetype=' + filetype)
        self.filetype = filetype

    def getresp(self):
        """
        ftplib.getresp :
        parse JOBNAME in 250/125 z/OS FTP response 
        """
        resp = self.getmultiline()
        if self.debugging:
            print '*resp*', self.sanitize(resp)
        self.lastresp = resp[:3]
        c = resp[:1]
        if c in ('1', '2', '3'):
            if resp[:3] in('250','125'):                   #|Zftp spec
                sx0 = re.search(r"\s+(JOB\d{5})\s+", resp) #| 
                if sx0:                                    #| 
                    self.__jobid = sx0.group(1)            #|
            return resp
        if c == '4':
            raise ftplib.error_temp, resp
        if c == '5':
            raise ftplib.error_perm, resp
        raise ftplib.error_proto, resp

    def download_text(self, mvsname, localpath):
        " download one file by FTP in text mode "
        self._setfiletype('SEQ')
        localfile = open(localpath, 'w')
        mvsname = sanitize_mvsname(mvsname)
        def callback(line):
            localfile.write(line + '\n')
        self.retrlines('RETR ' + mvsname, callback)
        localfile.close()

    def download_binary(self, mvsname, localpath):
        " download one file by FTP in binary mode "
        self._setfiletype('SEQ')
        localfile = open(localpath, 'wb')
        mvsname = sanitize_mvsname(mvsname)
        self.retrbinary('RETR ' + mvsname, localfile.write)
        localfile.close()

    def upload_text(self, localpath, mvsname, sitecmd=''):
        " upload one file by FTP in text mode "
        self._setfiletype('SEQ')
        sitecmd = sitecmd or 'lrecl=80 blk=3200 cyl pri=1 sec=5'
        self.sendcmd('SITE ' + sitecmd)
        mvsname = sanitize_mvsname(mvsname)
        localfile = open(localpath, 'rb')
        self.storlines('STOR ' + mvsname, localfile)
        localfile.close()

    def upload_binary(self, localpath, mvsname, sitecmd=''):
        " upload one file by FTP in binary mode "
        self._setfiletype('SEQ')
        sitecmd = sitecmd or 'lrecl=80 blk=3200 cyl pri=1 sec=5'
        self.sendcmd('SITE ' + sitecmd)
        mvsname = sanitize_mvsname(mvsname)
        localfile = open(localpath, 'rb')
        self.storbinary('STOR ' + mvsname, localfile)
        localfile.close()       

    def list_jes_spool(self, jobmask='', owner='', status='ALL'):
        """
        list all jobname from jes spool where jobname like mask, owner and status
        """
        jes_spool = []
        if status.upper() not in ('ALL', 'INPUT', 'OUTPUT', 'ACTIVE'):
            status = 'ALL'
        try:
            self._setfiletype('JES')
            if jobmask:
                self.sendcmd('SITE JESJOBNAME=' + jobmask)
            if owner:
                self.sendcmd('SITE JESOWNER=' + owner)
            self.sendcmd('SITE JESSTATUS=' + status)
            self.dir(jes_spool.append)
        except (ZftpError, ftplib.all_errors), msg:
            if '550 No jobs found' in str(msg):
                return jes_spool
            else:
                raise
        return jes_spool

    def get_job_infos(self, jobid, jobmask='*'):
        """
        retrieve JES spool information from a jobid and a jobmask 
        """
        # jesinterfacelevel1 output regexp:
        sr_v1 = re.compile(r"\s*(\S+)\s+(\S+)\s+(\S+)\s+(\d+) Spool Files")
        # jesinterfacelevel2 output regexp:
        sr_v2 = re.compile(r"\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(.*) "
                           r"(\d+) spool files")
        job = {"jobid":jobid, "owner":'?', "class":'?', "rc":'?',
               "jobname":'?', "spool":'?'}  
        for linej in self.list_jes_spool(jobmask, status='ALL'):
            if not linej.startswith('JOBNAME'):
                if self.__jesinterfacelevel == '2': 
                    sx0 = re.search(sr_v2, linej)
                    if sx0 and sx0.group(2) == jobid:
                        (job["jobname"],
                         _, # jobid
                         job["owner"],
                         job["status"],
                         job["class"],
                         job["rc"],
                         job["spool"]) = sx0.group(1, 2, 3, 4, 5, 6, 7)
                        break
                else: #self.__jesinterfacelevel = '1' 
                    sx0 = re.search(sr_v1, linej)
                    if sx0: 
                        (job["jobname"],
                         _, # jobid
                         job["status"],
                         job["spool"]) = sx0.group(1, 2, 3, 4)
                        break
        return job

    def submit_job(self, jcl, jobname='', retry_info=3):
        """
        You can submit a job using FTP by putting a jcl file
        in JES 'internal reader'
        """
        resp = ''
        retry_info = retry_info or 0
        try:
            self._setfiletype('JES')
            self.__jobid = None
            resp = self.storlines('STOR INTRDR',
                                  ensure_cntlfile(jcl, jobcontrol=jobname))  
            while retry_info > 0 :
                job = self.get_job_infos(self.__jobid, jobname + '*')
                if job["rc"] == '?':
                    if self.debugging:
                        print "** retry get_job_infos **", retry_info 
                    retry_info -= 1
                    import time   
                    time.sleep(1)
                else:
                    break
        except (ZftpError, ftplib.all_errors), msg:
            raise ZftpError( "submit_job error: %s %s"%(msg, resp))
        return job
   
    def submit_wait_job(self, jcl, jobname='', cntlfile='', spoolback=None,
                        purge = False, timeout=None):
        """
        You can submit a job using FTP and automatically receive your output.
        Rather than using the JCL you built on the FTP client, this function
        uses the JCL you have built on the FTP server.
        Automatic retrieval of jobs works only if the file contains a single 
        job. It does not work for files that include more than one job
        (multiple JOB cards).
        """
 
        output = []
        resp   = ''
        spoolback = spoolback or (lambda line: output.append(line))       
        cntlfile  = sanitize_mvsname(cntlfile) or ("'" + self.user +
                                                         ".FTPTEMP0.CNTL'")
        jobname   = jobname or self.user
        timeout   = timeout or self.timeout
        if timeout != self.timeout: # new timeout value => reconnect
            self.close() 
            self.__init__(self.host, self.user, self.passwd, self.acct, timeout,
                          self.sbdataconn, **self.__kwargs)
        try:
            self._setfiletype('SEQ')
            resp = self.storlines('STOR ' + cntlfile,
                                  ensure_cntlfile(jcl, jobcontrol=jobname))
            self._setfiletype('JES NOJESGETBYDSN') 
            #200-JESINTERFACELEVEL=1. value of JESJOBname cannot be modified
            if (self.__jesinterfacelevel == '1' and
                not jobname.startswith(self.user)):
                raise JobnameError("JESINTERFACELEVEL=1, The value of "
                                   "JESJOBname cannot be modified: %s"%jobname)
            else:
                self.sendcmd('SITE JESJOBNAME=' + jobname + '*')
            self.__jobid = None
            resp = self.retrlines('RETR ' + cntlfile, spoolback)
            #self.__jobid was parsed from self.getresp() during RETR cmd
            job = self.get_job_infos(self.__jobid, jobname + '*')
            if purge and job["jobid"]:
                resp = self.sendcmd('DELE ' + job["jobid"])
                job["status"] += ' (job purged)'
            job["output"] = output    
           
        except (ZftpError, ftplib.all_errors), msg:
            raise ZftpError( "submit_wait_job error: %s (last response:%s)"
                             %(msg, resp))

        return job
    
# When submitting a job and automatically receiving the output, remember that
# your session is suspended. You should use care, based on the anticipated run
# time of your job, when using this function. If your session times out, you
# must restart FTP and manually retrieve your output. Session timeouts are
# caused by the following:
# The FTP Server does not wait long enough for the job that is executing to end
# Increase the JESPUTGETTO interval in the FTP.DATA data statement on the
# server. This defaults to 10 minutes and defines the amount of time FTP waits
# for the submitted job to complete before timing out.
# The FTP client does not wait long enough for the job to complete and the
# server to retrieve the output. Increase DATACTTIME timer value in the client.
# This defaults to two minutes and defines the amount of time the client waits
# for a response from the server. The control or data connection is closed.
# This is usually caused by a firewall that timed out the session because of
# inactivity. Add FTPKEEPALIVE (control connection) and DATAKEEPALIVE
# (data connection) statements in the FTP.DATA data file. FTP client and FTP
# Server receive resets. This is usually caused by a firewall that timed out
# the session because of a lack of activity. Add an FTPKEEPALIVE statement or
# decrease the time interval on the current FTPKEEPALIVE statement in the
# FTP.DATA data file. The keepalive value on FTPKEEPALIVE must be less than
# the expected value of the server.
       
    def db2_ssid(self):
        """Find DB2 subsystem name in FTP STATS cmd outputs"""
        db2_re   = re.compile(r"211-SITE DB2 subsystem name is (.*)")
        db2_find = re.findall(db2_re, self.stats)
        if db2_find:
            return db2_find[0] 
        else:
            return None

    def exec_sql(self, query='', cntlfile='', db2id='', spread=''):
        """
        Allows submitting DB2 queries and retrieving their output
          | DB2 plan EZAFTPMQ should be declared in in your 'TCPIP.FTP.DATA':
          | DB2PLAN       EZAFTPMQ        ; db2 plan name for OE-FTP 
          | and authorised in Db2: 'GRANT EXECUTE ON PLAN EZAFTPMQ TO PUBLIC'
        """
        resultset = []
        resp = ''
        cntlfile = sanitize_mvsname(cntlfile) or ("'" + self.user +
                                                        ".FTPTEMP0.SQL'")
        spread   = spread or "SPREAD"
        db2id    = db2id or self.db2_ssid()
        if not db2id:
            raise ZftpError( "exec_sql DSN Error (DB2 subsystem name):"
                             "%s" % (db2id,))
        query = query or ("select 'DB2 Subsystem " + db2id +
                              " is OK !' from SYSIBM.SYSDUMMY1")
        try:
            self._setfiletype('SQL')
            if db2id:
                self.sendcmd('SITE DB2=' + db2id)
            self.sendcmd('SITE ' + spread)
            self.cwd("''")
            self.sendcmd('SITE lrecl=80 blk=3200 cyl pri=1 sec=5')
            resp = self.storlines('STOR ' + cntlfile, ensure_cntlfile(query))
            self.retrlines("RETR " + cntlfile, lambda l: resultset.append(l)) 
        except ftplib.all_errors, msg:
            if resultset:
                hlp = ''.join([l + '\n' for l in resultset])
            else:    
                hlp = ("control DB2 parameters in your 'TCPIP.FTP.DATA' file:\n"
                       " DB2           xxxx        ; db2 subsystem name\n"
                       " DB2PLAN       EZAFTPMQ    ; db2 plan name for OE-FTP")
            raise ZftpError( "exec_sql Error %s %s (%s)" % (msg, resp, hlp))
        return resultset               
                  
    def list_catalog(self, mask):
        """ Scans the MVS Catalog and returns a list of dictionaries with keys:
            'Recfm', 'Used', 'Lrecl', 'Dsname', 'Dsorg', 'Volume', 'Ext',
            'BlkSz', 'Unit', 'Referred'
        """
       
        def parse_and_store_catalog_line(line):
            """ parse ftp dir cmd outputs
            """
            if 'DSNAME' in line.upper(): 
                self.__offsets = self.CATALOG_OFS
            else:
                entry = {}
                entry["Dsname"] = line[56:].replace("'","")
                for (label, pos , length)  in self.__offsets:
                    if not label == 'Dsname':
                        if "User catalog connector" in line:
                            entry[label] = None
                        elif "Error determining attributes" in line:
                            entry[label] = '?'
                        else:
                            entry[label] = line[pos:length].strip()
                catalog.append(entry)

        catalog = []
        self.__offsets = None                                    
        mask = sanitize_mvsname(mask)
        self._setfiletype('SEQ')
        self.cwd("''")
        try:
            self.dir(mask, parse_and_store_catalog_line)
        except (ZftpError, ftplib.error_perm), msg:
            if '550 No data sets found' in str(msg):
                return catalog
            else:
                raise

        return catalog
         
    def get_pds_directory(self, pdsname, attrs=False, samples=None):
        """ Returns a dictionnary from PDS directory
            Attributes are different between sources and loads member
        """ 
        def parse_and_store_directory_line(line):
            """ parse ftp dir cmd output from a PDS
            """
            if 'NAME' in line.upper(): # first line
                if 'Alias-of' in line: # is a loadmodule directory
                    self.__offsets = self.PDSLOAD_OFS
                else:
                    self.__offsets = self.PDSTXT_OFS
            else:
                try:
                    member = line[0:8].strip()
                    directory[member] = [line[pos:length].strip()
                                        for (_, pos , length) in self.__offsets]
                except Exception, msg:
                    raise ZftpError("parse_and_store_directory_line error:"
                                    "line=%s msg=%s offsets=:%s"
                                    %(line, msg, self.__offsets))

        directory = {}
        self.__offsets = None
        pdsname = sanitize_mvsname(pdsname)
        self._setfiletype('SEQ')
        # PDS test : '250 The working directory is a partitioned data set'
        if not self.cwd(pdsname).find('is a partitioned data set') > 0:
            raise ZftpError("dataset %s is not partitionned"%(pdsname,))
        try:
            if attrs:
                self.dir(parse_and_store_directory_line)
            else:
                for entry in self.nlst():
                    directory[entry] = None
        except (ZftpError, ftplib.error_perm), msg:
            if "550 No members found" in str(msg):
                return directory
            else:
                raise ZftpError("get_pds_directory error: %s"%(msg))        
        if samples:
            import random
            sample_dic = {}
            try:
                for memb in random.sample(directory, samples):
                    sample_dic[memb] = directory[memb]
                return sample_dic    
            except ValueError:
                del sample_dic
                return directory
        else:
            return directory

    def get_members(self, pdsname, localpath, lmembers='*', retr='',
                     callback=None, ftp_threads=1, samples=None, fmback=None):
        """
        Retrieves members from a PDS
        """
        
        def get_partial(partial_directory, partial_id=1, partial_lock=None):
            """ get partial directory members
            """
            # $TODO :
            # - Exception handling :
            #   garbage in member name (Computer Associates PDSM...)
            # - Multiple Get
            if partial_id > 1: # create new session
                partial_ftp = Zftp(self.host, self.user, self.passwd, self.acct,
                                   self.timeout,self.sbdataconn,**self.__kwargs)
            else:
                partial_ftp = self # keep the current session
            if self.debugging:
                partial_ftp.set_debuglevel(self.debugging)    
            if not partial_ftp.cwd(pdsname).find('partitioned data set') > 0:
                raise ZftpError("get_members error: dataset %s"
                                " is not partitionned"%(pdsname,))
            for member in partial_directory:
                onepath = os.path.join(localpath, member)
                try:
                    if callback is None:
                        if retr == 'LINES':
                            fmemb = open(onepath,'wb')
                            partial_ftp.retrlines('RETR ' + member,
                                             lambda l: fmemb.write('%s\n' % l))
                            fmemb.close()
                        else:  # 'BINARY':
                            partial_ftp.retrbinary('RETR ' + member, open(
                                onepath, 'wb').write)
                        if fmback:
                            fmback(onepath) # member callback func ?
                    else:
                        if retr == 'LINES':
                            partial_ftp.retrlines('RETR ' + member,
                                                  lambda l: callback(l, member))
                        else: # 'BINARY':
                            partial_ftp.retrbinary('RETR ' + member, callback,
                                                   blocksize=8000)
                    if partial_lock:
                        partial_lock.acquire()
                        self.__processed_members += 1 
                        partial_lock.release()
                    else:
                        self.__processed_members += 1
                except ftplib.error_perm, msg:        
                    echecs.append((member, msg))
            if partial_id  > 1:
                partial_ftp.close()
            else:
                pass # not quit this session 

        echecs = []
        self.__processed_members = 0
        retr = retr.upper() or 'LINES'
        pdsname = sanitize_mvsname(pdsname)
        if not os.path.isdir(localpath):
            raise ZftpError("get_members %s error, no such "
                            "directory %s"%(pdsname, localpath))
        if lmembers in ('*', 'ALL'):        
            directory = self.get_pds_directory(pdsname, attrs=False,
                                               samples=samples)
        else:
            if isinstance(lmembers, list) or isinstance(lmembers, tuple):
                directory = lmembers
            else:
                raise ZftpError("get_members %s, liste members type error, '*'"
                          " or list or tuple expected: %s"%(pdsname, lmembers))
        self._setfiletype('SEQ')
        nb_members = len(directory)
        if ftp_threads <= 1:
            get_partial(list(directory), localpath) # 1 session
        else:
            if ftp_threads > 16:
                ftp_threads = min(16, nb_members / 10)
            import thread, threading
            thread_list = []
            lock_thread = thread.allocate_lock()  # init lock
            # slice size:
            if nb_members % ftp_threads == 0:  
                slice_len = nb_members / ftp_threads
            else:   
                slice_len = (nb_members / ftp_threads) + 1
            # prepare directory slicing:
            full_dir = [d for d in directory if not d.startswith('PDS')]
            full_dir.sort()
            slice_num = 1
            for pos in range(0, nb_members, slice_len):  # prepare ftp threads..
                slice_dir = full_dir[pos:pos + slice_len]
                th0 = threading.Thread(target=get_partial,
                                       args=(slice_dir, slice_num, lock_thread))
                thread_list.append(th0)
                slice_num += 1             
            for th0 in thread_list:   
                th0.start()
            for th0 in thread_list:  
                th0.join()
        if self.__processed_members != nb_members:
            if self.__processed_members > 0:
                raise ZftpError("get_members %s  partial result "
                                "(%s Ok members(s)/%s), errors: %s"%
                                (pdsname, self.__processed_members,
                                         nb_members,echecs))
            else:
                raise ZftpError("get_members %s  all members in error "
                                "(%s members(s) OK/%s)"%
                                (pdsname, self.__processed_members, nb_members))
            
            

