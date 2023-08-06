Python 3.4.0 (v3.4.0:04f714765c13, Mar 16 2014, 19:24:06) [MSC v.1600 32 bit (Intel)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> movies = ["AAA", 1975, "BBB", 91, ["CCC", ["DDD","EEE","FFF", "GGG", "HHH"]]]
>>> print(movies)
['AAA', 1975, 'BBB', 91, ['CCC', ['DDD', 'EEE', 'FFF', 'GGG', 'HHH']]]
>>> def print_lol(the_list):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)
print_lol(movies)
SyntaxError: invalid syntax
>>> def print_lol(the_list):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)
print_lol(movies)
SyntaxError: invalid syntax
>>> def print_lol(the_list):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)

			
>>> print_lol(movies)
AAA
1975
BBB
91
CCC
DDD
EEE
FFF
GGG
HHH
>>> def print_lol2(the_list, level):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item, level)
		else:
			print(each_item)

			
>>> print_lol2(movies,0)
AAA
1975
BBB
91
Traceback (most recent call last):
  File "<pyshell#15>", line 1, in <module>
    print_lol2(movies,0)
  File "<pyshell#14>", line 4, in print_lol2
    print_lol(each_item, level)
TypeError: print_lol() takes 1 positional argument but 2 were given
>>> def print_lol2(the_list, level):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol2(each_item, level)
		else:
			print(each_item)

			
>>> print_lol2(movies,0)
AAA
1975
BBB
91
CCC
DDD
EEE
FFF
GGG
HHH
>>> print_lol2(movies,1)
AAA
1975
BBB
91
CCC
DDD
EEE
FFF
GGG
HHH
>>> print_lol2(movies,2)
AAA
1975
BBB
91
CCC
DDD
EEE
FFF
GGG
HHH
>>> def print_lol2(the_list, level):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol2(each_item, level+1)
		else:
			print(each_item)

			
>>> print_lol2(movies,0)
AAA
1975
BBB
91
CCC
DDD
EEE
FFF
GGG
HHH
>>> def print_lol3(the_list, level):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol3(each_item, level)
		else:
			for tab_stop in range(level):
				print("\t",end='')
			print(each_item)

			
>>> print_lol3(movies,0)
AAA
1975
BBB
91
CCC
DDD
EEE
FFF
GGG
HHH
>>> print_lol3(movies,1)
	AAA
	1975
	BBB
	91
	CCC
	DDD
	EEE
	FFF
	GGG
	HHH
>>> def print_lol4(the_list, level):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol4(each_item, level+1)
		else:
			for tab_stop in range(level):
				print("\t",end='')
			print(each_item)

			
>>> print_lol4(movies,1)
	AAA
	1975
	BBB
	91
		CCC
			DDD
			EEE
			FFF
			GGG
			HHH
>>> print_lol4(movies,0)
AAA
1975
BBB
91
	CCC
		DDD
		EEE
		FFF
		GGG
		HHH
>>> 
