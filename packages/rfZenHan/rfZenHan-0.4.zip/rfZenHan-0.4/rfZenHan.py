# -*- coding: utf-8 -*-

# rfZenHan.py 全角半角その他を変換するライブラリです。
# ・文字種別ごとに全角半角を変換できる。
# ・cp932(Windows-31J)の特殊文字を一般化できる。
# ・ファイルシステム上安全な文字に変換できる。
# ・個別に変換ルールを設定することで、英数記号は半角、カナは全角といった変換が一発で可能。
# ・PerlのライブラリUnicode::Japaneseの全角半角変換メソッド互換。
#   http://d.hatena.ne.jp/dayflower/20060530/1148951624
#
# 使い方：
u"""
>>> import rfZenHan
>>> print rfZenHan.h2z(u" 012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ㈱:")
　０１２ＡＢＣａｂｃ！＠＃アイウガダパ㈱：
>>> rfzh = rfZenHan.z2hI()
>>> print rfzh.conv(u"　０１２ＡＢＣａｂｃ！＠＃アイウガダパ(株)：")
 012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ(株):
>>> rfzh = rfZenHan.rfZenHan() # use Normalize
>>> print rfzh.conv(u"　０１２ＡＢＣａｂｃ！＠＃ｱｲｳｶﾞﾀﾞﾊﾟ㈱:")
 012ABCabc!@#アイウガダパ(株):
>>> hoge2fuga = (["hoge"], ["fuga"], [{"e": 3}])
>>> rfzh = rfZenHan.rfZenHan(hoge2fuga)
>>> print rfzh.conv(u"hohogege")
hofugage
"""
#
# 注意！：
#  変換対象文字列はUnicode前提です。
#  変換されてない場合は事前に変換して渡してください。
#   # リテラルの場合は""の前にuをつける。
#   print rfZenHan.h2z(u" 012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ㈱:")
#   # それ以外はunicode()関数で変換する。
#   print rfZenHan.h2z(unicode(utf8str, "utf-8"))

# 変換テーブル 数字
zNumberL = [u"０", u"１", u"２", u"３", u"４", u"５", u"６", u"７", u"８", u"９"]
hNumberL = [u"0" , u"1" , u"2" , u"3" , u"4" , u"5" , u"6" , u"7" , u"8" , u"9" ]
zNumberB = {}
hNumberB = {}

# 変換テーブル ASCII記号
zSymbolL = [u"　", u"！", u"”", u"＃", u"＄", u"％", u"＆", u"’", u"（", u"）", u"＊"
          , u"＋", u"，", u"－", u"．", u"／", u"：", u"；", u"＜", u"＝", u"＞", u"？"
          , u"＠", u"［", u"￥", u"］", u"＾", u"＿", u"‘", u"｛", u"｜", u"｝"]
hSymbolL = [u" " , u"!" , u"\"", u"#" , u"$" , u"%" , u"&" , u"'" , u"(" , u")" , u"*"
          , u"+" , u"," , u"-" , u"." , u"/" , u":" , u";" , u"<" , u"=" , u">" , u"?"
          , u"@" , u"[" , u"\\", u"]" , u"^" , u"_" , u"`" , u"{" , u"|" , u"}" ]
zSymbolB = {}
hSymbolB = {}

# 変換テーブル アルファベット
zAlphaL = [u"Ａ", u"Ｂ", u"Ｃ", u"Ｄ", u"Ｅ", u"Ｆ", u"Ｇ", u"Ｈ", u"Ｉ"
         , u"Ｊ", u"Ｋ", u"Ｌ", u"Ｍ", u"Ｎ", u"Ｏ", u"Ｐ", u"Ｑ", u"Ｒ"
         , u"Ｓ", u"Ｔ", u"Ｕ", u"Ｖ", u"Ｗ", u"Ｘ", u"Ｙ", u"Ｚ"
         , u"ａ", u"ｂ", u"ｃ", u"ｄ", u"ｅ", u"ｆ", u"ｇ", u"ｈ", u"ｉ"
         , u"ｊ", u"ｋ", u"ｌ", u"ｍ", u"ｎ", u"ｏ", u"ｐ", u"ｑ", u"ｒ"
         , u"ｓ", u"ｔ", u"ｕ", u"ｖ", u"ｗ", u"ｘ", u"ｙ", u"ｚ"]
