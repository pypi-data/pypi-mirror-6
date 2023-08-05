PyMediaFire
===========

This module provides a subset of MediaFire's REST API.
Only the basic stuff is done : upload, download, create folder, read folder.
We support http(s) proxy.

If you have questions, patches, etc. feel free to contact the author directly at schampailler at skynet dot be. Follow  us on Twitter : \@Arakowa1.

Please note that this module is *in no way* endorsed by MediaFire.


Example
-------

Let's look at a simple session::

 from pymediafire import MediaFireSession

 # Open a session with your credential (check MediaFire's developper page
 # for all the information). It's basically email, password, appid, sessionkey.
 # You can pass http(s) proxy information as well; check the source code
 # for full constructor parameters.

 mf = MediaFireSession('youremail@gonzo.be', 'password', '123123',
                       '7kjshfksjdhf435lkj435345kj')

 # Load the root folder (no parameter == root folder)

 f = mf.load_folder()

 # The following print will give a list of pymediafire objects representing
 # files and folders on the server.

 print(f)

 # [FILE: dbcr.txt 198 bytes 2013-12-04 14:41:56 ma32h6y9fkmdmub,
 # FOLDER: backup_folder q3w4bx45i432c]

 # Download the first file of the loaded folder 

 mf.download(f[0], f[0].filename)
