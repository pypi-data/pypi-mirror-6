import sys
import optparse
import rfZenHan

converters = {}
converters['normalize']     = rfZenHan.normalizeI
converters['normalizeCIFS'] = rfZenHan.normalizeCIFSI
converters['doshirouto']    = rfZenHan.doshiroutoI
converters['z2h']           = rfZenHan.z2hI
converters['h2z']           = rfZenHan.h2zI
converters['z2hNum']        = rfZenHan.z2hNumI
converters['h2zNum']        = rfZenHan.h2zNumI
converters['z2hSym']        = rfZenHan.z2hSymI
converters['h2zSym']        = rfZenHan.h2zSymI
converters['z2hAlpha']      = rfZenHan.z2hAlphaI
converters['h2zAlpha']      = rfZenHan.h2zAlphaI
converters['z2hKana']       = rfZenHan.z2hKanaI
converters['h2zKana']       = rfZenHan.h2zKanaI
converters['z2hKanaK']      = rfZenHan.z2hKanaKI
converters['h2zKanaK']      = rfZenHan.h2zKanaKI
converters['z2hKanaD']      = rfZenHan.z2hKanaDI
converters['h2zKanaD']      = rfZenHan.h2zKanaDI
converters['z2hCP932']      = rfZenHan.z2hCP932I
converters['h2zCP932']      = rfZenHan.h2zCP932I
converters['z2hCIFS']       = rfZenHan.z2hCIFSI
converters['h2zCIFS']       = rfZenHan.h2zCIFSI

parser = optparse.OptionParser(usage='Usage: rfZenHan [options] [files]')
parser.add_option('-e', '--encode', dest='encode', default=sys.stdin.encoding or sys.stdout.encoding, help='input text encoding.')
parser.add_option('-c', '--converter', dest='converter', default='normalize', help='convert method. (default: normalize) value: ' + ' '.join(sorted(converters.keys())))
(options, args) = parser.parse_args()

inputs = []
if args:
	for i in range(len(args)):
		inputs.append(open(args[i]))
else:
	inputs.append(sys.stdin)

rfzh = converters[options.converter]()
for i in range(len(inputs)):
	text = unicode(inputs[i].read(), options.encode)
	sys.stdout.write(rfzh.conv(text).encode(options.encode))