hAlphaL = [u"A",  u"B",  u"C",  u"D",  u"E",  u"F",  u"G",  u"H",  u"I"
         , u"J",  u"K",  u"L",  u"M",  u"N",  u"O",  u"P",  u"Q",  u"R"
         , u"S",  u"T",  u"U",  u"V",  u"W",  u"X",  u"Y",  u"Z"
         , u"a",  u"b",  u"c",  u"d",  u"e",  u"f",  u"g",  u"h",  u"i"
         , u"j",  u"k",  u"l",  u"m",  u"n",  u"o",  u"p",  u"q",  u"r"
         , u"s",  u"t",  u"u",  u"v",  u"w",  u"x",  u"y",  u"z" ]
zAlphaB = {}
hAlphaB = {}

# 変換テーブル カナ
zKanaL = [u"ア", u"イ", u"ウ", u"エ", u"オ"
        , u"カ", u"キ", u"ク", u"ケ", u"コ"
        , u"サ", u"シ", u"ス", u"セ", u"ソ"
        , u"タ", u"チ", u"ツ", u"テ", u"ト"
        , u"ナ", u"ニ", u"ヌ", u"ネ", u"ノ"
        , u"ハ", u"ヒ", u"フ", u"ヘ", u"ホ"
        , u"マ", u"ミ", u"ム", u"メ", u"モ"
        , u"ヤ"       , u"ユ"       , u"ヨ"
        , u"ラ", u"リ", u"ル", u"レ", u"ロ"
        , u"ワ"                     , u"ヲ"
        , u"ガ", u"ギ", u"グ", u"ゲ", u"ゴ"
        , u"ザ", u"ジ", u"ズ", u"ゼ", u"ゾ"
        , u"ダ", u"ヂ", u"ヅ", u"デ", u"ド"
        , u"バ", u"ビ", u"ブ", u"ベ", u"ボ"
        , u"パ", u"ピ", u"プ", u"ペ", u"ポ"
        , u"ァ", u"ィ", u"ゥ", u"ェ", u"ォ"
        , u"ャ"       , u"ュ"       , u"ョ"
        , u"ヴ", u"ン", u"ッ", u"ー", u"゛", u"゜"
        , u"、", u"。", u"・", u"「", u"」"]
hKanaL = [u"ｱ" , u"ｲ" , u"ｳ" , u"ｴ" , u"ｵ"
        , u"ｶ" , u"ｷ" , u"ｸ" , u"ｹ" , u"ｺ"
        , u"ｻ" , u"ｼ" , u"ｽ" , u"ｾ" , u"ｿ"
        , u"ﾀ" , u"ﾁ" , u"ﾂ" , u"ﾃ" , u"ﾄ"
        , u"ﾅ" , u"ﾆ" , u"ﾇ" , u"ﾈ" , u"ﾉ"
        , u"ﾊ" , u"ﾋ" , u"ﾌ" , u"ﾍ" , u"ﾎ"
        , u"ﾏ" , u"ﾐ" , u"ﾑ" , u"ﾒ" , u"ﾓ"
        , u"ﾔ"        , u"ﾕ"        , u"ﾖ"
        , u"ﾗ" , u"ﾘ" , u"ﾙ" , u"ﾚ" , u"ﾛ"
        , u"ﾜ"                      , u"ｦ"
        , u"ｶﾞ", u"ｷﾞ", u"ｸﾞ", u"ｹﾞ", u"ｺﾞ"
        , u"ｻﾞ", u"ｼﾞ", u"ｽﾞ", u"ｾﾞ", u"ｿﾞ"
        , u"ﾀﾞ", u"ﾁﾞ", u"ﾂﾞ", u"ﾃﾞ", u"ﾄﾞ"
        , u"ﾊﾞ", u"ﾋﾞ", u"ﾌﾞ", u"ﾍﾞ", u"ﾎﾞ"
        , u"ﾊﾟ", u"ﾋﾟ", u"ﾌﾟ", u"ﾍﾟ", u"ﾎﾟ"
        , u"ｧ" , u"ｨ" , u"ｩ" , u"ｪ" , u"ｫ"
        , u"ｬ"        , u"ｭ"        , u"ｮ"
        , u"ｳﾞ", u"ﾝ" , u"ｯ" , u"ｰ" , u"ﾞ" , u"ﾟ"
        , u"､" , u"｡" , u"･" , u"｢" , u"｣"]
