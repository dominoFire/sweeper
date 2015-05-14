#! /usr/bin/python3

import OpenSSL


key = OpenSSL.crypto.PKey()
key.generate_key(OpenSSL.crypto.TYPE_RSA, 1024)
cert = OpenSSL.crypto.X509()
cert.set_serial_number(0)
cert.get_subject().CN = "pulsarcloud"
cert.set_issuer(cert.get_subject())
cert.gmtime_adj_notBefore(0)
cert.gmtime_adj_notAfter(10*365*24*60*60)
cert.set_pubkey(key)
cert.sign( key, 'md5' )
open( "certificate.cer", 'wb' ).write(
  OpenSSL.crypto.dump_certificate( OpenSSL.crypto.FILETYPE_PEM, cert ) )
open( "private_key.pem", 'wb' ).write(
  OpenSSL.crypto.dump_privatekey( OpenSSL.crypto.FILETYPE_PEM, key ) )
p12 = OpenSSL.crypto.PKCS12()
p12.set_privatekey( key )
p12.set_certificate( cert )
open( "container.pfx", 'wb' ).write( p12.export() )
