"""
zosftp Tests Unit 
"""
import zosftplib
import os, shutil        
import unittest

class TestSequenceFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(self):
      print "Setup a test mvs ftp session"
      self.host   = raw_input("MVS host:") or '9.24.115.101'
      self.user   = raw_input("MVS user:") or 'IBMUSER'
      self.passwd = raw_input("MVS pass:") or 'AZERT'

    def setUp(self):
        self.ftp = zosftplib.Zftp(self.host, self.user, self.passwd)
      
    def tearDown(self):
        self.ftp.close()

    def test_001_invalid_hostname(self):
        self.ftp.close()
        with self.assertRaises(zosftplib.ZftpError) as context:
            self.ftp = zosftplib.Zftp('inexitanthostname?', 'IBMUSER', 'AZERT',ping=True)
        self.assertTrue('Unknown hostname' in context.exception.message)

    def test_002_invalid_ip(self):
        self.ftp.close()
        with self.assertRaises(zosftplib.ZftpError) as context:
            self.ftp = zosftplib.Zftp('1.1.1.1', 'IBMUSER', 'AZERT',ping=True)
        self.assertTrue('Unknown hostname' in context.exception.message)

    def test_003_invalid_user(self):
        self.ftp.close()
        with self.assertRaises(zosftplib.ftplib.all_errors) as context:
            self.ftp = zosftplib.Zftp('9.24.115.101', 'TOTO', 'AZERT')
        self.assertTrue('530 PASS command failed' in context.exception.message)

    def test_004_invalid_passwd(self):
        self.ftp.close()
        with self.assertRaises(zosftplib.ftplib.all_errors) as context:
            self.ftp = zosftplib.Zftp('9.24.115.101', 'IBMUSER', 'AAAAA')
        self.assertTrue('530 PASS command failed' in context.exception.message)

    def test_005_invalid_FTP_platform(self):
        self.ftp.close()
        with self.assertRaises(zosftplib.ZftpError) as context:
            self.ftp = zosftplib.Zftp('cbttape.org')
        self.assertTrue('not a MVS or z/OS platform' in context.exception.message)

    def test_101_get_directory_not_partitionned(self):
        # Get PDS directory : data set not partitionned:
        with self.assertRaises(zosftplib.ZftpError) as context:
            self.ftp.get_pds_directory('SYS1.MAN1')
        self.assertTrue('is not partitionned' in context.exception.message)

    def test_102_get_directory_attrs(self):
        d=self.ftp.get_pds_directory('SYS1.LPALIB', attrs=True)
        # Get PDS directory : member name
        self.assertTrue(d.has_key('IKJEFT1A'))
        # Get PDS directory : Alias attributes:
        self.assertTrue(d['IKJEFT1A'][2] == 'IKJEFT01',
                        'Invalid Alias IKJEFT01 in entry directory :'\
                         + str(d['IKJEFT1A']))
        # Get PDS directory : Amode/Rmode attributes:
        self.assertTrue(d['IKJEFT1A'][5:7] == ['31','ANY'],
                        'Invalid Amode/Rmode IKJEFT01 in entry directory :'\
                         + str(d['IKJEFT1A']))


    def test_201_get_members_not_partitionned(self):
        with self.assertRaises(zosftplib.ZftpError) as context:
            self.ftp.get_members('SYS1.COMMON', '/tmp/',
                                  lmembers=['IKJEFT1A', 'ZZZZZZZ'])
        self.assertTrue('is not partitionned' in context.exception.message)

    def test_202_get_members_partial_errors(self):
        with self.assertRaises(zosftplib.ZftpError) as context:
            self.ftp.get_members('SYS1.LPALIB','/tmp/',
                                  lmembers=['IKJEFT1A', 'ZZZZZZZ'])
        self.assertTrue('partial result' in context.exception.message)

    def test_203_get_members_threaded(self):
        pds = 'PARMLIB' 
        try:
            shutil.rmtree('/tmp/' + pds + '/')
        except:
            pass
        os.mkdir('/tmp/' + pds + '/')
        mvs_nb = len(self.ftp.get_pds_directory('SYS1.' + pds))
        self.ftp.get_members('SYS1.' + pds,'/tmp/' + pds + '/',
                             lmembers='*', ftp_threads=7)
        loc_nb = len(os.listdir('/tmp/' + pds + '/'))
        self.assertTrue(mvs_nb == loc_nb)
        
    def test_301_get_catalog(self):
        C = self.ftp.list_catalog("SYS1.COMMON.PAGE")
        self.assertTrue(C[0]["Dsorg"] == 'VSAM')

    def test_302_download(self):
        self.ftp.download_text("'SYS1.MACLIB(ABEND)'",
                               '/tmp/SYS1.MACLIB.ABEND.ascii')
        txt = open('/tmp/SYS1.MACLIB.ABEND.ascii', 'r').read()
        self.assertTrue('MACRO NAME = ABEND' in txt)

        self.ftp.download_binary('SYS1.MACLIB(ABEND)',
                               '/tmp/SYS1.MACLIB.ABEND.bin')
        txt = open('/tmp/SYS1.MACLIB.ABEND.bin', 'r').read().decode("cp1140")
        self.assertTrue('MACRO NAME = ABEND' in txt)

        with self.assertRaises(zosftplib.ftplib.error_perm) as context:
            self.ftp.download_text('SYS9.WINDOWS', '/tmp/non_existing')
        self.assertTrue('not found' in context.exception.message)

        with self.assertRaises(zosftplib.ftplib.all_errors) as context:
            self.ftp.download_text('SYS1.COMMON.PAGE', '/tmp/SYS1.COMMON.PAGE')
        self.assertTrue('VSAM data set' in context.exception.message)

    def test_303_upload(self):
        self.ftp.upload_text('/tmp/SYS1.MACLIB.ABEND.ascii',
                             self.ftp.user + '.SYS1.MACLIB.ABEND',
                             sitecmd='lrecl=70')
        C = self.ftp.list_catalog(self.ftp.user + '.SYS1.MACLIB.ABEND')
        self.assertTrue(C[0]["Lrecl"] == '70',C)

 
    def test_401_submiting_and_waiting_jobs(self):
        j0 = ('//TOTO0  JOB (ACCT),SH,CLASS=A,MSGCLASS=H')
        j1 = ('//TOTO1  JOB (ACCT),SH,CLASS=A,MSGCLASS=H\n'
              '//STEP00   EXEC PGM=IEFBR14')
        j2 = ('//TOTO1  JOB (ACCT),SH,CLASS=A,MSGCLASS=H\n'
              '//STEP00   EXEC PGM=WIN32DLL')
        j3 = ('//TOTO0  JOB (ACCT),SH,CLASS=A,MSGCLASS=H')
        j4 = ('//TOTO0  JOB (ACCT),SH,CLASS=A,MSGCLASS=H'
              '________________________________________')
        # submit job: JCL ERROR       
        job = self.ftp.submit_wait_job(j0, 'TOTO0', purge=True)
        self.assertTrue(job['rc'] == '(JCL error)')
        # submit job status: 'OUTPUT (job purged)'    
        self.assertTrue(job['status'] == 'OUTPUT (job purged)')
        # submit job: RC=0000
        job = self.ftp.submit_wait_job(j1, 'TOTO1', purge=True)
        self.assertTrue(job['rc'] == 'RC=0000')
        # submit job: Abend 806:
        job = self.ftp.submit_wait_job(j2, 'TOTO1', purge=True)
        self.assertTrue(job['rc'] == 'ABEND=806')
        # submit job: jcl as local file:
        job = self.ftp.submit_wait_job('jcl.txt', 'IBMUSER', purge=True)
        self.assertTrue(job['rc'] == 'RC=0000')
        # submit job: Invalid JOBNAME:
        with self.assertRaises(zosftplib.ZftpError) as context:
            job = self.ftp.submit_wait_job(j3, 'TOTO1', purge=True)
        self.assertTrue('invalid jobname' in context.exception.message)
        # submit job: Invalid input jcl file:
        with self.assertRaises(zosftplib.ZftpError) as context:
            job = self.ftp.submit_wait_job(1234, 'TOTO1', purge=True)
        self.assertTrue('invalid cntlfile' in context.exception.message)
        # submit job: Invalid cntfile lrecl:
        with self.assertRaises(zosftplib.ZftpError) as context:
            job = self.ftp.submit_wait_job(j4, 'TOTO1', purge=True)
        self.assertTrue('invalid cntlfile' in context.exception.message)
        

    def test_402_submiting_jobs(self):
        j0 = '//TOTOX  JOB (ACCT),SH,CLASS=A,MSGCLASS=H'
        j1 = ('//TOTOX  JOB (ACCT),SH,CLASS=A,MSGCLASS=H\n'
              '//STEP00   EXEC PGM=IEFBR14')
       
        job = self.ftp.submit_job(j0, 'TOTOX')
        self.assertTrue(job['rc'] == '(JCL error)', str(job))
        job = self.ftp.submit_job(j1, 'TOTOX')
        self.assertTrue(job['rc'] == 'RC=0000', str(job))


    def test_403_submit_wait_job_timeout(self):
        j0 = ('//TOTO1  JOB (ACCT),SH,CLASS=A,MSGCLASS=H,TYPRUN=HOLD\n'
              '//STEP00   EXEC PGM=IEFBR14')
        with self.assertRaises(zosftplib.ZftpError) as context:
            job = self.ftp.submit_wait_job(j0,'TOTO1',timeout=1)
        self.assertTrue('timed out' in context.exception.message)
                
    def test_500_exec_sql(self):
        request = self.ftp.exec_sql()
        self.assertTrue(request[1].startswith('DB2 Subsystem'))

        with self.assertRaises(zosftplib.ZftpError) as context:
            request = self.ftp.exec_sql(db2id='DB2X')
        self.assertTrue('exec_sql Error' in context.exception.message)

        with self.assertRaises(zosftplib.CntlError) as context:
            request = self.ftp.exec_sql('                    '
                                        '                    '
                                        '                    '
                                        '                    X')
        self.assertTrue('invalid cntlfile' in context.exception.message)    


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)