# 変換補助テーブル 濁点・半濁点の前方向の変換候補を探す深さ。
zKanaB = {}
hKanaB = {u"ﾞ": 1 , u"ﾟ": 1}

# 変換テーブル 全角カナの濁点・半濁点を分離する。
zKanaKL = [u"カ゛", u"キ゛", u"ク゛", u"ケ゛", u"コ゛"
         , u"サ゛", u"シ゛", u"ス゛", u"セ゛", u"ソ゛"
         , u"タ゛", u"チ゛", u"ツ゛", u"テ゛", u"ト゛"
         , u"ハ゛", u"ヒ゛", u"フ゛", u"ヘ゛", u"ホ゛"
         , u"ハ゜", u"ヒ゜", u"フ゜", u"ヘ゜", u"ホ゜"
         , u"ウ゛"]
hKanaKL = [u"ガ", u"ギ", u"グ", u"ゲ", u"ゴ"
         , u"ザ", u"ジ", u"ズ", u"ゼ", u"ゾ"
         , u"ダ", u"ヂ", u"ヅ", u"デ", u"ド"
         , u"バ", u"ビ", u"ブ", u"ベ", u"ボ"
         , u"パ", u"ピ", u"プ", u"ペ", u"ポ"
         , u"ヴ"]
# 変換補助テーブル 濁点・半濁点の前方向の変換候補を探す深さ。
zKanaKB = {u"゛": 1, u"゜": 1}
hKanaKB = {}

# 変換テーブル 濁点・半濁点のつく文字のみ変換。
zKanaDL = [u"ガ", u"ギ", u"グ", u"ゲ", u"ゴ"
         , u"ザ", u"ジ", u"ズ", u"ゼ", u"ゾ"
         , u"ダ", u"ヂ", u"ヅ", u"デ", u"ド"
         , u"バ", u"ビ", u"ブ", u"ベ", u"ボ"
         , u"パ", u"ピ", u"プ", u"ペ", u"ポ"
         , u"ヴ"]
hKanaDL = [u"ｶﾞ", u"ｷﾞ", u"ｸﾞ", u"ｹﾞ", u"ｺﾞ"
         , u"ｻﾞ", u"ｼﾞ", u"ｽﾞ", u"ｾﾞ", u"ｿﾞ"
         , u"ﾀﾞ", u"ﾁﾞ", u"ﾂﾞ", u"ﾃﾞ", u"ﾄﾞ"
         , u"ﾊﾞ", u"ﾋﾞ", u"ﾌﾞ", u"ﾍﾞ", u"ﾎﾞ"
         , u"ﾊﾟ", u"ﾋﾟ", u"ﾌﾟ", u"ﾍﾟ", u"ﾎﾟ"
         , u"ｳﾞ"]
# 変換補助テーブル 濁点・半濁点の前方向の変換候補を探す深さ。
zKanaDB = {}
hKanaDB = {u"ﾞ": 1 , u"ﾟ": 1}

