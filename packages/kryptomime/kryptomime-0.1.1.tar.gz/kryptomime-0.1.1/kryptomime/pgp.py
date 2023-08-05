# -*- coding: utf-8 -*-
#
# PGP/MIME (GnuPG) support
#
# This file is part of kryptomime, a Python module for email kryptography.
# Copyright © 2013 Thomas Tanner <tanner@gmx.net>
# partially inspired by the Mailman Secure List Server patch by 
#  Stefan Schlott <stefan.schlott informatik.uni-ulm.de>
#  Joost van Baal <joostvb-mailman-pgp-smime.mdcc.cx>
# 
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the included LICENSE file for details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# For more details see the file COPYING.

from .mail import KryptoMIME

class PGPMIME(KryptoMIME):

    def find_key(self,addr,secret=False):
        """find key (fingerprint) for email 'addr' or return None.
        If addr is a list or tuple, return a dict(addr:keyid).
        secret searches in the secrety keyring """
        return NotImplementedError

    def sign_file(self, file, **kwargs):
        return NotImplementedError

    def sign_str(self, data, **kwargs):
        return NotImplementedError

    def verify_file(self, file, signature=None):
        return NotImplementedError

    def verify_str(self, data, signature=None):
        return NotImplementedError

    def encrypt_file(self, file, *recipients, **kwargs):
        return NotImplementedError

    def encrypt_str(self, data, *recipients, **kwargs):
        return NotImplementedError

    def decrypt_file(self, file, **kwargs):
        return NotImplementedError
    
    def decrypt_str(self, data, **kwargs):
        return NotImplementedError

    # WARNING: Be EXTREMLY CAREFUL with modifying the following code. It's very RFC-sensitive

    @staticmethod
    def _fix_quoting(text):
        "fix broken Thunderbird quoting"
        import re
        text = re.sub('^=3D','=',text,flags=re.MULTILINE)
        return text

    @staticmethod
    def _plaintext(mail, inline = False, protect=False):
        # Extract / generate plaintext
        from email.parser import HeaderParser
        import copy
        multipart = mail.is_multipart()
        if not multipart and inline: return mail.get_payload(), None
        # delete all headers except content
        mail = copy.copy(mail)
        for key in mail.keys():
            if key=='Content-Type': continue
            if not multipart and key=='Content-Transfer-Encoding': continue
            del mail[key]
        #mail.add_header('Content-Disposition','inline')
        if multipart: mail.preamble='This is a multi-part message in MIME format.'
        return mail.as_string(), mail

    @staticmethod
    def _ciphertext(mail):
        ciphertext = None
        is_pgpmime = False
        # Check: Is inline pgp?
        if type(mail)==str: mail = Parser().parsestr(mail)
        if mail.get_content_type()=='application/pgp' or mail.get_param('x-action')=='pgp-encrypted':
            ciphertext = mail.get_payload()
            is_pgpmime = False
        # Check: Is pgp/mime?
        elif mail.get_content_type()=='multipart/encrypted' and mail.get_param('protocol')=='application/pgp-encrypted':
            if mail.is_multipart():
                for submsg in mail.get_payload():
                    if submsg.get_content_type()=='application/octet-stream':
                        is_pgpmime = True
                        ciphertext = submsg.get_payload()
            else:
                ciphertext = mail.get_payload()
        # Some clients send text/plain messages containing PGP-encrypted data :-(
        if not mail.is_multipart() and (ciphertext==None) and len(mail.get_payload())>10:
            firstline = mail.get_payload().splitlines()[0]
            if firstline=='-----BEGIN PGP MESSAGE-----':
                is_pgpmime = False
                ciphertext = mail.get_payload()
        return ciphertext, is_pgpmime

    @staticmethod
    def _has_signature(mail):
        if mail.is_multipart():
            if mail.get_content_type()=='multipart/signed' and mail.get_param('protocol')=='application/pgp-signature':
                # handle detached signatures, these look like:
                for submsg in mail.get_payload():
                    if submsg.get_content_type()=='application/pgp-signature':
                        return True
            elif mail.get_content_type()=='multipart/mixed' and not mail.get_param('protocol'):
                nonsig = []
                for submsg in mail.get_payload():
                    if submsg.get_content_type()=='application/pgp-signature':
                        return True
        else:
            payload = mail.get_payload()
            if mail.get_content_type()!='text/plain' or len(payload)<=10:
                return False
            # handle inline signature; message
            firstline = payload.splitlines()[0]
            if firstline=='-----BEGIN PGP SIGNED MESSAGE-----': return True
        return False

    @staticmethod
    def _signature(mail):
        from email.parser import HeaderParser, Parser
        from .mail import as_protected, _mail_raw, _mail_transfer_content
        payload = ''
        signatures = []
        rawmail = mail
        mail = as_protected(mail)
        if mail.is_multipart():
            rawmail = as_protected(mail,headersonly=True)
            rawmail.epilogue='' # ensure final newline, workaround for http://bugs.python.org/issue14983
            if mail.get_content_type()=='multipart/signed' and mail.get_param('protocol')=='application/pgp-signature':
                # handle detached signatures, these look like:
                for submsg in mail.get_payload():
                    if submsg.get_content_type()=='application/pgp-signature':
                        signatures.append(submsg.get_payload())
                    elif not payload:
                        # yes, including headers
                        payload = submsg.as_string()
                        _mail_transfer_content(submsg,rawmail)
                        if submsg.is_multipart():
                            rawmail.set_payload(None)
                            for subsubmsg in submsg.get_payload():
                                rawmail.attach(subsubmsg)
                        else:
                            rawmail.set_payload(submsg.get_payload())
                    else:
                        # we only deal with exactly one payload part and one or more signatures parts
                        assert False, 'multipart/signed message with more than one body'
            elif mail.get_content_type()=='multipart/mixed' and not mail.get_param('protocol'):
                nonsig = []
                for submsg in mail.get_payload():
                    if submsg.get_content_type()=='application/pgp-signature':
                        signatures.append(submsg.get_payload())
                    else: nonsig.append(submsg)
                if not len(signatures): # no signature found
                    return payload, signatures, mail
                rawmail.set_payload(None)
                for submsg in nonsig:
                    if submsg.get_content_type()=='text/plain':
                        signatures = [None]
                        payload = submsg.get_payload()
                        rawmail.set_payload(payload)
                        break
                    elif not payload: # multipart?
                        # yes, including headers
                        payload = _mail_raw(submsg)
                        _mail_transfer_content(submsg,rawmail)
                        if submsg.is_multipart():
                            rawmail.set_payload(None)
                            for subsubmsg in submsg.get_payload():
                                rawmail.attach(subsubmsg)
                        else:
                            rawmail.set_payload(submsg.get_payload())
                    else:
                        # we only deal with exactly one payload part and one or more signatures parts
                        assert False, 'multipart/mixed message with more than one body'
        else:
            payload = mail.get_payload()
            if mail.get_content_type()!='text/plain' or len(payload)<=10:
                return payload, signatures, mail # no signature
            # handle inline signature; message
            firstline = payload.splitlines()[0]
            if firstline!='-----BEGIN PGP SIGNED MESSAGE-----':
                # no signature
                return payload, signatures, mail # no inline signature
            text = ''
            for line in payload.splitlines(True)[3:]: # remove first three lines
                if line.rstrip()=='-----BEGIN PGP SIGNATURE-----': break
                text += line
            signatures = [None]
            rawmail = HeaderParser().parsestr(mail.as_string())
            rawmail.del_param("x-action")
            rawmail.set_payload(text)
        return payload, signatures, rawmail

    @staticmethod
    def _decoded(mail,plaintext,is_pgpmime):
        # Check transfer type
        from email.parser import HeaderParser, Parser
        from .mail import _mail_addreplace_header, _mail_transfer_content
        mail = HeaderParser().parsestr(mail.as_string())
        tmpmsg = Parser().parsestr(plaintext)
        if mail.get_content_type()=='application/pgp': mail.set_type("text/plain")
        mail.del_param("x-action")
        if tmpmsg.is_multipart() and len(tmpmsg.get_payload())==1:
            tmppayload = tmpmsg.get_payload(0)
            _mail_transfer_content(tmppayload,mail)
            mail.set_payload(tmppayload.get_payload())
        else:
            _mail_transfer_content(tmpmsg,mail)
            if tmpmsg.is_multipart():
                mail.set_payload(None)
                for i in tmpmsg.get_payload(): mail.attach(i)
            else:
                tmppayload = tmpmsg.get_payload()
                mail.set_payload(tmppayload)
        return mail

    def analyze(self,mail):
        """Checks whether the email is encrypted or signed.
        
        :param mail: A string or email
        :returns: Whether the email is encrypted and whether it is signed (if it is not encrypted).
        :rtype: (bool,bool/None)
        """
        from email.parser import Parser
        from email.message import Message
        if type(mail)==str: mail = Parser().parsestr(mail)
        elif not isinstance(mail,Message): return False, False
        ciphertext, is_pgpmime = self._ciphertext(mail)
        if not ciphertext is None: return True, None
        if self._has_signature(mail): return False, True
        return False, False

    def strip_signature(self,mail):
        """Returns the raw email without signature. Does not check for valid signature.
        
        :param mail: A string or email
        :returns: An email without signature and whether the input was signed
        :rtype: (Message,bool)
        """
        from email.parser import Parser
        from email.message import Message
        if type(mail)==str: mail = Parser().parsestr(mail)
        elif not isinstance(mail,Message): return None, False
        payload, signatures, rawmail = self._signature(mail)
        return rawmail, len(signatures)>0

    def _check_signatures(self,payload,signatures,rawmail,strict=True):
        "returns mail without signature, whether it was signed and with which keyids"
        from .mail import protect_mail
        results, key_ids = [], []
        signed = False
        for signature in signatures:
            for ending in (None,'\n','\r\n'):
                if ending:
                    tmp = fix_lines(payload,ending=ending)
                    if tmp==payload: continue
                else: tmp = payload
                if signature is None:
                    result = self.verify_str(tmp)
                else:
                    signature = self._fix_quoting(signature)
                    result = self.verify_str(tmp, signature)
                if signed or strict: break # already found format
                if result: # found
                    if not signed and ending:
                        payload = tmp # correct format
                        rawmail = protect_mail(rawmail,ending=ending,sevenbit=False)
                    break
            if not result: continue # no signature
            signed = True
            key_ids.append(result.key_id)
            results.append(result)
        return rawmail, {'signed':signed,'key_ids':key_ids,'results':results}

    def verify(self, mail, strict=True, **kwargs):
        """Verifies the validity of the signature of an email.
        
        :type mail: string or Message object
        :param mail: A string or email
        :param strict: Whether verify the message as is. Otherwise try with different line endings.
        :type strict: bool
        :returns: whether the input was signed by the sender and detailed results
             (whether it was 'encrypted',the 'decryption' results, whether it was 'signed',
             the verification 'results' and valid 'key_ids')
        :rtype: (bool,{encrypted:bool,signed:bool,key_ids:list,decryption:dict,results:list of dicts})

        RFC1847 2.1 requires no modification of signed payloads, but some MTA change the line endings,
        which breaks the signature. With strict=False it is also checked, whether the signature would
        be valid after conversion to full CR/LF or LF.
        """
        results = {'encrypted':False,'decryption':None,'signed':False,'key_ids':[],'results':[]}
        # possible encryptions: nothing,only signed, encrypted+signed, encrypted after signed 
        from email.parser import Parser
        from email.message import Message
        import email.utils
        if type(mail)==str: mail = Parser().parsestr(mail)
        elif not isinstance(mail,Message): return False, None
        sender = mail.get('from', [])
        sender = self.find_key(email.utils.parseaddr(sender)[1])
        ciphertext, is_pgpmime = self._ciphertext(mail)
        if ciphertext: # Ciphertext present?
            results['encrypted'] = True
            ciphertext = self._fix_quoting(ciphertext)
            result = self.decrypt_str(ciphertext, **kwargs)
            results['decryption'] = result
            if not result: return False, results # cannot decrypt
            if result.valid:
                results['signed'] = True
                results['key_ids'] = [result.key_id]
                results['results'] = [result]
                return sender == result.key_id, results
            plaintext = str(result)
            mail = self._decoded(mail,plaintext,is_pgpmime)
        payload, signatures, rawmail = self._signature(mail)
        if not payload: return False, results # no plain msg
        rawmail, sresults = self._check_signatures(payload, signatures, rawmail, strict=strict)
        results.update(sresults)
        return results['signed'] and sender in results['key_ids'], results

    def decrypt(self, mail, strict=True, **kwargs):
        """Decrypts and verifies an email.
        
        :param mail: A string or email
        :type mail: string or Message object
        :param strict: Whether verify the message as is. Otherwise try with different line endings.
        :type strict: bool
        :returns: An email without signature (None if the decryption failed),
             whether the input was signed by the sender and detailed results
             (whether it was 'encrypted',the 'decryption' results, whether it was 'signed',
             the decryption 'results' and valid 'key_ids')
        :rtype: (Message,bool,{encrypted:bool,signed:bool,key_ids:list,decryption:dict,results:list of dicts})

        RFC1847 2.1 requires no modification of signed payloads, but some MTA change the line endings,
        which breaks the signature. With strict=False it is also checked, whether the signature would
        be valid after conversion to full CR/LF or LF.
        """
        results = {'encrypted':False,'decryption':None,'signed':False,'key_ids':[],'results':[]}
        # possible encryptions: nothing,only signed, encrypted+signed, encrypted after signed 
        from email.parser import Parser
        from email.message import Message
        import email.utils
        if type(mail)==str: mail = Parser().parsestr(mail)
        elif not isinstance(mail,Message): return None, False, None
        sender = mail.get('from', [])
        sender = self.find_key(email.utils.parseaddr(sender)[1])
        ciphertext, is_pgpmime = self._ciphertext(mail)
        if ciphertext: # Ciphertext present? Decode
            results['encrypted'] = True
            ciphertext = self._fix_quoting(ciphertext)
            result = self.decrypt_str(ciphertext, **kwargs)
            results['decryption'] = result
            if not result: return None, False, results
            plaintext = str(result)
            mail = self._decoded(mail,plaintext,is_pgpmime)
            if result.valid:
                results['signed'] = True
                results['key_ids'] = [result.key_id]
                results['results'] = [result]
                return mail, sender == result.key_id, results
        payload, signatures, rawmail = self._signature(mail)
        if not payload: return rawmail, False, results # no plain msg
        rawmail, sresults = self._check_signatures(payload, signatures, rawmail, strict=strict)
        results.update(sresults)
        return rawmail, results['signed'] and sender in results['key_ids'], results

    def sign(self, mail, inline=False, verify=False, **kwargs):
        """Signs an email with the sender's (From) signature.
        
        :param mail: A string or email
        :type mail: string or Message object
        :param inline: Whether to use the PGP inline format for messages with attachments, i.e. no multipart.
        :type inline: bool
        :param verify: Whether to verify the signed mail immediately
        :type verify: bool
        :returns: The signed email (None if it fails) and the sign details.
        :rtype: (Message,dict)
        """
        from email.message import Message
        from email.parser import HeaderParser, Parser
        from .mail import protect_mail
        if not isinstance(mail,(Message,str)): return None, None
        mail = protect_mail(mail,ending='\r\n',sevenbit=True) # fix line endings + 7bit
        if not 'default_key' in kwargs:
            import email.utils
            sender = mail.get('from', [])
            if sender: kwargs['default_key'] = email.utils.parseaddr(sender)[1]
        plaintext, submsg = self._plaintext(mail, inline)
        # Generate signature, report errors
        if not mail.is_multipart() and inline:
            result = self.sign_str(plaintext, clearsign=True, detach=False, **kwargs)
        else:
            result = self.sign_str(plaintext, clearsign=False, detach=True, **kwargs)
        if not result: return None, result
        signature = str(result)
        # Compile signed message
        #_mail_addreplace_header(mail,'Content-Transfer-Encoding','7bit')
        if not mail.is_multipart() and inline:
            mail.set_payload(signature)
            mail.set_param('x-action','pgp-signed')
            if verify:
                vresult = self.verify_str(signature)
                if not vresult: return None, result
        else:
            # workaround to preserve header order
            tmp = Message()
            tmp['Content-Type'] = mail['Content-Type']
            tmp.set_type('multipart/signed')
            tmp.del_param('boundary') # delete boundary as we need a new one
            tmp.set_param('protocol','application/pgp-signature')
            tmp.set_param('micalg','pgp-sha1;')
            mail.replace_header('Content-Type',tmp['Content-Type'])
            mail.set_payload(None)
            mail.preamble = 'This is an OpenPGP/MIME signed message (RFC 4880 and 3156)'
            assert submsg.as_string()==plaintext, "plaintext was broken"
            mail.attach(submsg)
            submsg = Message()
            submsg.add_header('Content-Type','application/pgp-signature; name="signature.asc"')
            submsg.add_header('Content-Description', 'OpenPGP digital signature')
            submsg.add_header('Content-Disposition','attachment; filename="signature.asc"')
            submsg.set_payload(signature)
            mail.attach(submsg)
            if verify:
                vresult = self.verify_str(mail.get_payload(0).as_string(),signature)
                if not vresult: return None, result
        return mail, result

    def encrypt(self, mail, sign=True, inline = False, verify=False, **kwargs):
        """Encrypts an email for the recipients in To/CC.
        
        :param mail: A string or email
        :type mail: string or Message object
        :param sign: Whether to sign the mail with the sender's (From) signature
        :type sign: bool
        :param inline: Whether to use the PGP inline format for messages with attachments, i.e. no multipart.
        :type inline: bool
        :param verify: Whether to verify the encrypted mail immediately
        :type verify: bool
        :returns: The encrypted email (None if it fails) and the encryption details.
        :rtype: (Message,dict)
        """
        import email.utils
        from email.message import Message
        from email.parser import HeaderParser, Parser
        from .mail import _mail_addreplace_header
        if type(mail)==str: mail = Parser().parsestr(mail)
        elif not isinstance(mail,Message): return None, None
        if sign and not 'default_key' in kwargs:
            sender = mail.get('from', [])
            if sender: kwargs['default_key'] = email.utils.parseaddr(sender)[1]
        tos = mail.get_all('to', [])
        ccs = mail.get_all('cc', [])
        recipients = [email.utils.formataddr(to) for to in email.utils.getaddresses(tos + ccs)]
        plaintext, submsg = self._plaintext(mail, inline, protect=False)
        # Do encryption, report errors
        kwargs['sign'] = sign
        kwargs['armor'] = True
        result = self.encrypt_str(plaintext, recipients, **kwargs)
        if not result: return None, result
        ciphertext = str(result)
        if verify:
            vresult = self.decrypt_str(ciphertext, **kwargs)
            if not vresult: return None, result
            if sign and not result.key_id: return None, result
        # Compile encrypted message
        encmail = HeaderParser().parsestr(mail.as_string())
        _mail_addreplace_header(encmail,'Content-Transfer-Encoding','7bit')
        if not mail.is_multipart() and inline:
            encmail.set_payload(ciphertext)
            encmail.set_param('x-action','pgp-encrypted')
        else:
            # workaround to preserve header order
            tmp = Message()
            tmp['Content-Type'] = encmail['Content-Type']
            tmp.set_type('multipart/encrypted')
            tmp.set_param('protocol','application/pgp-encrypted')
            encmail.replace_header('Content-Type',tmp['Content-Type'])
            encmail.preamble = 'This is an OpenPGP/MIME signed message (RFC 4880 and 3156)'
            encmail.set_payload(None)
            submsg = Message()
            submsg.add_header('Content-Type','application/pgp-encrypted')
            submsg.set_payload('Version: 1\n')
            encmail.attach(submsg)
            submsg = Message()
            submsg.add_header('Content-Type','application/octet-stream; name="encrypted.asc"')
            submsg.add_header('Content-Description', 'OpenPGP encrypted message')
            submsg.add_header('Content-Disposition','inline; filename="encrypted.asc"')
            submsg.set_payload(ciphertext)
            encmail.attach(submsg)
        return encmail, result

