# -*- coding: UTF-8 -*-
'''这是一个"nester.py"模块，包含递归方式打印嵌套列表的方法
'''
def p(l):
	for i in l:
		if isinstance(i,list):
			p(i)
		else:
			print(i)








			