# 変換テーブル cp932(Windows Shift-JIS)の特殊文字を変換する。
#              (一般化の文字については検討の余地あり？)
zCP932L = [u"(1)" , u"(2)" , u"(3)" , u"(4)" , u"(5)" , u"(6)" , u"(7)" , u"(8)" , u"(9)" , u"(10)"
         , u"(11)", u"(12)", u"(13)", u"(14)", u"(15)", u"(16)", u"(17)", u"(18)", u"(19)", u"(20)"
         , u"I", u"II", u"III", u"IV", u"V", u"VI", u"VII", u"VIII", u"IX", u"X"
         , u"i", u"ii", u"iii", u"iv", u"v", u"vi", u"vii", u"viii", u"ix", u"x"
         , u"ミリ", u"キロ", u"センチ", u"メートル", u"グラム", u"トン", u"アール", u"ヘクタール"
         , u"リットル", u"ワット", u"カロリー", u"ドル", u"セント", u"パーセント", u"ミリバール", u"ページ"
         , u"mm", u"cm", u"km", u"mg", u"kg", u"cc", u"m2", u"No.", u"K.K.", u"Tel"
         , u"“", u"”", u"(上)", u"(中)", u"(下)", u"(左)", u"(右)"
         , u"(株)", u"(有)", u"(代)", u"明治", u"大正", u"昭和", u"平成"]
hCP932L = [u"①", u"②", u"③", u"④", u"⑤", u"⑥", u"⑦", u"⑧", u"⑨", u"⑩"
         , u"⑪", u"⑫", u"⑬", u"⑭", u"⑮", u"⑯", u"⑰", u"⑱", u"⑲", u"⑳"
         , u"Ⅰ", u"Ⅱ", u"Ⅲ", u"Ⅳ", u"Ⅴ", u"Ⅵ", u"Ⅶ", u"Ⅷ", u"Ⅸ", u"Ⅹ"
         , u"ⅰ", u"ⅱ", u"ⅲ", u"ⅳ", u"ⅴ", u"ⅵ", u"ⅶ", u"ⅷ", u"ⅸ", u"ⅹ"
         , u"㍉", u"㌔", u"㌢", u"㍍", u"㌘", u"㌧", u"㌃", u"㌶"
         , u"㍑", u"㍗", u"㌍", u"㌦", u"㌣", u"㌫", u"㍊", u"㌻"
         , u"㎜", u"㎝", u"㎞", u"㎎", u"㎏", u"㏄", u"㎡", u"№", u"㏍", u"℡"
         , u"〝", u"〟", u"㊤", u"㊥", u"㊦", u"㊧", u"㊨"
         , u"㈱", u"㈲", u"㈹", u"㍾", u"㍽", u"㍼", u"㍻"]
# 変換補助テーブル 各文字の末尾から前方向の変換候補を探す深さ。
zCP932B = {u")": 3, u"I": 3, u"V": 1, u"X": 1, u"i": 3, u"v": 1, u"x": 1
         , u"リ": 1, u"ロ": 1, u"チ": 2, u"ル": 4, u"ム": 2, u"ン": 1, u"ト": 4, u"ー": 3, u"ジ": 2
         , u"m": 1, u"g": 1, u"c": 1, u"2": 1, u".": 3, u"l": 2
         , u"治": 1, u"正": 1, u"和": 1, u"成": 1}
hCP932B = {}

# 変換テーブル CIFS上で複数のOSからアクセスする際の安全性を考慮する。
zCIFSL = [u"／", u"￥", u"＊", u"？", u"：", u"＜", u"＞", u"｜", u"_"]
hCIFSL = [u"/" , u"\\", u"*" , u"?" , u":" , u"<" , u">" , u"|" , u" "]
zCIFSB = {}
hCIFSB = {}

def marge_types(types):
	(mfr, mto, mdes) = ([], [], [])
	for type in types:
		(fr, to, des) = type
		mfr  += fr
		mto  += to
		mdes += des
	return (mfr, mto, mdes)