class GPGMIME(PGPMIME):
    "A PGP implementation based on GPG and the gnupg module"
    
    def __init__(self, gpg, default_key=None):
        "initialize with a gnupg instance and optionally a default_key (keyid,passphrase) tuple"
        self.gpg = gpg
        if not default_key: pass
        elif type(default_key)==str:
            defkey = self.find_key(default_key,secret=True)
            if defkey: default_key = defkey
        elif len(default_key)==2 and default_key[0]:
            defkey = self.find_key(default_key[0],secret=True)
            if defkey: default_key = (defkey,default_key[0])
        else: assert False, "default_key must be keyid or (keyid,passphrase)"
        super(GPGMIME,self).__init__(default_key)

    def _set_default_key(self,kwargs):
        if self.default_key and 'default_key' in kwargs:
            key = kwargs['default_key']
            if not key:
                del kwargs['default_key']
                return kwargs
            if type(self.default_key) in (tuple,list):
                defkey,passphrase= self.default_key
            else:
                defkey,passphrase= self.default_key,None
            if key==True:
                kwargs['default_key'] = defkey
            elif key != defkey:
                 return kwargs
            if not 'passphrase' in kwargs and passphrase:
                kwargs['passphrase'] = passphrase
        return kwargs

    def find_key(self,addr,secret=False):
        """find key (fingerprint) for email 'addr' or return None.
        If addr is a list or tuple, return a dict(addr:keyid) """
        import email.utils
        if type(addr) in (list,tuple):
            result = {}
            for a in addr: result[a] = self.find_key(a,secret)
            return result
        addr = email.utils.parseaddr(addr)[1]
        if not addr: return None
        for key in self.gpg.list_keys(secret):
            for uid in key['uids']:
                if uid.find(addr)>=0:
                    return key['keyid']
        return None

    def _sign_params(self, kwargs):
        if 'default_key' in kwargs:
            defkey = kwargs['default_key']
            if type(defkey)!=bool:
                defkey = self.find_key(defkey,secret=True)
                if defkey: kwargs['default_key'] = defkey
        elif self.default_key:
            kwargs['default_key'] = True
        return self._set_default_key(kwargs)

    def sign_file(self, file, **kwargs):
        return self.gpg.sign(file, **self._sign_params(kwargs))

    def sign_str(self, data, **kwargs):
        return self.gpg.sign(data, **self._sign_params(kwargs))

    def verify_file(self, file, signature=None):
        return self.gpg.verify_file(file,signature)

    def verify_str(self, data, signature=None):
        import gnupg
        f = gnupg._util._make_binary_stream(data, self.gpg._encoding)
        if signature:
            import os, tempfile
            tmp = tempfile.NamedTemporaryFile(prefix='gnupg',delete=False)
            fd = tmp.file
            fn = tmp.name
            fd.write(signature)
            fd.close()
            try: result = self.gpg.verify_file(f,fn)
            finally: os.unlink(fn)
        else:
            result = self.gpg.verify_file(f)
        f.close()
        return result

    def _encrypt_params(self, recipients, kwargs):
        if 'sign' in kwargs:
            if kwargs['sign']: kwargs['default_key'] = kwargs['sign']
            del kwargs['sign']
        if 'default_key' in kwargs:
            defkey = kwargs['default_key']
            if type(defkey)!=bool:
                defkey = self.find_key(defkey,secret=True)
                if defkey: kwargs['default_key'] = defkey
        kwargs = self._set_default_key(kwargs)
        fingerprints = []
        for recipient in recipients:
            key = self.find_key(recipient)
            if key: fingerprints.append(key)
            else: fingerprints.append(recipient)
        return fingerprints, kwargs

    def encrypt_file(self, file, recipients, **kwargs):
        recipients, kwargs = self._encrypt_params(recipients, kwargs)
        return self.gpg._encrypt(file, recipients, **kwargs)

    def encrypt_str(self, data, recipients, **kwargs):
        recipients, kwargs = self._encrypt_params(recipients, kwargs)
        return self.gpg.encrypt(data, *recipients, **kwargs)

    def decrypt_file(self, file, **kwargs):
        return self.gpg.decrypt_file(file, **self._set_default_key(kwargs))
    
    def decrypt_str(self, data, **kwargs):
        return self.gpg.decrypt(data, **self._set_default_key(kwargs))