# 変換プリセット 通常はZ2H、H2Z、Normalizeを使うのがよいでしょう。
# 変換ルールセットを自分で組み合わせて使うことも出来ます。
Z2HNum   = (zNumberL, hNumberL, [zNumberB])
H2ZNum   = (hNumberL, zNumberL, [hNumberB])
Z2HSym   = (zSymbolL, hSymbolL, [zSymbolB])
H2ZSym   = (hSymbolL, zSymbolL, [hSymbolB])
Z2HAlpha = (zAlphaL , hAlphaL , [zAlphaB])
H2ZAlpha = (hAlphaL , zAlphaL , [hAlphaB])
Z2HKana  = (zKanaL  , hKanaL  , [zKanaB])
H2ZKana  = (hKanaL  , zKanaL  , [hKanaB])
zKanaK   = (zKanaKL , hKanaKL , [zKanaKB])
hKanaK   = (hKanaKL , zKanaKL , [hKanaKB])
Z2HKanaK = marge_types([Z2HKana, zKanaK])
H2ZKanaK = marge_types([H2ZKana, hKanaK])
Z2HKanaD = (zKanaDL , hKanaDL , [zKanaDB])
H2ZKanaD = (hKanaDL , zKanaDL , [hKanaDB])
Z2HCP932 = (zCP932L , hCP932L , [zCP932B])
H2ZCP932 = (hCP932L , zCP932L , [hCP932B])
Z2HCIFS  = (zCIFSL  , hCIFSL  , [zCIFSB])
H2ZCIFS  = (hCIFSL  , zCIFSL  , [hCIFSB])
Z2H = marge_types([Z2HNum, Z2HSym, Z2HAlpha, Z2HKana])
H2Z = marge_types([H2ZNum, H2ZSym, H2ZAlpha, H2ZKana])
Doshirouto = marge_types([H2ZNum, H2ZSym, H2ZAlpha, Z2HKana, Z2HCP932, Z2HCIFS])
Normalize  = marge_types([Z2HNum, Z2HSym, Z2HAlpha, H2ZKana, H2ZCP932])
NormalizeCIFS = marge_types([Normalize, H2ZCIFS])

class rfZenHan:
	# コンストラクタ 変換ルールを指定します。デフォルトはNormalize
	def __init__(self, type = Normalize):
		self.table = {}
		self.depth = {}
		reverse = {}

		(fr, to, des) = type
		for ci in range(len(fr)):
			a = fr[ci]
			b = to[ci]
			self.table[a] = b
			# 置換のループを排除します。
			# "："=>":"があったときに":"=>"："が定義されたら
			# "："=>":"の定義を削除します。
			if b in self.table:
				del self.table[b]
			# 置換の連鎖を探して単純化します。
			# "ｶﾞ"=>"ガ"があったときに"ガ"=>"カ゛"が定義されたら
			# "ｶﾞ"=>"カ゛"に再定義します。
			if b not in reverse:
				reverse[b] = []
			reverse[b].append(a)
			if a in reverse:
				for o in reverse[a]:
					if o != b:
						self.table[o] = b
						reverse[b].append(o)
				del reverse[a]
		# 変換補助テーブルをセットします。
		# 同一文字がある場合は深さが最大のものを選択します。
		for de in des:
			for di in de.keys():
				if di in self.depth:
					if self.depth[di] < de[di]:
						self.depth[di] = de[di]
				else:
					self.depth[di] = de[di]

	# 実際の変換処理 濁点・半濁点の判定を容易にするため、後方から検索・置換してます。
	def conv(self, str):
		v = []
		i = len(str) - 1
		while(i > -1):
			c = str[i]
			if c in self.depth:
				for d in range(self.depth[c], -1, -1):
					cc = str[i - d:i + 1]
					if cc in self.table:
						c = self.table[cc]
						i = i - d
						break
			else:
				if c in self.table:
					c = self.table[c]
			v.append(c)
			i = i - 1

		v.reverse()
		return "".join(v)

# 英数記号は半角に、カナは全角に、cp932特殊文字は一般化します。
# コンストラクタのデフォルト値に設定されています。
def normalizeI():
	return rfZenHan(Normalize)

def normalize(str):
	u"""
	>>> print normalize(u" 012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ㈱:")
	 012ABCabc!@#アイウガダパ(株):
	"""
	return normalizeI().conv(str)

# normalizeに加えて、ファイルシステム上安全な文字に変換します。
def normalizeCIFSI():
	return rfZenHan(NormalizeCIFS)

def normalizeCIFS(str):
	u"""
	>>> print normalizeCIFS(u" 012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ㈱:")
	_012ABCabc!@#アイウガダパ(株)：
	"""
	return normalizeCIFSI().conv(str)

# お願いですからやめてください。
def doshiroutoI():
	return rfZenHan(Doshirouto)

def doshirouto(str):
	u"""
	>>> print doshirouto(u" 012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ㈱:")
	 ０１２ＡＢＣａｂｃ！＠＃ｱｲｳｶﾞﾀﾞﾊﾟ㈱:
	"""
	return doshiroutoI().conv(str)

# 英数記号カナを半角に変換します。
# PerlのUnicode::Japanese->z2h互換。
def z2hI():
	return rfZenHan(Z2H)

def z2h(str):
	u"""
	>>> print z2h(u"　０１２ＡＢＣａｂｃ！＠＃アイウガダパ(株)：")
	 012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ(株):
	"""
	return z2hI().conv(str)

# 英数記号カナを全角に変換します。
# PerlのUnicode::Japanese->h2z互換。
def h2zI():
	return rfZenHan(H2Z)

def h2z(str):
	u"""
	>>> print h2z(u" 012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ㈱:")
	　０１２ＡＢＣａｂｃ！＠＃アイウガダパ㈱：
	"""
	return h2zI().conv(str)

# 数字を半角に変換します。
# PerlのUnicode::Japanese->z2hNum互換。
def z2hNumI():
	return rfZenHan(Z2HNum)

def z2hNum(str):
	u"""
	>>> print z2hNum(u"　０１２ＡＢＣａｂｃ！＠＃アイウガダパ(株)：")
	　012ＡＢＣａｂｃ！＠＃アイウガダパ(株)：
	"""
	return z2hNumI().conv(str)

# 数字を全角に変換します。
# PerlのUnicode::Japanese->h2zNum互換。
def h2zNumI():
	return rfZenHan(H2ZNum)

def h2zNum(str):
	u"""
	>>> print h2zNum(u" 012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ㈱:")
	 ０１２ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ㈱:
	"""
	return h2zNumI().conv(str)

# ASCII記号を半角に変換します。
# PerlのUnicode::Japanese->z2hSym互換。
def z2hSymI():
	return rfZenHan(Z2HSym)

def z2hSym(str):
	u"""
	>>> print z2hSym(u"　０１２ＡＢＣａｂｃ！＠＃アイウガダパ(株)：")
	 ０１２ＡＢＣａｂｃ!@#アイウガダパ(株):
	"""
	return z2hSymI().conv(str)

# ASCII記号を全角に変換します。
# PerlのUnicode::Japanese->h2zSym互換。
def h2zSymI():
	return rfZenHan(H2ZSym)

def h2zSym(str):
	u"""
	>>> print h2zSym(u" 012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ㈱:")
	　012ABCabc！＠＃ｱｲｳｶﾞﾀﾞﾊﾟ㈱：
	"""
	return h2zSymI().conv(str)

# アルファベットを半角に変換します。
# PerlのUnicode::Japanese->z2hAlpha互換。
def z2hAlphaI():
	return rfZenHan(Z2HAlpha)

def z2hAlpha(str):
	u"""
	>>> print z2hAlpha(u"　０１２ＡＢＣａｂｃ！＠＃アイウガダパ(株)：")
	　０１２ABCabc！＠＃アイウガダパ(株)：
	"""
	return z2hAlphaI().conv(str)

# アルファベットを全角に変換します。
# PerlのUnicode::Japanese->h2zAlpha互換。
def h2zAlphaI():
	return rfZenHan(H2ZAlpha)

def h2zAlpha(str):
	u"""
	>>> print h2zAlpha(u" 012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ㈱:")
	 012ＡＢＣａｂｃ!@#ｱｲｳｶﾞﾀﾞﾊﾟ㈱:
	"""
	return h2zAlphaI().conv(str)

# カナを半角に変換します。
# PerlのUnicode::Japanese->z2hKana互換。
def z2hKanaI():
	return rfZenHan(Z2HKana)

def z2hKana(str):
	u"""
	>>> print z2hKana(u"　０１２ＡＢＣａｂｃ！＠＃アイウガダパ(株)：")
	　０１２ＡＢＣａｂｃ！＠＃ｱｲｳｶﾞﾀﾞﾊﾟ(株)：
	"""
	return z2hKanaI().conv(str)

# カナを全角に変換します。
# PerlのUnicode::Japanese->h2zKana互換。
def h2zKanaI():
	return rfZenHan(H2ZKana)

def h2zKana(str):
	u"""
	>>> print h2zKana(u" 012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ㈱:")
	 012ABCabc!@#アイウガダパ㈱:
	"""
	return h2zKanaI().conv(str)

# カナを半角に変換します。濁点・半濁点のつく文字は全角に変換します。
# PerlのUnicode::Japanese->z2hKanaK互換。
def z2hKanaKI():
	return rfZenHan(Z2HKanaK)

def z2hKanaK(str):
	u"""
	>>> print z2hKanaK(u"　０１２ＡＢＣａｂｃ！＠＃アイウガダパ(株)：")
	　０１２ＡＢＣａｂｃ！＠＃ｱｲｳガダパ(株)：
	"""
	return z2hKanaKI().conv(str)

# カナを全角に変換します。濁点・半濁点を分離します。
# PerlのUnicode::Japanese->h2zKanaK互換。
def h2zKanaKI():
	return rfZenHan(H2ZKanaK)

def h2zKanaK(str):
	u"""
	>>> print h2zKanaK(u" 012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ㈱:")
	 012ABCabc!@#アイウカ゛タ゛ハ゜㈱:
	"""
	return h2zKanaKI().conv(str)

# 濁点・半濁点のつくカナのみ半角に変換します。
# PerlのUnicode::Japanese->z2hKanaD互換。
def z2hKanaDI():
	return rfZenHan(Z2HKanaD)

def z2hKanaD(str):
	u"""
	>>> print z2hKanaD(u"　０１２ＡＢＣａｂｃ！＠＃アイウガダパ(株)：")
	　０１２ＡＢＣａｂｃ！＠＃アイウｶﾞﾀﾞﾊﾟ(株)：
	"""
	return z2hKanaDI().conv(str)

# 濁点・半濁点のつくカナのみ全角に変換します。
# PerlのUnicode::Japanese->h2zKanaD互換。
def h2zKanaDI():
	return rfZenHan(H2ZKanaD)

def h2zKanaD(str):
	u"""
	>>> print h2zKanaD(u" 012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ㈱:")
	 012ABCabc!@#ｱｲｳガダパ㈱:
	"""
	return h2zKanaDI().conv(str)

# cp932特殊文字に変換します。
# ※非推奨です！ 理由がない限り使うべきではありません！
def z2hCP932I():
	return rfZenHan(Z2HCP932)

def z2hCP932(str):
	u"""
	>>> print z2hCP932(u"　０１２ＡＢＣａｂｃ！＠＃アイウガダパ(株)：")
	　０１２ＡＢＣａｂｃ！＠＃アイウガダパ㈱：
	"""
	return z2hCP932I().conv(str)

# cp932特殊文字を一般化します。
def h2zCP932I():
	return rfZenHan(H2ZCP932)

def h2zCP932(str):
	u"""
	>>> print h2zCP932(u" 012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ㈱:")
	 012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ(株):
	"""
	return h2zCP932I().conv(str)

# ファイルシステム上、安全ではない文字に変換します。
# ※あえてこれを使うよりは、normalize、z2h、z2hSymを使うべきでしょう。
def z2hCIFSI():
	return rfZenHan(Z2HCIFS)

def z2hCIFS(str):
	u"""
	>>> print z2hCIFS(u"　０１２ＡＢＣａｂｃ！＠＃アイウガダパ(株)：")
	　０１２ＡＢＣａｂｃ！＠＃アイウガダパ(株):
	"""
	return z2hCIFSI().conv(str)

# ファイルシステム上、安全な文字に変換します。
def h2zCIFSI():
	return rfZenHan(H2ZCIFS)

def h2zCIFS(str):
	u"""
	>>> print h2zCIFS(u" 012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ㈱:")
	_012ABCabc!@#ｱｲｳｶﾞﾀﾞﾊﾟ㈱：
	"""
	return h2zCIFSI().conv(str)

if __name__ == "__main__":
	import doctest
	doctest.testmod()
